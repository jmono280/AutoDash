# Automania Dashboard — Frontend

React 19 + Vite 6 + TypeScript + Tailwind CSS v3.

---

## Setup

```bash
cd frontend
npm install
```

Copia `.env.example` a `.env`:

```bash
cp .env.example .env
```

```env
VITE_API_BASE_URL=http://localhost:8001
```

> Ajusta el puerto al del backend que tengas corriendo (`8000` ó `8001`).

---

## Arrancar en desarrollo

```bash
npm run dev
# http://localhost:5173
```

El servidor de Vite tiene proxy configurado: `/api/*` redirige al backend automáticamente
(definido en `vite.config.ts`). La variable `VITE_API_BASE_URL` es la que usa
el cliente Axios en `src/models/api.ts`.

---

## Build de producción

```bash
npm run build     # genera dist/
npm run preview   # sirve el build en http://localhost:4173
```

---

## Lint

```bash
npm run lint
```

---

## Usuarios disponibles para login

| Email | Password | Rol |
|---|---|---|
| admin@automania.com | password123 | admin (puede importar) |
| viewer@automania.com | viewer123 | viewer (solo lectura) |

Crea los usuarios con los scripts del backend antes de abrir la app:

```bash
cd ../backend
source venv/bin/activate
python -m app.scripts.seed_admin
python -m app.scripts.seed_viewer
```

---

## Rutas de la aplicación

| Ruta | Componente | Descripción |
|---|---|---|
| `/login` | `LoginView` | Formulario de acceso |
| `/` | `OverviewDashboard` | Resumen ejecutivo — 6 KPIs + 2 gráficas + top 3 técnicos |
| `/sales` | `SalesDashboard` | Ventas diarias — tendencia, día de semana, tabla de 28 días |
| `/hours` | `HoursDashboard` | Horas del taller — gauges de eficiencia y proficiency |
| `/technicians` | `TechniciansDashboard` | Ranking por métrica + tabla completa de técnicos |
| `/wip` | `WorkInProgressDashboard` | Snapshot de órdenes — aging, categoría, asesor, filtros |
| `/imports` | `ImportsView` | Subir los 4 archivos fuente (solo rol admin) |

Cualquier ruta desconocida redirige a `/`. Rutas protegidas redirigen a `/login` si no hay sesión activa.

---

## Arquitectura MVVM

```
src/views/          JSX puro — sin axios, sin useState de datos remotos
src/viewmodels/     Custom hooks — TanStack Query + estado local de filtros
src/models/         *Api.ts — funciones axios tipadas, sin estado
src/store/          authStore.ts — Zustand con tokens JWT en memoria
src/types/          Interfaces TypeScript que espeja los schemas Pydantic
src/components/     ui/ (KpiCard, DataTable…) y charts/ (Recharts)
```

---

## Verificar la conexión al backend con curl

Los siguientes ejemplos reproducen exactamente las llamadas que hace el frontend.
Todos asumen el backend en `http://localhost:8001`; ajusta el puerto si hace falta.

### Obtener token

```bash
TOKEN=$(curl -sX POST http://localhost:8001/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@automania.com","password":"password123"}' \
  | jq -r .access_token)

echo $TOKEN   # debe imprimir el JWT
```

Sin `jq`:

```bash
TOKEN=$(curl -sX POST http://localhost:8001/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@automania.com","password":"password123"}' \
  | python3 -c "import sys,json; print(json.load(sys.stdin)['access_token'])")
```

---

### Auth

```bash
# Perfil del usuario autenticado (equivale a montar el Layout)
curl http://localhost:8001/auth/me \
  -H "Authorization: Bearer $TOKEN" | jq .

# Sin token → debe devolver 401
curl -o /dev/null -w "%{http_code}" http://localhost:8001/auth/me

# Refresh token
REFRESH=$(curl -sX POST http://localhost:8001/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@automania.com","password":"password123"}' \
  | jq -r .refresh_token)

curl -sX POST http://localhost:8001/auth/refresh \
  -H "Content-Type: application/json" \
  -d "{\"refresh_token\":\"$REFRESH\"}" | jq .

# Logout
curl -sX POST http://localhost:8001/auth/logout \
  -H "Authorization: Bearer $TOKEN" | jq .
```

---

### Imports (pestaña /imports)

