// KlinikPortal — components

// ─── Icons (inline SVG, lucide-style hairline) ─────────────────────
const Ico = ({ d, size = 18, stroke = 1.75, ...rest }) => (
  <svg width={size} height={size} viewBox="0 0 24 24" fill="none"
       stroke="currentColor" strokeWidth={stroke}
       strokeLinecap="round" strokeLinejoin="round" {...rest}>
    {d}
  </svg>
);

const I = {
  // Brand mark — laser/zap
  Spark: (p) => <Ico {...p} d={<>
    <path d="M12 2v4M12 18v4M4.93 4.93l2.83 2.83M16.24 16.24l2.83 2.83M2 12h4M18 12h4M4.93 19.07l2.83-2.83M16.24 7.76l2.83-2.83"/>
  </>}/>,
  // Globe (SEO)
  Globe: (p) => <Ico {...p} d={<>
    <circle cx="12" cy="12" r="10"/>
    <path d="M2 12h20"/>
    <path d="M12 2a15.3 15.3 0 0 1 4 10 15.3 15.3 0 0 1-4 10 15.3 15.3 0 0 1-4-10 15.3 15.3 0 0 1 4-10z"/>
  </>}/>,
  Settings: (p) => <Ico {...p} d={<>
    <circle cx="12" cy="12" r="3"/>
    <path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 1 1-2.83 2.83l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 1 1-4 0v-.09a1.65 1.65 0 0 0-1-1.51 1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 1 1-2.83-2.83l.06-.06a1.65 1.65 0 0 0 .33-1.82 1.65 1.65 0 0 0-1.51-1H3a2 2 0 1 1 0-4h.09a1.65 1.65 0 0 0 1.51-1 1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 1 1 2.83-2.83l.06.06a1.65 1.65 0 0 0 1.82.33h0a1.65 1.65 0 0 0 1-1.51V3a2 2 0 1 1 4 0v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 1 1 2.83 2.83l-.06.06a1.65 1.65 0 0 0-.33 1.82v0a1.65 1.65 0 0 0 1.51 1H21a2 2 0 1 1 0 4h-.09a1.65 1.65 0 0 0-1.51 1z"/>
  </>}/>,
  Dashboard: (p) => <Ico {...p} d={<>
    <rect x="3" y="3" width="7" height="9"/>
    <rect x="14" y="3" width="7" height="5"/>
    <rect x="14" y="12" width="7" height="9"/>
    <rect x="3" y="16" width="7" height="5"/>
  </>}/>,
  Calendar: (p) => <Ico {...p} d={<>
    <rect x="3" y="4" width="18" height="18" rx="2"/>
    <path d="M16 2v4M8 2v4M3 10h18"/>
  </>}/>,
  Chart: (p) => <Ico {...p} d={<>
    <path d="M3 3v18h18"/>
    <path d="M7 14l3-3 3 3 5-6"/>
  </>}/>,
  Scissors: (p) => <Ico {...p} d={<>
    <circle cx="6" cy="6" r="3"/>
    <circle cx="6" cy="18" r="3"/>
    <path d="M20 4L8.12 15.88M14.47 14.48L20 20M8.12 8.12L12 12"/>
  </>}/>,
  Play: (p) => <Ico {...p} d={<polygon points="6 4 20 12 6 20 6 4"/>}/>,
  Stop: (p) => <Ico {...p} d={<rect x="5" y="5" width="14" height="14" rx="1"/>}/>,
  Check: (p) => <Ico {...p} d={<>
    <circle cx="12" cy="12" r="10"/><path d="M9 12l2 2 4-4"/>
  </>}/>,
  AlertTri: (p) => <Ico {...p} d={<>
    <path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"/>
    <path d="M12 9v4M12 17h.01"/>
  </>}/>,
  XCircle: (p) => <Ico {...p} d={<>
    <circle cx="12" cy="12" r="10"/><path d="M15 9l-6 6M9 9l6 6"/>
  </>}/>,
  Sitemap: (p) => <Ico {...p} d={<>
    <rect x="9" y="2" width="6" height="5" rx="1"/>
    <rect x="2" y="17" width="6" height="5" rx="1"/>
    <rect x="16" y="17" width="6" height="5" rx="1"/>
    <path d="M12 7v4M5 17v-2a1 1 0 0 1 1-1h12a1 1 0 0 1 1 1v2M12 11v3"/>
  </>}/>,
  Search: (p) => <Ico {...p} d={<>
    <circle cx="11" cy="11" r="7"/><path d="M21 21l-4.3-4.3"/>
  </>}/>,
  ChevronDown: (p) => <Ico {...p} d={<polyline points="6 9 12 15 18 9"/>}/>,
  ArrowUp: (p) => <Ico {...p} d={<>
    <path d="M12 19V5M5 12l7-7 7 7"/>
  </>}/>,
  ArrowDown: (p) => <Ico {...p} d={<>
    <path d="M12 5v14M19 12l-7 7-7-7"/>
  </>}/>,
  Lock: (p) => <Ico {...p} d={<>
    <rect x="3" y="11" width="18" height="11" rx="2"/>
    <path d="M7 11V7a5 5 0 0 1 10 0v4"/>
  </>}/>,
  Save: (p) => <Ico {...p} d={<>
    <path d="M19 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h11l5 5v11a2 2 0 0 1-2 2z"/>
    <polyline points="17 21 17 13 7 13 7 21"/>
    <polyline points="7 3 7 8 15 8"/>
  </>}/>,
  Network: (p) => <Ico {...p} d={<>
    <circle cx="12" cy="5" r="2"/>
    <circle cx="5" cy="19" r="2"/>
    <circle cx="19" cy="19" r="2"/>
    <path d="M12 7v4M12 11l-5.5 6M12 11l5.5 6"/>
  </>}/>,
};

