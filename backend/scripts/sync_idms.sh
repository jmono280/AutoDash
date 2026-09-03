#!/usr/bin/env bash
set -euo pipefail

# ------------------------------------------------------------------------------
# Script de sincronización IDMS para AutoDash
# ------------------------------------------------------------------------------
# Uso:
#   IDMS_PASSWORD=tu-password ./scripts/sync_idms.sh
#
# Opcional:
#   API_URL=http://localhost:8001 \
#   IDMS_EMAIL=admin@automania.com \
#   IDMS_PASSWORD=tu-password \
#   IDMS_YEARS="2025 2026" \
#   IDMS_VERIFY_YEAR=2026 \
#   ./scripts/sync_idms.sh
# ------------------------------------------------------------------------------

API_URL=${API_URL:-http://localhost:8001}
IDMS_EMAIL=${IDMS_EMAIL:-admin@automania.com}
IDMS_PASSWORD=${IDMS_PASSWORD:-}
IDMS_YEARS=${IDMS_YEARS:-"2025 2026"}
IDMS_VERIFY_YEAR=${IDMS_VERIFY_YEAR:-2026}

# ------------------------------------------------------------------------------

log() {
  echo "[$(date '+%Y-%m-%d %H:%M:%S')] $*"
}

if [ -z "$IDMS_PASSWORD" ]; then
  log "Error: IDMS_PASSWORD no está definida."
  log "Uso: IDMS_PASSWORD=tu-password ./scripts/sync_idms.sh"
  exit 1
fi

# Detectar si jq está disponible
if command -v jq >/dev/null 2>&1; then
  HAS_JQ=1
else
  HAS_JQ=0
  if ! command -v python3 >/dev/null 2>&1; then
    log "Error: se requiere jq o python3 para parsear la respuesta."
    exit 1
  fi
fi

pretty_json() {
  if [ "$HAS_JQ" -eq 1 ]; then
    jq .
  else
    cat
  fi
}

parse_token() {
  if [ "$HAS_JQ" -eq 1 ]; then
    jq -r '.access_token'
  else
    python3 -c "import sys, json; print(json.load(sys.stdin)['access_token'])"
  fi
}

# ------------------------------------------------------------------------------

log "Obteniendo token de AutoDash en $API_URL ..."
TOKEN=$(curl -sS -X POST "$API_URL/auth/login" \
  -H "Content-Type: application/json" \
  -d "{\"email\":\"$IDMS_EMAIL\",\"password\":\"$IDMS_PASSWORD\"}" \
  | parse_token)

if [ -z "$TOKEN" ] || [ "$TOKEN" = "null" ]; then
  log "Error: no se pudo obtener el token. Revisa las credenciales."
  exit 1
fi

log "Token obtenido correctamente."

# ------------------------------------------------------------------------------

log "Verificando sesión IDMS ..."
curl -sS "$API_URL/idms/session" \
  -H "Authorization: Bearer $TOKEN" | pretty_json

# ------------------------------------------------------------------------------

for YEAR in $IDMS_YEARS; do
  log "Sincronizando Charge Offs para el año $YEAR ..."
  curl -sS -X POST "$API_URL/idms/charge-offs/sync?year=$YEAR" \
    -H "Authorization: Bearer $TOKEN" | pretty_json
done

# ------------------------------------------------------------------------------

log "Sincronizando Month End ..."
curl -sS -X POST "$API_URL/idms/month-end/sync" \
  -H "Authorization: Bearer $TOKEN" | pretty_json

# ------------------------------------------------------------------------------

log "Verificando overview para el año $IDMS_VERIFY_YEAR ..."
curl -sS "$API_URL/idms/charge-offs/overview?year=$IDMS_VERIFY_YEAR" \
  -H "Authorization: Bearer $TOKEN" | pretty_json

log "Sincronización completada."