```bash
# Daily Sales PDF
curl -X POST http://localhost:8001/imports/daily-sales \
  -H "Authorization: Bearer $TOKEN" \
  -F "file=@../backend/sample_data/daily_sales_20260428.pdf" | jq .

# Hours Summary PDF
curl -X POST http://localhost:8001/imports/hours-summary \
  -H "Authorization: Bearer $TOKEN" \
  -F "file=@../backend/sample_data/hours_20260428.pdf" | jq .

# Hours Detail PDF (técnicos)
curl -X POST http://localhost:8001/imports/hours-detail \
  -H "Authorization: Bearer $TOKEN" \
  -F "file=@../backend/sample_data/hours_detail_20260428.pdf" | jq .

# Work in Progress XLSX
curl -X POST http://localhost:8001/imports/work-in-progress \
  -H "Authorization: Bearer $TOKEN" \
  -F "file=@../backend/sample_data/work_in_progress_detail_20260428.xlsx" | jq .

# Archivo inválido → debe devolver 400 con detail
echo "fake" > /tmp/bad.pdf
curl -w "\nHTTP %{http_code}" -X POST http://localhost:8001/imports/daily-sales \
  -H "Authorization: Bearer $TOKEN" \
  -F "file=@/tmp/bad.pdf"
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

### Overview Dashboard (/)

El Overview consulta simultáneamente sales KPIs, hours KPIs, WIP KPIs, aging y trend.

```bash
# KPIs de ventas
curl "http://localhost:8001/sales/kpis?from=2026-04-01&to=2026-04-28" \
  -H "Authorization: Bearer $TOKEN" | jq .

# KPIs de horas
curl "http://localhost:8001/hours/kpis?from=2026-04-01&to=2026-04-28" \
  -H "Authorization: Bearer $TOKEN" | jq .

# KPIs de WIP
curl "http://localhost:8001/wip/kpis" \
  -H "Authorization: Bearer $TOKEN" | jq .

# Aging (para el gráfico de barras)
curl "http://localhost:8001/wip/aging" \
  -H "Authorization: Bearer $TOKEN" | jq .

# Tendencia de ventas diarias
curl "http://localhost:8001/sales/trend?from=2026-04-01&to=2026-04-28" \
  -H "Authorization: Bearer $TOKEN" | jq '.[0:5]'

# Ranking de técnicos (para el top 3)
curl "http://localhost:8001/technicians/ranking?metric=hours_sold&from=2026-04-01&to=2026-04-28" \
  -H "Authorization: Bearer $TOKEN" | jq '[.[:3][] | {technician_name, hours_sold}]'
```

Valores esperados con los archivos de muestra (abril 2026):

```
total_cars:         91
total_gross:        $71,740.61
total_profit:       $45,447.73
profit_pct:         63.35 %
advisor_efficiency: 81.09 %
open_ros:           256
oldest_ro_days:     91
```

---

### Sales Dashboard (/sales)

```bash
# KPIs del período
curl "http://localhost:8001/sales/kpis?from=2026-04-01&to=2026-04-28" \
  -H "Authorization: Bearer $TOKEN" | jq .

# Tendencia diaria (para el AreaChart)
curl "http://localhost:8001/sales/trend?from=2026-04-01&to=2026-04-28" \
  -H "Authorization: Bearer $TOKEN" | jq '.[0:3]'

# Promedio por día de la semana (para el BarChart)
curl "http://localhost:8001/sales/by-day-of-week?from=2026-04-01&to=2026-04-28" \
  -H "Authorization: Bearer $TOKEN" | jq .

# Lista de días (para la DataTable)
curl "http://localhost:8001/sales/?from=2026-04-01&to=2026-04-28" \
  -H "Authorization: Bearer $TOKEN" | jq 'length'
# → 28
```

---

### Hours Dashboard (/hours)

```bash
# KPIs + gauges
curl "http://localhost:8001/hours/kpis?from=2026-04-01&to=2026-04-28" \
  -H "Authorization: Bearer $TOKEN" | jq .

# Lista de períodos importados
curl "http://localhost:8001/hours/?from=2026-04-01&to=2026-04-28" \
  -H "Authorization: Bearer $TOKEN" | jq .
```

Respuesta `/hours/kpis`:

```json
{
  "labor_dollars":            "36977.05",
  "hours_sold":               "385.20",
  "hours_paid":               "475.00",
  "hours_worked":             "1094.53",
  "advisor_efficiency":       "81.09",
  "technician_proficiency":   "43.40",
  "technician_productivity":  "0",
  "technician_efficiency":    null
}
```

---

### Technicians Dashboard (/technicians)

```bash
# Lista completa del período
curl "http://localhost:8001/technicians/?from=2026-04-01&to=2026-04-28" \
  -H "Authorization: Bearer $TOKEN" | jq '[.[] | {technician_name, hours_sold, hours_paid}]'

