# Quickstart: Reserva de Vehículos Corporativos

**Feature**: `001-reserva-vehiculos-corporativos` | **Date**: 2026-07-22

Guía para levantar el stack localmente y validar de punta a punta las 3
historias de usuario de `spec.md`. Los comandos de arranque son los ya
documentados en `Agents.md`; acá solo se agrega la secuencia de validación
funcional.

## Prerrequisitos

- PostgreSQL corriendo localmente con la base y el usuario creados (ver
  `Agents.md` § Base de datos).
- Backend levantado (`uvicorn app.main:app --reload`, con `alembic upgrade
  head` ya aplicado) — ver `Agents.md` § Backend.
- Frontend levantado (`npm run dev`) — ver `Agents.md` § Frontend.
- Variables de entorno del backend configuradas: `DATABASE_URL`,
  `ADMIN_USER`, `ADMIN_PASSWORD_HASH`, `APP_TIMEZONE`, `FRONTEND_ORIGIN`
  (ver `research.md` §4, §5, §7).

## Escenario 1 — Alta de vehículo (precondición para todo lo demás)

Sin al menos un vehículo cargado, no hay nada para reservar (Edge Case
"pool vacío" en `spec.md`).

```bash
curl -u "$ADMIN_USER:$ADMIN_PASSWORD" -X POST http://localhost:8000/admin/vehiculos \
  -H "Content-Type: application/json" \
  -d '{"patente": "AB123CD", "tipo": "auto"}'
```

**Esperado**: `201`, el vehículo queda en estado `activo` (contrato en
`contracts/api.md` § `POST /admin/vehiculos`).

## Escenario 2 — Historia 1: empleado reserva un vehículo disponible

1. `GET /vehiculos` → el vehículo recién creado aparece con
   `estado: "activo"` (AC-01).
2. `POST /reservas` con datos completos y un período futuro válido →
   `201` (AC-02).
3. Repetir el mismo `POST /reservas` con el mismo vehículo y un período
   que se superponga → `409` (AC-05, SC-003).
4. `POST /reservas` sin `destino` → `400`, indica el campo faltante
   (AC-03).
5. `POST /reservas` con `fecha_fin <= fecha_inicio` → `400` (AC-04).
6. `POST /reservas` con `fecha_inicio` en el pasado → `400` (FR-005a).

**Validación de concurrencia (SC-003)**: disparar dos `POST /reservas`
simultáneos para el mismo vehículo/período (ej. con `curl` en paralelo o
un script de test) y confirmar que exactamente uno devuelve `201` y el
otro `409`.

## Escenario 3 — Historia 2: empleado consulta y cancela sus reservas

1. `GET /reservas?estado=futura` → solo reservas con `fecha_inicio` futura
   (AC-08).
2. `POST /reservas/{id}/cancelar` con el `legajo` que creó la reserva del
   Escenario 2 → `200`, el vehículo vuelve a estar disponible en ese
   período (AC-11).
3. Repetir la cancelación sobre la misma reserva → `409` (FR-009a, ya
   cancelada).
4. `POST /reservas/{id}/cancelar` sobre una reserva ajena con un `legajo`
   distinto al que la creó → `403` (AC-12).

## Escenario 4 — Historia 3: administrador gestiona el pool

1. `PUT /admin/vehiculos/{id}` cambiando la patente a una ya usada por
   otro vehículo → `409` (AC-25/AC-26).
2. Crear una reserva activa sobre el vehículo del Escenario 1, luego
   `POST /admin/vehiculos/{id}/baja-temporal` → `409` (AC-18).
3. Cancelar esa reserva y reintentar la baja temporal → `200`, vehículo en
   `baja_temporal` y ya no aparece disponible en `GET /vehiculos` (AC-16).
4. `POST /admin/vehiculos/{id}/reactivar` → `200`, vehículo vuelve a
   `activo` (AC-23).
5. `POST /admin/vehiculos/{id}/baja-definitiva` → `200`, vehículo en
   `baja_definitiva`.
6. `POST /admin/vehiculos/{id}/reactivar` sobre ese vehículo → `409`
   (AC-24, estado terminal).
7. Repetir cualquier operación de `/admin/*` sin credenciales → `401`
   (AC-22).
8. `GET /reservas` → las reservas pasadas del vehículo dado de baja siguen
   listadas (AC-20/AC-21).

## Resultado esperado

Si los 4 escenarios se completan con los códigos de estado indicados, las
3 historias de usuario de `spec.md` quedan validadas de punta a punta.
Para el detalle de cada endpoint y sus condiciones de error, ver
`contracts/api.md`; para el modelo de datos subyacente, ver
`data-model.md`.
