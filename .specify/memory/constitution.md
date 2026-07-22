<!--
Sync Impact Report
==================
Version change: [TEMPLATE] → 1.0.0 (initial ratification)
Modified principles: N/A (first fill of template placeholders)
Added sections:
  - Core Principles: I. Aislamiento de la Lógica de IA
  - Core Principles: II. Respuestas Ancladas en la Base de Conocimiento (Grounding)
  - Core Principles: III. Desarrollo Test-First para Clasificación (NON-NEGOTIABLE)
  - Core Principles: IV. Gestión Segura de Credenciales
  - Core Principles: V. Alcance Limitado al PRD Vigente
  - Requisitos del Módulo de IA y Base de Conocimiento
  - Flujo de Desarrollo y Calidad
  - Governance
Removed sections: none
Templates requiring updates:
  - .specify/templates/plan-template.md ✅ no changes needed (Constitution Check gate is generic, reads from this file at plan time)
  - .specify/templates/spec-template.md ✅ no changes needed (no constitution-specific references)
  - .specify/templates/tasks-template.md ✅ no changes needed (no constitution-specific references)
  - Agents.md / CLAUDE.md ⚠ pending (manual, optional): could cross-reference these principles, not required for consistency
Follow-up TODOs:
  - TODO(RATIFICATION_DATE): original ratification date unknown before this update; set to the date this constitution was first adopted (2026-07-21) since no earlier record exists.
-->

# ReservaVehiculos Constitution

## Core Principles

### I. Aislamiento de la Lógica de IA
Toda la lógica de IA (clasificación automática, generación de borradores de
respuesta, o cualquier otro uso de modelos/LLMs) DEBE vivir en un módulo
dedicado y aislado, separado de la lógica de negocio de reservas, vehículos
y empleados. El código de negocio NO DEBE importar directamente librerías o
clientes de IA/LLM; DEBE interactuar con el módulo de IA únicamente a través
de una interfaz de servicio bien definida.

**Rationale**: Mantiene la lógica de negocio determinista, testeable sin
dependencias externas, y permite reemplazar, actualizar o incluso eliminar
el módulo de IA sin impactar el resto del sistema.

### II. Respuestas Ancladas en la Base de Conocimiento (Grounding)
Ningún borrador de respuesta generado por IA DEBE afirmar datos, hechos o
compromisos que no estén explícitamente presentes en la base de
conocimiento (KB). Ante ambigüedad, información insuficiente o duda
razonable, el sistema DEBE derivar la consulta a un humano en lugar de
generar una respuesta especulativa o inventada.

**Rationale**: Previene alucinaciones que podrían comprometer la confianza
del usuario, inducir a error a empleados o generar compromisos no
autorizados por la organización.

### III. Desarrollo Test-First para Clasificación (NON-NEGOTIABLE)
La lógica de clasificación DEBE desarrollarse siguiendo TDD estricto: los
tests se escriben primero, se validan, se confirma que fallan, y solo
entonces se implementa el código de producción. El ciclo Red-Green-Refactor
es obligatorio y no puede omitirse por presión de tiempo.

**Rationale**: La clasificación determina el enrutamiento de solicitudes y
decisiones automatizadas; TDD garantiza cobertura desde el inicio y previene
regresiones silenciosas al modificar reglas de clasificación.

### IV. Gestión Segura de Credenciales
Ningún secreto, credencial, API key, token o contraseña DEBE aparecer
hardcodeado en el código fuente ni en el historial de commits. Toda
credencial DEBE configurarse mediante variables de entorno u otro mecanismo
de gestión de secretos externo al repositorio.

**Rationale**: Evita la exposición de credenciales en el control de
versiones y facilita la rotación y gestión segura por entorno
(desarrollo/staging/producción).

### V. Alcance Limitado al PRD Vigente
No se DEBEN agregar features, endpoints o funcionalidades que no estén
contempladas en el PRD vigente. Cualquier funcionalidad nueva REQUIERE
primero su incorporación al PRD y su aprobación antes de ser implementada.

**Rationale**: Evita scope creep, mantiene el foco del equipo en las
prioridades acordadas y asegura trazabilidad entre requisitos y código.

## Requisitos del Módulo de IA y Base de Conocimiento

El módulo de IA DEBE exponer una interfaz de servicio clara (función, clase
de servicio o API interna) consumida por el backend de negocio, nunca al
revés. La KB es la única fuente de verdad para contenido factual usado en
respuestas generadas; cualquier dato no presente en ella se considera
desconocido a los efectos de la Principio II. El mecanismo de derivación a
un humano DEBE quedar registrado (trazabilidad mínima: cuándo y por qué se
activó) para permitir auditoría posterior.

## Flujo de Desarrollo y Calidad

Todo cambio en lógica de clasificación DEBE incluir en el mismo PR la
evidencia del ciclo TDD (tests agregados antes de la implementación). Los
endpoints de administración y los que involucren el módulo de IA DEBEN
pasar por revisión de seguridad antes de mergear, conforme a las reglas de
"Qué hacer / Qué no hacer" definidas en Agents.md. Cualquier solicitud de
feature fuera del PRD vigente DEBE resolverse primero actualizando el PRD,
no codificando directamente.

## Governance

Esta constitución prevalece sobre cualquier otra práctica o convención del
proyecto en caso de conflicto. Las enmiendas requieren: (1) documentación
explícita del cambio y su motivación, (2) aprobación antes de aplicarse, y
(3) incremento de versión según semver: MAJOR para eliminaciones o
redefiniciones incompatibles de principios, MINOR para principios o
secciones nuevas o expansión material de guías existentes, PATCH para
aclaraciones y correcciones de redacción sin cambio semántico. Toda
revisión de PR DEBE verificar cumplimiento de estos principios; la
complejidad agregada debe justificarse explícitamente. Para guía de
desarrollo específica de stack y reglas de negocio en tiempo de ejecución,
usar Agents.md.

**Version**: 1.0.0 | **Ratified**: 2026-07-21 | **Last Amended**: 2026-07-21
