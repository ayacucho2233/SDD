---

description: "Task list template for feature implementation"
---

# Tasks: Reserva de Vehículos Corporativos

**Input**: Design documents from `/specs/001-reserva-vehiculos-corporativos/`

**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/api.md, quickstart.md

**Tests**: Se incluyen tareas de test (contract/integration/unit) porque `plan.md` ya
define carpetas dedicadas para ellas (`backend/tests/{contract,integration,unit}`,
`frontend/tests/`) y el dominio depende de reglas de negocio críticas
(solapamiento, concurrencia, transiciones de estado) que se benefician de
verificación automatizada.

**Organization**: Las tareas están agrupadas por historia de usuario (US1/US2/US3
de `spec.md`) para permitir implementación y prueba independientes de cada una.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Puede ejecutarse en paralelo (archivos distintos, sin dependencias)
- **[Story]**: A qué historia de usuario pertenece la tarea (US1, US2, US3)
- Cada tarea incluye la ruta de archivo exacta

## Path Conventions

Web app con `backend/` y `frontend/` separados (ver `plan.md` § Project Structure).

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Inicialización del proyecto y estructura base

- [X] T001 Crear estructura de directorios del backend per plan.md: `backend/app/{models,schemas,routers,services,repositories}/`, `backend/tests/{contract,integration,unit}/`
- [X] T002 [P] Crear estructura de directorios del frontend per plan.md: `frontend/src/{components,pages,services}/`, `frontend/tests/{components,pages}/`
- [X] T003 [P] Inicializar dependencias del backend en `backend/requirements.txt` (fastapi, uvicorn, sqlalchemy[asyncio], asyncpg, alembic, pydantic, passlib[bcrypt], pytest, pytest-asyncio, httpx)
- [X] T004 [P] Inicializar proyecto Vite+React y dependencias en `frontend/package.json` (react, react-dom, axios, vite, vitest, @testing-library/react)
- [X] T005 [P] Crear `backend/.env.example` con `DATABASE_URL`, `ADMIN_USER`, `ADMIN_PASSWORD_HASH`, `APP_TIMEZONE`, `FRONTEND_ORIGIN` (research.md §4, §5, §7)
- [X] T006 [P] Crear `frontend/.env.example` con `VITE_API_URL`
- [X] T007 [P] Inicializar Alembic en `backend/alembic/` y configurar `backend/alembic/env.py` para leer `DATABASE_URL`

**Checkpoint**: Proyecto inicializado, listo para infraestructura compartida.

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Infraestructura central que DEBE estar completa antes de implementar cualquier historia de usuario

**⚠️ CRITICAL**: Ninguna historia de usuario puede empezar hasta completar esta fase

- [X] T008 [P] Configurar engine/sesión async de SQLAlchemy en `backend/app/database.py`
- [X] T009 [P] Implementar carga de configuración desde variables de entorno en `backend/app/config.py`
- [X] T010 [P] Crear modelo SQLAlchemy `Vehiculo` en `backend/app/models/vehiculo.py` (patente única, `CHECK tipo IN ('auto','camioneta')`, `CHECK estado IN ('activo','baja_temporal','baja_definitiva')`) — depende de T008
- [X] T011 [P] Crear modelo SQLAlchemy `Reserva` en `backend/app/models/reserva.py` (FK a Vehiculo, `CHECK fecha_fin > fecha_inicio`) — depende de T008
- [X] T012 Crear migración Alembic para tablas `vehiculo`/`reserva` + índice único en patente + índice compuesto `(vehiculo_id, fecha_inicio, fecha_fin)` en `backend/alembic/versions/` (data-model.md § Índices) — depende de T010, T011
- [X] T013 Implementar dependencia de autenticación HTTP Basic (valida `ADMIN_USER`/`ADMIN_PASSWORD_HASH` con passlib/bcrypt) en `backend/app/auth.py` — depende de T009
- [X] T014 Configurar app FastAPI, `CORSMiddleware` restringido a `FRONTEND_ORIGIN` y registro de routers en `backend/app/main.py` — depende de T009
- [X] T015 [P] Crear cliente HTTP centralizado (wrapper de axios, base URL desde `VITE_API_URL`) en `frontend/src/services/apiClient.js`

**Checkpoint**: Fundación lista — la implementación de historias de usuario puede empezar.

---

## Phase 3: User Story 1 - Empleado reserva un vehículo disponible (Priority: P1) 🎯 MVP

**Goal**: Un empleado consulta el listado de vehículos y su disponibilidad, y crea
una reserva a su propio nombre; el sistema valida campos, fechas y evita
solapamientos incluso ante solicitudes concurrentes.

