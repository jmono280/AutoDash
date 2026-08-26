# AGENTS.md — Automania Dashboard

Este archivo es el contexto maestro para cualquier agente de código que trabaje en el proyecto. Combina lo especificado en `SPEC.md` y `CLAUDE.md` con el estado real actual del repositorio. Léelo completo antes de tocar archivos.

---

## 1. Qué es este proyecto

Dashboard analítico para el taller mecánico **Automania**. Visualiza métricas operativas y financieras a partir de 4 archivos fuente que se cargan periódicamente:

1. `daily_sales_*.pdf` → tabla `daily_sales` (ventas diarias)
2. `hours_*.pdf` → tabla `hours_summary` (eficiencia del taller)
3. `hours_detail_*.pdf` → tabla `technician_hours` (performance por técnico)
4. `work_in_progress_*.xlsx` → tabla `work_in_progress` (órdenes en curso)

Además, el repositorio ya ha evolucionado para incluir funcionalidades extra:

- **Chat IA** (`/chat`) con OpenRouter + streaming SSE.
- **Call Analytics** (`/analytics/calls`) para métricas de llamadas (RingCentral).
- **Payment Report** (`/payment`) para reportes de pagos/cobranza.

La arquitectura base es **MVVM** en el frontend y **capas limpias** en el backend (routers → services → repositories → models).

---

## 2. Stack tecnológico — no sustituir

| Capa | Tecnología |
|---|---|
| Frontend | React 19 + Vite 6 + TypeScript 5.8 |
| Estilos | Tailwind CSS v3.4 |
| Routing | React Router v7 |
| Estado global | Zustand v5 |
| Estado servidor | TanStack Query v5 |
| Formularios | React Hook Form + Zod |
| HTTP | Axios v1.9 |
| Gráficas | Recharts v2.15 |
| Backend | FastAPI v0.115+ |
| ORM | SQLAlchemy 2.0 async |
| Validación | Pydantic v2 |
| Auth | python-jose + bcrypt |
| Driver BD | asyncpg |
| Migraciones | Alembic |
| Parser PDF | pdfplumber |
| Parser Excel | openpyxl + pandas |
| Base de datos | PostgreSQL 15+ |
| AI | openai (OpenRouter) |
| Otros | ringcentral, rich, python-dotenv |

---

## 3. Arquitectura MVVM — regla fundamental

```
FRONTEND (React)
├── View       → src/views/         Solo JSX + props. Cero lógica, cero llamadas a API.
├── ViewModel  → src/viewmodels/    Custom hooks. Orquesta estado y llama al Model.
└── Model      → src/models/        Funciones async que llaman a FastAPI. Solo HTTP.

BACKEND (FastAPI)
├── routers/      Endpoints REST por dominio
├── schemas/      Pydantic DTOs
├── services/     Lógica de negocio + agregaciones SQL
├── repositories/ Queries SQL
├── importers/    Parseo de PDFs y Excel → modelos
├── models/       Modelos ORM SQLAlchemy
└── core/         Config, JWT, dependencias
```

### Violaciones que nunca debes hacer

- ❌ Llamar `axios` o `fetch` dentro de un componente View.
- ❌ Hacer agregaciones de datos en el frontend que el backend debería hacer en SQL.
- ❌ Importar un `*Api` directamente en una View — siempre pasa por el ViewModel hook.
- ❌ Retornar el modelo ORM SQLAlchemy directamente desde un endpoint — siempre usar schema Pydantic.
- ❌ Mezclar lógica de parseo dentro de un router — el parseo va en `app/importers/`.

---

## 4. Tablas principales

### 4 tablas base del dashboard

```
daily_sales         (date, day_of_week, total_cars, gross_sales, net_sales, sales,
                     ticket_average, cost_of_goods, cogs_percent, gross_profit,
                     gross_profit_pct, period_start, period_end, imported_at)

hours_summary       (shop_name, labor_dollars, hours_sold, hours_paid, hours_worked,
                     actual_hours, advisor_efficiency, technician_proficiency,
                     technician_productivity, technician_efficiency, period_start,
                     period_end, imported_at)

technician_hours    (technician_name, labor_dollars, hours_sold, hours_paid,
                     hours_worked, actual_hours, technician_proficiency,
                     technician_productivity, period_start, period_end, imported_at)

work_in_progress    (shop_number, ro_number, op_code, supplier, advisor, opened,
                     days_open, customer, stock_other_id, vehicle, vin, estimated,
                     category, cog, col, imported_at)
```

