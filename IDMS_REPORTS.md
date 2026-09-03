# IDMS Reports — Resumen de implementación

> Integración del scraper de IDMS/AutoAnalytix dentro del dashboard profesional `AutoDash`.

---

## 1. Estado actual

### ✅ Terminado

#### Backend (AutoDash)

- **Autenticación con IDMS** mediante scraping del login de DealerSocket/Solera B2C.
- **Exportación de reportes** vía Exago AJAX a CSV.
- **Persistencia en PostgreSQL** con SQLAlchemy async.
- **Endpoints creados** bajo `/idms`:
  - `GET  /idms/session`
  - `POST /idms/login`
  - `POST /idms/charge-offs/sync?year=YYYY`
  - `POST /idms/charge-offs/import-historical` (Excel histórico)
  - `GET  /idms/charge-offs`
  - `GET  /idms/charge-offs/kpis`
  - `GET  /idms/charge-offs/monthly`
  - `GET  /idms/charge-offs/years`

#### Frontend (AutoDash)

- Nueva ruta: `/idms-reports`
- Nuevo ítem de menú: **Finanzas → IDMS Reports** (visible para todos los usuarios autenticados)
- Pantalla con:
  - Login a IDMS (con campo opcional de MFA/OTP)
  - Selector de año
  - Botón **Sincronizar año**
  - KPIs (Charge Offs, Original Balance, Total C/O Balance, Recovery, Adjusted)
  - Gráfica de barras mensual
  - Tabla mensual
  - Tabla de detalle de cuentas

#### Base de datos

- Tabla creada: `idms_charge_offs`
- Migración Alembic: `c47db103ab76_add_idms_charge_offs_table.py`

#### Datos cargados

Se importó el archivo histórico `Auto Analytix - Charge Offs - Manual Pull.xlsx` (1230 cuentas únicas).

| Año | Unidades | Original Balance |
|---|---|---|
| 2021 | 171 | $1,272,687.82 |
| 2022 | 264 | $2,548,603.56 |
| 2023 | 258 | $2,425,760.62 |
| 2024 | 224 | $2,126,400.10 |
| 2025 | 203 | $1,829,570.06 |
| 2026 | 110 | $962,743.39 |

Los datos de **2025 y 2026** fueron validados contra el Excel de AutoAnalytix y coinciden exactamente en unidades y montos.

---

## 2. Arquitectura y archivos

### Backend

```
backend/app/
├── core/config.py                    ← settings IDMS (IDMS_URL, IDMS_USERNAME, IDMS_PASSWORD, IDMS_DEVICE_KEY, IDMS_CLIENT_KEY_API)
├── importers/
│   ├── idms_session_store.py         ← guarda cookies de sesión IDMS en data/idms_session.json
│   ├── idms_client.py                ← login y export CSV de IDMS/Exago
│   ├── idms_parsers.py               ← parseo de CSV a dicts
│   └── idms_chargeoff_excel.py       ← parseo del Excel histórico
├── models/
│   └── idms_charge_off.py            ← modelo SQLAlchemy
├── repositories/
│   └── idms_repo.py                  ← queries y sync
├── services/
│   └── idms_service.py               ← lógica de negocio
├── routers/
│   └── idms.py                       ← endpoints FastAPI
├── schemas/
│   └── idms.py                       ← DTOs Pydantic
└── main.py                           ← registro del router /idms
```

### Frontend

```
frontend/src/
├── types/idms.ts
├── models/idmsApi.ts
├── viewmodels/useIdms.ts
├── views/IdmsDashboard.tsx
├── router/index.tsx                  ← ruta /idms-reports
└── components/layout/Sidebar.tsx     ← ítem de menú
```

### Otros archivos modificados

- `backend/requirements.txt` — añadido `requests`
- `backend/.env.example` — añadidas variables IDMS
- `backend/alembic/versions/c47db103ab76_add_idms_charge_offs_table.py`

---

## 3. Cómo levantar y probar

### Requisitos

- PostgreSQL corriendo (el mismo de AutoDash).
- Variables IDMS en `backend/.env`:
  ```env
  IDMS_URL=https://idms.dealersocket.com
  IDMS_USERNAME=tu-usuario
  IDMS_PASSWORD=tu-password
  IDMS_DEVICE_KEY=
  IDMS_CLIENT_KEY_API=
  ```
  > Nota: las credenciales se copiaron desde `IdmsAuto/.env` durante la implementación.

### Comandos

