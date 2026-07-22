# Feature Specification: Reserva de Vehículos Corporativos

**Feature Branch**: `001-reserva-vehiculos-corporativos`

**Created**: 2026-07-21

**Status**: Draft

**Input**: User description: "Generá el spec a partir del PRD en C:/Users/fepgen/Proyecto/RV_Espec/reserva-vehiculos-corporativos.md"

## Clarifications

### Session 2026-07-21

- Q: ¿A qué red estará expuesto el sistema? → A: Solo accesible en la red interna de la empresa (intranet/VPN)
- Q: ¿Cuál es el orden de magnitud esperado del pool de vehículos y de uso concurrente? → A: Pool chico: menos de 50 vehículos, decenas de empleados concurrentes
- Q: ¿Qué reservas se pueden cancelar según su estado? → B: Se pueden cancelar reservas futuras y en curso; se bloquean pasadas o ya canceladas

### Session 2026-07-22

- Q: ¿En qué zona horaria se registran e interpretan las fechas/horas de las reservas? → A: Una única zona horaria fija (la de la sede/oficina de la empresa), igual para todos los usuarios
- Q: ¿El sistema debe permitir crear una reserva cuya fecha/hora de inicio ya pasó? → A: No permitido, la fecha/hora de inicio debe ser igual o posterior al momento actual

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Empleado reserva un vehículo disponible (Priority: P1)

Un empleado que necesita un vehículo del pool para una fecha determinada consulta
el listado de vehículos, verifica disponibilidad para el período que necesita y
crea una reserva a su propio nombre indicando sus datos (nombre, legajo,
licencia), el vehículo, el período (inicio/fin) y el destino. No requiere
autenticación ni aprobación previa: la reserva queda confirmada de inmediato si
no hay conflicto.

**Why this priority**: Es el valor central del sistema — sin esta capacidad no
existe producto. Resuelve el problema de origen (falta de visibilidad y
conflictos de uso de la flota) permitiendo que cualquier empleado reserve de
forma simple y directa.

**Independent Test**: Con al menos un vehículo ya cargado en el pool, un
empleado puede completar el flujo de reserva de punta a punta (ver
disponibilidad → completar datos → confirmar) y la reserva queda registrada,
sin depender de que otras historias estén implementadas.

**Acceptance Scenarios**:

1. **Given** el empleado ingresa al sistema, **When** visualiza el listado de
   vehículos, **Then** se muestra cada vehículo con su patente y tipo (auto /
   camioneta).
2. **Given** un vehículo disponible y todos los campos requeridos completos,
   **When** el empleado envía la reserva, **Then** la reserva se confirma y
   queda registrada.
3. **Given** el empleado no completa algún campo obligatorio (nombre, legajo,
   licencia, vehículo, fecha/hora inicio, fecha/hora fin, destino), **When**
   intenta enviar la reserva, **Then** el sistema no la crea y señala el campo
   faltante.
4. **Given** la fecha/hora de fin es anterior o igual a la de inicio, **When**
   el empleado envía la reserva, **Then** el sistema la rechaza con un mensaje
   de error descriptivo.
5. **Given** un vehículo con una reserva activa en un período determinado,
   **When** otro empleado intenta reservar el mismo vehículo en un período que
   se superpone, **Then** el sistema rechaza la reserva e informa el
   conflicto.
6. **Given** un vehículo disponible, **When** llegan dos solicitudes de
   reserva simultáneas para el mismo vehículo y el mismo período, **Then** el
   sistema confirma solo una de las reservas y rechaza la otra indicando el
   conflicto.
7. **Given** un vehículo con una reserva activa que se superpone con el
   período consultado y otro vehículo sin reservas en ese período, **When**
   se consulta disponibilidad para ese rango horario, **Then** el primero se
   marca como no disponible y el segundo como disponible.
8. **Given** la fecha/hora de inicio indicada es anterior al momento actual,
   **When** el empleado envía la reserva, **Then** el sistema la rechaza con
   un mensaje de error descriptivo.

