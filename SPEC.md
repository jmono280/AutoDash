# Automania Dashboard — Spec para Claude Code

## Objetivo
Construir un **dashboard analítico** para el taller mecánico Automania que visualice métricas operativas y financieras a partir de 4 fuentes de datos (3 PDFs + 1 Excel) que se cargan periódicamente y se almacenan en PostgreSQL como 4 tablas.

Arquitectura **MVVM**, backend **FastAPI**, base de datos **PostgreSQL** con **SQLAlchemy ORM** (tablas como objetos Python), frontend **React + Vite + Tailwind CSS**.

---

## Stack tecnológico

### Frontend
| Capa | Tecnología |
|---|---|
| Framework | React 18 + Vite |
| Estilos | Tailwind CSS v3 |
| Routing | React Router v6 |
| Estado global | Zustand |
| Estado servidor | TanStack Query v5 |
| Formularios | React Hook Form + Zod |
| HTTP client | Axios (con interceptores JWT) |
| Gráficas | Recharts |

### Backend
| Capa | Tecnología |
|---|---|
| Framework | FastAPI |
| ORM | SQLAlchemy 2.0 async |
| Validación | Pydantic v2 |
| Auth | python-jose (JWT) + bcrypt |
| Driver BD | asyncpg |
| Migraciones | Alembic |
| Parseo PDF | pdfplumber |
| Parseo Excel | openpyxl + pandas |

---

## Las 4 tablas de la base de datos

Cada tabla se alimenta de un archivo fuente. Los archivos se suben mediante un endpoint de importación que parsea y persiste los registros.

### Tabla 1: `daily_sales` (de daily_sales_*.pdf)
Reporte diario de ventas por día del mes.
```
id              UUID PK
date            DATE          (ej: 2026-04-01)
day_of_week     VARCHAR(10)   (Monday, Tuesday…)
total_cars      INT
gross_sales     NUMERIC(10,2)
net_sales       NUMERIC(10,2)
sales           NUMERIC(10,2)
ticket_average  NUMERIC(10,2)
cost_of_goods   NUMERIC(10,2)
cogs_percent    NUMERIC(5,2)
gross_profit    NUMERIC(10,2)
gross_profit_pct NUMERIC(5,2)
period_start    DATE          (rango del reporte)
period_end      DATE
imported_at     TIMESTAMPTZ
```

### Tabla 2: `hours_summary` (de hours_*.pdf, página 2)
Resumen de horas por taller con KPIs de eficiencia.
```
id                      UUID PK
shop_name               VARCHAR(100)  (ej: "Automania")
labor_dollars           NUMERIC(10,2)
hours_sold              NUMERIC(8,2)
hours_paid              NUMERIC(8,2)
hours_worked            NUMERIC(8,2)
actual_hours            NUMERIC(8,2)
advisor_efficiency      NUMERIC(5,2)  (Hours Sold / Hours Paid)
technician_proficiency  NUMERIC(5,2)  (Hours Paid / Hours Worked)
technician_productivity NUMERIC(5,2)  (Actual Hours / Hours Worked)
technician_efficiency   NUMERIC(5,2)  (Hours Paid / Actual Hours, nullable)
period_start            DATE
period_end              DATE
imported_at             TIMESTAMPTZ
```

### Tabla 3: `technician_hours` (de hours_detail_*.pdf, agregado por técnico)
Detalle de horas por técnico individual.
```
id                      UUID PK
technician_name         VARCHAR(100)  (ej: "Joe Davis", "No Tech")
labor_dollars           NUMERIC(10,2)
hours_sold              NUMERIC(8,2)
hours_paid              NUMERIC(8,2)
hours_worked            NUMERIC(8,2)
actual_hours            NUMERIC(8,2)
technician_proficiency  NUMERIC(5,2)  nullable
technician_productivity NUMERIC(5,2)  nullable
period_start            DATE
period_end              DATE
imported_at             TIMESTAMPTZ
```

### Tabla 4: `work_in_progress` (del work_in_progress_detail_*.xlsx)
Órdenes de reparación en curso, una fila por línea de pieza/labor.
```
id              UUID PK
shop_number     INT
ro_number       VARCHAR(20)       (RO #)
op_code         VARCHAR(50)
supplier        VARCHAR(100)      nullable
advisor         VARCHAR(50)       nullable
opened          TIMESTAMPTZ
days_open       INT
customer        VARCHAR(150)
stock_other_id  VARCHAR(50)       nullable
vehicle         VARCHAR(150)
vin             VARCHAR(20)
estimated       NUMERIC(10,2)     nullable
category        VARCHAR(100)      (ej: "Engine", "Brakes / ABS")
cog             NUMERIC(10,2)     (Cost of Goods)
col             NUMERIC(10,2)     (Cost of Labor)
imported_at     TIMESTAMPTZ
```