// ─── Sidebar ────────────────────────────────────────────────────────
function Sidebar({ active = 'seo' }) {
  const item = (key, Icon, label, badge) => {
    const isActive = active === key;
    return (
      <div key={key}
        className={`group flex items-center gap-2.5 px-3 py-2 mx-2 rounded-md text-[13px] font-medium cursor-pointer transition-colors ${
          isActive
            ? 'bg-indigo-500/15 text-white ring-1 ring-inset ring-indigo-400/25'
            : 'text-slate-300 hover:bg-slate-800/60 hover:text-white'
        }`}>
        <span className={isActive ? 'text-indigo-300' : 'text-slate-400'}>
          <Icon size={16}/>
        </span>
        <span className="flex-1">{label}</span>
        {badge && <span className="text-[10px] uppercase tracking-wider text-slate-500">{badge}</span>}
      </div>
    );
  };

  const stub = (key, Icon, label) => (
    <div key={key}
      className="flex items-center gap-2.5 px-3 py-2 mx-2 rounded-md text-[13px] font-medium text-slate-500/70 cursor-not-allowed">
      <span className="text-slate-600"><Icon size={16}/></span>
      <span className="flex-1">{label}</span>
      <span className="w-1.5 h-1.5 rounded-full bg-slate-700"/>
    </div>
  );

  return (
    <aside className="w-[220px] shrink-0 h-full bg-[#0f172a] text-slate-200 flex flex-col"
           style={{ fontFamily: 'Inter, system-ui, sans-serif' }}>
      {/* Brand */}
      <div className="px-4 py-4 flex items-center gap-2.5 border-b border-slate-800/80">
        <div className="w-7 h-7 rounded-md bg-gradient-to-br from-indigo-400 to-indigo-600 flex items-center justify-center text-white shadow-[0_1px_0_rgba(255,255,255,0.15)_inset]">
          <I.Spark size={16} stroke={2.25}/>
        </div>
        <div className="leading-tight">
          <div className="text-[14px] font-semibold tracking-tight text-white">KlinikPortal</div>
          <div className="text-[10px] uppercase tracking-[0.12em] text-slate-500">Hellerup Laserklinik</div>
        </div>
      </div>

      {/* Nav */}
      <nav className="flex-1 py-3 overflow-hidden">
        <div className="px-4 pb-1.5 text-[10px] font-semibold uppercase tracking-[0.14em] text-slate-500">
          Værktøjer
        </div>
        <div className="flex flex-col gap-0.5">
          {item('seo', I.Globe, 'SEO & Hjemmeside')}
          {item('settings', I.Settings, 'Indstillinger')}
        </div>

        <div className="mt-5 px-4 pb-1.5 text-[10px] font-semibold uppercase tracking-[0.14em] text-slate-500 flex items-center gap-1.5">
          <span>Bookinger</span>
          <span className="text-slate-600 normal-case tracking-normal font-normal">(kommer snart)</span>
        </div>
        <div className="flex flex-col gap-0.5">
          {stub('oversigt', I.Dashboard, 'Oversigt')}
          {stub('bookinger', I.Calendar, 'Bookinger')}
          {stub('statistik', I.Chart, 'Statistik')}
          {stub('behandlinger', I.Scissors, 'Behandlinger')}
        </div>
      </nav>

      {/* Footer */}
      <div className="px-4 py-3 border-t border-slate-800/80 text-[11px] text-slate-500 flex items-center justify-between">
        <span>v0.3.1 · lokal</span>
        <span className="flex items-center gap-1.5">
          <span className="w-1.5 h-1.5 rounded-full bg-emerald-400"/>
          Forbundet
        </span>
      </div>
    </aside>
  );
}

// ─── Shell wrapper ─────────────────────────────────────────────────
function Shell({ active, title, breadcrumb, children, footer }) {
  return (
    <div className="flex h-full bg-slate-50" style={{ fontFamily: 'Inter, system-ui, sans-serif' }}>
      <Sidebar active={active}/>
      <main className="flex-1 min-w-0 flex flex-col">
        {/* Top header */}
        <header className="h-[56px] shrink-0 bg-white border-b border-slate-200 px-6 flex items-center">
          <div className="flex items-baseline gap-2">
            <h1 className="text-[15px] font-semibold text-slate-900 tracking-tight">{title}</h1>
            {breadcrumb && (
              <span className="text-[12px] text-slate-500">/ {breadcrumb}</span>
            )}
          </div>
        </header>
        <div className="flex-1 min-h-0 flex flex-col">
          {children}
        </div>
        {footer}
      </main>
    </div>
  );
}