Las 3 primeras tienen `period_start` y `period_end`. La cuarta (`work_in_progress`) es un snapshot vivo (se sobrescribe en cada importación).

### Tablas adicionales actuales

```
users               (email, hashed_password, full_name, role, is_active, timestamps + soft delete)
call_analytics      (extensión, fecha, llamadas entrantes/salientes, duración, etc.)
collection_stat     / payment_transaction  (reporte de pagos/cobranza)
```

---

## 5. Estructura de archivos real

```
AutoDash/
├── backend/
│   ├── app/
│   │   ├── main.py                 # Setup FastAPI, CORS, routers
│   │   ├── database.py             # Engine async, get_db
│   │   ├── core/
│   │   │   ├── config.py           # Settings desde .env
│   │   │   ├── security.py         # JWT + bcrypt
│   │   │   └── dependencies.py     # Depends(get_db), get_current_user
│   │   ├── models/                 # ORM SQLAlchemy (base.py + entidades)
│   │   ├── schemas/                # Pydantic DTOs
│   │   ├── repositories/           # Queries SQL
│   │   ├── services/               # Lógica de negocio
│   │   ├── importers/              # Parsers puros bytes → list[dict]
│   │   ├── routers/                # Endpoints FastAPI
│   │   └── scripts/                # seed_admin, seed_viewer, analitycs, chat
│   ├── alembic/                    # Migraciones
│   ├── sample_data/                # PDFs y XLSX de ejemplo
│   ├── .env.example
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/
│   ├── src/
│   │   ├── views/                  # Páginas (*Dashboard.tsx, *View.tsx)
│   │   ├── viewmodels/             # Custom hooks (use*.ts)
│   │   ├── models/                 # Funciones axios tipadas (*Api.ts)
│   │   ├── store/                  # authStore.ts (Zustand)
│   │   ├── types/                  # Interfaces TypeScript
│   │   ├── components/
│   │   │   ├── ui/                 # KpiCard, DataTable, DateRangePicker, Spinner…
│   │   │   └── charts/             # Gráficas Recharts reutilizables
│   │   ├── lib/                    # dateRange.ts
│   │   ├── router/                 # index.tsx rutas + protección
│   │   ├── App.tsx
│   │   ├── main.tsx
│   │   └── index.css
│   ├── .env
│   ├── .env.example
│   ├── vite.config.ts              # Proxy /api → backend
│   ├── tailwind.config.ts
│   └── Dockerfile
├── docker-compose.yaml             # Prod: db + backend + frontend
├── docker-compose.dev.yaml         # Solo PostgreSQL para dev local
├── README.md                       # Guía de deploy con Docker
├── CLAUDE.md                       # Convenciones originales
├── SPEC.md                         # Especificación funcional original
└── AGENTS.md                       # Este archivo
```

---

## 6. Variables de entorno

### `backend/.env` (copiar de `.env.example`)

```env
# Base de datos
POSTGRES_USER=automania
POSTGRES_PASSWORD=cambia-esto
POSTGRES_DB=automania_db
POSTGRES_HOST=localhost
POSTGRES_PORT=5432

# Seguridad
SECRET_KEY=cambiar-en-produccion
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7
CORS_ORIGINS=http://localhost,http://localhost:5173
UPLOAD_DIR=./uploads

# OpenRouter (Chat IA)
OPENROUTER_API_KEY=tu-api-key-de-openrouter
OPENROUTER_MODEL=nvidia/nemotron-3-super-120b-a12b:free
OPENROUTER_MAX_TOKENS_OUT=512
OPENROUTER_MAX_HISTORY=10
OPENROUTER_MAX_CONTEXT_CHARS=500

# RingCentral (solo para scripts de analitycs)
RC_APP_CLIENT_ID=tu-client-id
RC_APP_CLIENT_SECRET=tu-client-secret
RC_SERVER_URL=https://platform.ringcentral.com
RC_USER_JWT=tu-jwt-token
RC_EXTENSION_IDS=101,102,103
```

