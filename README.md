# Reserva de Vehículos Corporativos

Sistema para que los empleados reserven vehículos del pool corporativo y un
administrador mantenga ese pool. Ver el PRD en
`reserva-vehiculos-corporativos.md` y la especificación funcional completa en
`specs/001-reserva-vehiculos-corporativos/`.

## Stack

React + Vite (frontend) · Python + FastAPI (backend) · PostgreSQL (base de
datos). Detalle de decisiones técnicas en
`specs/001-reserva-vehiculos-corporativos/research.md`.

## Arranque local

### Base de datos

```bash
psql -U postgres -c "CREATE USER reserva_app WITH PASSWORD 'elegí-una-password';"
psql -U postgres -c "CREATE DATABASE reserva_vehiculos OWNER reserva_app;"
```

### Backend

```bash
cd backend
python -m venv venv
source venv/bin/activate        # Linux/Mac
venv\Scripts\activate           # Windows

pip install -r requirements.txt

cp .env.example .env
# Editar .env: DATABASE_URL, y ADMIN_PASSWORD_HASH generado con:
#   python -c "from passlib.hash import bcrypt; print(bcrypt.hash('tu-password'))"

alembic upgrade head
uvicorn app.main:app --reload
# API en http://localhost:8000 · docs en http://localhost:8000/docs
```

### Frontend

```bash
cd frontend
npm install
cp .env.example .env
# Editar .env: VITE_API_URL=http://localhost:8000
npm run dev
# App en http://localhost:5173
```

## Tests

```bash
# Backend (requiere una base de datos de test — ver TEST_DATABASE_URL en
# backend/tests/conftest.py; por defecto usa reserva_vehiculos_test)
cd backend && pytest

# Frontend
cd frontend && npm test
```

## Validación end-to-end

Ver `specs/001-reserva-vehiculos-corporativos/quickstart.md` para los 4
escenarios curl que validan las 3 historias de usuario de punta a punta.
