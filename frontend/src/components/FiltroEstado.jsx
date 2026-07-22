const OPCIONES = [
  { valor: "", etiqueta: "Todas" },
  { valor: "futura", etiqueta: "Futuras" },
  { valor: "en_curso", etiqueta: "En curso" },
  { valor: "pasada", etiqueta: "Pasadas" },
];

export default function FiltroEstado({ valor, onChange }) {
  return (
    <label>
      Filtrar por estado
      <select value={valor} onChange={(e) => onChange(e.target.value)}>
        {OPCIONES.map((opcion) => (
          <option key={opcion.valor} value={opcion.valor}>
            {opcion.etiqueta}
          </option>
        ))}
      </select>
    </label>
  );
}
