# Automania Dashboard — Backend

FastAPI + SQLAlchemy 2.0 async + PostgreSQL 15.

---

## Setup

```bash
cd backend
python -m venv venv
source venv/bin/activate          # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

Copia `.env.example` a `.env` y ajusta las variables:

```bash
cp .env.example .env
```

```env
DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/automania_db
SECRET_KEY=cambiar-en-produccion
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7
CORS_ORIGINS=http://localhost:5173
```

---

## Base de datos

```bash
# Crear la base de datos (si no existe)
docker exec <container> psql -U postgres -c "CREATE DATABASE automania_db;"

# Aplicar migraciones
alembic upgrade head

# Nueva migración (tras cambiar modelos)
alembic revision --autogenerate -m "descripcion"
```

---

## Usuarios de prueba

Ejecuta los scripts antes de arrancar el servidor por primera vez.

```bash
# Admin — acceso completo + endpoints de importación
python -m app.scripts.seed_admin
# Con credenciales personalizadas:
python -m app.scripts.seed_admin admin@automania.com password123 "Admin"

# Viewer — solo lectura, sin importaciones
python -m app.scripts.seed_viewer
# Con credenciales personalizadas:
python -m app.scripts.seed_viewer viewer@automania.com viewer123 "Viewer"
```

| Email | Password | Rol |
|---|---|---|
| admin@automania.com | password123 | admin |
| viewer@automania.com | viewer123 | viewer |

Los scripts son idempotentes: si el usuario ya existe, imprimen un aviso sin duplicar.

---

## Arrancar el servidor

```bash
uvicorn app.main:app --reload --port 8000
# Docs interactivas: http://localhost:8000/docs
```

> Si el puerto 8000 está ocupado (Portainer u otro servicio), usa `--port 8001`.

---

## Ejemplos de API con curl

Todos los ejemplos asumen el servidor en `http://localhost:8000`. Ajusta el puerto si usas 8001.

### 1. Obtener token

```bash
TOKEN=$(curl -sX POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@automania.com","password":"password123"}' \
  | jq -r .access_token)
```

### 2. Auth

```bash
# Datos del usuario autenticado
curl http://localhost:8000/auth/me \
  -H "Authorization: Bearer $TOKEN" | jq .

# Renovar token con refresh_token
REFRESH=$(curl -sX POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@automania.com","password":"password123"}' \
  | jq -r .refresh_token)

curl -sX POST http://localhost:8000/auth/refresh \
  -H "Content-Type: application/json" \
  -d "{\"refresh_token\":\"$REFRESH\"}" | jq .

# Logout (invalida el token en el cliente)
curl -sX POST http://localhost:8000/auth/logout \
  -H "Authorization: Bearer $TOKEN" | jq .
```

---

### 3. Importar archivos

Los archivos de muestra están en `sample_data/`. Los PDFs van a los primeros 3 endpoints;
el `.xlsx` al último. Extensión incorrecta devuelve HTTP 400.

```bash
# Ventas diarias
curl -X POST http://localhost:8000/imports/daily-sales \
  -H "Authorization: Bearer $TOKEN" \
  -F "file=@sample_data/daily_sales_20260428.pdf" | jq .

# Resumen de horas del taller
curl -X POST http://localhost:8000/imports/hours-summary \
  -H "Authorization: Bearer $TOKEN" \
  -F "file=@sample_data/hours_20260428.pdf" | jq .

# Horas por técnico
curl -X POST http://localhost:8000/imports/hours-detail \
  -H "Authorization: Bearer $TOKEN" \
  -F "file=@sample_data/hours_detail_20260428.pdf" | jq .

# Work in Progress (snapshot — reemplaza registros anteriores)
curl -X POST http://localhost:8000/imports/work-in-progress \
  -H "Authorization: Bearer $TOKEN" \
  -F "file=@sample_data/work_in_progress_detail_20260428.xlsx" | jq .
```

