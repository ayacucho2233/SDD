# Reserva de Vehículos Corporativos

Sistema para que los empleados reserven vehículos del pool corporativo y un
administrador mantenga ese pool. Ver el PRD en
`reserva-vehiculos-corporativos.md` y la especificación funcional completa en
`specs/001-reserva-vehiculos-corporativos/`.

## Stack

React + Vite (frontend) · Python + FastAPI (backend) · PostgreSQL (base de
datos). Detalle de decisiones técnicas en
`specs/001-reserva-vehiculos-corporativos/research.md`.

## Requisitos previos

- Git
- Python 3.11 o superior
- Node.js 18 o superior (incluye npm)
- PostgreSQL 14 o superior, corriendo localmente (`pg_isready` debe devolver
  "accepting connections")

## Guía rápida para probarlo (paso a paso)

### 1. Clonar el repositorio

```bash
git clone git@github.com:ayacucho2233/SDD.git
cd SDD
```

(Si no tenés acceso SSH configurado, usar la URL HTTPS:
`git clone https://github.com/ayacucho2233/SDD.git`)

### 2. Base de datos

```bash
psql -U postgres -c "CREATE USER reserva_app WITH PASSWORD 'elegi-una-password';"
psql -U postgres -c "CREATE DATABASE reserva_vehiculos OWNER reserva_app;"
```

**Si `psql -U postgres` falla con "Peer authentication failed"**: agregar
`-h 127.0.0.1` para forzar autenticación por contraseña en vez de por
usuario del sistema operativo:

```bash
psql -h 127.0.0.1 -U postgres -c "CREATE USER reserva_app WITH PASSWORD 'elegi-una-password';"
psql -h 127.0.0.1 -U postgres -c "CREATE DATABASE reserva_vehiculos OWNER reserva_app;"
```

### 3. Backend

```bash
cd backend
python -m venv venv
source venv/bin/activate        # Linux/Mac
venv\Scripts\activate           # Windows

pip install -r requirements.txt

cp .env.example .env
```

Editar `backend/.env`:

- `DATABASE_URL`: reemplazar `elegi-una-password` por la password real que
  usaste en el paso 2 (y `localhost` por `127.0.0.1` si tuviste que usar
  `-h 127.0.0.1` arriba).
- `ADMIN_USER`: usuario para entrar a la sección Administración (ej. `admin`).
- `ADMIN_PASSWORD_HASH`: generar con la contraseña que quieras usar para
  entrar como admin:

  ```bash
  python -c "from passlib.hash import bcrypt; print(bcrypt.hash('tu-password'))"
  ```

  **Importante**: para loguearte en el frontend usás `ADMIN_USER` +
  `tu-password` (la contraseña en texto plano), **no** el hash — el hash
  solo va en el `.env`.

Aplicar las migraciones y levantar el servidor:

```bash
alembic upgrade head
uvicorn app.main:app --reload
# API en http://localhost:8000 · documentación interactiva (Swagger) en
# http://localhost:8000/docs
```

Dejar esta terminal corriendo.

### 4. Cargar al menos un vehículo

El pool arranca **vacío** a propósito (ver PRD, dependencia D-01): sin este
paso, el frontend no va a mostrar nada para reservar. En otra terminal:

```bash
curl -u admin:tu-password -X POST http://localhost:8000/admin/vehiculos \
  -H "Content-Type: application/json" \
  -d '{"patente": "AB123CD", "tipo": "auto"}'
```

(Reemplazar `admin:tu-password` por el `ADMIN_USER` y la contraseña que
configuraste en el paso 3. También se puede hacer este alta desde
`http://localhost:8000/docs`, endpoint `POST /admin/vehiculos`.)

### 5. Frontend

En otra terminal (sin cerrar la del backend):

```bash
cd frontend
npm install
cp .env.example .env
# El valor por defecto (VITE_API_URL=http://localhost:8000) ya funciona
# si el backend quedó en el puerto 8000 del paso 3.
npm run dev
# App en http://localhost:5173
```

### 6. Probar en el navegador

Abrir `http://localhost:5173`:

- **Reservar**: debería verse el vehículo cargado en el paso 4; completar
  el formulario y confirmar la reserva.
- **Mis reservas**: ver la reserva recién creada, filtrar por estado,
  cancelarla ingresando el legajo usado al crearla.
- **Administración**: loguearse con `ADMIN_USER` / la contraseña en texto
  plano del paso 3; dar de alta, editar, dar de baja (temporal/definitiva)
  o reactivar vehículos.

## Tests

```bash
# Backend (requiere una base de datos de test; ver TEST_DATABASE_URL en
# backend/tests/conftest.py — por defecto reserva_vehiculos_test, pero
# también puede apuntar a la misma base del paso 2 si el rol reserva_app
# no tiene permiso para crear bases nuevas)
cd backend && pytest

# Frontend
cd frontend && npm test
```

## Validación end-to-end

Ver `specs/001-reserva-vehiculos-corporativos/quickstart.md` para los 4
escenarios curl (equivalentes a los pasos 4 y 6 de arriba, pero con más
casos de error) que validan las 3 historias de usuario de punta a punta.