---

### User Story 2 - Empleado consulta y cancela sus propias reservas (Priority: P2)

Un empleado consulta el listado de reservas existentes, puede filtrarlas por
estado (futuras, en curso, pasadas) para ubicar la suya, y puede cancelar
únicamente la reserva que él mismo creó, identificándose con su número de
legajo.

**Why this priority**: Complementa el valor de la reserva permitiendo
corregir errores o liberar un vehículo que ya no se necesita, y da
visibilidad sobre el uso de la flota. Depende de que existan reservas
creadas (Historia 1) pero es una capacidad separable y demostrable por sí
misma sobre datos ya existentes.

**Independent Test**: Con reservas ya existentes en el sistema (futuras, en
curso y pasadas), un empleado puede filtrar el listado por cada estado y
cancelar una reserva propia indicando su legajo, sin necesidad de ejecutar el
flujo de creación en el mismo test.

**Acceptance Scenarios**:

1. **Given** el empleado accede al listado de reservas sin aplicar ningún
   filtro, **When** consulta el listado, **Then** el sistema muestra todas
   las reservas existentes.
2. **Given** el empleado filtra las reservas por estado "futuras", **When**
   aplica el filtro, **Then** el sistema muestra únicamente las reservas con
   fecha de inicio posterior al momento actual.
3. **Given** el empleado filtra las reservas por estado "en curso", **When**
   aplica el filtro, **Then** el sistema muestra únicamente las reservas cuyo
   período (inicio–fin) abarca el momento actual.
4. **Given** el empleado filtra las reservas por estado "pasadas", **When**
   aplica el filtro, **Then** el sistema muestra únicamente las reservas con
   fecha de fin anterior al momento actual.
5. **Given** el empleado que creó una reserva futura o en curso ingresa su
   número de legajo, **When** solicita la cancelación, **Then** la reserva se
   cancela y el vehículo queda disponible de inmediato para ese período.
6. **Given** una reserva creada por un legajo determinado, **When** otro
   empleado intenta cancelarla con un número de legajo distinto, **Then** el
   sistema rechaza la cancelación e informa que solo el solicitante original
   puede cancelarla.
7. **Given** una reserva ya pasada o ya cancelada previamente, **When** el
   empleado que la creó intenta cancelarla nuevamente, **Then** el sistema
   rechaza la operación e informa que la reserva no admite cancelación en su
   estado actual.

---

### User Story 3 - Administrador gestiona el pool de vehículos (Priority: P3)

Un administrador autenticado mantiene la base de vehículos del pool: da de
alta nuevos vehículos, modifica patente/tipo de vehículos existentes, y da de
baja (temporal o definitiva) o reactiva vehículos según corresponda, sin
afectar el historial de reservas pasadas.

**Why this priority**: Es condición necesaria para que exista contenido que
reservar, pero es una capacidad administrativa de backoffice, ejecutada con
mucha menor frecuencia que las Historias 1 y 2, y evaluable de forma
totalmente aislada (alta/edición/baja de vehículos) sin necesidad de que el
flujo de reserva de empleados esté operativo.

**Independent Test**: Autenticado como administrador, se puede dar de alta un
vehículo, editarlo, darlo de baja temporal, reactivarlo y darlo de baja
definitiva, verificando en cada paso el estado resultante y que las
operaciones sin credenciales válidas se rechazan — todo sin depender de que
haya reservas creadas.

**Acceptance Scenarios**:

1. **Given** el administrador ingresa patente y tipo válidos para un vehículo
   nuevo, **When** lo agrega al pool, **Then** el vehículo queda disponible
   para ser reservado.
2. **Given** un vehículo existente, **When** el administrador modifica su
   patente o tipo, **Then** los cambios quedan reflejados de inmediato en el
   listado de vehículos.
3. **Given** un vehículo activo sin reservas activas, **When** el
   administrador lo da de baja temporalmente, **Then** el vehículo pasa a
   estado "baja temporal" y deja de aparecer disponible para nuevas
   reservas.
