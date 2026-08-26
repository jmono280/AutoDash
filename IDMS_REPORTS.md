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

- [ ] **Implementar Sales**
  - Modelo `idms_sales`
  - Parser del reporte IDMS `2159264`
  - Endpoints: `/idms/sales/sync`, `/idms/sales`, `/idms/sales/kpis`, `/idms/sales/monthly`, `/idms/sales/years`
  - Frontend: tab o sección de Sales en `IdmsDashboard.tsx`

- [ ] **Implementar Collections**
  - Modelo `idms_collections`
  - Parser del reporte IDMS `2160337`
  - Endpoints similares a Sales
  - Frontend: tab o sección de Collections

### Media prioridad

- [ ] **Arreglar `npm run build` del frontend**
  - Error previo en `tsconfig.app.json`: `"ignoreDeprecations": "6.0"` no es válido en la versión de TypeScript instalada.
  - `npm run dev` funciona; el build de producción falla.

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