// ─── SEO control bar ────────────────────────────────────────────────
function SeoControlBar({ url, depth = 5, crawling }) {
  return (
    <div className="h-[56px] shrink-0 bg-white border-b border-slate-200 px-6 flex items-center gap-3">
      <label className="text-[12.5px] font-medium text-slate-700 shrink-0">Hjemmeside URL:</label>
      <div className="flex-1 relative">
        <input
          readOnly
          value={url}
          placeholder="https://www.helleruplaserklinik.dk"
          className="w-full h-9 px-3 pr-9 rounded-md bg-slate-50 border border-slate-300 text-[13px] text-slate-800 font-mono placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-indigo-200 focus:border-indigo-400"
          style={{ fontFamily: 'JetBrains Mono, ui-monospace, monospace' }}
        />
        <span className="absolute right-2.5 top-1/2 -translate-y-1/2 text-slate-400">
          <I.Search size={14}/>
        </span>
      </div>
      <label className="text-[12.5px] font-medium text-slate-700 shrink-0 pl-1">Maks. dybde:</label>
      <div className="relative">
        <select
          defaultValue={depth}
          className="appearance-none h-9 pl-3 pr-8 rounded-md bg-white border border-slate-300 text-[13px] text-slate-800 font-medium focus:outline-none focus:ring-2 focus:ring-indigo-200 focus:border-indigo-400">
          {[2,3,4,5,6,7,8].map(n => <option key={n} value={n}>{n}</option>)}
        </select>
        <span className="absolute right-2 top-1/2 -translate-y-1/2 text-slate-500 pointer-events-none">
          <I.ChevronDown size={14}/>
        </span>
      </div>

      <button
        disabled={crawling}
        className={`h-9 px-3.5 inline-flex items-center gap-1.5 rounded-md text-[13px] font-semibold transition-colors shadow-sm ${
          crawling
            ? 'bg-emerald-600/40 text-white/70 cursor-not-allowed'
            : 'bg-emerald-600 hover:bg-emerald-700 text-white'
        }`}>
        <I.Play size={13} stroke={2.5}/> Start crawl
      </button>
      <button
        disabled={!crawling}
        className={`h-9 px-3.5 inline-flex items-center gap-1.5 rounded-md text-[13px] font-semibold transition-colors shadow-sm ${
          crawling
            ? 'bg-rose-600 hover:bg-rose-700 text-white'
            : 'bg-slate-100 text-slate-400 cursor-not-allowed border border-slate-200'
        }`}>
        <I.Stop size={12} stroke={2.5}/> Stop
      </button>
    </div>
  );
}

// ─── Status strip ──────────────────────────────────────────────────
function StatusStrip({ status, count, crawling }) {
  return (
    <div className="h-[40px] shrink-0 bg-slate-50 border-b border-slate-200 px-6 flex items-center gap-4">
      <div className="flex items-center gap-2 min-w-[260px]">
        {crawling
          ? <span className="w-2 h-2 rounded-full bg-indigo-500 animate-pulse"/>
          : <span className="w-2 h-2 rounded-full bg-emerald-500"/>}
        <span className="text-[12.5px] text-slate-700">{status}</span>
      </div>
      <div className="flex-1 h-1.5 rounded-full bg-slate-200 overflow-hidden relative">
        {crawling ? (
          <div className="absolute inset-y-0 w-1/3 rounded-full bg-gradient-to-r from-transparent via-indigo-500 to-transparent kp-indeterminate"/>
        ) : (
          <div className="h-full bg-emerald-500 rounded-full" style={{ width: '100%' }}/>
        )}
      </div>
      <div className="text-[12.5px] text-slate-600 tabular-nums min-w-[80px] text-right">
        Sider: <span className="font-semibold text-slate-900">{count}</span>
      </div>
    </div>
  );
}

// ─── Tabs ──────────────────────────────────────────────────────────
function Tabs({ active = 0, onChange = () => {} }) {
  const tabs = ['Sider & problemer', 'Sidestatistik', 'Hierarki'];
  return (
    <div className="shrink-0 bg-white border-b border-slate-200 px-6 flex items-end gap-1">
      {tabs.map((t, i) => (
        <button key={t}
          onClick={() => onChange(i)}
          className={`relative px-3.5 py-2.5 text-[13px] font-medium transition-colors ${
            i === active
              ? 'text-indigo-700'
              : 'text-slate-500 hover:text-slate-800'
          }`}>
          {t}
          {i === active && (
            <span className="absolute inset-x-2 -bottom-px h-0.5 bg-indigo-600 rounded-t"/>
          )}
        </button>
      ))}
    </div>
  );
}

