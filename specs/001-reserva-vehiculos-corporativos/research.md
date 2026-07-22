# Research: Reserva de Vehículos Corporativos

**Feature**: `001-reserva-vehiculos-corporativos` | **Date**: 2026-07-22

Este documento resuelve las incógnitas técnicas del Technical Context del
plan, a partir del stack ya fijado en `Agents.md` (React + Vite / Python +
FastAPI / PostgreSQL) y de las decisiones de negocio ya clarificadas en
`spec.md`.

## 1. Tipado del frontend: JavaScript vs TypeScript

- **Decision**: JavaScript (ES2022+), sin TypeScript.
- **Rationale**: `Agents.md` fija el stack como "React + Vite" sin mencionar
  TypeScript. El dominio es acotado (3 entidades, formularios simples) y no
  hay ningún requisito que dependa de tipado estático. Mantener el stack tal
  como está declarado evita introducir herramienta/configuración adicional
  no solicitada (alineado con el principio constitucional V de no exceder
  el alcance vigente).
- **Alternatives considered**: TypeScript — más seguridad de tipos en
  formularios y en el cliente HTTP, pero agrega configuración (tsconfig,
  tipado de props) sin que el PRD lo requiera; se descarta para mantener
  simplicidad.

## 2. ORM y acceso a datos (backend)