---

## Arquitectura MVVM

```
FRONTEND (React)
├── View          → src/views/           Páginas del dashboard
├── ViewModel     → src/viewmodels/      Custom hooks por dashboard
└── Model         → src/models/          API services TypeScript

BACKEND (FastAPI)
├── routers/      Endpoints REST por dominio
├── schemas/      Pydantic DTOs
├── services/     Lógica de negocio + agregaciones SQL
├── repositories/ Queries SQL
├── importers/    Parseo de PDFs y Excel → modelos
├── models/       Modelos ORM SQLAlchemy
└── core/         Config, JWT, dependencias
```

---

## Estructura de carpetas completa

```
automania-dashboard/
├── backend/
│   ├── app/
│   │   ├── main.py
│   │   ├── database.py
│   │   ├── core/
│   │   │   ├── config.py
│   │   │   ├── security.py
│   │   │   └── dependencies.py
│   │   ├── models/
│   │   │   ├── base.py              # TimestampMixin con UUID
│   │   │   ├── user.py
│   │   │   ├── daily_sales.py
│   │   │   ├── hours_summary.py
│   │   │   ├── technician_hours.py
│   │   │   └── work_in_progress.py
│   │   ├── schemas/
│   │   │   ├── auth.py
│   │   │   ├── daily_sales.py
│   │   │   ├── hours.py
│   │   │   ├── work_in_progress.py
│   │   │   └── kpis.py              # Schemas agregados para dashboards
│   │   ├── repositories/
│   │   │   ├── daily_sales_repo.py
│   │   │   ├── hours_repo.py
│   │   │   ├── technician_repo.py
│   │   │   └── wip_repo.py
│   │   ├── services/
│   │   │   ├── auth_service.py
│   │   │   ├── sales_service.py
│   │   │   ├── hours_service.py
│   │   │   ├── technician_service.py
│   │   │   └── wip_service.py
│   │   ├── importers/
│   │   │   ├── daily_sales_pdf.py   # Parsea daily_sales_*.pdf
│   │   │   ├── hours_summary_pdf.py # Parsea hours_*.pdf (pág. 2)
│   │   │   ├── hours_detail_pdf.py  # Parsea hours_detail_*.pdf
│   │   │   └── wip_excel.py         # Parsea work_in_progress_*.xlsx
│   │   └── routers/
│   │       ├── auth.py
│   │       ├── sales.py             # GET /sales, /sales/kpis
│   │       ├── hours.py             # GET /hours, /hours/kpis
│   │       ├── technicians.py       # GET /technicians, /technicians/ranking
│   │       ├── wip.py               # GET /wip, /wip/aging, /wip/by-category
│   │       └── imports.py           # POST /imports/{type}
│   ├── alembic/
│   ├── requirements.txt
│   └── .env.example
│
└── frontend/
    ├── index.html
    ├── vite.config.ts
    ├── tailwind.config.ts
    ├── tsconfig.json
    └── src/
        ├── main.tsx
        ├── App.tsx
        ├── views/
        │   ├── OverviewDashboard.tsx        # Resumen ejecutivo
        │   ├── SalesDashboard.tsx           # Ventas diarias
        │   ├── HoursDashboard.tsx           # Eficiencia de horas
        │   ├── TechniciansDashboard.tsx     # Performance por técnico
        │   ├── WorkInProgressDashboard.tsx  # WIP y aging
        │   ├── ImportsView.tsx              # Subida de archivos
        │   └── LoginView.tsx
        ├── viewmodels/
        │   ├── useOverview.ts
        │   ├── useSales.ts
        │   ├── useHours.ts
        │   ├── useTechnicians.ts
        │   ├── useWip.ts
        │   ├── useImports.ts
        │   └── useAuth.ts
        ├── models/
        │   ├── api.ts
        │   ├── salesApi.ts
        │   ├── hoursApi.ts
        │   ├── techniciansApi.ts
        │   ├── wipApi.ts
        │   ├── importsApi.ts
        │   └── authApi.ts
        ├── components/
        │   ├── layout/
        │   │   ├── Sidebar.tsx
        │   │   └── Navbar.tsx
        │   ├── ui/
        │   │   ├── KpiCard.tsx
        │   │   ├── DateRangePicker.tsx
        │   │   ├── Spinner.tsx
        │   │   └── EmptyState.tsx
        │   └── charts/
        │       ├── DailySalesBarChart.tsx
        │       ├── EfficiencyGaugeChart.tsx
        │       ├── TechnicianRankingChart.tsx
        │       ├── CategoryPieChart.tsx
        │       └── WipAgingChart.tsx
        ├── store/
        │   └── authStore.ts
        ├── types/
        │   ├── sales.ts
        │   ├── hours.ts
        │   ├── technician.ts
        │   ├── wip.ts
        │   └── kpis.ts
        └── router/
            └── index.tsx
```