// ─── Status badges ─────────────────────────────────────────────────
function StatusBadge({ code }) {
  const n = parseInt(code, 10);
  let cls = '', dot = '', Icon = null;
  if (n >= 200 && n < 300) { cls = 'bg-emerald-50 text-emerald-700 ring-emerald-200'; Icon = I.Check; }
  else if (n >= 300 && n < 400) { cls = 'bg-amber-50 text-amber-700 ring-amber-200'; Icon = I.ArrowUp; }
  else { cls = 'bg-rose-50 text-rose-700 ring-rose-200'; Icon = I.XCircle; }
  return (
    <span className={`inline-flex items-center gap-1 px-1.5 py-0.5 rounded text-[11px] font-semibold ring-1 ring-inset ${cls}`}>
      <Icon size={11} stroke={2.5}/>
      {code}
    </span>
  );
}

function YesNoBadge({ yes }) {
  return yes ? (
    <span className="inline-flex items-center gap-1 px-1.5 py-0.5 rounded text-[11px] font-semibold ring-1 ring-inset bg-amber-50 text-amber-700 ring-amber-200">
      <I.AlertTri size={10} stroke={2.5}/> Ja
    </span>
  ) : (
    <span className="inline-flex items-center gap-1 px-1.5 py-0.5 rounded text-[11px] font-medium ring-1 ring-inset bg-slate-50 text-slate-500 ring-slate-200">
      Nej
    </span>
  );
}

// Row variant style — color coding (border-left + subtle tint)
function rowClasses(kind) {
  switch (kind) {
    case 'orphan': return 'bg-amber-50/40 border-l-[3px] border-l-amber-400';
    case 'error':  return 'bg-rose-50/40 border-l-[3px] border-l-rose-500';
    case 'deep':   return 'bg-sky-50/40 border-l-[3px] border-l-sky-400';
    default:       return 'bg-white border-l-[3px] border-l-transparent';
  }
}

function ProblemTag({ kind }) {
  const map = {
    orphan: { label: 'Forældreløs', cls: 'bg-amber-100 text-amber-800', Icon: I.AlertTri },
    error:  { label: 'Fejl 404',    cls: 'bg-rose-100 text-rose-800',   Icon: I.XCircle },
    error5: { label: 'Fejl 500',    cls: 'bg-rose-100 text-rose-800',   Icon: I.XCircle },
    deep:   { label: 'Dyb side',    cls: 'bg-sky-100 text-sky-800',     Icon: I.ArrowDown },
    redir:  { label: 'Omdirigeret', cls: 'bg-amber-100 text-amber-800', Icon: I.ArrowUp },
    none:   null,
  };
  if (!kind || !map[kind]) return <span className="text-slate-400 text-[12px]">—</span>;
  const { label, cls, Icon } = map[kind];
  return (
    <span className={`inline-flex items-center gap-1 px-1.5 py-0.5 rounded text-[11px] font-medium ${cls}`}>
      <Icon size={11} stroke={2.5}/> {label}
    </span>
  );
}

// ─── Sample data ───────────────────────────────────────────────────
const SAMPLE_PAGES = [
  { url: '/',                                  status: 200, depth: 0, problem: 'none',  title: 'Hellerup Laserklinik · Forside',          inLinks: 18, outLinks: 24, words: 612,  orphan: false, kind: 'ok' },
  { url: '/behandlinger/laser-haarfjerning',   status: 200, depth: 2, problem: 'none',  title: 'Laser hårfjerning',                       inLinks: 9,  outLinks: 12, words: 1284, orphan: false, kind: 'ok' },
  { url: '/behandlinger/laser-hudpleje',       status: 200, depth: 2, problem: 'none',  title: 'Laser hudpleje',                          inLinks: 7,  outLinks: 11, words: 1102, orphan: false, kind: 'ok' },
  { url: '/priser',                            status: 200, depth: 1, problem: 'none',  title: 'Priser & pakker',                         inLinks: 12, outLinks: 8,  words: 488,  orphan: false, kind: 'ok' },
  { url: '/kontakt',                           status: 200, depth: 1, problem: 'none',  title: 'Kontakt og åbningstider',                 inLinks: 14, outLinks: 6,  words: 240,  orphan: false, kind: 'ok' },
  { url: '/booking',                           status: 301, depth: 1, problem: 'redir', title: 'Book tid → ekstern',                      inLinks: 11, outLinks: 0,  words: 0,    orphan: false, kind: 'ok' },
  { url: '/gammel-kampagne-2023',              status: 200, depth: 3, problem: 'orphan',title: 'Sommerkampagne 2023',                     inLinks: 0,  outLinks: 4,  words: 312,  orphan: true,  kind: 'orphan' },
  { url: '/behandlinger/aergamle-priser',      status: 404, depth: 3, problem: 'error', title: '— ikke fundet —',                         inLinks: 2,  outLinks: 0,  words: 0,    orphan: false, kind: 'error' },
  { url: '/blog/2021/laserens-historie',       status: 200, depth: 5, problem: 'deep',  title: 'Laserens historie',                       inLinks: 1,  outLinks: 3,  words: 845,  orphan: false, kind: 'deep' },
  { url: '/om-os/personalet/dr-jensen',        status: 200, depth: 4, problem: 'none',  title: 'Dr. Jensen — speciallæge',                inLinks: 5,  outLinks: 2,  words: 380,  orphan: false, kind: 'ok' },
];

