# KlinikPortal — Vision og formål

## Hvad er KlinikPortal?

KlinikPortal er et lokalt Windows-program til Hellerup Laserklinik, der samler to ting i én flot brugerflade:

1. **Booking & statistik** — trækker data fra Gecko Booking og viser omsætning, bookingmønstre, populære behandlinger og kundeadfærd
2. **SEO & hjemmesideanalyse** — gennemsøger klinikkens hjemmeside og kortlægger struktur, brudte links og forbedringsmuligheder

Programmet kræver ingen sky-server og ingen ekstern IT-support. Det installeres som én `.exe` på en Windows-PC og kører helt lokalt.

---

## Primære brugere

- Klinikejeren / administrator — statistik, omsætningsoversigt, booking-trends
- Den der vedligeholder hjemmesiden — SEO-analyse, linkstruktur, side-hierarki

---

## Hvad systemet skal kunne

### Dashboard

- Overordnet overblik: bookinger i dag / denne uge / denne måned
- Omsætning fordelt på periode (dag, uge, måned, år) vist som graf
- Sammenligning med tilsvarende periode tidligere (fx denne måned vs. samme måned sidste år)

### Bookingstatistik (Gecko Booking API)

- **Bookinger:** liste og søgning med filtre (dato, behandler, service, status)
- **Behandlinger/services:** hvilke behandlinger bookes mest, gennemsnitlig pris, aflyste vs. gennemførte
- **Kunder:** nye vs. tilbagevendende kunder over tid, kundegrupper
- **Medarbejdere:** belægningsgrad pr. behandler, bookinger pr. ansat
- **Omsætning:** total pr. periode, fordelt på service-kategori og behandler
- **Gavekort/vouchers:** udstedte, indløste, udestående saldo
- **Arbejdstimer:** registrerede timer vs. faktiske bookinger (kapacitetsudnyttelse)

### SEO & hjemmesideanalyse (crawler)

- Gennemsøg klinikkens hjemmeside (JavaScript-renderet indhold via Playwright/Chromium)
- Kortlæg alle sider, interne og eksterne links
- Find brudte links (HTTP 4xx/5xx)
- Find forældreløse sider (ingen indbinding fra andre sider)
- Visualiser sidestruktur som interaktivt hierarki og force-graph (D3.js)
- Eksporter inventory og linkmatrix som CSV

### Indstillinger

- Gecko API-nøgle (gemmes lokalt, aldrig i kildekode)
- Standard URL til hjemmesideanalyse
- Sprog og præferencer

---

## Hvad systemet ikke skal

- Kræve en sky-server eller ekstern hosting
- Kræve IT-support til at starte eller opdatere
- Håndtere direkte booking fra klienter (det klarer Gecko)
- Erstatte Gecko Booking — det supplerer det med analyse

---

## Teknisk fundament (overordnet)

| Lag | Teknologi |
|---|---|
| Brugerflade | Vue 3.5 + TypeScript + Tailwind CSS |
| Backend (lokal server) | Python / FastAPI på localhost |
| Booking-data | Gecko Booking API (REST, JSON) |
| Crawler | Scrapy + Playwright (Chromium) |
| Database | SQLite (lokal, ingen opsætning) |
| Grafer | Chart.js eller Apache ECharts |
| Distribution | PyInstaller + Inno Setup → `.exe`-installer |
| Styring | Windows 10/11 (64-bit) |

---

## Brugerrejse ved første opstart

1. Brugeren dobbeltklikker på `KlinikPortal-Setup.exe`
2. Installationen kører standard Windows-wizard (~ 1 min)
3. Første gang programmet åbnes: indtast Gecko API-nøgle
4. Programmet henter data fra Gecko og viser dashboard
5. Al efterfølgende brug: dobbeltklik på genvej på skrivebordet

---

## Fremtidige udvidelsesmuligheder (ikke i scope nu)

- Automatisk daglig rapport sendt som PDF eller email
- Integration med Google Analytics (hjemmesidetrafik vs. bookinger)
- Notifikation ved pludselig fald i bookinger
- Eksport til regnskabssystem