**Independent Test**: Con al menos un vehículo cargado (vía fixture de test, sin
depender de US3), completar el flujo ver disponibilidad → crear reserva, y
verificar que una segunda reserva superpuesta (incluso simultánea) se rechaza.

### Tests for User Story 1

> **NOTA**: Escribir estos tests PRIMERO y confirmar que fallan antes de implementar

- [X] T016 [P] [US1] Contract test `GET /vehiculos` (con y sin filtro de disponibilidad) en `backend/tests/contract/test_vehiculos_get.py`
- [X] T017 [P] [US1] Contract test `GET /vehiculos/{id}/disponibilidad` (200/400/404) en `backend/tests/contract/test_disponibilidad.py`
- [X] T018 [P] [US1] Contract test `POST /reservas` (201, 400 campo faltante, 400 fecha fin≤inicio, 400 inicio pasado, 404 vehículo inexistente, 409 solapamiento) en `backend/tests/contract/test_reservas_post.py`
- [X] T019 [P] [US1] Integration test de concurrencia: dos `POST /reservas` simultáneos para el mismo vehículo/período → exactamente uno 201 y el otro 409 (SC-003) en `backend/tests/integration/test_concurrencia_reservas.py`
- [X] T020 [P] [US1] Unit test de la lógica de solapamiento de períodos en `backend/tests/unit/test_disponibilidad_service.py`

### Implementation for User Story 1

- [X] T021 [P] [US1] Schemas Pydantic `VehiculoOut`, `ReservaCreate`, `ReservaOut` en `backend/app/schemas/vehiculo.py` y `backend/app/schemas/reserva.py`
- [X] T022 [US1] `VehiculoRepository` (list, get_by_id, lock_for_update) en `backend/app/repositories/vehiculo_repository.py` — depende de T010
- [X] T023 [US1] `ReservaRepository` (create, list_activas_solapadas con `SELECT ... FOR UPDATE` per research.md §3) en `backend/app/repositories/reserva_repository.py` — depende de T011
- [X] T024 [US1] `DisponibilidadService` (verifica solapamiento para un vehículo/período) en `backend/app/services/disponibilidad_service.py` — depende de T023
- [X] T025 [US1] `ReservaService.crear_reserva` (valida campos obligatorios FR-004, fecha_fin>fecha_inicio FR-005, fecha_inicio≥ahora FR-005a, y llama a `DisponibilidadService` dentro de una transacción) en `backend/app/services/reserva_service.py` — depende de T024
- [X] T026 [US1] Router `GET /vehiculos` y `GET /vehiculos/{id}/disponibilidad` en `backend/app/routers/vehiculos.py` — depende de T022, T024, T021
- [X] T027 [US1] Router `POST /reservas` en `backend/app/routers/reservas.py` — depende de T025, T021
- [X] T028 [P] [US1] Componente `VehiculoList` (consume `GET /vehiculos`) en `frontend/src/components/VehiculoList.jsx`
- [X] T029 [P] [US1] Componente `ReservaForm` con validación de campos obligatorios y fechas (fin>inicio, inicio≥ahora) en `frontend/src/components/ReservaForm.jsx`
- [X] T030 [US1] Página `PaginaReservar` que integra `VehiculoList` + `ReservaForm`, con estados de carga/éxito/error (incluye manejo de 409 por solapamiento) en `frontend/src/pages/PaginaReservar.jsx` — depende de T028, T029, T015

**Checkpoint**: User Story 1 completamente funcional y testeable de forma independiente.

---

## Phase 4: User Story 2 - Empleado consulta y cancela sus propias reservas (Priority: P2)

**Goal**: Un empleado lista y filtra reservas por estado (futuras/en curso/pasadas)
y cancela una reserva propia identificándose con su legajo.

**Independent Test**: Con reservas ya existentes (futuras, en curso y pasadas,
cargadas vía fixture), filtrar el listado por cada estado y cancelar una reserva
propia con su legajo, sin depender del flujo de creación de US1 en el mismo test.

### Tests for User Story 2

- [X] T031 [P] [US2] Contract test `GET /reservas` con filtro `estado` (futura/en_curso/pasada) en `backend/tests/contract/test_reservas_get.py`
- [X] T032 [P] [US2] Contract test `POST /reservas/{id}/cancelar` (200, 403 legajo distinto, 409 ya pasada/cancelada, 404) en `backend/tests/contract/test_reservas_cancelar.py`
- [X] T033 [P] [US2] Unit test del cálculo de estado derivado (futura/en curso/pasada/activa) en `backend/tests/unit/test_reserva_estado.py`

### Implementation for User Story 2

