# Automania Dashboard

Dashboard analítico para el taller Automania. Visualiza ventas, horas, técnicos y trabajo en progreso importando archivos PDF/Excel.

**Stack:** FastAPI · PostgreSQL · React + Vite · Docker

---

## Requisitos

- Docker + Docker Compose v2
- Git

---

## Primer despliegue en el servidor

### 1. Clonar el repositorio

```bash
git clone <repo-url> AutoDash
cd AutoDash
```

### 2. Configurar variables de entorno

```bash
cp backend/.env.example backend/.env
```

Editar `backend/.env` con los valores reales:

```env
# Base de datos
POSTGRES_USER=automania
POSTGRES_PASSWORD=password-seguro
POSTGRES_DB=automania_db
POSTGRES_HOST=localhost      # no cambiar, docker-compose sobreescribe esto
POSTGRES_PORT=5432

# Seguridad
SECRET_KEY=genera-una-clave-larga-y-aleatoria
CORS_ORIGINS=https://tu-dominio.com   # URL del frontend que verán los usuarios

# OpenRouter (IA)
OPENROUTER_API_KEY=tu-api-key-de-openrouter
```

Generar un `SECRET_KEY` seguro:
```bash
openssl rand -hex 32
```

### 3. Configurar la URL del backend para el frontend

El frontend necesita saber la URL pública del backend (la ve el browser del usuario, no el servidor):

```bash
export VITE_API_BASE_URL=https://api.tu-dominio.com
# o si usas Coolify/proxy inverso con el mismo dominio:
export VITE_API_BASE_URL=http://IP-DEL-SERVIDOR:8001
```

### 4. Construir y levantar

```bash
docker compose --env-file ./backend/.env up --build -d
```

### 5. Crear el usuario administrador (solo la primera vez)

```bash
docker compose exec backend python -m app.scripts.seed_admin
```

Credenciales por defecto: `admin@automania.com` / `password123`
Cambiar la contraseña desde la app después del primer login.

### 6. Cargar datos de muestra (opcional)

```bash
# Copiar los archivos de muestra al contenedor
docker compose cp backend/sample_data backend:/app/sample_data

# Ejecutar el script de importación
docker compose exec backend bash scripts/import_sample_data.sh
```

Para una fecha específica:
```bash
docker compose exec backend bash -c "DATE_TAG=20260423 bash scripts/import_sample_data.sh"
```

### 7. Verificar que todo funciona

```bash
docker compose ps

# Backend
curl http://localhost:8001/
# → {"status":"ok","app":"automania"}

# Frontend
curl -I http://localhost/
# → HTTP/1.1 200 OK
```

---

## Actualizar en el servidor

```bash
git pull
docker compose --env-file ./backend/.env up --build -d
```

Docker solo reconstruye los servicios con cambios. Las migraciones de base de datos corren automáticamente al reiniciar el backend.

---

## Comandos útiles

### Ver logs

```bash
docker compose logs -f              # todos los servicios
docker compose logs -f backend      # solo backend
docker compose logs -f frontend     # solo frontend
docker compose logs -f db           # solo base de datos
```

### Estado de los servicios

```bash
docker compose ps
```

### Reiniciar un servicio

```bash
docker compose restart backend
docker compose restart frontend
```

### Reconstruir un servicio específico

```bash
docker compose build --no-cache backend
docker compose up -d backend

docker compose build --no-cache frontend
docker compose up -d frontend
```

### Conectarse a la base de datos

```bash
docker compose exec db psql -U $POSTGRES_USER -d $POSTGRES_DB
```

### Ejecutar comandos en el backend

```bash
docker compose exec backend python -m app.scripts.seed_admin   # crear admin
docker compose exec backend alembic upgrade head               # aplicar migraciones
docker compose exec backend alembic current                    # ver migración activa
```

---

## Parar y limpiar

```bash
# Parar servicios (conserva datos)
docker compose down

# Parar y eliminar volúmenes (BORRA la base de datos)
docker compose down -v
```

---

## Desarrollo local (sin Docker)

### Backend

```bash
cd backend
python -m venv venv
source venv/bin/activate          # Windows: venv\Scripts\activate
pip install -r requirements.txt

# Requiere PostgreSQL corriendo en localhost:5432
alembic upgrade head
uvicorn app.main:app --reload --port 8001
```

### Frontend

```bash
cd frontend
npm install
npm run dev                        # http://localhost:5173
```

### Variables para dev local

`backend/.env` debe tener `POSTGRES_HOST=localhost`.
`frontend/.env` debe tener `VITE_API_BASE_URL=http://localhost:8001`.

---

## Estructura del proyecto

```
AutoDash/
├── backend/                  FastAPI + PostgreSQL
│   ├── app/
│   │   ├── routers/          Endpoints (auth, sales, hours, wip, chat...)
│   │   ├── services/         Lógica de negocio
│   │   ├── repositories/     Queries SQL
│   │   ├── importers/        Parsers PDF/Excel
│   │   ├── schemas/          DTOs Pydantic
│   │   └── models/           ORM SQLAlchemy
│   ├── alembic/              Migraciones de BD
│   ├── .env                  Variables de entorno (no commitear)
│   ├── .env.example          Template
│   └── Dockerfile
├── frontend/                 React + Vite + TypeScript
│   ├── src/
│   │   ├── views/            Páginas (dashboards)
│   │   ├── viewmodels/       Hooks de datos
│   │   ├── models/           Clientes HTTP
│   │   └── components/       UI reutilizable
│   ├── nginx.conf
│   └── Dockerfile
├── docker-compose.yaml
└── README.md
```

---

## Puertos

| Servicio  | Puerto | Descripción |
|-----------|--------|-------------|
| Frontend  | 80     | Interfaz web (nginx) |
| Backend   | 8001   | API REST + SSE |
| PostgreSQL | 5432  | Solo interno (no expuesto) |

Para cambiar puertos, exportar antes de levantar:
```bash
export FRONTEND_PORT=3000
docker compose --env-file ./backend/.env up -d
```
