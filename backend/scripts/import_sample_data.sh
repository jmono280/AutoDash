#!/usr/bin/env bash
# ---------------------------------------------------------------------------
# import_sample_data.sh
# Sube los 4 archivos de muestra al backend en un solo comando.
#
# Uso:
#   cd backend
#   bash scripts/import_sample_data.sh
#
# Variables de entorno opcionales (valores por defecto entre paréntesis):
#   API_URL   — URL base del backend     (http://localhost:8001)
#   EMAIL     — email del admin           (admin@automania.com)
#   PASSWORD  — contraseña del admin      (password123)
#   SAMPLE    — directorio con los PDFs   (sample_data)
#   DATE_TAG  — sufijo de fecha del archivo (20260428)
#
# Ejemplos:
#   API_URL=http://localhost:8000 bash scripts/import_sample_data.sh
#   DATE_TAG=20260423 bash scripts/import_sample_data.sh
# ---------------------------------------------------------------------------

set -euo pipefail

API_URL="${API_URL:-http://localhost:8001}"
EMAIL="${EMAIL:-admin@automania.com}"
PASSWORD="${PASSWORD:-password123}"
SAMPLE="${SAMPLE:-sample_data}"
DATE_TAG="${DATE_TAG:-20260428}"

# ── Colores ────────────────────────────────────────────────────────────────
GREEN="\033[0;32m"
RED="\033[0;31m"
YELLOW="\033[1;33m"
BLUE="\033[0;34m"
RESET="\033[0m"

ok()   { echo -e "${GREEN}  ✓ $*${RESET}"; }
fail() { echo -e "${RED}  ✗ $*${RESET}"; }
info() { echo -e "${BLUE}  → $*${RESET}"; }
warn() { echo -e "${YELLOW}  ! $*${RESET}"; }

# ── Verificar dependencias ──────────────────────────────────────────────────
if ! command -v curl &>/dev/null; then
  fail "curl no está instalado"; exit 1
fi

# Detectar si jq está disponible para pretty-print (opcional)
USE_JQ=false
if command -v jq &>/dev/null; then
  USE_JQ=true
fi

pretty() {
  if $USE_JQ; then
    jq -C '.' 2>/dev/null || cat
  else
    python3 -m json.tool 2>/dev/null || cat
  fi
}

echo ""
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${RESET}"
echo -e "${BLUE}  Automania — Import Sample Data${RESET}"
echo -e "${BLUE}  Backend : $API_URL${RESET}"
echo -e "${BLUE}  Archivos: $SAMPLE/*$DATE_TAG.*${RESET}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${RESET}"
echo ""

# ── 1. Login ────────────────────────────────────────────────────────────────
echo -e "${YELLOW}[1/5] Login${RESET}"
info "POST $API_URL/auth/login  →  $EMAIL"

LOGIN_RESPONSE=$(curl -sf -X POST "$API_URL/auth/login" \
  -H "Content-Type: application/json" \
  -d "{\"email\":\"$EMAIL\",\"password\":\"$PASSWORD\"}" 2>&1) || {
  fail "No se pudo conectar al backend en $API_URL"
  fail "¿Está corriendo uvicorn?"
  exit 1
}

TOKEN=$(echo "$LOGIN_RESPONSE" | python3 -c "import sys,json; print(json.load(sys.stdin)['access_token'])" 2>/dev/null) || {
  fail "Login fallido. Respuesta: $LOGIN_RESPONSE"
  exit 1
}

ok "Token obtenido: ${TOKEN:0:30}…"
echo ""

# ── Función auxiliar de upload ───────────────────────────────────────────────
upload() {
  local label="$1"      # descripción legible
  local endpoint="$2"   # /imports/daily-sales etc.
  local filepath="$3"   # ruta al archivo

  if [[ ! -f "$filepath" ]]; then
    fail "Archivo no encontrado: $filepath"
    warn "Saltando $label"
    return 0
  fi

  info "POST $API_URL$endpoint"
  info "Archivo: $filepath ($(du -h "$filepath" | cut -f1))"

  HTTP_CODE=$(curl -s -o /tmp/import_response.json -w "%{http_code}" \
    -X POST "$API_URL$endpoint" \
    -H "Authorization: Bearer $TOKEN" \
    -F "file=@$filepath")

  if [[ "$HTTP_CODE" == "201" ]]; then
    ok "$label importado (HTTP $HTTP_CODE)"
    cat /tmp/import_response.json | pretty
  else
    fail "$label falló (HTTP $HTTP_CODE)"
    cat /tmp/import_response.json | pretty
  fi
  echo ""
}

# ── 2. Daily Sales PDF ───────────────────────────────────────────────────────
echo -e "${YELLOW}[2/5] Daily Sales${RESET}"
upload "daily_sales" "/imports/daily-sales" "$SAMPLE/daily_sales_$DATE_TAG.pdf"

# ── 3. Hours Summary PDF ─────────────────────────────────────────────────────
echo -e "${YELLOW}[3/5] Hours Summary${RESET}"
upload "hours_summary" "/imports/hours-summary" "$SAMPLE/hours_$DATE_TAG.pdf"

# ── 4. Hours Detail PDF ──────────────────────────────────────────────────────
echo -e "${YELLOW}[4/5] Hours Detail (técnicos)${RESET}"
upload "hours_detail" "/imports/hours-detail" "$SAMPLE/hours_detail_$DATE_TAG.pdf"

# ── 5. Work in Progress XLSX ─────────────────────────────────────────────────
echo -e "${YELLOW}[5/5] Work in Progress${RESET}"
upload "work_in_progress" "/imports/work-in-progress" "$SAMPLE/work_in_progress_detail_$DATE_TAG.xlsx"

# ── Verificación rápida de KPIs ──────────────────────────────────────────────
echo -e "${YELLOW}[✓] Verificación de KPIs post-import${RESET}"
echo ""

# Derivar from/to desde DATE_TAG (asume mes completo hasta ese día)
YEAR="${DATE_TAG:0:4}"
MONTH="${DATE_TAG:4:2}"
FROM_DATE="$YEAR-$MONTH-01"
TO_DATE="$YEAR-$MONTH-${DATE_TAG:6:2}"

info "Período: $FROM_DATE → $TO_DATE"
echo ""

echo "  Sales KPIs:"
curl -s "$API_URL/sales/kpis?from=$FROM_DATE&to=$TO_DATE" \
  -H "Authorization: Bearer $TOKEN" | pretty
echo ""

echo "  Hours KPIs:"
curl -s "$API_URL/hours/kpis?from=$FROM_DATE&to=$TO_DATE" \
  -H "Authorization: Bearer $TOKEN" | pretty
echo ""

echo "  WIP KPIs:"
curl -s "$API_URL/wip/kpis" \
  -H "Authorization: Bearer $TOKEN" | pretty
echo ""

echo "  WIP Aging:"
curl -s "$API_URL/wip/aging" \
  -H "Authorization: Bearer $TOKEN" | pretty
echo ""

echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${RESET}"
echo -e "${GREEN}  Importación completa.${RESET}"
echo -e "${GREEN}  Abre http://localhost:5173 y navega al Overview.${RESET}"
echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${RESET}"
echo ""
