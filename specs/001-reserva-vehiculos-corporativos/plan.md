# Implementation Plan: Reserva de Vehículos Corporativos

**Branch**: `001-reserva-vehiculos-corporativos` | **Date**: 2026-07-22 | **Spec**: [spec.md](./spec.md)

**Input**: Feature specification from `/specs/001-reserva-vehiculos-corporativos/spec.md`

## Summary

Sistema de reserva de vehículos corporativos: los empleados consultan
disponibilidad y crean/cancelan reservas a su propio nombre sin
autenticación (acceso restringido a la red interna de la empresa); un
administrador autenticado con HTTP Basic mantiene el pool de vehículos
(alta, modificación, baja temporal/definitiva, reactivación). El enfoque
técnico es una app web clásica de 3 capas — React + Vite (frontend),
FastAPI en capas routers/services/repositories (backend), PostgreSQL con
transacciones `SELECT FOR UPDATE` para evitar reservas duplicadas
concurrentes — siguiendo el stack y las reglas ya fijadas en `Agents.md`.

## Technical Context

**Language/Version**: Python 3.11+ (backend) · JavaScript ES2022+, sin TypeScript (frontend) — ver `research.md` §1

**Primary Dependencies**: FastAPI, SQLAlchemy 2.0 (async), Alembic, Pydantic, passlib[bcrypt] (backend) · React 18, Vite, axios (frontend) — ver `research.md` §2, §4

**Storage**: PostgreSQL 15+

**Testing**: pytest + pytest-asyncio + httpx.AsyncClient (backend) · vitest + @testing-library/react (frontend) — ver `research.md` §6

**Target Platform**: Servidor Linux (backend) accesible solo desde la red interna/VPN de la empresa; navegador de escritorio (frontend) — sin app móvil nativa (Assumptions, spec.md)

**Project Type**: Web application (frontend + backend separados)

**Performance Goals**: Consultas de disponibilidad p95 < 2s bajo carga normal (pool <50 vehículos, decenas de empleados concurrentes) — SC-002

**Constraints**: Reserva completable por un empleado en <1 minuto (SC-001); prevención de doble reserva concurrente sin excepciones (SC-003); sin exposición a Internet público (Assumptions, spec.md); zona horaria única fija por configuración (research.md §5)

**Scale/Scope**: Pool de vehículos <50 unidades; decenas de empleados consultando/reservando de forma concurrente; un único rol administrador (Assumptions, spec.md)

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principio | Aplica | Evaluación |
|---|---|---|
| I. Aislamiento de la Lógica de IA | No | Esta feature no incluye lógica de IA/LLM; no hay módulo de IA que aislar. |
| II. Respuestas Ancladas en la KB (Grounding) | No | No hay generación de respuestas por IA en esta feature. |
| III. Test-First para Clasificación | No | No hay lógica de clasificación por IA. La lógica de negocio crítica (solapamiento, transiciones de estado) se cubre igualmente con tests de contrato/integración (ver `contracts/api.md`, `quickstart.md`), aunque no es un mandato constitucional en este caso. |
| IV. Gestión Segura de Credenciales | Sí | Las credenciales de administrador (usuario + hash bcrypt) se leen de variables de entorno (`ADMIN_USER`, `ADMIN_PASSWORD_HASH`); ninguna credencial se hardcodea (`research.md` §4). **PASS**. |
| V. Alcance Limitado al PRD Vigente | Sí | Todos los artefactos de este plan (endpoints, entidades, casos de prueba) trazan 1:1 a los FR-001..FR-021/FR-005a/FR-009a de `spec.md`, sin funcionalidad adicional. **PASS**. |

**Resultado**: Sin violaciones. No aplica la tabla de Complexity Tracking.

## Project Structure

### Documentation (this feature)

```text
specs/001-reserva-vehiculos-corporativos/
├── plan.md              # This file (/speckit-plan command output)
├── research.md          # Phase 0 output (/speckit-plan command)
├── data-model.md        # Phase 1 output (/speckit-plan command)
├── quickstart.md        # Phase 1 output (/speckit-plan command)
├── contracts/
│   └── api.md            # Phase 1 output (/speckit-plan command)
└── tasks.md              # Phase 2 output (/speckit-tasks command - NOT created by /speckit-plan)
```

### Source Code (repository root)

```text
backend/
├── app/
│   ├── main.py            # App FastAPI, wiring de routers y CORS
│   ├── config.py          # Carga de variables de entorno
│   ├── database.py        # Engine/sesión SQLAlchemy async
│   ├── auth.py             # Dependencia HTTPBasic para /admin
│   ├── models/              # Vehiculo, Reserva (SQLAlchemy)
│   ├── schemas/              # Pydantic: request/response por endpoint
│   ├── routers/                # vehiculos.py, reservas.py, admin_vehiculos.py
│   ├── services/                 # disponibilidad, reservas, vehiculos (lógica de negocio)
│   └── repositories/               # acceso a datos (queries, incluye SELECT FOR UPDATE)
├── alembic/
│   └── versions/
├── tests/
│   ├── contract/            # 1 archivo por endpoint de contracts/api.md
│   ├── integration/         # flujos de quickstart.md (incluye test de concurrencia)
│   └── unit/                # servicios (validación de solapamiento, transiciones de estado)
├── requirements.txt
└── .env.example

frontend/
├── src/
│   ├── components/         # VehiculoList, ReservaForm, ReservaList, FiltroEstado, AdminVehiculoForm
│   ├── pages/                # PaginaReservar, PaginaMisReservas, PaginaAdmin
│   ├── services/               # cliente HTTP centralizado (axios wrapper) por dominio
│   └── App.jsx
├── tests/
│   ├── components/
│   └── pages/
├── package.json
└── .env.example
```

**Structure Decision**: Web application con `backend/` y `frontend/`
separados (Opción 2 del template), tal como fija `Agents.md`. El backend
sigue la separación en capas que exige `Agents.md` §Backend (routers /
services / repositories); el frontend organiza por componentes
reutilizables y un cliente HTTP centralizado, también por indicación de
`Agents.md` §Frontend.

## Complexity Tracking

> No hay violaciones de la Constitution Check — tabla no aplica.
