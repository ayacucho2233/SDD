# Data Model: Reserva de Vehículos Corporativos

**Feature**: `001-reserva-vehiculos-corporativos` | **Date**: 2026-07-22

Deriva de `spec.md` § Key Entities y de las reglas de negocio en §
Functional Requirements. Los tipos de columna son los recomendados por
`Agents.md` (§ Base de datos).

## Vehiculo

Representa una unidad del pool corporativo.

| Campo | Tipo | Reglas |
|---|---|---|
| `id` | `SERIAL` / `UUID` PK | Generado por el sistema |
| `patente` | `VARCHAR(10)` | `NOT NULL`, `UNIQUE` (FR-020) |
| `tipo` | `VARCHAR(10)` | `NOT NULL`, `CHECK (tipo IN ('auto','camioneta'))` (FR-021) |
| `estado` | `VARCHAR(20)` | `NOT NULL`, `DEFAULT 'activo'`, `CHECK (estado IN ('activo','baja_temporal','baja_definitiva'))` |
| `created_at` | `TIMESTAMP WITH TIME ZONE` | `NOT NULL DEFAULT now()` |
| `updated_at` | `TIMESTAMP WITH TIME ZONE` | `NOT NULL DEFAULT now()` |

### Máquina de estados

```
activo ──────────────► baja_temporal ──────────────► activo   (FR-018, reactivar)
  │                         │
  │                         └────────────────────────► baja_definitiva  (FR-014)
  │
  └──────────────────────────────────────────────────► baja_definitiva  (FR-014)

baja_definitiva: estado terminal, sin transiciones salientes (FR-019)
```

- Transición a `baja_temporal` o a `baja_definitiva` **bloqueada** si el
  vehículo tiene alguna Reserva activa asociada (FR-015).
- El vehículo nunca se borra físicamente (soft delete vía `estado`); sus
  reservas pasadas permanecen visibles (FR-016).

### Reglas de validación (además de constraints de DB)

- Unicidad de `patente` verificada tanto en alta (FR-020) como en
  modificación (FR-020), excluyendo el propio registro al modificar.
- `tipo` limitado a `auto` / `camioneta`, tanto en alta como en
  modificación (FR-021).

## Reserva

Representa el uso planificado de un vehículo por un empleado (que es
también el conductor).

| Campo | Tipo | Reglas |
|---|---|---|
| `id` | `SERIAL` / `UUID` PK | Generado por el sistema |
| `vehiculo_id` | FK → `Vehiculo.id` | `NOT NULL` |
| `nombre_empleado` | `VARCHAR(200)` | `NOT NULL` (FR-002, FR-004) |
| `legajo` | `VARCHAR(20)` | `NOT NULL` (FR-002, FR-004); sin validación de formato (Assumptions) |
| `licencia` | `VARCHAR(20)` | `NOT NULL` (FR-002, FR-004); sin validación de formato (Assumptions) |
| `fecha_inicio` | `TIMESTAMP WITH TIME ZONE` | `NOT NULL` |
| `fecha_fin` | `TIMESTAMP WITH TIME ZONE` | `NOT NULL`, `CHECK (fecha_fin > fecha_inicio)` (FR-005) |
| `destino` | `VARCHAR(300)` | `NOT NULL` (FR-002, FR-004) |
| `cancelada` | `BOOLEAN` | `NOT NULL DEFAULT false` |
| `created_at` | `TIMESTAMP WITH TIME ZONE` | `NOT NULL DEFAULT now()` |

### Estado derivado (no persistido)

Calculado comparando `fecha_inicio`/`fecha_fin` contra el momento actual
(en la zona horaria fija de la aplicación, ver `research.md` §5):

- **futura**: `fecha_inicio > now()`
- **en curso**: `fecha_inicio <= now() <= fecha_fin`
- **pasada**: `fecha_fin < now()`
- **activa** (a efectos de solapamiento y de bloquear bajas de vehículo):
  `NOT cancelada AND fecha_fin >= now()` (futura o en curso, no cancelada)

### Reglas de validación

- `fecha_fin` debe ser posterior a `fecha_inicio` (FR-005).
- `fecha_inicio` debe ser igual o posterior al momento actual al momento de
  crear la reserva (FR-005a).
- No puede existir otra reserva **activa** para el mismo `vehiculo_id` cuyo
  período se superponga con el solicitado (FR-003) — verificado dentro de
  una transacción con `SELECT ... FOR UPDATE` (ver `research.md` §3).
- Solo puede cancelarse (`cancelada = true`) una reserva que esté
  **activa** en el momento de la solicitud; una reserva pasada o ya
  cancelada rechaza la operación (FR-009a).
- Cancelar requiere que el `legajo` recibido coincida exactamente con el
  `legajo` que creó la reserva (FR-009).

## Relación

```
Vehiculo (1) ──── (0..N) Reserva
```

Un vehículo puede tener cero o muchas reservas históricas; una reserva
pertenece a exactamente un vehículo.

## Índices

- `UNIQUE INDEX` sobre `Vehiculo.patente`.
- `INDEX` compuesto sobre `Reserva (vehiculo_id, fecha_inicio, fecha_fin)`
  para acelerar la verificación de solapamiento y las consultas de
  disponibilidad (recomendado explícitamente en `Agents.md` § Base de
  datos: "Crear índices en los campos más consultados: vehículo + fechas").