```bash
# Backend
cd /home/gutidev/Documents/Dev/AutoDash/backend
venv/bin/python -m uvicorn app.main:app --host 0.0.0.0 --port 8001

# Frontend (otra terminal)
cd /home/gutidev/Documents/Dev/AutoDash/frontend
npm run dev
```

### Flujo de prueba

1. Abrir `http://localhost:5173/idms-reports`
2. Loguearse en AutoDash
3. Si no hay sesión IDMS activa, ingresar el OTP de la app autenticadora y conectar
4. Seleccionar un año (2021-2026)
5. Click en **Sincronizar año** (para años 2025-2026 actualiza desde IDMS; para años históricos no es necesario porque ya están cargados)

---

## 4. Pendientes (por hacer)

### Alta prioridad

- [x] **Completar Charge Offs (tab Overview de AutoAnalytix)**
  - Modelo `idms_month_end` + migración `b1da0cd3226f`, más la columna
    `recovery_acv` en `idms_charge_offs`.
  - Parser `parse_aa_month_end` (reporte `2159272`) y **fix**: charge offs y el
    importador de Excel leían la columna equivocada para Recovery.
  - Endpoints: `/idms/charge-offs/overview`, `/idms/charge-offs/monthly-detail`,
    `/idms/month-end/sync`.
  - Frontend: KPIs YTD con delta contra el año anterior y su MTD, los 3 ratios,
    tabla mensual con las 9 columnas y gráfica Current vs Prior Year.
  - Validado: los 12 meses de 2025 reproducen exactamente los montos, el Recovery
    ACV (561.529,09) y el Recovery Ratio (30,69%) de AutoAnalytix.

- [x] **Implementar Sales**
  - Modelo `idms_sales` + migración `e7c7c0474609`.
  - Parsers: `parse_aa_sales` (reporte IDMS `2159264`) y `parse_aa_sales_manual`
    (histórico CSV).
  - Endpoints: `/idms/sales/sync`, `/idms/sales/import-historical`, `/idms/sales`,
    `/idms/sales/kpis`, `/idms/sales/monthly`, `/idms/sales/years`,
    `/idms/sales/by-salesperson`, `/idms/sales/by-vehicle`.
  - Frontend: tab **Sales** en `IdmsDashboard.tsx` con KPIs, gráfica mensual,
    tabla mensual, top vendedores, top vehículos y detalle de ventas.

- [ ] **Implementar Collections**
  - Modelo `idms_collections`
  - Parser del reporte IDMS `2160337`
  - Endpoints similares a Sales
  - Frontend: tab o sección de Collections

### Media prioridad

- [x] **Arreglar `npm run build` del frontend**
  - Se quitó `"ignoreDeprecations": "6.0"` de `tsconfig.app.json` (no suprimía ninguna deprecación real, solo rompía el build con TS 5.8.3).
  - Además había una función muerta (`todayStr`) en `CallAnalyticsDashboard.tsx` rechazada por `noUnusedLocals`; se eliminó.
  - `npm run build` compila limpio (solo queda un warning no bloqueante de tamaño de chunk en `vite build`).

- [ ] **Mejorar manejo de sesión IDMS**
  - Actualmente requiere OTP la primera vez si el device key no evita el challenge.
  - Evaluar si se puede guardar una sesión persistente más robusta o programar sync automático.

- [ ] **Sync automático programado**
  - Actualmente la sincronización es manual.
  - Agregar un scheduler (por ejemplo, diario) para actualizar 2025/2026 desde IDMS.

### Baja prioridad

- [ ] **Tests**
  - Agregar tests de los parsers.
  - Agregar tests de los endpoints.

- [ ] **Documentación de despliegue**
  - Actualizar `README.md` de AutoDash con la nueva funcionalidad IDMS Reports.

---

## 5. Módulo Sales

### Tabla

`idms_sales` — una fila por cuenta vendida.

### Fuentes

- **IDMS**: reporte `2159264` (Sales MySQL).
- **Histórico manual**: `examples_sales/Auto Analytix - Sales - Manual Pull.csv`.

### Endpoints

```http
POST /idms/sales/sync?year=YYYY
POST /idms/sales/import-historical
GET  /idms/sales?year=YYYY
GET  /idms/sales/kpis?year=YYYY
GET  /idms/sales/monthly?year=YYYY
GET  /idms/sales/years
GET  /idms/sales/by-salesperson?year=YYYY
GET  /idms/sales/by-vehicle?year=YYYY
```

### Notas

- El CSV histórico no trae `Contract Sales Price` ni `Contract Cash Down`, así que
  esas columnas quedan en `0` para años anteriores a 2025.
