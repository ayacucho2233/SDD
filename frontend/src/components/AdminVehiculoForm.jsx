import { useState } from "react";

export default function AdminVehiculoForm({ onSubmit, enviando }) {
  const [patente, setPatente] = useState("");
  const [tipo, setTipo] = useState("auto");

  function handleSubmit(event) {
    event.preventDefault();
    if (!patente) return;
    onSubmit({ patente, tipo });
    setPatente("");
  }

  return (
    <form onSubmit={handleSubmit}>
      <label>
        Patente
        <input value={patente} onChange={(e) => setPatente(e.target.value)} />
      </label>
      <label>
        Tipo
        <select value={tipo} onChange={(e) => setTipo(e.target.value)}>
          <option value="auto">Auto</option>
          <option value="camioneta">Camioneta</option>
        </select>
      </label>
      <button type="submit" disabled={enviando}>
        {enviando ? "Guardando…" : "Agregar vehículo"}
      </button>
    </form>
  );
}