- **Decision**: SQLAlchemy 2.0 (modo async) + Alembic para migraciones.
- **Rationale**: `Agents.md` indica explícitamente "Usar un ORM (SQLAlchemy)
  o query builder" y documenta el flujo `alembic upgrade head` como parte
  del arranque del backend. SQLAlchemy 2.0 async permite no bloquear el
  event loop de FastAPI, requisito explícito de `Agents.md` ("No bloquear
  el event loop con operaciones síncronas pesadas").
- **Alternatives considered**: Query builder crudo (ej. `asyncpg` directo) —
  más liviano, pero pierde las validaciones de esquema y las migraciones
  versionadas que ya están documentadas en el flujo de arranque del proyecto.

## 3. Concurrencia al crear reservas (prevención de race conditions)

- **Decision**: Transacción de base de datos que ejecuta `SELECT ... FOR
  UPDATE` sobre la fila del **vehículo** (no sobre sus reservas) antes de
  leer sus reservas activas, verificar solapamiento e insertar la nueva
  reserva, todo dentro de la misma transacción atómica.
- **Rationale**: Es el mecanismo explícitamente indicado en `Agents.md`
  ("Usar transacciones de base de datos al crear reservas para prevenir
  race conditions (`SELECT FOR UPDATE`)") y es lo que exige FR-003/SC-003.
  El lock debe tomarse sobre la fila del vehículo y no sobre sus reservas:
  si el vehículo todavía no tiene ninguna reserva, un `SELECT ... FOR
  UPDATE` filtrado por `vehiculo_id` no bloquea nada (no hay fila que
  bloquear), y dos transacciones concurrentes verían ambas "disponible" e
  insertarían igual — esto se detectó con el test de integración de
  concurrencia (`tests/integration/test_concurrencia_reservas.py`) corriendo
  contra Postgres real, donde ambas reservas concurrentes se confirmaban
  (201/201) en lugar de 201/409. Como el vehículo siempre existe, bloquear
  su fila sí serializa correctamente a los solicitantes concurrentes,
  tengan o no reservas previas.
- **Alternatives considered**: Constraint `EXCLUDE` de PostgreSQL sobre
  rango de fechas (usando `btree_gist`) — es una alternativa robusta a
  nivel de base de datos, pero Agents.md indica explícitamente
  `SELECT FOR UPDATE` en capa de transacción de aplicación y pide no
  delegar lógica de negocio a la base de datos ("No manejar la lógica de
  negocio en stored procedures... mantenerla en el backend"); se descarta
  para respetar esa guía, aunque se recomienda evaluarla como refuerzo
  futuro a nivel de constraint de integridad.

## 4. Autenticación de administrador

- **Decision**: HTTP Basic Auth vía la dependencia `HTTPBasic` de FastAPI,
  validando usuario y contraseña contra variables de entorno
  (`ADMIN_USER`, `ADMIN_PASSWORD_HASH`), comparando el hash con `passlib`
  (bcrypt).
- **Rationale**: Es el mecanismo que ya documenta el flujo de arranque en
  `Agents.md` (`ADMIN_PASSWORD_HASH` generado con
  `passlib.hash.bcrypt`) y satisface FR-017 (autenticación requerida en
  todo endpoint de administración) sin introducir infraestructura adicional
  (sesiones, JWT) no solicitada por el PRD.
- **Alternatives considered**: JWT — mencionado como alternativa en
  `Agents.md` ("HTTP Basic o JWT simple"), pero agrega superficie
  (emisión/expiración/refresh de tokens) innecesaria para un solo rol
  administrador sin gestión de usuarios múltiples; se descarta.

## 5. Manejo de zona horaria

- **Decision**: Todas las columnas de fecha/hora se almacenan como
  `TIMESTAMP WITH TIME ZONE` en PostgreSQL (normalizado a UTC internamente,
  como hace Postgres por defecto). La comparación contra "el momento
  actual" (para futura/en curso/pasada, y para bloquear inicios en el
  pasado) se realiza en el backend usando una única zona horaria fija de
  la empresa, configurable vía variable de entorno (`APP_TIMEZONE`).
- **Rationale**: Responde directamente a la clarificación de `spec.md`
  ("Una única zona horaria fija... igual para todos los usuarios") y sigue
  la recomendación de `Agents.md` de usar `TIMESTAMP WITH TIME ZONE` para
  fechas.
- **Alternatives considered**: Zona horaria del navegador de cada empleado
  — descartada explícitamente en la clarificación de `spec.md` para evitar
  ambigüedad de conversión.

## 6. Testing

- **Decision**:
  - Backend: `pytest` + `pytest-asyncio` + `httpx.AsyncClient` contra la
    app de FastAPI, con una base de datos PostgreSQL de test (o
    contenedor efímero) para los tests de integración que ejercen
    transacciones reales.
  - Frontend: `vitest` + `@testing-library/react`, el par estándar que
    ya trae Vite sin configuración adicional relevante.
- **Rationale**: Son las herramientas de facto para cada mitad del stack
  declarado (FastAPI / Vite), minimizan configuración adicional y permiten
  testear tanto contratos de API como flujos de UI sin introducir un
  framework de testing no alineado con el stack.
- **Alternatives considered**: Testing de integración con SQLite en
  memoria para el backend — más rápido, pero no reproduce fielmente el
  comportamiento de `SELECT FOR UPDATE` sobre PostgreSQL que es crítico
  para validar SC-003/FR-003; se descarta para los tests de concurrencia
  (puede usarse igualmente para tests unitarios que no dependan de
  locking).

## 7. CORS y exposición de red

- **Decision**: `CORSMiddleware` de FastAPI restringido al origen exacto
  del frontend (`FRONTEND_ORIGIN` en variable de entorno, típicamente la
  URL interna donde se sirve el build de Vite). El despliegue completo
  (frontend + backend) vive dentro de la red interna/VPN de la empresa,
  sin exposición a Internet público, conforme a la clarificación de
  `spec.md`.
- **Rationale**: Cumple con `Agents.md` ("Configurar CORS correctamente
  para permitir solo el origen del frontend") y con la decisión de alcance
  de red ya clarificada.
- **Alternatives considered**: CORS abierto (`*`) — descartado, viola
  explícitamente la guía de `Agents.md`.

## Resumen de decisiones para Technical Context

| Aspecto | Decisión |
|---|---|
| Lenguaje backend | Python 3.11+ |
| Framework backend | FastAPI |
| Lenguaje frontend | JavaScript (ES2022+), sin TypeScript |
| Framework frontend | React 18 + Vite |
| Base de datos | PostgreSQL 15+ |
| ORM / migraciones | SQLAlchemy 2.0 (async) + Alembic |
| Autenticación admin | HTTP Basic (passlib/bcrypt) vía variables de entorno |
| Control de concurrencia | Transacción + `SELECT ... FOR UPDATE` |
| Testing backend | pytest + pytest-asyncio + httpx |
| Testing frontend | vitest + @testing-library/react |
| Zona horaria | Fija por configuración (`APP_TIMEZONE`), `TIMESTAMPTZ` en DB |
| Exposición de red | Solo intranet/VPN, sin acceso público a Internet |