4. **Given** un vehículo activo o en "baja temporal" sin reservas activas,
   **When** el administrador lo da de baja definitiva, **Then** el vehículo
   pasa a estado "baja definitiva" y deja de aparecer disponible para nuevas
   reservas.
5. **Given** un vehículo con reservas activas, **When** el administrador
   intenta darlo de baja temporal o definitiva, **Then** el sistema rechaza
   la operación e informa que el vehículo tiene reservas vigentes.
6. **Given** un vehículo en estado "baja temporal" o "baja definitiva" con
   reservas pasadas asociadas, **When** se consulta el listado de reservas,
   **Then** esas reservas pasadas siguen siendo visibles.
7. **Given** un request a un endpoint de administración de vehículos sin
   credenciales válidas, **When** se realiza la petición, **Then** el
   sistema rechaza la acción e indica que no está autorizada.
8. **Given** un vehículo en estado "baja temporal", **When** el administrador
   lo reactiva, **Then** el vehículo pasa a estado "activo" y vuelve a estar
   disponible para nuevas reservas.
9. **Given** un vehículo en estado "baja definitiva", **When** el
   administrador intenta reactivarlo, **Then** el sistema rechaza la
   operación e informa que un vehículo en baja definitiva no puede
   reactivarse.
10. **Given** un vehículo existente con una patente determinada, **When** el
    administrador intenta dar de alta o modificar otro vehículo asignándole
    esa misma patente, **Then** el sistema rechaza la operación e informa que
    la patente ya existe.
11. **Given** un tipo de vehículo distinto de "auto" o "camioneta", **When**
    el administrador intenta dar de alta o modificar un vehículo con ese
    tipo, **Then** el sistema rechaza la operación e informa que el tipo no
    es válido.

---

### Edge Cases

- ¿Qué pasa si el pool de vehículos está vacío (no se cargó ningún vehículo
  antes del go-live)? El listado de vehículos y de disponibilidad se muestra
  vacío; no hay nada para reservar hasta que el administrador dé de alta al
  menos un vehículo.
- ¿Qué pasa si llegan dos solicitudes de reserva simultáneas para el mismo
  vehículo y período? Solo una se confirma; la otra se rechaza informando el
  conflicto (ninguna reserva duplicada queda registrada).
- ¿Qué pasa si se intenta reservar un vehículo que está en "baja temporal" o
  "baja definitiva"? El vehículo no figura como disponible y la reserva se
  rechaza.
- ¿Qué pasa si el administrador intenta dar de baja (temporal o definitiva)
  un vehículo con reservas activas? La operación se rechaza informando que
  el vehículo tiene reservas vigentes.
- ¿Qué pasa si se intenta reactivar un vehículo en "baja definitiva"? La
  operación se rechaza; ese estado es terminal.
- ¿Qué pasa si se intenta dar de alta o modificar un vehículo con una
  patente ya usada por otro vehículo, o con un tipo distinto de "auto" /
  "camioneta"? La operación se rechaza indicando el motivo específico.
- ¿Qué pasa si alguien intenta cancelar una reserva con un legajo que no es
  el del creador original? La cancelación se rechaza.
- ¿Qué pasa si se intenta cancelar una reserva ya pasada o ya cancelada
  previamente? La cancelación se rechaza; solo las reservas futuras o en
  curso admiten cancelación.
- ¿Qué pasa si se intenta crear una reserva con fecha/hora de inicio
  anterior al momento actual? Se rechaza; el inicio debe ser igual o
  posterior al momento actual.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: El sistema DEBE mostrar el listado de vehículos del pool con su
  patente y tipo (auto / camioneta).
- **FR-002**: El sistema DEBE permitir crear una reserva indicando: nombre
  del empleado (quien será el conductor), número de legajo, número de
  licencia de conducir, vehículo, fecha/hora de inicio, fecha/hora de fin y
  destino.