Respuesta exitosa (HTTP 201):
```json
{
  "rows_inserted": 28,
  "rows_updated": 0,
  "period_start": "2026-04-01",
  "period_end": "2026-04-28",
  "file_type": "daily_sales",
  "message": "Imported 28 daily sales rows for 2026-04-01 – 2026-04-28"
}
```

---

### 4. Ventas (`/sales`)

```bash
# KPIs del período
curl "http://localhost:8000/sales/kpis?from=2026-04-01&to=2026-04-28" \
  -H "Authorization: Bearer $TOKEN" | jq .

# Lista completa de días
curl "http://localhost:8000/sales/?from=2026-04-01&to=2026-04-28" \
  -H "Authorization: Bearer $TOKEN" | jq '.[0:3]'

# Serie de tiempo (para gráfica de barras)
curl "http://localhost:8000/sales/trend?from=2026-04-01&to=2026-04-28" \
  -H "Authorization: Bearer $TOKEN" | jq '.[0:5]'

# Promedio por día de la semana
curl "http://localhost:8000/sales/by-day-of-week?from=2026-04-01&to=2026-04-28" \
  -H "Authorization: Bearer $TOKEN" | jq .
```

Respuesta `/sales/kpis`:
```json
{
  "total_cars": 91,
  "total_gross": "71740.61",
  "total_net": "71740.61",
  "avg_ticket": "396.89",
  "total_cogs": "26292.88",
  "total_profit": "45447.73",
  "profit_pct": "63.35",
  "cogs_pct": "36.65"
}
```

---

### 5. Horas del taller (`/hours`)

```bash
# KPIs de eficiencia
curl "http://localhost:8000/hours/kpis?from=2026-04-01&to=2026-04-28" \
  -H "Authorization: Bearer $TOKEN" | jq .

# Registros del período
curl "http://localhost:8000/hours/?from=2026-04-01&to=2026-04-28" \
  -H "Authorization: Bearer $TOKEN" | jq .
```

Respuesta `/hours/kpis`:
```json
{
  "labor_dollars": "36977.05",
  "hours_sold": "385.20",
  "hours_paid": "475.00",
  "hours_worked": "1094.53",
  "actual_hours": "0",
  "advisor_efficiency": "81.09",
  "technician_proficiency": "43.40",
  "technician_productivity": "0",
  "technician_efficiency": null
}
```

---

### 6. Técnicos (`/technicians`)

```bash
# Lista todos los técnicos del período
curl "http://localhost:8000/technicians/?from=2026-04-01&to=2026-04-28" \
  -H "Authorization: Bearer $TOKEN" | jq '[.[] | {technician_name, hours_sold, hours_paid}]'

# Ranking por horas vendidas
curl "http://localhost:8000/technicians/ranking?metric=hours_sold&from=2026-04-01&to=2026-04-28" \
  -H "Authorization: Bearer $TOKEN" | jq '[.[] | {technician_name, hours_sold}]'

# Ranking por horas pagadas (metric=labor es alias de labor_dollars)
curl "http://localhost:8000/technicians/ranking?metric=labor&from=2026-04-01&to=2026-04-28" \
  -H "Authorization: Bearer $TOKEN" | jq '.[0:3]'

# Ranking por proficiency
curl "http://localhost:8000/technicians/ranking?metric=proficiency&from=2026-04-01&to=2026-04-28" \
  -H "Authorization: Bearer $TOKEN" | jq .

# Detalle de un técnico (URL-encode los espacios)
curl "http://localhost:8000/technicians/Joe%20Davis?from=2026-04-01&to=2026-04-28" \
  -H "Authorization: Bearer $TOKEN" | jq .

# Técnico inexistente → 404
curl "http://localhost:8000/technicians/Nobody%20Here?from=2026-04-01&to=2026-04-28" \
  -H "Authorization: Bearer $TOKEN" | jq .
```

Valores del sample (métrica `hours_sold`):
| Técnico | hours_sold | hours_paid |
|---|---|---|
| Joe Davis | 64.66 | 90.40 |
| Erbin (Tony) Mota | 40.06 | 59.80 |
| Chuck Hanson | 38.96 | 54.80 |