---

## Endpoints FastAPI

### Auth
```
POST   /auth/login
POST   /auth/refresh
GET    /auth/me
```

### Sales (daily_sales)
```
GET /sales                      ?from=&to=                  → list[DailySaleOut]
GET /sales/kpis                 ?from=&to=                  → SalesKpisOut
   {total_cars, total_gross, total_net, avg_ticket, total_cogs, total_profit, profit_pct}
GET /sales/by-day-of-week       ?from=&to=                  → agrupado por día de semana
GET /sales/trend                ?from=&to=&granularity=day  → serie temporal
```

### Hours (hours_summary)
```
GET /hours                      ?from=&to=                  → list[HoursSummaryOut]
GET /hours/kpis                 ?from=&to=                  → HoursKpisOut
   {labor_dollars, hours_sold, hours_paid, advisor_eff, tech_proficiency, tech_productivity}
```

### Technicians (technician_hours)
```
GET /technicians                ?from=&to=                  → list[TechnicianOut]
GET /technicians/ranking        ?from=&to=&metric=labor     → ranking ordenado
GET /technicians/{name}         ?from=&to=                  → detalle individual
```

### Work in Progress (work_in_progress)
```
GET /wip                        ?advisor=&category=&min_days=&max_days=&page=&limit=
GET /wip/aging                                              → buckets de antigüedad
   {0-7d, 8-14d, 15-30d, 31-60d, 60+d}  con counts y total_estimated
GET /wip/by-category                                        → agrupado por categoría
GET /wip/by-advisor                                         → agrupado por advisor
GET /wip/kpis                                               → WipKpisOut
   {total_ros, total_estimated, total_cog, total_col, avg_days_open, oldest_ro_days}
```

### Imports
```
POST /imports/daily-sales       multipart/form-data: file (.pdf)
POST /imports/hours-summary     multipart/form-data: file (.pdf)
POST /imports/hours-detail      multipart/form-data: file (.pdf)
POST /imports/work-in-progress  multipart/form-data: file (.xlsx)
GET  /imports/history                                       → últimas 50 importaciones
```

Cada importación:
1. Parsea el archivo
2. Detecta el período (period_start / period_end) o `imported_at`
3. Inserta los registros (con upsert si ya existen registros del mismo período)
4. Retorna `{rows_inserted, rows_updated, period_start, period_end}`

---

## Páginas del frontend

### 1. Overview Dashboard (`/`)
Vista ejecutiva con los KPIs más importantes de las 4 tablas.
- Selector de rango de fechas (default: mes actual)
- 6 KPI cards principales:
  - Total cars (daily_sales)
  - Net sales totales
  - Gross profit %
  - Advisor efficiency (hours_summary)
  - WIP total ($ estimated abierto)
  - ROs vencidas (>30 días abiertas)
- Mini-gráfica de ventas diarias (line chart)
- Top 3 técnicos por labor $
- WIP por antigüedad (bar chart)

### 2. Sales Dashboard (`/sales`)
- KPIs: total cars, gross sales, net sales, ticket avg, COGS %, profit %
- Bar chart de ventas diarias
- Line chart de tendencia (gross sales vs net sales)
- Bar chart por día de la semana
- Tabla detallada de los días del período

### 3. Hours Dashboard (`/hours`)
- KPIs: labor $, hours sold, advisor efficiency, technician proficiency
- Gauge charts para los 4 ratios de eficiencia
- Comparativa hours_sold vs hours_paid vs hours_worked

### 4. Technicians Dashboard (`/technicians`)
- Ranking por labor $ (bar chart horizontal)
- Comparativa de proficiency entre técnicos
- Tabla con todas las métricas por técnico
- Click en un técnico → drill-down con gráficas individuales