- [X] T034 [US2] Extender `ReservaRepository` con `list_by_estado` y `get_by_id` en `backend/app/repositories/reserva_repository.py` — depende de T023
- [X] T035 [US2] `ReservaService.listar_reservas` (filtro por estado derivado FR-007) en `backend/app/services/reserva_service.py` — depende de T034
- [X] T036 [US2] `ReservaService.cancelar_reserva` (valida legajo del creador FR-009, valida que esté activa FR-009a) en `backend/app/services/reserva_service.py` — depende de T034
- [X] T037 [US2] Router `GET /reservas` y `POST /reservas/{id}/cancelar` en `backend/app/routers/reservas.py` — depende de T035, T036
- [X] T038 [P] [US2] Componente `ReservaList` con filtro por estado en `frontend/src/components/ReservaList.jsx`
- [X] T039 [P] [US2] Componente `FiltroEstado` (futuras/en curso/pasadas) en `frontend/src/components/FiltroEstado.jsx`
- [X] T040 [US2] Página `PaginaMisReservas` que integra `ReservaList` + `FiltroEstado` + acción de cancelar (solicita legajo, maneja 403/409) en `frontend/src/pages/PaginaMisReservas.jsx` — depende de T038, T039, T015

**Checkpoint**: User Stories 1 y 2 funcionan de forma independiente.

---

## Phase 5: User Story 3 - Administrador gestiona el pool de vehículos (Priority: P3)

**Goal**: Un administrador autenticado con HTTP Basic da de alta, modifica, da de
baja (temporal/definitiva) y reactiva vehículos del pool, sin afectar el
historial de reservas pasadas.

**Independent Test**: Autenticado como administrador, dar de alta un vehículo,
editarlo, darlo de baja temporal, reactivarlo y darlo de baja definitiva,
verificando el estado resultante en cada paso y que las operaciones sin
credenciales válidas se rechazan — sin depender de que existan reservas.

### Tests for User Story 3

- [X] T041 [P] [US3] Contract test `POST /admin/vehiculos` (201, 400 tipo inválido, 401 sin credenciales, 409 patente duplicada) en `backend/tests/contract/test_admin_vehiculos_post.py`
- [X] T042 [P] [US3] Contract test `PUT /admin/vehiculos/{id}` (200, 400, 401, 404, 409) en `backend/tests/contract/test_admin_vehiculos_put.py`
- [X] T043 [P] [US3] Contract test `POST /admin/vehiculos/{id}/baja-temporal` y `/baja-definitiva` (200, 401, 404, 409 con reservas activas) en `backend/tests/contract/test_admin_vehiculos_baja.py`
- [X] T044 [P] [US3] Contract test `POST /admin/vehiculos/{id}/reactivar` (200, 401, 404, 409 desde baja_definitiva) en `backend/tests/contract/test_admin_vehiculos_reactivar.py`
- [X] T045 [P] [US3] Unit test de transiciones de estado de vehículo, incluyendo bloqueo por reservas activas, en `backend/tests/unit/test_vehiculo_estado.py`

### Implementation for User Story 3

- [X] T046 [US3] Extender `VehiculoRepository` con `create`, `update`, `has_reservas_activas` en `backend/app/repositories/vehiculo_repository.py` — depende de T022
- [X] T047 [US3] `VehiculoService` (alta/modificación con validación de patente única FR-020 y tipo FR-021; baja temporal/definitiva bloqueada por reservas activas FR-015; reactivar bloqueado desde baja_definitiva FR-019) en `backend/app/services/vehiculo_service.py` — depende de T046
- [X] T048 [US3] Router `POST /admin/vehiculos` y `PUT /admin/vehiculos/{id}`, protegidos con la dependencia de auth, en `backend/app/routers/admin_vehiculos.py` — depende de T047, T013
- [X] T049 [US3] Router `POST /admin/vehiculos/{id}/baja-temporal`, `/baja-definitiva` y `/reactivar`, protegidos con la dependencia de auth, en `backend/app/routers/admin_vehiculos.py` — depende de T047, T013
- [X] T050 [P] [US3] Componente `AdminVehiculoForm` (alta/edición de patente y tipo) en `frontend/src/components/AdminVehiculoForm.jsx`
- [X] T051 [P] [US3] Componente `AdminVehiculoList` con acciones de baja temporal/definitiva/reactivar en `frontend/src/components/AdminVehiculoList.jsx`
- [X] T052 [US3] Página `PaginaAdmin` que solicita credenciales HTTP Basic e integra `AdminVehiculoForm` + `AdminVehiculoList`, manejando 401 en `frontend/src/pages/PaginaAdmin.jsx` — depende de T050, T051, T015

**Checkpoint**: Las 3 historias de usuario funcionan de forma independiente.

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Mejoras que afectan a varias historias de usuario