### `frontend/.env`

```env
VITE_API_BASE_URL=http://localhost:8001
```

Nunca hardcodear URLs ni secrets. Siempre `settings.X` en Python e `import.meta.env.VITE_X` en TypeScript.

---

## 7. Comandos del proyecto

### Backend (local)

```bash
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Base de datos (requiere PostgreSQL corriendo)
alembic upgrade head

# Crear usuarios de prueba
python -m app.scripts.seed_admin
python -m app.scripts.seed_viewer

# Arrancar servidor
uvicorn app.main:app --reload --port 8001
```

### Frontend (local)

```bash
cd frontend
npm install
npm run dev          # http://localhost:5173
npm run build
npm run lint
```

### Docker (producción)

```bash
# Configurar variables
cp backend/.env.example backend/.env
# Editar backend/.env con valores reales

# Levantar todo
docker compose --env-file ./backend/.env up --build -d

# Crear admin la primera vez
docker compose exec backend python -m app.scripts.seed_admin

# Cargar datos de muestra (opcional)
docker compose cp backend/sample_data backend:/app/sample_data
docker compose exec backend bash scripts/import_sample_data.sh
```

### Docker (dev — solo DB)

```bash
# Desde la raíz
docker compose -f docker-compose.dev.yaml up -d
# Luego correr backend y frontend localmente contra localhost:5432
```

### PostgreSQL útiles

```bash
# Ver conteo de registros
docker exec <container_db> psql -U $POSTGRES_USER -d $POSTGRES_DB -c "
SELECT 'daily_sales' AS tabla, COUNT(*) FROM daily_sales
UNION ALL SELECT 'hours_summary', COUNT(*) FROM hours_summary
UNION ALL SELECT 'technician_hours', COUNT(*) FROM technician_hours
UNION ALL SELECT 'work_in_progress', COUNT(*) FROM work_in_progress
UNION ALL SELECT 'users', COUNT(*) FROM users;"
```

---

## 8. Convenciones de código

### Python / FastAPI

```python
# ✅ Importer — función pura, sin DB
def parse_daily_sales_pdf(file_bytes: bytes) -> list[DailySalesRow]:
    """Recibe bytes del PDF, retorna lista de filas tipadas. Sin side effects."""
    ...

# ✅ Repositorio — solo queries
class DailySalesRepository:
    async def get_range(self, db, start: date, end: date) -> list[DailySales]:
        result = await db.execute(
            select(DailySales)
            .where(DailySales.date.between(start, end))
            .order_by(DailySales.date)
        )
        return result.scalars().all()

# ✅ Servicio — agregaciones y lógica de negocio
class SalesService:
    def __init__(self, repo: DailySalesRepository):
        self.repo = repo
    async def get_kpis(self, db, start, end) -> SalesKpisOut:
        return await self.repo.aggregate_kpis(db, start, end)

# ✅ Router — delega al servicio, retorna schema Pydantic
@router.get("/kpis", response_model=SalesKpisOut)
async def get_sales_kpis(
    from_date: date = Query(..., alias="from"),
    to_date: date = Query(..., alias="to"),
    service: SalesService = Depends(),
    db: AsyncSession = Depends(get_db),
):
    return await service.get_kpis(db, from_date, to_date)
```

**Códigos HTTP:**

- `200` respuesta normal
- `201` recurso creado / importación exitosa
- `400` archivo malformado en importación
- `401` no autenticado
- `403` sin permisos
- `404` no encontrado
- `422` validación Pydantic

**Modelos SQLAlchemy:** heredan del mixin base con `id` UUID, `created_at`, `updated_at`, `deleted_at`. Soft delete obligatorio excepto en los upserts de importación por período.

**Agregaciones SQL:** usar `func.sum`, `func.avg`, `func.count`, `case`, `group_by`. No traer todo a Python para agregar.

