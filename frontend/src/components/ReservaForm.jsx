import { useState } from "react";

const CAMPOS_INICIALES = {
  nombre_empleado: "",
  legajo: "",
  licencia: "",
  fecha_inicio: "",
  fecha_fin: "",
  destino: "",
};

export default function ReservaForm({ vehiculoId, onSubmit, enviando }) {
  const [campos, setCampos] = useState(CAMPOS_INICIALES);
  const [errorValidacion, setErrorValidacion] = useState(null);

  function actualizarCampo(nombre, valor) {
    setCampos((prev) => ({ ...prev, [nombre]: valor }));
  }

  function validar() {
    for (const [nombre, valor] of Object.entries(campos)) {
      if (!valor) return `El campo "${nombre}" es obligatorio.`;
    }
    if (!vehiculoId) return "Seleccioná un vehículo del listado.";

    const inicio = new Date(campos.fecha_inicio);
    const fin = new Date(campos.fecha_fin);
    if (fin <= inicio) return "La fecha/hora de fin debe ser posterior a la de inicio.";
    if (inicio < new Date()) return "La fecha/hora de inicio no puede ser anterior al momento actual.";

    return null;
  }

  function handleSubmit(event) {
    event.preventDefault();
    const error = validar();
    if (error) {
      setErrorValidacion(error);
      return;
    }
    setErrorValidacion(null);
    onSubmit({ ...campos, vehiculo_id: vehiculoId });
  }

  return (
    <form onSubmit={handleSubmit}>
      <label>
        Nombre y apellido
        <input
          value={campos.nombre_empleado}
          onChange={(e) => actualizarCampo("nombre_empleado", e.target.value)}
        />
      </label>
      <label>
        Legajo
        <input value={campos.legajo} onChange={(e) => actualizarCampo("legajo", e.target.value)} />
      </label>
      <label>
        Licencia de conducir
        <input
          value={campos.licencia}
          onChange={(e) => actualizarCampo("licencia", e.target.value)}
        />
      </label>
      <label>
        Fecha/hora de inicio
        <input
          type="datetime-local"
          value={campos.fecha_inicio}
          onChange={(e) => actualizarCampo("fecha_inicio", e.target.value)}
        />
      </label>
      <label>
        Fecha/hora de fin
        <input
          type="datetime-local"
          value={campos.fecha_fin}
          onChange={(e) => actualizarCampo("fecha_fin", e.target.value)}
        />
      </label>
      <label>
        Destino
        <input value={campos.destino} onChange={(e) => actualizarCampo("destino", e.target.value)} />
      </label>

      {errorValidacion && <p role="alert">{errorValidacion}</p>}

      <button type="submit" disabled={enviando}>
        {enviando ? "Reservando…" : "Reservar"}
      </button>
    </form>
  );
}
