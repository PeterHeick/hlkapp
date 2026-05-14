# Gecko Booking — Dataanalyse og statistikmuligheder

Undersøgelse af tilgængelige data til butiksoptimering. Kildemateriale: VBA-makroer i `ExcelMakroer/`, Python-scripts og API-snapshots i `~/Projects/hellerup-laserklinik/`.

---

## API

**Base URL:** `https://app.geckobooking.dk/api/v1`  
**Auth:** Bearer token  
**Pagination:** `page` + `rowsPerPage` (standard 50–100 pr. side)  
**Datofilter:** `period[start]` + `period[end]` (YYYY-MM-DD)  
**Felter:** `fields=f1,f2` + `expand[objekt]=felt` for indlejrede objekter

---

## Endpoints relevante for statistik

| Endpoint | Beskrivelse |
|----------|-------------|
| `GET /booking` | Bookingdata pagineret |
| `GET /calendar` | Behandlerliste (5 stk.) |
| `GET /service` | Behandlingstyper (150 stk.) |
| `GET /servicegroup` | Kategorier (24 stk.) |
| `GET /customer` | Kundedata (4.360 stk.) |

---

## Feltdækning — booking

| Felt | Dækning | Bemærkning |
|------|---------|------------|
| `bookingId` | 100% | |
| `bookedTime.date` | 100% | Format YYYY-MM-DD |
| `bookedTime.interval[].from` | 100% | Starttidspunkt HH:MM |
| `bookedTime.interval[].to` | 100% | Sluttidspunkt HH:MM |
| `bookingStart` | 100% | Unix timestamp |
| `calendar.calendarId` | 100% | Behandler-ID |
| `noShow` | 100% | Boolean |
| `bookedOnline` | 100% | Boolean |
| `createdDate` + `createdTime` | 100% | Oprettelsestidspunkt |
| `service.serviceId` | ~90% | Null ved interne blokeringer |
| `bookingText` | ~30% | Fritekst, ustruktureret |
| `status` | 0% | Altid null — ignorer |
| `order` | 0% | Altid null — ignorer |
| `cashRegisterReceipt` | 0% | Altid null — ignorer |

**Interval-struktur:** Altid ét interval pr. booking (array med ét objekt). Varighed = `to - from` i minutter.

```json
"bookedTime": {
  "date": "2025-01-02",
  "interval": [{"from": "12:15", "to": "12:45"}]
}
```

---

## Feltdækning — kunde

| Felt | Dækning | Bemærkning |
|------|---------|------------|
| `customerId` | 100% | |
| `customerName` | 100% | |
| `customerEmail` | ~70% | |
| `customerMobile` | ~70% | |
| `customerPostalcode` | ~70% | Brugbar til geografi |
| `customerCity` | ~70% | |
| `customerGender` | 100% men ubrugelig | Flertallet er `0` (ukendt) |
| `customerBirthYear` | ~98% men upræcis | Mange har `1970` (placeholder) |
| `customerCreateDate` | 100% | Unix timestamp |
| `customerImportantNote` | ~20% | Journalnoter — fritekst |
| `customerNote` | 0% | Aldrig brugt — ignorer |
| `customerNo` | 0% | Aldrig brugt — ignorer |

---

## Behandlere (5 kalendere)

| ID | Navn | Aktiv |
|----|------|-------|
| 3742692 | Jeanette Heick | ✓ |
| 3742693 | Line Stjernholm | ✓ |
| 4789080 | Henriette Klekner | ✓ |
| 3745793 | Gigalaser | ✓ |
| 3933373 | Andre bookinger | ✗ |

---

## Priser

**Kilde:** Webscraping af Gecko Booking-siden via Selenium + Firefox  
**Script:** `~/Projects/hellerup-laserklinik/pysrc/hentpriser-ubuntu.py`  
**Output:** `behandlinger.csv` — **123 behandlinger med listepris i DKK**