### TypeScript / React

```typescript
// ✅ Model — solo HTTP, sin estado
export const salesApi = {
  getKpis: (params: { from: string; to: string }) =>
    api.get<SalesKpis>('/sales/kpis', { params }),
}

// ✅ ViewModel — hook que combina queries
export function useSales(range: DateRange) {
  const kpis = useQuery({
    queryKey: ['sales', 'kpis', range],
    queryFn: () => salesApi.getKpis(range),
  })
  return { kpis: kpis.data, isLoading: kpis.isLoading }
}

// ✅ View — solo presenta
export function SalesDashboard() {
  const [range, setRange] = useState(defaultRange())
  const { kpis, isLoading } = useSales(range)
  if (isLoading) return <Spinner />
  return <DateRangePicker value={range} onChange={setRange} />
}
```

**Reglas TypeScript:**

- Nunca `any` — si no sabes el tipo, usa `unknown` + narrowing.
- Interfaces de datos en `src/types/` deben coincidir con schemas Pydantic.
- `as` casting solo con comentario explicando por qué.

### Recharts — paleta consistente

- Verde `#1D9E75` → profit, sales (positivas)
- Púrpura `#534AB7` → volumen (cars, ROs)
- Azul `#378ADD` → horas
- Ámbar `#BA7517` → warnings (días abiertos altos)
- Rojo `#A32D2D` → vencidos
- No mezclar más de 4 colores en una misma gráfica.

### Tailwind CSS

- Clases utilitarias directamente en JSX.
- Componentes reutilizables en `src/components/ui/` y `src/components/charts/`.
- Nunca `style={{}}` para algo que Tailwind puede manejar.

---

## 9. Patrones importantes

### Estrategia de importación / upsert

- **`daily_sales`, `hours_summary`, `technician_hours`**: identificar `period_start` y `period_end`, borrar registros existentes en ese período y reinsertar. Re-subir el mismo PDF no duplica.
- **`work_in_progress`**: snapshot vivo. Cada importación elimina TODOS los registros anteriores y carga el snapshot nuevo. No hay histórico de WIP.

### Agregaciones de KPIs

Todos los endpoints `/kpis` reciben `from` y `to` como query params (`YYYY-MM-DD`). Si no se proveen, default = mes actual. Las agregaciones se hacen en SQL.

### Aging buckets para WIP

```python
case(
    (WorkInProgress.days_open <= 7, "0-7d"),
    (WorkInProgress.days_open <= 14, "8-14d"),
    (WorkInProgress.days_open <= 30, "15-30d"),
    (WorkInProgress.days_open <= 60, "31-60d"),
    else_="60+d"
).label("bucket")
```

### JWT flow

1. Login → `access_token` (30 min) + `refresh_token` (7 días).
2. Zustand guarda tokens en memoria, NO localStorage.
3. Axios interceptor añade `Authorization: Bearer {token}`.
4. Si `401` → llama `/auth/refresh` automáticamente y reintenta.
5. Si refresh falla → logout + redirect a `/login`.

### Soft delete

Nunca `db.delete(obj)` para datos del usuario. Siempre:

```python
obj.deleted_at = datetime.utcnow()
await db.commit()
```

Las queries de listado filtran `Model.deleted_at.is_(None)`.

**Excepción:** los upserts de período en importadores SÍ usan `delete()` físico.

---

## 10. Endpoints actuales (FastAPI)

### Auth

```
POST /auth/login
POST /auth/refresh
POST /auth/logout
GET  /auth/me
POST /auth/change-password
```

### Imports

```
POST /imports/daily-sales
POST /imports/hours-summary
POST /imports/hours-detail
POST /imports/work-in-progress
GET  /imports/history
```

### Sales

```
GET /sales
GET /sales/kpis
GET /sales/trend
GET /sales/by-day-of-week
```

### Hours

```
GET /hours
GET /hours/kpis
```

### Technicians

```
GET /technicians
GET /technicians/ranking
GET /technicians/{name}
```

### WIP

```
GET /wip
GET /wip/kpis
GET /wip/aging
GET /wip/by-category
GET /wip/by-advisor
```