### 5. Work in Progress Dashboard (`/wip`)
- KPIs: total ROs, total estimated, total COG, avg days open
- Aging chart (0-7d, 8-14d, 15-30d, 31-60d, 60+d)
- Pie chart por categoría
- Bar chart por advisor
- Tabla filtrable de ROs (search por customer, vehicle, RO#)
- Filtros: advisor, category, días abiertos

### 6. Imports (`/imports`)
- 4 zonas drag-and-drop, una por tipo de archivo
- Historial de últimas 50 importaciones (fecha, tipo, filas, periodo)
- Mensajes de éxito/error con detalles del parseo

---

## Importadores — lógica de parseo

### daily_sales_pdf.py
- Parsea con pdfplumber, busca tabla con columnas: Date, Day of Week, Total Cars, Gross Sales, Net Sales, Sales, Ticket Average, Cost of Goods, COGS %, Gross Profit, Gross Profit %
- Ignora filas de Totals/Averages
- Detecta período del título: "MM/DD/YYYY - MM/DD/YYYY"
- Convierte montos quitando $ y comas

### hours_summary_pdf.py
- Solo parsea la página con la tabla "Hours Report" (segunda sección)
- Una fila por shop (Automania) + Company Totals
- Convierte porcentajes (81.09% → 81.09)

### hours_detail_pdf.py
- Identifica secciones por técnico (header con el nombre)
- Captura el "{Nombre} Total" de cada técnico
- "No Tech" también es un técnico válido
- Una fila por técnico

### wip_excel.py
- pandas read_excel sobre la primera hoja
- Mapea columnas Excel a campos del modelo
- Cada fila del Excel = una fila en work_in_progress
- Parsea fechas con pd.to_datetime
- Trata "Estimated" NaN como NULL

**Estrategia de upsert por período:**
Para `daily_sales`, `hours_summary`, `technician_hours`: si ya existen registros del mismo `period_start`/`period_end`, los borra antes de insertar los nuevos.
Para `work_in_progress`: snapshot completo — borra todo lo importado anteriormente y carga el snapshot nuevo (es un estado vivo, no histórico).

---

## Variables de entorno

### backend/.env
```
DATABASE_URL=postgresql+asyncpg://user:password@localhost:5432/automania_db
SECRET_KEY=cambiar-en-produccion
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7
CORS_ORIGINS=http://localhost:5173
UPLOAD_DIR=./uploads
```

### frontend/.env
```
VITE_API_BASE_URL=http://localhost:8000
```

---

## Convenciones de código

### Backend
- Async/await en todos los endpoints, queries y parsers
- Dependency injection con `Depends()` para DB session y usuario
- Repositorios SOLO queries SQL; los servicios manejan agregaciones y lógica
- Responses con esquemas Pydantic, nunca el modelo ORM directamente
- Los importadores son funciones puras: reciben bytes/path, retornan list[dict]
- HTTP 401 no autenticado, 403 sin permisos, 404 no encontrado, 422 validación

### Frontend
- Nunca llamar `axios` desde un componente — siempre vía ViewModel hook
- Recharts para todas las gráficas con paleta consistente
- KPI cards reutilizables vía componente `<KpiCard>`
- Formato de números con `Intl.NumberFormat` (USD para $, % para porcentajes)
- DateRangePicker controlado a nivel ViewModel (no en cada componente)

---

## Cómo arrancar el proyecto

```bash
# Backend
cd backend
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
alembic upgrade head
uvicorn app.main:app --reload --port 8000

# Frontend
cd frontend
npm install
npm run dev
```

---

## Orden de implementación sugerido para Claude Code

1. **Backend models** — los 4 modelos SQLAlchemy + User + base mixin
2. **Alembic** — migración inicial con las 5 tablas
3. **Backend schemas** — Pydantic DTOs para cada entidad + KPIs
4. **Backend auth** — JWT login/refresh/me
5. **Backend importers** — los 4 parsers (PDF y Excel)
6. **Backend imports router** — endpoints de subida
7. **Backend repositorios y servicios** — agregaciones SQL para dashboards
8. **Backend routers de datos** — sales, hours, technicians, wip
9. **Frontend setup** — Vite + Tailwind + Router + Zustand + TanStack
10. **Frontend Model** — axios + todos los API services
11. **Frontend ViewModel** — todos los custom hooks
12. **Frontend Charts components** — librería de gráficas reutilizables
13. **Frontend Views** — Overview → Sales → Hours → Technicians → WIP → Imports

---

## Prompt sugerido para iniciar Claude Code

```
Lee CLAUDE.md y SPEC.md completos antes de escribir código.
Implementa el paso 1: los 4 modelos SQLAlchemy de las tablas
de datos (daily_sales, hours_summary, technician_hours,
work_in_progress) más el modelo User, todos heredando del
TimestampMixin con UUID, timestamps y soft delete.
```