- [X] T053 [P] Ejecutar y validar manualmente los 4 escenarios de `quickstart.md` de punta a punta
- [X] T054 [P] Revisar que todos los routers devuelvan errores en formato consistente `{"detail": "..."}` (contracts/api.md)
- [X] T055 Revisión final de que ninguna credencial esté hardcodeada, conforme al principio IV de la constitución
- [X] T056 [P] Documentar arranque local (backend + frontend) en `README.md`, referenciando los comandos de `Agents.md`

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: Sin dependencias — puede iniciar de inmediato
- **Foundational (Phase 2)**: Depende de Setup — BLOQUEA todas las historias de usuario
- **User Stories (Phase 3-5)**: Todas dependen de que Foundational esté completa
  - Pueden avanzar en paralelo (si hay más de un desarrollador) o secuencialmente en orden de prioridad (US1 → US2 → US3)
- **Polish (Phase 6)**: Depende de que las historias deseadas estén completas

### User Story Dependencies

- **User Story 1 (P1)**: Puede empezar después de Foundational — sin dependencias de otras historias
- **User Story 2 (P2)**: Puede empezar después de Foundational — reutiliza `ReservaRepository` creado en US1 (T023) pero es independientemente testeable con datos de fixture
- **User Story 3 (P3)**: Puede empezar después de Foundational — reutiliza `VehiculoRepository` creado en US1 (T022) pero es independientemente testeable sin reservas

### Within Each User Story

- Tests se escriben y deben fallar antes de implementar
- Repositories antes que Services
- Services antes que Routers
- Backend antes que los componentes de frontend que lo consumen
- Historia completa antes de pasar a la siguiente prioridad

### Parallel Opportunities

- Todas las tareas [P] de Setup pueden correr en paralelo
- Todas las tareas [P] de Foundational pueden correr en paralelo (T008-T011, T015)
- Una vez completada Foundational, US1/US2/US3 pueden empezar en paralelo si hay capacidad de equipo (con la salvedad de que US2/US3 reutilizan repositorios creados en US1)
- Todos los tests [P] de una historia pueden correr en paralelo
- Los componentes de frontend [P] dentro de una historia pueden correr en paralelo

---

## Parallel Example: User Story 1

```bash
# Lanzar todos los tests de User Story 1 juntos:
Task: "Contract test GET /vehiculos en backend/tests/contract/test_vehiculos_get.py"
Task: "Contract test GET /vehiculos/{id}/disponibilidad en backend/tests/contract/test_disponibilidad.py"
Task: "Contract test POST /reservas en backend/tests/contract/test_reservas_post.py"
Task: "Integration test de concurrencia en backend/tests/integration/test_concurrencia_reservas.py"
Task: "Unit test de solapamiento en backend/tests/unit/test_disponibilidad_service.py"

# Lanzar los componentes de frontend de User Story 1 juntos:
Task: "Componente VehiculoList en frontend/src/components/VehiculoList.jsx"
Task: "Componente ReservaForm en frontend/src/components/ReservaForm.jsx"
```

---

## Implementation Strategy

### MVP First (User Story 1 solamente)

1. Completar Phase 1: Setup
2. Completar Phase 2: Foundational (CRÍTICO — bloquea todas las historias)
3. Completar Phase 3: User Story 1
4. **DETENER Y VALIDAR**: probar User Story 1 de forma independiente (escenario 1-2 de `quickstart.md`)
5. Desplegar/demostrar si está listo

### Incremental Delivery

1. Completar Setup + Foundational → Fundación lista
2. Agregar User Story 1 → probar independientemente → Deploy/Demo (¡MVP!)
3. Agregar User Story 2 → probar independientemente → Deploy/Demo
4. Agregar User Story 3 → probar independientemente → Deploy/Demo
5. Cada historia agrega valor sin romper las anteriores

### Parallel Team Strategy

Con más de un desarrollador:

1. El equipo completa Setup + Foundational en conjunto
2. Una vez lista Foundational:
   - Desarrollador A: User Story 1
   - Desarrollador B: User Story 2 (puede empezar en paralelo, integrando con `ReservaRepository` de US1 al mergear)
   - Desarrollador C: User Story 3 (puede empezar en paralelo, integrando con `VehiculoRepository` de US1 al mergear)
3. Las historias se completan e integran de forma independiente

---

## Notes

- [P] = archivos distintos, sin dependencias
- [Story] mapea cada tarea a su historia de usuario para trazabilidad
- Cada historia de usuario debe ser completable y testeable de forma independiente
- Verificar que los tests fallen antes de implementar
- Commitear después de cada tarea o grupo lógico
- Detenerse en cada checkpoint para validar la historia de forma independiente
- Evitar: tareas vagas, conflictos de archivo entre tareas paralelas, dependencias cruzadas entre historias que rompan su independencia
