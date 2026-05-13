"""Scrapy project settings — WordPress REST API crawling."""

BOT_NAME = "klinik_portal"

SPIDER_MODULES = ["scrapy_crawler.src.crawler.spiders"]
NEWSPIDER_MODULE = "scrapy_crawler.src.crawler.spiders"

ALLOWED_SCHEMES = ["http", "https"]
ROBOTSTXT_OBEY = False

CONCURRENT_REQUESTS = 2
DOWNLOAD_DELAY = 1.0

DEFAULT_REQUEST_HEADERS = {
    "Accept": "application/json",
    "Accept-Language": "da-DK,da;q=0.9,en-US;q=0.8,en;q=0.7",
    "Accept-Encoding": "gzip, deflate, br",
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    ),
}

LOG_LEVEL = "INFO"
REQUEST_FINGERPRINTER_IMPLEMENTATION = "2.7"