- **FR-003**: El sistema DEBE validar que no exista otra reserva activa para
  el mismo vehículo en el período solicitado, rechazando la reserva e
  informando el conflicto si existe solapamiento.
- **FR-004**: El sistema DEBE rechazar la creación de una reserva si falta
  algún campo obligatorio, señalando el campo faltante.
- **FR-005**: El sistema DEBE rechazar la creación de una reserva si la
  fecha/hora de fin es anterior o igual a la de inicio, con un mensaje de
  error descriptivo.
- **FR-005a**: El sistema DEBE rechazar la creación de una reserva si la
  fecha/hora de inicio es anterior al momento actual, con un mensaje de
  error descriptivo.
- **FR-006**: El sistema DEBE listar las reservas existentes.
- **FR-007**: El sistema DEBE permitir filtrar las reservas por estado:
  futuras (inicio posterior al momento actual), en curso (el momento actual
  está dentro del período) y pasadas (fin anterior al momento actual).
- **FR-008**: El sistema DEBE permitir cancelar una reserva futura o en
  curso, solicitando el número de legajo de quien pide la cancelación; al
  cancelarse, el vehículo queda disponible de inmediato para ese período.
- **FR-009**: El sistema NO DEBE permitir cancelar una reserva si el legajo
  indicado no coincide con el legajo que la creó, informando que solo el
  solicitante original puede cancelarla.
- **FR-009a**: El sistema NO DEBE permitir cancelar una reserva que ya está
  pasada (finalizada) o que ya fue cancelada previamente, informando que la
  reserva no admite cancelación en su estado actual.
- **FR-010**: El sistema DEBE indicar si un vehículo está disponible para un
  período dado.
- **FR-011**: El sistema DEBE permitir al administrador agregar vehículos al
  pool indicando patente y tipo (auto / camioneta).
- **FR-012**: El sistema DEBE permitir al administrador modificar la patente
  y el tipo de un vehículo existente.
- **FR-013**: El sistema DEBE permitir al administrador dar de baja temporal
  a un vehículo, pasándolo al estado "baja temporal" (no disponible para
  nuevas reservas, sin eliminarse del pool).
- **FR-014**: El sistema DEBE permitir al administrador dar de baja
  definitiva a un vehículo desde el estado "activo" o "baja temporal",
  pasándolo al estado "baja definitiva" (no disponible para nuevas reservas,
  sin eliminarse del pool).
- **FR-015**: El sistema NO DEBE permitir pasar un vehículo a "baja
  temporal" ni a "baja definitiva" si tiene reservas activas, informando que
  el vehículo tiene reservas vigentes.
- **FR-016**: El sistema DEBE mantener visibles en el listado de reservas
  las reservas pasadas de vehículos en estado "baja temporal" o "baja
  definitiva".
- **FR-017**: El sistema DEBE requerir autenticación (usuario y contraseña)
  para toda operación de administración de vehículos: alta, modificación,
  baja temporal, baja definitiva y reactivación. Las solicitudes sin
  credenciales válidas se rechazan sin ejecutar la acción.
- **FR-018**: El sistema DEBE permitir al administrador reactivar un
  vehículo en estado "baja temporal", devolviéndolo al estado "activo" y
  disponible para nuevas reservas.
- **FR-019**: El sistema NO DEBE permitir reactivar un vehículo en estado
  "baja definitiva", informando que no puede reactivarse.
- **FR-020**: El sistema DEBE validar que la patente de un vehículo sea
  única dentro del pool, tanto al darlo de alta como al modificarlo,
  rechazando la operación e informando que la patente ya existe en caso de
  duplicado.
- **FR-021**: El sistema DEBE validar que el tipo de un vehículo sea "auto"
  o "camioneta", tanto al darlo de alta como al modificarlo, rechazando la
  operación con un tipo inválido.

### Key Entities *(include if feature involves data)*