### Chat IA

```
POST /chat/completions
```

### Analytics / Payment

```
GET/POST /analytics/calls/*
GET/POST /payment/*
```

(Consultar los routers correspondientes para la firma exacta.)

---

## 11. Rutas del frontend

| Ruta | Componente | Descripción |
|---|---|---|
| `/login` | `LoginView` | Formulario de acceso |
| `/` | `OverviewDashboard` | Resumen ejecutivo |
| `/sales` | `SalesDashboard` | Ventas diarias |
| `/hours` | `HoursDashboard` | Eficiencia de horas |
| `/technicians` | `TechniciansDashboard` | Ranking y tabla de técnicos |
| `/wip` | `WorkInProgressDashboard` | WIP y aging |
| `/imports` | `ImportsView` | Subida de archivos (solo admin) |
| `/chat` | `ChatView` | Asistente IA |
| `/analytics` | `CallAnalyticsDashboard` | Métricas de llamadas |
| `/payment-report` | `PaymentReportDashboard` | Reporte de pagos |
| `/profile` | `ProfileView` | Cambiar contraseña del usuario logueado |

Cualquier ruta desconocida redirige a `/`. Rutas protegidas redirigen a `/login` si no hay sesión.

### Control de acceso por rol

El rol del usuario viene en `/auth/me` (`admin` | `viewer`) y se guarda en `authStore`. Para restringir una ruta:

1. En el router usar `<RoleRoute roles={['admin']}>...</RoleRoute>`.
2. En el Sidebar agregar `roles: ['admin']` al `NavItem`.
3. Usar `hasRole(user, roles)` desde `frontend/src/lib/permissions.ts` para checks puntuales.

Rutas restringidas actualmente:

- `/imports` → admin
- `/payment` → admin
- `/chat` → admin

Las demás rutas son accesibles para cualquier usuario autenticado.

---

## 12. Probar el backend con curl

### Login

```bash
TOKEN=$(curl -sX POST http://localhost:8001/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@automania.com","password":"password123"}' | jq -r .access_token)
```

### Importar archivos de muestra

```bash
# Daily sales
curl -X POST http://localhost:8001/imports/daily-sales \
  -H "Authorization: Bearer $TOKEN" \
  -F "file=@backend/sample_data/daily_sales_20260428.pdf" | jq .

# Hours summary
curl -X POST http://localhost:8001/imports/hours-summary \
  -H "Authorization: Bearer $TOKEN" \
  -F "file=@backend/sample_data/hours_20260428.pdf" | jq .

# Hours detail (técnicos)
curl -X POST http://localhost:8001/imports/hours-detail \
  -H "Authorization: Bearer $TOKEN" \
  -F "file=@backend/sample_data/hours_detail_20260428.pdf" | jq .

# Work in progress
curl -X POST http://localhost:8001/imports/work-in-progress \
  -H "Authorization: Bearer $TOKEN" \
  -F "file=@backend/sample_data/work_in_progress_detail_20260428.xlsx" | jq .
```

### Verificar KPIs

```bash
# Sales
curl "http://localhost:8001/sales/kpis?from=2026-04-01&to=2026-04-28" \
  -H "Authorization: Bearer $TOKEN" | jq .

# Hours
curl "http://localhost:8001/hours/kpis?from=2026-04-01&to=2026-04-28" \
  -H "Authorization: Bearer $TOKEN" | jq .

# WIP
curl "http://localhost:8001/wip/kpis" \
  -H "Authorization: Bearer $TOKEN" | jq .

# WIP aging
curl "http://localhost:8001/wip/aging" \
  -H "Authorization: Bearer $TOKEN" | jq .
```

### Cambiar contraseña vía Docker

Ejecutar desde la raíz del repo (donde está `docker-compose.yaml`):