> `labor_dollars` = 0 en todos los técnicos porque el PDF `hours_detail` solo
> expone horas pagadas y vendidas, sin el desglose de dólares por técnico.

---

### 7. Work in Progress (`/wip`)

```bash
# Lista paginada (50 por defecto)
curl "http://localhost:8000/wip/" \
  -H "Authorization: Bearer $TOKEN" | jq '{total, pages}'

# Filtrar por advisor
curl "http://localhost:8000/wip/?advisor=MFal&limit=5" \
  -H "Authorization: Bearer $TOKEN" | jq '.items | length'

# Filtrar por antigüedad mínima
curl "http://localhost:8000/wip/?min_days=30&limit=10" \
  -H "Authorization: Bearer $TOKEN" | jq '{total, items: [.items[] | {ro_number, days_open}]}'

# KPIs generales del snapshot
curl "http://localhost:8000/wip/kpis" \
  -H "Authorization: Bearer $TOKEN" | jq .

# Aging por buckets (orden cronológico: 0-7d → 8-14d → 15-30d → 31-60d → 60+d)
curl "http://localhost:8000/wip/aging" \
  -H "Authorization: Bearer $TOKEN" | jq .

# Agrupado por categoría
curl "http://localhost:8000/wip/by-category" \
  -H "Authorization: Bearer $TOKEN" | jq '.[0:5]'

# Agrupado por advisor
curl "http://localhost:8000/wip/by-advisor" \
  -H "Authorization: Bearer $TOKEN" | jq .
```

Respuesta `/wip/kpis` (sample abril 2026):
```json
{
  "total_ros": 256,
  "total_estimated": "0",
  "total_cog": "18105.74",
  "total_col": "0",
  "avg_days_open": "11.15",
  "oldest_ro_days": 91
}
```

Respuesta `/wip/aging`:
```json
[
  { "bucket": "0-7d",   "count": 139, "total_estimated": "0" },
  { "bucket": "8-14d",  "count": 27,  "total_estimated": "0" },
  { "bucket": "15-30d", "count": 87,  "total_estimated": "0" },
  { "bucket": "60+d",   "count": 3,   "total_estimated": "0" }
]
```

---

## Verificar tablas directamente en PostgreSQL

```bash
docker exec <container> psql -U postgres -d automania_db -c "
SELECT 'daily_sales'      AS tabla, COUNT(*) FROM daily_sales
UNION ALL
SELECT 'hours_summary',            COUNT(*) FROM hours_summary
UNION ALL
SELECT 'technician_hours',         COUNT(*) FROM technician_hours
UNION ALL
SELECT 'work_in_progress',         COUNT(*) FROM work_in_progress
UNION ALL
SELECT 'users',                    COUNT(*) FROM users;"
```

---

## Estructura del proyecto

```
backend/
├── app/
│   ├── core/          config, security (JWT+bcrypt), dependencies (OAuth2)
│   ├── models/        SQLAlchemy 2.0 async (TimestampMixin + UUID PKs)
│   ├── schemas/       Pydantic v2 DTOs y schemas de KPIs
│   ├── importers/     Parsers puros: bytes → list[dict] (sin acceso a BD)
│   ├── repositories/  Queries SQL con func.sum/avg/case — sin lógica de negocio
│   ├── services/      Lógica de negocio, convierte ORM → schemas Pydantic
│   ├── routers/       FastAPI routers, solo Depends + delegación al servicio
│   └── scripts/       seed_admin.py, seed_viewer.py
├── alembic/           Migraciones async
├── sample_data/       PDFs y XLSX de ejemplo para pruebas
├── .env.example
├── requirements.txt
└── README.md
```


---

### 8. Chat IA (`/chat`)

El endpoint usa **OpenRouter** (compatible con la API de OpenAI). Requiere `OPENROUTER_API_KEY` en `.env`. Soporta respuesta directa y streaming SSE.

#### Obtener token (paso previo)