Priser i CSV er listepriser. Individuelle afvigelser (rabatter, pakker) kan forekomme — de fremgår af `bookingText` eller `customerImportantNote` som ustruktureret fritekst.

**Eksempler:**

| Behandling | Pris |
|-----------|------|
| Gratis konsultation | 0 kr |
| Botox — 1 område | 1.900 kr |
| Botox — 3 områder | 3.500 kr |
| Fraxel, Helt ansigt | 3.000 kr |
| IPL — Helt ansigt | 4.000 kr |
| UltraTerapi — Ansigt og hals | 15.000 kr |
| Hårfjerning — Hele ben | 2.600 kr |
| Gigalaser 15 min | 300 kr |

---

## Dataomfang

| Enhed | Antal |
|-------|-------|
| Aktive bookinger (snapshot) | 188 |
| Slettede bookinger | 70 |
| Kunder | 4.360 |
| Aktive behandlingstyper | 150 |
| Servicekategorier | 24 |
| Behandlere (aktive) | 4 |
| Officielle priser | 123 |

---

## Statistikker der kan bygges

### Høj datakvalitet — byg med fuld sikkerhed

#### Butiksoptimering (kernemål)

| Statistik | Felter | Formål |
|-----------|--------|--------|
| **Kr/time pr. behandlingstype** | `interval.from/to` + `service` + CSV-pris | Vigtigste metrik: hvad er mest profitabelt pr. tidsenhed |
| Gennemsnitlig varighed pr. behandling | `interval.from/to` + `service` | Forstå tidsforbrug |
| Behandlermix — hvad laver hvem | `calendar` + `service` | Specialisering og kapacitet |
| Behandler-belægningsgrad | `interval` + åbningstider | Udnyttelse af kapacitet |

#### Behandler-performance

| Metrik | Felter | Beregning |
|--------|--------|-----------|
| **Belægningsgrad** | `interval.from/to` + åbningstider fra `workhour` | Booket tid / tilgængelig tid × 100% |
| **Estimeret omsætning pr. behandler** | `calendar` + `service` + CSV-pris | Sum af listepriser pr. behandler pr. periode |
| **Kr/time pr. behandler** | `interval.from/to` + CSV-pris | Estimeret omsætning / faktisk booket tid |
| **Antal bookinger pr. behandler** | `calendar` | Volumen-sammenligning |
| **Gennemsnitlig behandlingsvarighed** | `interval.from/to` pr. `calendar` | Hvem bruger mest tid pr. booking |
| **No-show rate pr. behandler** | `noShow` + `calendar` | % no-shows ud af totale bookinger |
| **Behandlingsmix pr. behandler** | `calendar` + `service` | Hvilke behandlingstyper udfører hvem |
| **Aflysningsrate pr. behandler** | `deletedbooking` + `calendar` | Slettede bookinger / totale bookinger |
| **Bookinghorisont pr. behandler** | `createdDate` vs. `bookedTime.date` + `calendar` | Er der forskel på leadtime hos behandlerne |

**Belægningsgrad — beregning:**

```
booket_tid_min    = sum(interval.to - interval.from) pr. behandler pr. dag
tilgængelig_tid   = workhour.activeTime (fra /workhour endpoint, pr. kalender)
belægningsgrad    = booket_tid_min / tilgængelig_tid_min × 100%
```

`workhour`-data er tilgængeligt (336 records, 100% feltdækning) og indeholder `activeTime`, `activeWeekdays` og evt. `dateLimitedFrom/To` for periodespecifikke åbningstider.

#### Volumen og trends

| Statistik | Felter | Formål |
|-----------|--------|--------|
| Bookinger pr. dag/uge/måned | `bookedTime.date` | Sæsonvariation |
| Bookinger pr. behandler | `calendar` | Arbejdsbyrde |
| Bookinger pr. behandlingstype | `service` | Popularitet |
| Top-10 behandlinger | `service` + count | Hvad efterspørges |
| Travleste tidspunkter på dagen | `interval.from` | Kapacitetsplanlægning |