- **Vehículo**: representa una unidad del pool corporativo. Atributos clave:
  patente (única dentro del pool), tipo (auto / camioneta), estado (activo /
  baja temporal / baja definitiva). Conserva su historial de reservas aunque
  esté dado de baja.
- **Reserva**: representa el uso planificado de un vehículo por un empleado.
  Atributos clave: nombre del empleado (conductor), número de legajo, número
  de licencia de conducir, vehículo asociado, fecha/hora de inicio,
  fecha/hora de fin, destino, y si está cancelada o no. Su estado temporal
  (futura / en curso / pasada) se deriva de comparar su período con el
  momento actual; se considera "activa" (a efectos de solapamiento y de
  bloquear bajas de vehículo) si no fue cancelada y su período es futuro o
  está en curso. Solo una reserva activa puede cancelarse; una reserva
  pasada o ya cancelada no admite una nueva cancelación.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Un empleado puede completar una reserva en menos de 1 minuto,
  sin necesidad de capacitación previa.
- **SC-002**: Las consultas de disponibilidad de vehículos responden en
  menos de 2 segundos, medido en el percentil 95 (p95), bajo carga normal
  esperada: un pool de menos de 50 vehículos con decenas de empleados
  consultando o reservando de forma concurrente.
- **SC-003**: Ante dos solicitudes simultáneas de reserva sobre el mismo
  vehículo y el mismo período, el sistema confirma exactamente una y rechaza
  la otra, sin excepción.
- **SC-004**: El 100% de los intentos de reserva con campos obligatorios
  incompletos, con fecha de fin anterior o igual a la de inicio, o con fecha
  de inicio anterior al momento actual, son rechazados con un mensaje de
  error claro.
- **SC-005**: El 100% de los intentos de dar de baja (temporal o definitiva)
  un vehículo con reservas activas son rechazados.
- **SC-006**: Las altas, modificaciones, bajas y reactivaciones de vehículos
  se reflejan de inmediato en el listado visible para los empleados.
- **SC-007**: El 100% de las cancelaciones solicitadas con un legajo distinto
  al que creó la reserva son rechazadas.
- **SC-008**: El 100% de los intentos de cancelar una reserva ya pasada o ya
  cancelada previamente son rechazados.

## Assumptions

- El sistema es accesible únicamente dentro de la red interna de la empresa
  (intranet/VPN), no está expuesto públicamente en Internet. Esto es lo que
  hace aceptable que los empleados no requieran autenticación: el acceso ya
  está acotado a personal de la compañía.
- Los empleados no requieren autenticación ni gestión de roles: cualquier
  persona puede crear una reserva a su propio nombre, confiando en los datos
  que declara (nombre, legajo, licencia) para trazabilidad básica.
- No hay aprobación previa de reservas por parte de superiores, supervisores
  ni administradores; toda reserva sin conflicto se confirma de inmediato.
- No se gestiona mantenimiento ni estado técnico de los vehículos — solo su
  disponibilidad para reservas.
- No se envían notificaciones por email, SMS ni push.
- No se lleva historial de kilometraje ni combustible.
- No se valida el formato específico de legajo ni de licencia de conducir;
  solo se exige que sean campos obligatorios no vacíos.
- No hay aplicación móvil nativa ni integración con sistemas de RRHH o ERP.
- El administrador debe cargar el pool inicial de vehículos antes de que los
  empleados puedan reservar (proceso de carga inicial fuera del alcance de
  esta feature, a definir antes del go-live).
- Las credenciales de administrador se gestionan y provisionan de forma
  segura fuera del código fuente (variables de entorno u otro mecanismo
  externo al repositorio).
- La escala esperada es la de un pool de vehículos chico (menos de 50
  vehículos) con decenas de empleados consultando o reservando de forma
  concurrente; no se dimensiona el sistema para volúmenes mayores.
- Todas las fechas/horas de reservas se registran e interpretan en una única
  zona horaria fija (la de la sede/oficina de la empresa), igual para todos
  los empleados; no hay conversión por zona horaria del dispositivo del
  usuario.