# Ranking por horas vendidas (default)
curl "http://localhost:8001/technicians/ranking?metric=hours_sold&from=2026-04-01&to=2026-04-28" \
  -H "Authorization: Bearer $TOKEN" | jq '[.[] | {technician_name, hours_sold}]'

# Ranking por labor_dollars
curl "http://localhost:8001/technicians/ranking?metric=labor&from=2026-04-01&to=2026-04-28" \
  -H "Authorization: Bearer $TOKEN" | jq '.[0:3]'

# Ranking por proficiency
curl "http://localhost:8001/technicians/ranking?metric=proficiency&from=2026-04-01&to=2026-04-28" \
  -H "Authorization: Bearer $TOKEN" | jq .

# Detalle individual (click en fila de la tabla)
curl "http://localhost:8001/technicians/Joe%20Davis?from=2026-04-01&to=2026-04-28" \
  -H "Authorization: Bearer $TOKEN" | jq .

# 404 si no existe
curl -o /dev/null -w "%{http_code}" \
  "http://localhost:8001/technicians/Nadie%20Aqui?from=2026-04-01&to=2026-04-28" \
  -H "Authorization: Bearer $TOKEN"
# → 404
```

Ranking `hours_sold` con sample data:

| Técnico | hours_sold | hours_paid |
|---|---|---|
| Joe Davis | 64.66 | 90.40 |
| No Tech | 62.15 | 42.00 |
| Kevin Anderson | 43.34 | 47.10 |
| Erbin (Tony) Mota | 40.06 | 59.80 |

> `labor_dollars` = 0 en todos los técnicos: el PDF `hours_detail` solo
> expone horas pagadas y vendidas, no el desglose de dólares por técnico.

---

### WIP Dashboard (/wip)

```bash
# KPIs del snapshot actual
curl "http://localhost:8001/wip/kpis" \
  -H "Authorization: Bearer $TOKEN" | jq .

# Aging (orden cronológico: 0-7d → 8-14d → 15-30d → 31-60d → 60+d)
curl "http://localhost:8001/wip/aging" \
  -H "Authorization: Bearer $TOKEN" | jq .

# Por categoría (para el PieChart)
curl "http://localhost:8001/wip/by-category" \
  -H "Authorization: Bearer $TOKEN" | jq '.[0:5]'

# Por asesor (para el BarChart)
curl "http://localhost:8001/wip/by-advisor" \
  -H "Authorization: Bearer $TOKEN" | jq .

# Lista paginada (DataTable, 5 ítems por página en este ejemplo)
curl "http://localhost:8001/wip/?page=1&limit=5" \
  -H "Authorization: Bearer $TOKEN" | jq '{total, page, pages}'

# Filtro por asesor
curl "http://localhost:8001/wip/?advisor=MFal" \
  -H "Authorization: Bearer $TOKEN" | jq '{total}'
# → {"total": 65}

# Filtro por categoría
curl "http://localhost:8001/wip/?category=Engine" \
  -H "Authorization: Bearer $TOKEN" | jq '{total}'
# → {"total": 25}

# Filtro por antigüedad mínima (ROs con más de 30 días)
curl "http://localhost:8001/wip/?min_days=30&limit=10" \
  -H "Authorization: Bearer $TOKEN" | jq '{total, items: [.items[] | {ro_number, days_open, customer}]}'

# Combinado: asesor + categoría
curl "http://localhost:8001/wip/?advisor=MFal&category=Engine" \
  -H "Authorization: Bearer $TOKEN" | jq '{total}'
```

Respuesta `/wip/kpis` con sample data:

```json
{
  "total_ros":       256,
  "total_estimated": "0",
  "total_cog":       "18105.74",
  "total_col":       "0",
  "avg_days_open":   "11.15",
  "oldest_ro_days":  91
}
```

---

## Estructura del proyecto

```
frontend/
├── src/
│   ├── views/           Un archivo por pantalla (*Dashboard.tsx, *View.tsx)
│   ├── viewmodels/      Custom hooks con TanStack Query (use*.ts)
│   ├── models/          Funciones axios tipadas (*Api.ts)
│   ├── store/           authStore.ts — Zustand, tokens en memoria
│   ├── types/           Interfaces TypeScript (espeja schemas Pydantic)
│   ├── components/
│   │   ├── ui/          KpiCard, DataTable, DateRangePicker, Spinner…
│   │   └── charts/      DailySalesTrendChart, WipAgingChart, EfficiencyGauges…
│   ├── lib/             dateRange.ts — defaultRange(), formatDate()
│   └── router/          index.tsx — rutas + PrivateRoute
├── .env                 VITE_API_BASE_URL
├── .env.example
├── tailwind.config.js
├── vite.config.ts
└── tsconfig.json
```
