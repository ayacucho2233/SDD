# API Contract: Reserva de Vehículos Corporativos

**Feature**: `001-reserva-vehiculos-corporativos` | **Date**: 2026-07-22

Contrato funcional de la API REST expuesta por el backend (FastAPI). El
detalle exacto de request/response se formaliza en el OpenAPI que FastAPI
genera automáticamente (`/docs`); este documento fija el contrato mínimo
que las pruebas de contrato deben verificar.

Convenciones:
- Todas las respuestas de error usan el formato `{"detail": "<mensaje>"}`.
- Los endpoints bajo `/admin` requieren HTTP Basic Auth (FR-017); sin
  credenciales válidas responden `401` sin ejecutar la acción.
- Ningún endpoint requiere autenticación de empleado (Assumptions §spec.md).

## Endpoints públicos (empleado)

### `GET /vehiculos`

Lista el pool de vehículos (FR-001). Soporta filtro opcional de
disponibilidad para un período.

- **Query params** (opcionales, deben ir juntos): `disponible_desde`,
  `disponible_hasta` (ISO 8601) — cuando se pasan, cada vehículo incluye si
  está disponible para ese período (FR-007, FR-010, AC-13).
- **200**: lista de `{ id, patente, tipo, estado, disponible? }`.
- **400**: si se pasa uno de los dos params de disponibilidad sin el otro,
  o `disponible_hasta <= disponible_desde`.

### `GET /vehiculos/{id}/disponibilidad`

Indica si un vehículo puntual está disponible para un período (FR-010).

- **Query params**: `inicio`, `fin` (ISO 8601, requeridos).
- **200**: `{ disponible: boolean }`.
- **400**: fin ≤ inicio.
- **404**: vehículo inexistente.

### `POST /reservas`

Crea una reserva (FR-002).

- **Body**: `{ nombre_empleado, legajo, licencia, vehiculo_id,
  fecha_inicio, fecha_fin, destino }` — todos obligatorios.
- **201**: reserva creada, devuelve el recurso completo.
- **400/422**: falta algún campo obligatorio (FR-004, validado por FastAPI
  como 422 antes de llegar a la lógica de negocio); `fecha_fin <=
  fecha_inicio` (FR-005); `fecha_inicio` anterior al momento actual
  (FR-005a); `vehiculo_id` no está en estado `activo` (estos tres, 400,
  validados en la capa de servicio).
- **404**: `vehiculo_id` inexistente.
- **409**: existe otra reserva activa que se superpone en el mismo
  vehículo y período (FR-003) — incluye el caso de dos solicitudes
  concurrentes, donde solo una obtiene `201` y la otra `409` (SC-003).

### `GET /reservas`

Lista reservas existentes (FR-006), con filtro opcional de estado.

- **Query params**: `estado` (opcional) ∈ `{futura, en_curso, pasada}`
  (FR-007).
- **200**: lista de reservas con su estado derivado incluido en la
  respuesta (`futura` / `en_curso` / `pasada`, y `cancelada`).

### `POST /reservas/{id}/cancelar`

Cancela una reserva propia (FR-008).

- **Body**: `{ legajo }`.
- **200**: reserva cancelada.
- **403**: `legajo` no coincide con el legajo que creó la reserva (FR-009).
- **409**: la reserva ya está pasada o ya fue cancelada (FR-009a).
- **404**: reserva inexistente.

## Endpoints de administración (requieren HTTP Basic)

### `POST /admin/vehiculos`

Alta de vehículo (FR-011).

- **Body**: `{ patente, tipo }`.
- **201**: vehículo creado en estado `activo`.
- **400**: `tipo` inválido (FR-021, FR-019).
- **401**: sin credenciales válidas.
- **409**: `patente` ya existe (FR-020, FR-017).

### `PUT /admin/vehiculos/{id}`

Modifica patente/tipo de un vehículo existente (FR-012).

- **Body**: `{ patente, tipo }`.
- **200**: vehículo actualizado.
- **400**: `tipo` inválido (FR-021, FR-020 aplicado en modificación).
- **401**: sin credenciales válidas.
- **404**: vehículo inexistente.
- **409**: `patente` ya usada por otro vehículo (FR-020, FR-018).

### `POST /admin/vehiculos/{id}/baja-temporal`

Da de baja temporal a un vehículo (FR-013).

- **200**: vehículo pasa a `baja_temporal`.
- **401**: sin credenciales válidas.
- **404**: vehículo inexistente.
- **409**: el vehículo tiene reservas activas (FR-015).

### `POST /admin/vehiculos/{id}/baja-definitiva`

Da de baja definitiva a un vehículo, desde `activo` o `baja_temporal`
(FR-014).

- **200**: vehículo pasa a `baja_definitiva`.
- **401**: sin credenciales válidas.
- **404**: vehículo inexistente.
- **409**: el vehículo tiene reservas activas (FR-015).

### `POST /admin/vehiculos/{id}/reactivar`

Reactiva un vehículo en `baja_temporal` (FR-018).

- **200**: vehículo pasa a `activo`.
- **401**: sin credenciales válidas.
- **404**: vehículo inexistente.
- **409**: el vehículo está en `baja_definitiva` (estado terminal, FR-019),
  o ya está `activo`.

## Trazabilidad FR → Endpoint

| FR | Endpoint(s) |
|---|---|
| FR-001 | `GET /vehiculos` |
| FR-002, FR-004, FR-005, FR-005a | `POST /reservas` |
| FR-003 | `POST /reservas` (409) |
| FR-006, FR-007 | `GET /reservas` |
| FR-008, FR-009, FR-009a | `POST /reservas/{id}/cancelar` |
| FR-010 | `GET /vehiculos/{id}/disponibilidad`, `GET /vehiculos` |
| FR-011, FR-019 (tipo), FR-020 (patente) | `POST /admin/vehiculos` |
| FR-012, FR-018 (patente), FR-020 (tipo) | `PUT /admin/vehiculos/{id}` |
| FR-013, FR-015 | `POST /admin/vehiculos/{id}/baja-temporal` |
| FR-014, FR-015 | `POST /admin/vehiculos/{id}/baja-definitiva` |
| FR-016 | `GET /reservas` (no oculta reservas de vehículos dados de baja) |
| FR-017 | Todos los `/admin/*` |
| FR-018, FR-019 | `POST /admin/vehiculos/{id}/reactivar` |