- El sync desde IDMS (`2159264`) sí trae `Contract Sales Price` y el resto de
  columnas del reporte MySQL.
- Los KPIs principales son: # of Sales, Gross Profit, Amount Financed y
  Sales Price.

### Importar histórico

```bash
curl -s -X POST http://localhost:8001/idms/sales/import-historical \
  -H "Authorization: Bearer $TOKEN" \
  -F "file=@examples_sales/Auto Analytix - Sales - Manual Pull.csv" | jq
```

---

## 4.b Dónde viven los reportes en IDMS

Los reportes que alimentan AutoAnalytix son de **Martin Gutierrez (`owner_id 109916`)**
y están en **Custom Reports**. Dos detalles del filtro de IDMS que conviene recordar:

- `qreporttype_id`: `0` = All, `1` = Standard, `2` = **Custom**.
- `qowner_id`: `0` **no** es "todos", es `[Public]`.

`IdmsClient.list_reports()` pide tipo 1 + owner 0, así que no lista ninguno de estos.

Familia MySQL (la generación vigente), 11 reportes:

| ID | Reporte | Usado |
|---|---|---|
| `2159264` | Sales (MySQL) | sí |
| `2159268` | Charge Offs (MySQL) | sí |
| `2160337` | iDMS Collections (MySQL) | sí |
| `2159272` | Month End (MySQL) | sí — snapshot de cartera |
| `2159270` | Aging and Recency (MySQL) | no |
| `2159265` | Inventory (MySQL) | no |
| `2159271` | Projections (MySQL) | no |
| `2159266` | Promise To Pay (MySQL) | no |
| `2160339` | iDMS Collector Stats (MySQL) | no |
| `2159269` / `2163772` | Service (MySQL) | no |
| `2160649` | Write Offs (MySQL) | no |

## 4.c Fórmulas del Charge Off Overview

Verificadas contra los números reales de AutoAnalytix, no deducidas:

- **Recovery ACV** = columna `Charge Off ACV Adjusted`. **No** es
  `Total_Charge_Off_Recovery`, que viene casi siempre en cero.
- **Recovery Ratio** = Recovery ACV / Original C/O Balance.
- **Gross C/O Ratio** = Original C/O Balance / Month End Principal Bal.
- **Annualized C/O Ratio** = Gross C/O Ratio × 12.
- **Avg Prin Bal C/O** = Original C/O Balance / unidades.
- **YTD** = meses del año con datos; el delta compara contra **ese mismo rango de
  meses** del año anterior. **MTD** = último mes con datos.

El **Month End Principal Bal** sale del reporte `2159272`, que es un snapshot vivo:
IDMS no guarda los saldos de meses cerrados. Como solo disponemos del snapshot más
reciente, el backend usa ese balance para calcular `Gross C/O Ratio` y
`Annualized C/O Ratio` del año consultado. `has_portfolio_data` en el endpoint
`/overview` indica si hay un snapshot de cartera disponible.

**Months On Book** quedó implementado como la antigüedad promedio de la cartera
activa (contrato → fecha del snapshot). No se pudo contrastar contra AutoAnalytix
porque su captura es de meses para los que no hay snapshot; la mediana daba 13,00
contra el 13,00 que muestra AutoAnalytix, así que si el número no cuadra, probar
con mediana en `get_month_end_by_period`.

## 5. Notas importantes

- El scraper de IDMS es **frágil**: si IDMS cambia el login o los endpoints de Exago, el sync se romperá.
- La sesión IDMS se guarda en `backend/data/idms_session.json` (vigencia 30 días).
- El sync de IDMS **preserva los históricos** (2021-2024) y solo sobrescribe los años que vienen en el reporte descargado (2025-2026).
- Se creó un usuario de prueba `viewer@automania.com / Viewer123!` para probar endpoints; en producción debe cambiarse/eliminarlo.

---

## 6. Comandos útiles

```bash
# Ver años disponibles
curl -s http://localhost:8001/idms/charge-offs/years -H "Authorization: Bearer $TOKEN" | jq

# Sincronizar desde IDMS
curl -s -X POST 'http://localhost:8001/idms/charge-offs/sync?year=2025' -H "Authorization: Bearer $TOKEN" | jq

# Importar Excel histórico
curl -s -X POST http://localhost:8001/idms/charge-offs/import-historical \
  -H "Authorization: Bearer $TOKEN" \
  -F "file=@/ruta/al/Auto Analytix - Charge Offs - Manual Pull.xlsx" | jq
```