```bash
TOKEN=$(curl -sX POST http://localhost:8001/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@automania.com","password":"password123"}' \
  | python3 -c "import sys,json; print(json.load(sys.stdin)['access_token'])")
```

#### Respuesta directa

```bash
curl -X POST http://localhost:8001/chat/completions \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "messages": [{"role":"user","content":"¿Qué es el Gross Profit en un taller mecánico?"}]
  }' | python3 -m json.tool
```

Respuesta esperada:
```json
{
  "message": {
    "role": "assistant",
    "content": "El Gross Profit es la diferencia entre los ingresos por servicios y el costo directo..."
  },
  "model": "nvidia/nemotron-3-super-120b-a12b-20230311:free"
}
```

#### Context-aware (con datos del dashboard)

El campo `context` inyecta datos reales del taller en el system prompt. El frontend puede pasar KPIs actuales para que el AI responda con información del negocio:

```bash
curl -X POST http://localhost:8001/chat/completions \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "messages": [{"role":"user","content":"¿Cómo están las ventas del taller?"}],
    "context": "Total Cars: 91, Gross Sales: $71740, Gross Profit: $45447, Profit%: 63.35%, Open ROs: 256, ROs >30d: 8"
  }' | python3 -m json.tool
```

#### Streaming SSE

Con `"stream": true` la respuesta es `text/event-stream`. Cada línea tiene el formato `data: {"delta":"...","done":false}` y termina con `data: [DONE]`.

```bash
curl -N -X POST http://localhost:8001/chat/completions \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "messages": [{"role":"user","content":"explica proficiency brevemente"}],
    "stream": true
  }'
```

Salida esperada:
```
data: {"delta":"**Proficiency**...","done":false}
data: {"delta":"","done":true}
data: [DONE]
```

#### Historial de conversación (multi-turn)

El backend es stateless — el cliente envía el historial completo en cada request:

```bash
curl -X POST http://localhost:8001/chat/completions \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "messages": [
      {"role":"user","content":"¿Qué es el Gross Profit?"},
      {"role":"assistant","content":"Es la ganancia antes de gastos generales..."},
      {"role":"user","content":"¿Y cómo se calcula el porcentaje?"}
    ]
  }' | python3 -m json.tool
```

---

## Notas

- **Puerto por defecto**: siempre `--port 8001` (el 8000 puede estar ocupado por Portainer u otro servicio).
- **Modelo IA gratuito**: `nvidia/nemotron-3-super-120b-a12b:free` vía OpenRouter. Se puede cambiar con la variable `OPENROUTER_MODEL` en `.env`.
- **`labor_dollars` = 0 en técnicos**: el PDF `hours_detail` no incluye desglose de dólares por técnico, solo horas pagadas y vendidas.
- **WIP es snapshot vivo**: cada importación de Work in Progress elimina todos los registros anteriores y carga el estado actual. No hay histórico de WIP.
- **Re-importación idempotente**: `daily_sales`, `hours_summary` y `technician_hours` borran el período e insertan de nuevo — subir el mismo PDF dos veces no duplica datos.
- **Streaming SSE en el frontend**: requiere `fetch` nativo (no Axios) porque Axios no expone `ReadableStream` para consumo incremental.

---

## Comandos rápidos

```bash
# Importar todos los archivos de muestra de una vez
bash scripts/import_sample_data.sh

# Con otro puerto o fecha
API_URL=http://localhost:8001 DATE_TAG=20260428 bash scripts/import_sample_data.sh

# Arrancar backend y frontend
# Terminal 1
source venv/bin/activate && uvicorn app.main:app --reload --port 8001

# Terminal 2
cd ../frontend && npm run dev

# Verificar que ambos responden
curl -s http://localhost:8001/ && curl -s http://localhost:5173 | head -3

# Detener ambos procesos
pkill -f "uvicorn app.main" && pkill -f "vite"

# Verificar imports de Python sin levantar el servidor
source venv/bin/activate && python -c "
from app.routers.chat import router
from app.services.chat_service import ChatService
from app.schemas.chat import ChatRequest
print('OK — imports limpios')
"
```