```bash
# 1. Obtener token
TOKEN=$(docker compose exec backend bash -c "curl -sX POST http://localhost:8001/auth/login \
  -H 'Content-Type: application/json' \
  -d '{\"email\":\"admin@automania.com\",\"password\":\"password123\"}'" \
  | python3 -c "import sys,json; print(json.load(sys.stdin)['access_token'])")

# 2. Cambiar contraseña (debe tener 8+ caracteres, mayúscula, número y signo de puntuación)
docker compose exec backend bash -c "curl -sX POST http://localhost:8001/auth/change-password \
  -H 'Content-Type: application/json' \
  -H \"Authorization: Bearer $TOKEN\" \
  -d '{\"current_password\":\"password123\",\"new_password\":\"NuevaPass1!\"}'" \
  | python3 -m json.tool
```

Respuesta esperada:

```json
{
  "message": "Contraseña actualizada correctamente"
}
```

---

## 13. Valores esperados con datos de muestra (abril 2026)

```
total_cars:          91
total_gross:         $71,740.61
total_net:           $71,740.61
total_profit:        $45,447.73
profit_pct:          63.35%
cogs_pct:            36.65%
avg_ticket:          $396.89
labor_dollars:       $36,977.05
hours_sold:          385.20
hours_paid:          475.00
hours_worked:        1094.53
advisor_efficiency:  81.09%
tech_proficiency:    43.40%
open_ros:            256
oldest_ro_days:      91
avg_days_open:       11.15
```

Top 3 técnicos por `hours_sold`:

| Técnico | hours_sold | hours_paid |
|---|---|---|
| Joe Davis | 64.66 | 90.40 |
| No Tech | 62.15 | 42.00 |
| Kevin Anderson | 43.34 | 47.10 |

> `labor_dollars` = 0 en todos los técnicos porque el PDF `hours_detail` solo expone horas pagadas y vendidas, sin desglose de dólares por técnico.

---

## 14. Checklist antes de marcar una tarea como completa

- [ ] El código sigue la capa MVVM correcta.
- [ ] No hay `any` en TypeScript.
- [ ] No hay secrets hardcodeados.
- [ ] Los endpoints retornan schemas Pydantic, no modelos ORM.
- [ ] Las queries de listado filtran `deleted_at IS NULL`.
- [ ] Las agregaciones se hacen en SQL, no en Python.
- [ ] Los importadores son funciones puras (sin DB session).
- [ ] Los componentes no llaman a la API directamente.
- [ ] Las gráficas usan la paleta definida.
- [ ] Se actualiza `AGENTS.md` si se modifican arquitectura, stack o convenciones.

---

## 15. Referencia rápida de archivos clave

| Archivo | Propósito |
|---|---|
| `backend/app/main.py` | Setup FastAPI, CORS, routers |
| `backend/app/database.py` | Engine async, `get_db` dependency |
| `backend/app/core/config.py` | Settings desde `.env` |
| `backend/app/core/security.py` | JWT + bcrypt |
| `backend/app/models/base.py` | `TimestampMixin` con UUID + soft delete |
| `backend/app/importers/*.py` | Parsers `bytes → list[dict]` |
| `backend/app/repositories/*.py` | Queries SQL |
| `backend/app/services/*.py` | Lógica de negocio |
| `backend/app/routers/*.py` | Endpoints REST |
| `frontend/src/models/api.ts` | Instancia axios con interceptores JWT |
| `frontend/src/store/authStore.ts` | Zustand, tokens en memoria |
| `frontend/src/components/ui/KpiCard.tsx` | Componente base de KPI |
| `frontend/src/components/charts/` | Librería de gráficas Recharts |
| `docker-compose.yaml` | Orquestación producción |
| `docker-compose.dev.yaml` | Solo PostgreSQL para desarrollo |

---

## 16. Notas finales para el agente

- El proyecto ya tiene código real en backend y frontend. No asumir que está en blanco.
- Antes de modificar algo, leer el archivo objetivo y sus dependencias directas.
- Preferir editar archivos existentes sobre crear nuevos.
- Si se agrega una nueva entidad, seguir el patrón: `model → schema → repository → service → router`.
- Si se agrega una nueva pantalla, seguir el patrón: `type → model → viewmodel → view`.
- Mantener consistencia con el estilo y nombres ya existentes.
- Para dudas de negocio, consultar `SPEC.md` y `CLAUDE.md` originales.
