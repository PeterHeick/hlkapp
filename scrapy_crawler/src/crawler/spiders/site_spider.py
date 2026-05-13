"""Site spider: WordPress REST API-baseret dataudtræk."""
from __future__ import annotations

import json
import re
from urllib.parse import urljoin, urlparse

import scrapy
from bs4 import BeautifulSoup
from klinik.config import settings

from scrapy_crawler.src.crawler.db import get_connection, init_db, page_count

WP_API_ENDPOINTS = [
    "/wp-json/wp/v2/pages?per_page=100",
    "/wp-json/wp/v2/posts?per_page=100",
]


class SiteSpider(scrapy.Spider):
    name = "site_spider"
    custom_settings = {
        "ITEM_PIPELINES": {"scrapy_crawler.src.crawler.pipelines.SqlitePipeline": 300},
        "HANDLE_HTTPSTATUS_LIST": [301, 302, 303, 307, 308, 404, 410, 500, 503],
    }

    @staticmethod
    def _normalize_domain(netloc: str) -> str:
        netloc = netloc.lower()
        if netloc.startswith("www."):
            netloc = netloc[4:]
        return netloc

    def __init__(self, start_url: str, max_depth: int = 5, *args, **kwargs) -> None:  # type: ignore[override]
        super().__init__(*args, **kwargs)
        start_url = re.sub(r'^(https?://)https?://', r'\1', start_url.strip())
        parsed = urlparse(start_url)
        if parsed.scheme not in ("http", "https"):
            raise ValueError(f"Ugyldigt scheme '{parsed.scheme}' — kun http/https er tilladt.")
        self._base_url = f"{parsed.scheme}://{parsed.netloc}"
        self._domain = parsed.netloc
        self._domain_norm = self._normalize_domain(parsed.netloc)
        conn = get_connection()
        init_db(conn)
        conn.close()

    def start_requests(self):  # type: ignore[override]
        for path in WP_API_ENDPOINTS:
            yield scrapy.Request(
                self._base_url + path,
                callback=self.parse_api_list,
                errback=self.handle_error,
                meta={"endpoint_path": path, "page": 1},
            )
        yield scrapy.Request(
            self._base_url + "/wp-json/wp/v2/menu-items?per_page=100",
            callback=self.parse_menu_items,
            errback=self.handle_menu_error,
        )
        # Hent forsiden som HTML for at ekstrahere navigationslinks fra <nav>
        yield scrapy.Request(
            self._base_url + "/",
            callback=self.parse_homepage_html,
            errback=self.handle_menu_error,
            meta={"handle_httpstatus_list": []},  # lad Scrapy følge redirects
        )

    def parse_api_list(self, response):  # type: ignore[override]
        conn = get_connection()
        count = page_count(conn)
        conn.close()
        if count >= settings.max_pages:
            self.logger.warning("Hukommelsesgrænse nået: %d sider.", settings.max_pages)
            return

        try:
            items = json.loads(response.text)
        except json.JSONDecodeError:
            self.logger.error("Ugyldigt JSON-svar fra %s", response.url)
            return

        if not isinstance(items, list):
            return

        for item in items:
            page_url = item.get("link", "")
            if not page_url:
                continue
            page_url = page_url.split("#")[0].rstrip("?") or page_url
            raw_content = item.get("content", {}).get("rendered", "")
            word_count = self._word_count(raw_content)
            title = item.get("title", {}).get("rendered", "")
            title = BeautifulSoup(title, "html.parser").get_text().strip()

            yield {
                "url": page_url,
                "status_code": 200,
                "depth": 1,
                "parent_url": None,
                "title": title,
                "word_count": word_count,
                "redirect_chain": "[]",
            }
            yield from self._extract_links(page_url, raw_content)

        total_pages = int(response.headers.get("X-WP-TotalPages", 1))
        current_page = response.meta.get("page", 1)
        if current_page < total_pages:
            endpoint_path = response.meta["endpoint_path"]
            base_path = endpoint_path.split("?")[0]
            params = endpoint_path.split("?")[1] if "?" in endpoint_path else ""
            param_parts = [p for p in params.split("&") if not p.startswith("page=")]
            param_parts.append(f"page={current_page + 1}")
            next_path = base_path + "?" + "&".join(param_parts)
            yield scrapy.Request(
                self._base_url + next_path,
                callback=self.parse_api_list,
                errback=self.handle_error,
                meta={"endpoint_path": next_path, "page": current_page + 1},
            )

    def _word_count(self, html_content: str) -> int:
        if not html_content:
            return 0
        return len(BeautifulSoup(html_content, "html.parser").get_text().split())

    def _extract_links(self, source_url: str, html_content: str):  # type: ignore[return]
        if not html_content:
            return
        soup = BeautifulSoup(html_content, "html.parser")
        for tag in soup.find_all("a", href=True):
            abs_url = urljoin(source_url, tag["href"])
            parsed = urlparse(abs_url)
            if parsed.scheme not in ("http", "https"):
                continue
            if self._normalize_domain(parsed.netloc) != self._domain_norm:
                continue
            clean = abs_url.split("#")[0].rstrip("?") or abs_url
            yield {"_link": True, "source": source_url, "target": clean}

    def parse_menu_items(self, response):  # type: ignore[override]
        try:
            items = json.loads(response.text)
        except json.JSONDecodeError:
            return
        if not isinstance(items, list):
            return
        id_to_url: dict[int, str] = {}
        for item in items:
            item_url = item.get("url", "").split("#")[0].rstrip("?")
            if item_url and self._normalize_domain(urlparse(item_url).netloc) == self._domain_norm:
                id_to_url[item["id"]] = item_url
        for item in items:
            target = item.get("url", "").split("#")[0].rstrip("?")
            if not target or self._normalize_domain(urlparse(target).netloc) != self._domain_norm:
                continue
            parent_id = item.get("parent", 0)
            root = self._base_url + "/"
            source = id_to_url.get(parent_id, root) if parent_id else root
            if source != target:
                yield {"_link": True, "source": source, "target": target}

    def parse_homepage_html(self, response):  # type: ignore[override]
        """Ekstraher navigationshierarki fra homepage HTML som supplement til menu-items API."""
        soup = BeautifulSoup(response.text, "html.parser")
        root_url = self._base_url + "/"
        count = 0
        for nav in soup.find_all("nav"):
            ul = nav.find("ul")
            if ul:
                for item in self._nav_ul_links(ul, root_url):
                    count += 1
                    yield item
        self.logger.info("Navigationshierarki fra homepage HTML: %d links", count)

    def _nav_ul_links(self, ul_element, parent_url: str):  # type: ignore[return]
        """Rekursivt udtræk parent→child-links fra <ul>/<li>-hierarki."""
        for li in ul_element.find_all("li", recursive=False):
            # Find <a> direkte i <li> (ikke i nested sub-menu)
            link = li.find("a", recursive=False, href=True)
            if not link:
                link = li.find("a", href=True)
            if not link:
                continue
            abs_url = urljoin(self._base_url + "/", link["href"])
            parsed = urlparse(abs_url)
            if parsed.scheme not in ("http", "https"):
                continue
            if self._normalize_domain(parsed.netloc) != self._domain_norm:
                continue
            clean = abs_url.split("#")[0].rstrip("?") or abs_url
            if clean and clean != parent_url:
                yield {"_link": True, "source": parent_url, "target": clean}
            sub_ul = li.find("ul")
            if sub_ul:
                yield from self._nav_ul_links(sub_ul, clean)

    def handle_menu_error(self, failure) -> None:  # type: ignore[override]
        self.logger.info("menu-items endpoint ikke tilgængeligt: %s", failure.value)

    def handle_error(self, failure):  # type: ignore[override]
        req = failure.request
        self.logger.error("Anmodning fejlede: %s — %s", req.url, failure.value)
        yield {
            "url": req.url,
            "status_code": 0,
            "depth": 1,
            "parent_url": None,
            "title": "",
            "word_count": 0,
            "redirect_chain": "[]",
        }