#### Risiko og tab

| Statistik | Felter | Formål |
|-----------|--------|--------|
| No-show rate total | `noShow` | Tabt omsætning |
| No-show rate pr. behandler | `noShow` + `calendar` | Mønstre |
| No-show rate pr. behandlingstype | `noShow` + `service` | Hvilke behandlinger aflyses |
| Slettede bookinger (aflysninger) | `deletedbooking` endpoint | Cancellation-rate |

#### Bookingadfærd

| Statistik | Felter | Formål |
|-----------|--------|--------|
| Bookinghorisont (leadtime) | `createdDate` vs. `bookedTime.date` | Hvornår booker kunder |
| Online vs. manuelt | `bookedOnline` | Kanalfordeling |

### Delvis datakvalitet — byg med forbehold

| Statistik | Felter | Forbehold |
|-----------|--------|-----------|
| Geografisk fordeling | `customerPostalcode` | ~30% mangler postnummer |
| Nye vs. returkunder | `customerId` på tværs af perioder | Kræver historisk data |
| Kundetilgang over tid | `customerCreateDate` | Fortæller om registrering, ikke første booking |

### Kan ikke bygges — data mangler

| Statistik | Årsag |
|-----------|-------|
| Kønsfordeling | `customerGender` = 0 (ukendt) for flertallet |
| Aldersanalyse | `customerBirthYear` — for mange `1970`-placeholders |
| Faktisk omsætning | Ingen betalingsdata i API — kun listepriser fra CSV |

---

## Kr/time — optimeringspotentiale

Kerneberegningen for at finde de mest profitable behandlinger:

```
kr_per_time = listepris / (varighed_minutter / 60)
```

Varighed hentes fra `bookedTime.interval[].from/to`.  
Listepris hentes fra `behandlinger.csv` via match på `service.serviceName`.

**Eksempel (estimat med listepriser):**

| Behandling | Pris | Varighed | Kr/time |
|-----------|------|----------|---------|
| Gigalaser 15 min | 300 kr | 15 min | 1.200 kr/t |
| Botox — 1 område | 1.900 kr | 30 min | 3.800 kr/t |
| Fraxel, Helt ansigt | 3.000 kr | 60 min | 3.000 kr/t |
| UltraTerapi — Ansigt og hals | 15.000 kr | 90 min | 10.000 kr/t |
| Hårfjerning — Hele ben | 2.600 kr | 60 min | 2.600 kr/t |

> Varighederne i eksemplet er estimater. Faktisk varighed beregnes fra reelle bookingdata.

---

## Eksisterende Python-kode

**`~/Projects/hellerup-laserklinik/pysrc/booking.py`**  
Henter bookinger for de seneste 400 dage og aggregerer:
- Antal pr. behandlingstype
- Antal pr. behandler
- Antal pr. dato

Kan porteres direkte til KlinikPortal backend som startpunkt.

---

## Næste skridt (implementering)

### Fase B — Backend (KlinikPortal)

- Port `pysrc/booking.py` → `backend/src/klinik/gecko/`
- Nye endpoints:
  - `GET /api/stats/bookings` — volumen med filtre
  - `GET /api/stats/revenue` — estimeret omsætning (booking × CSV-pris)
  - `GET /api/stats/providers` — behandler-utilization
  - `GET /api/stats/efficiency` — kr/time pr. behandlingstype
- Token i `data/config.json` (allerede placeholder i Fase 3)
- Priser: port `hentpriser-ubuntu.py` → erstatter Excel-Python-subprocess

### Fase C — Frontend (Vue)

- `/statistik`-view (i dag StubView)
- Datofilter (periode-vælger)
- Kr/time ranking (bar chart)
- Behandler-belægning
- Bookingvolumen over tid
- No-show oversigt
