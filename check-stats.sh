#!/usr/bin/env bash
# Hent booking-data direkte fra Gecko API og opsummer
# Brug: ./check-stats.sh [start] [end]
# Eks:  ./check-stats.sh 2026-02-01 2026-02-28

set -euo pipefail

ENV_FILE=".env"
if [[ ! -f "$ENV_FILE" ]]; then
  echo "FEJL: .env ikke fundet — kør fra projektets rodmappe" >&2
  exit 1
fi

# Læs .env — strip quotes og trailing komma
_env_val() {
  grep "^${1}=" "$ENV_FILE" | head -1 | sed 's/^[^=]*=//; s/[",]//g; s/^[[:space:]]*//; s/[[:space:]]*$//'
}

TOKEN=$(_env_val "GECKO_API_TOKEN")
if [[ -z "$TOKEN" ]]; then
  echo "FEJL: GECKO_API_TOKEN ikke fundet i .env" >&2
  exit 1
fi

GECKO_BASE="https://app.geckobooking.dk/api/v1"
START="${1:-2026-02-01}"
END="${2:-2026-02-28}"

FIELDS="bookingId,bookedTime,calendar,service,noShow"
EXPAND_CAL="calendarId,calendarName"
EXPAND_SVC="serviceId,serviceName"

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  Gecko API direkte"
echo "  Periode : $START → $END"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo

# Hent alle sider og saml i én JSON-array
ALL_BOOKINGS="[]"
PAGE=0
while true; do
  RESP=$(curl -sf \
    -H "Authorization: Bearer $TOKEN" \
    -G "${GECKO_BASE}/booking" \
    --data-urlencode "period[start]=${START}" \
    --data-urlencode "period[end]=${END}" \
    --data-urlencode "fields=${FIELDS}" \
    --data-urlencode "expand[calendar]=${EXPAND_CAL}" \
    --data-urlencode "expand[service]=${EXPAND_SVC}" \
    --data-urlencode "page=${PAGE}" \
    --data-urlencode "rowsPerPage=100") || {
    echo "FEJL: Gecko API svarede ikke (side $PAGE)" >&2
    exit 1
  }

  ITEMS=$(echo "$RESP" | jq '.list // []')
  COUNT=$(echo "$ITEMS" | jq 'length')
  ALL_BOOKINGS=$(echo "$ALL_BOOKINGS $ITEMS" | jq -s '.[0] + .[1]')

  TOTAL_ROWS=$(echo "$RESP" | jq '.paging.totalRows // .paging.total // 0')
  FETCHED=$(echo "$ALL_BOOKINGS" | jq 'length')

  if [[ "$COUNT" -lt 100 ]] || [[ "$TOTAL_ROWS" -gt 0 && "$FETCHED" -ge "$TOTAL_ROWS" ]]; then
    break
  fi
  PAGE=$((PAGE + 1))
done

TOTAL=$(echo "$ALL_BOOKINGS" | jq 'length')
echo "▶ Bookinger i alt: $TOTAL"
echo

# No-shows
NO_SHOW=$(echo "$ALL_BOOKINGS" | jq '[.[] | select(.noShow == true)] | length')
if [[ "$TOTAL" -gt 0 ]]; then
  NO_SHOW_PCT=$(echo "$ALL_BOOKINGS" | jq "($NO_SHOW / $TOTAL * 100 * 10 | round) / 10")
else
  NO_SHOW_PCT=0
fi
echo "▶ No-shows: $NO_SHOW  ($NO_SHOW_PCT%)"
echo

# Per behandler (calendar)
echo "▶ Per behandler:"
echo "$ALL_BOOKINGS" | jq -r '
  group_by(.calendar.calendarName)
  | sort_by(-length)
  | .[]
  | "  \(.[0].calendar.calendarName // "Ukendt")\n    bookinger: \(length)  no-shows: \([.[] | select(.noShow)] | length)"
'
echo

# Per behandling (service)
echo "▶ Per behandling (top 15):"
echo "$ALL_BOOKINGS" | jq -r '
  group_by(.service.serviceName)
  | sort_by(-length)
  | .[0:15][]
  | "  \(length)x  \(.[0].service.serviceName // "Ukendt")"
'

echo
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