// ─── Table: Sider & problemer ──────────────────────────────────────
function PagesTable({ rows }) {
  return (
    <div className="overflow-hidden border border-slate-200 rounded-lg bg-white">
      <table className="w-full text-[12.5px]">
        <thead className="bg-slate-50 border-b border-slate-200 text-slate-600">
          <tr className="text-left">
            <th className="px-3 py-2 font-semibold w-[58%]">URL</th>
            <th className="px-3 py-2 font-semibold w-[88px]">Status</th>
            <th className="px-3 py-2 font-semibold w-[72px] text-right tabular-nums">Dybde</th>
            <th className="px-3 py-2 font-semibold">Problem</th>
          </tr>
        </thead>
        <tbody>
          {rows.map((r, i) => (
            <tr key={i} className={`border-b border-slate-100 last:border-b-0 ${rowClasses(r.kind)} hover:bg-slate-50/60 transition-colors`}>
              <td className="px-3 py-1.5">
                <span className="font-mono text-[12px] text-slate-800" style={{ fontFamily: 'JetBrains Mono, ui-monospace, monospace' }}>
                  {r.url}
                </span>
              </td>
              <td className="px-3 py-1.5"><StatusBadge code={r.status}/></td>
              <td className="px-3 py-1.5 text-right tabular-nums text-slate-700">{r.depth}</td>
              <td className="px-3 py-1.5"><ProblemTag kind={r.problem}/></td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

// ─── Table: Sidestatistik (Tab 2) ──────────────────────────────────
function StatsTable({ rows }) {
  const SortHead = ({ children, sorted, dir = 'desc' }) => (
    <th className="px-3 py-2 font-semibold whitespace-nowrap">
      <button className={`inline-flex items-center gap-1 ${sorted ? 'text-indigo-700' : 'text-slate-600 hover:text-slate-900'}`}>
        {children}
        {sorted && (dir === 'desc' ? <I.ArrowDown size={11} stroke={2.5}/> : <I.ArrowUp size={11} stroke={2.5}/>)}
      </button>
    </th>
  );
  return (
    <div className="overflow-hidden border border-slate-200 rounded-lg bg-white">
      <table className="w-full text-[12.5px]">
        <thead className="bg-slate-50 border-b border-slate-200 text-slate-600">
          <tr className="text-left">
            <SortHead>URL</SortHead>
            <SortHead>Titel</SortHead>
            <SortHead>Status</SortHead>
            <SortHead sorted dir="asc">Dybde</SortHead>
            <SortHead>Indgående</SortHead>
            <SortHead>Udgående</SortHead>
            <SortHead>Ord</SortHead>
            <SortHead>Forældreløs</SortHead>
          </tr>
        </thead>
        <tbody>
          {rows.map((r, i) => (
            <tr key={i} className={`border-b border-slate-100 last:border-b-0 ${rowClasses(r.kind)} hover:bg-slate-50/60`}>
              <td className="px-3 py-1.5 max-w-0">
                <div className="truncate font-mono text-[12px] text-slate-800" style={{ fontFamily: 'JetBrains Mono, ui-monospace, monospace' }}>
                  {r.url}
                </div>
              </td>
              <td className="px-3 py-1.5 text-slate-700 max-w-[200px] truncate">{r.title}</td>
              <td className="px-3 py-1.5"><StatusBadge code={r.status}/></td>
              <td className="px-3 py-1.5 text-right tabular-nums text-slate-700">{r.depth}</td>
              <td className="px-3 py-1.5 text-right tabular-nums text-slate-700">{r.inLinks}</td>
              <td className="px-3 py-1.5 text-right tabular-nums text-slate-700">{r.outLinks}</td>
              <td className="px-3 py-1.5 text-right tabular-nums text-slate-700">{r.words}</td>
              <td className="px-3 py-1.5"><YesNoBadge yes={r.orphan}/></td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

// ─── Tab 3 hierarchy ───────────────────────────────────────────────
function HierarchyTable() {
  const rows = [
    { path: '/behandlinger', count: 8, maxDepth: 3 },
    { path: '/om-os',         count: 5, maxDepth: 4 },
    { path: '/blog',          count: 12, maxDepth: 5 },
    { path: '/priser',        count: 1, maxDepth: 1 },
    { path: '/kontakt',       count: 1, maxDepth: 1 },
  ];
  return (
    <div className="overflow-hidden border border-slate-200 rounded-lg bg-white">
      <table className="w-full text-[12.5px]">
        <thead className="bg-slate-50 border-b border-slate-200 text-slate-600">
          <tr className="text-left">
            <th className="px-3 py-2 font-semibold">Top-sti</th>
            <th className="px-3 py-2 font-semibold text-right tabular-nums w-[120px]">Undersider</th>
            <th className="px-3 py-2 font-semibold text-right tabular-nums w-[120px]">Maks. dybde</th>
          </tr>
        </thead>
        <tbody>
          {rows.map((r, i) => (
            <tr key={i} className="border-b border-slate-100 last:border-b-0 hover:bg-slate-50/60">
              <td className="px-3 py-1.5">
                <span className="font-mono text-[12px] text-slate-800" style={{ fontFamily: 'JetBrains Mono, ui-monospace, monospace' }}>
                  {r.path}
                </span>
              </td>
              <td className="px-3 py-1.5 text-right tabular-nums text-slate-700">{r.count}</td>
              <td className="px-3 py-1.5 text-right tabular-nums text-slate-700">{r.maxDepth}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

// ─── Footer (export bar) ───────────────────────────────────────────
function ExportFooter() {
  const Btn = ({ children }) => (
    <button className="h-8 px-3 inline-flex items-center gap-1.5 rounded-md border border-slate-300 bg-white text-slate-700 text-[12.5px] font-medium hover:border-slate-400 hover:bg-slate-50 transition-colors">
      <I.Save size={12}/> {children}
    </button>
  );
  return (
    <div className="h-[52px] shrink-0 bg-white border-t border-slate-200 px-6 flex items-center gap-2">
      <span className="text-[12.5px] font-medium text-slate-700 mr-1">Eksporter:</span>
      <Btn>Inventory (CSV)</Btn>
      <Btn>Link Matrix (CSV)</Btn>
      <Btn>To-Do reparationer (CSV)</Btn>
    </div>
  );
}

// ─── SEO screen ────────────────────────────────────────────────────
function SeoScreen({ state = 'done' }) {
  const crawling = state === 'crawling';
  const [tab, setTab] = React.useState(0);

  const crawlingRows = SAMPLE_PAGES.slice(0, 4);
  const doneRows     = SAMPLE_PAGES.slice(0, 10);

  const rows = crawling ? crawlingRows : doneRows;
  const orphanCount = rows.filter(r => r.kind === 'orphan').length;
  const errorCount  = rows.filter(r => r.kind === 'error').length;

  const status = crawling
    ? 'Crawling: https://www.helleruplaserklinik.dk/behandlinger/laser-hudpleje'
    : `Analyse færdig — ${orphanCount} forældreløs${orphanCount === 1 ? '' : 'e'} · ${errorCount} fejl`;
  const count  = crawling ? 23 : 42;

  return (
    <Shell active="seo" title="SEO & Hjemmeside" breadcrumb="Crawl & analyse"
           footer={<ExportFooter/>}>
      <SeoControlBar url={crawling ? 'https://www.helleruplaserklinik.dk' : 'https://www.helleruplaserklinik.dk'} crawling={crawling}/>
      <StatusStrip status={status} count={count} crawling={crawling}/>
      <Tabs active={tab} onChange={setTab}/>

      <div className="flex-1 min-h-0 overflow-auto px-6 py-4">
        {/* Tab 1 */}
        {tab === 0 && (
          <div className="space-y-3">
            <div className="flex items-center justify-between">
              <button className="h-8 px-3 inline-flex items-center gap-1.5 rounded-md border border-slate-300 bg-white text-slate-700 text-[12.5px] font-medium hover:border-indigo-400 hover:text-indigo-700 transition-colors">
                <I.Network size={13}/> Åbn interaktiv graf
              </button>
              <div className="text-[12.5px] text-slate-600">
                <span className="font-semibold text-slate-900">{count} sider</span>
                <span className="text-slate-400 px-1.5">·</span>
                <span className="text-amber-700 font-medium">{orphanCount} forældreløse</span>
                <span className="text-slate-400 px-1.5">·</span>
                <span className="text-rose-700 font-medium">{errorCount} fejl</span>
              </div>
            </div>
            {crawling && (
              <div className="rounded-md bg-indigo-50/60 border border-indigo-200/70 text-indigo-800 text-[12px] px-3 py-2 flex items-center gap-2">
                <span className="w-1.5 h-1.5 rounded-full bg-indigo-500 animate-pulse"/>
                Crawl i gang — tabellen opdateres efterhånden som sider analyseres.
              </div>
            )}
            <PagesTable rows={rows}/>
          </div>
        )}
        {tab === 1 && (
          <div className="space-y-3">
            <div className="text-[12.5px] text-slate-600">
              Sortérbare kolonner. Klik på en kolonneoverskrift for at sortere.
            </div>
            <StatsTable rows={rows}/>
          </div>
        )}
        {tab === 2 && (
          <div className="space-y-3">
            <div className="flex items-center gap-3">
              <button className="h-8 px-3 inline-flex items-center gap-1.5 rounded-md border border-slate-300 bg-white text-slate-700 text-[12.5px] font-medium hover:border-indigo-400 hover:text-indigo-700 transition-colors">
                <I.Sitemap size={13}/> Åbn hierarki-træ
              </button>
              <span className="text-[12.5px] text-slate-500">Oversigt over sektioner og deres dybeste stier.</span>
            </div>
            <HierarchyTable/>
          </div>
        )}
      </div>
    </Shell>
  );
}

// ─── Settings screen ───────────────────────────────────────────────
function SettingsScreen() {
  const Field = ({ label, children, hint }) => (
    <div className="space-y-1.5">
      <label className="text-[12.5px] font-medium text-slate-800 block">{label}</label>
      {children}
      {hint && <p className="text-[11.5px] text-slate-500">{hint}</p>}
    </div>
  );
  const input = "w-full h-9 px-3 rounded-md bg-white border border-slate-300 text-[13px] text-slate-800 focus:outline-none focus:ring-2 focus:ring-indigo-200 focus:border-indigo-400";

  return (
    <Shell active="settings" title="Indstillinger">
      <div className="flex-1 overflow-auto px-6 py-8 bg-slate-50">
        <div className="max-w-[600px] mx-auto space-y-5">
          <div className="bg-white border border-slate-200 rounded-lg shadow-sm">
            <div className="px-5 pt-4 pb-3 border-b border-slate-100">
              <h2 className="text-[14px] font-semibold text-slate-900">Hjemmeside</h2>
              <p className="text-[12px] text-slate-500 mt-0.5">Standardværdier for crawl-værktøjet.</p>
            </div>
            <div className="px-5 py-5 space-y-4">
              <Field label="Standard URL">
                <input className={input + ' font-mono'} style={{ fontFamily: 'JetBrains Mono, ui-monospace, monospace' }}
                       defaultValue="https://www.helleruplaserklinik.dk"/>
              </Field>
              <Field label="Maks. crawl-dybde" hint="Mellem 2 og 8. Dybere crawls tager længere tid.">
                <div className="relative w-32">
                  <input type="number" min="2" max="8" defaultValue="5" className={input + ' tabular-nums'}/>
                </div>
              </Field>
            </div>
          </div>

          <div className="bg-white border border-slate-200 rounded-lg shadow-sm">
            <div className="px-5 pt-4 pb-3 border-b border-slate-100 flex items-center justify-between">
              <div>
                <h2 className="text-[14px] font-semibold text-slate-900">Gecko Booking API</h2>
                <p className="text-[12px] text-slate-500 mt-0.5">Forbindelse til booking-systemet.</p>
              </div>
              <span className="text-[10.5px] uppercase tracking-wider px-2 py-0.5 rounded bg-slate-100 text-slate-600 ring-1 ring-inset ring-slate-200">
                Fase 3
              </span>
            </div>
            <div className="px-5 py-5 space-y-4">
              <Field label="API Token" hint="Tilsluttes i en kommende opdatering.">
                <div className="relative">
                  <input type="password" disabled defaultValue="••••••••••••••••" className={input + ' bg-slate-50 text-slate-400 cursor-not-allowed font-mono pr-9'}/>
                  <span className="absolute right-3 top-1/2 -translate-y-1/2 text-slate-400">
                    <I.Lock size={14}/>
                  </span>
                </div>
              </Field>
            </div>
          </div>

          <div className="flex justify-end gap-2 pt-1">
            <button className="h-9 px-4 rounded-md border border-slate-300 bg-white text-slate-700 text-[13px] font-medium hover:bg-slate-50">
              Annullér
            </button>
            <button className="h-9 px-4 inline-flex items-center gap-1.5 rounded-md bg-indigo-600 hover:bg-indigo-700 text-white text-[13px] font-semibold shadow-sm">
              <I.Save size={13}/> Gem indstillinger
            </button>
          </div>
        </div>
      </div>
    </Shell>
  );
}

// ─── Stub (empty state) ────────────────────────────────────────────
function StubScreen({ active = 'statistik', title = 'Statistik', heading = 'Bookingstatistik', Icon = I.Chart }) {
  return (
    <Shell active={active} title={title}>
      <div className="flex-1 flex items-center justify-center bg-slate-50 px-6">
        <div className="text-center max-w-md">
          <div className="mx-auto mb-5 w-20 h-20 rounded-2xl bg-white border border-slate-200 shadow-sm flex items-center justify-center text-slate-300">
            <Icon size={40} stroke={1.5}/>
          </div>
          <h2 className="text-[20px] font-semibold text-slate-800 tracking-tight">{heading}</h2>
          <p className="mt-2 text-[13.5px] text-slate-500 leading-relaxed">
            Denne funktion tilsluttes Gecko Booking API i en kommende opdatering.
          </p>
          <span className="inline-flex items-center gap-1.5 mt-5 px-2.5 py-1 rounded-full bg-indigo-50 text-indigo-700 ring-1 ring-inset ring-indigo-200 text-[11.5px] font-semibold uppercase tracking-wider">
            <span className="w-1.5 h-1.5 rounded-full bg-indigo-500"/>
            Fase 3
          </span>
        </div>
      </div>
    </Shell>
  );
}

// ─── Sidebar close-up ──────────────────────────────────────────────
function SidebarCloseup() {
  return (
    <div className="h-full flex" style={{ fontFamily: 'Inter, system-ui, sans-serif' }}>
      <Sidebar active="seo"/>
      <div className="flex-1 bg-slate-100/50 p-5">
        <div className="text-[11px] uppercase tracking-[0.14em] text-slate-500 font-semibold mb-3">Annotater</div>
        <div className="space-y-3 text-[12px] text-slate-600 leading-relaxed">
          <div className="flex gap-2">
            <span className="w-1 h-1 rounded-full bg-indigo-500 mt-1.5 shrink-0"/>
            <span><b className="text-slate-800">Aktiv:</b> indigo-tonet baggrund + tynd inset-ring.</span>
          </div>
          <div className="flex gap-2">
            <span className="w-1 h-1 rounded-full bg-slate-400 mt-1.5 shrink-0"/>
            <span><b className="text-slate-800">Dæmpet:</b> nedtonede tal til de stub-screens der venter på Gecko Booking API.</span>
          </div>
          <div className="flex gap-2">
            <span className="w-1 h-1 rounded-full bg-emerald-500 mt-1.5 shrink-0"/>
            <span><b className="text-slate-800">Status:</b> "Forbundet"-indikator i bunden viser at den lokale server kører.</span>
          </div>
          <div className="flex gap-2">
            <span className="w-1 h-1 rounded-full bg-slate-400 mt-1.5 shrink-0"/>
            <span><b className="text-slate-800">Sektioner:</b> "Værktøjer" og "Bookinger (kommer snart)" adskiller fungerende fra kommende.</span>
          </div>
        </div>
      </div>
    </div>
  );
}

// ─── Row color-coding close-up ─────────────────────────────────────
function RowCodingCloseup() {
  const rows = [
    { kind: 'ok',     url: '/behandlinger/laser-haarfjerning', status: 200, depth: 2, problem: 'none',  note: 'OK · normal række — hvid baggrund, ingen accent.' },
    { kind: 'orphan', url: '/gammel-kampagne-2023',            status: 200, depth: 3, problem: 'orphan',note: 'Forældreløs · gul venstrekant + svag varm tint.' },
    { kind: 'error',  url: '/behandlinger/aergamle-priser',    status: 404, depth: 3, problem: 'error', note: 'Fejl · rød venstrekant + svag rød tint.' },
    { kind: 'deep',   url: '/blog/2021/laserens-historie',     status: 200, depth: 5, problem: 'deep',  note: 'Dyb side · blå venstrekant + svag kølig tint.' },
  ];
  return (
    <div className="h-full bg-slate-50 p-6 flex flex-col gap-4" style={{ fontFamily: 'Inter, system-ui, sans-serif' }}>
      <div>
        <h3 className="text-[14px] font-semibold text-slate-900">Rækkefarvekoder</h3>
        <p className="text-[12px] text-slate-500 mt-0.5">Farve + ikon + tekstetiket — aldrig farve alene (WCAG).</p>
      </div>
      <div className="overflow-hidden border border-slate-200 rounded-lg bg-white shadow-sm">
        <table className="w-full text-[12.5px]">
          <thead className="bg-slate-50 border-b border-slate-200 text-slate-600">
            <tr className="text-left">
              <th className="px-3 py-2 font-semibold w-[34%]">URL</th>
              <th className="px-3 py-2 font-semibold w-[80px]">Status</th>
              <th className="px-3 py-2 font-semibold w-[64px] text-right tabular-nums">Dybde</th>
              <th className="px-3 py-2 font-semibold w-[120px]">Problem</th>
              <th className="px-3 py-2 font-semibold">Forklaring</th>
            </tr>
          </thead>
          <tbody>
            {rows.map((r, i) => (
              <tr key={i} className={`border-b border-slate-100 last:border-b-0 ${rowClasses(r.kind)}`}>
                <td className="px-3 py-2">
                  <span className="font-mono text-[12px] text-slate-800" style={{ fontFamily: 'JetBrains Mono, ui-monospace, monospace' }}>
                    {r.url}
                  </span>
                </td>
                <td className="px-3 py-2"><StatusBadge code={r.status}/></td>
                <td className="px-3 py-2 text-right tabular-nums text-slate-700">{r.depth}</td>
                <td className="px-3 py-2"><ProblemTag kind={r.problem}/></td>
                <td className="px-3 py-2 text-slate-600 text-[12px]">{r.note}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      <div className="grid grid-cols-4 gap-2 text-[11.5px]">
        {[
          { label: 'OK',          dot: 'bg-slate-300', cls: 'border-slate-200' },
          { label: 'Forældreløs', dot: 'bg-amber-400', cls: 'border-amber-200 bg-amber-50/60' },
          { label: 'Fejl',        dot: 'bg-rose-500',  cls: 'border-rose-200 bg-rose-50/60' },
          { label: 'Dyb side',    dot: 'bg-sky-400',   cls: 'border-sky-200 bg-sky-50/60' },
        ].map(s => (
          <div key={s.label} className={`px-2.5 py-1.5 rounded border ${s.cls} flex items-center gap-2`}>
            <span className={`w-2 h-2 rounded-full ${s.dot}`}/>
            <span className="font-medium text-slate-700">{s.label}</span>
          </div>
        ))}
      </div>
    </div>
  );
}

// ─── Export to window ──────────────────────────────────────────────
Object.assign(window, {
  SeoScreen, SettingsScreen, StubScreen, SidebarCloseup, RowCodingCloseup, I,
});
