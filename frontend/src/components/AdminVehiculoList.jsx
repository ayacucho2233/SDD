export default function AdminVehiculoList({ vehiculos, onBajaTemporal, onBajaDefinitiva, onReactivar }) {
  if (vehiculos.length === 0) return <p>No hay vehículos cargados en el pool.</p>;

  return (
    <table>
      <thead>
        <tr>
          <th>Patente</th>
          <th>Tipo</th>
          <th>Estado</th>
          <th>Acciones</th>
        </tr>
      </thead>
      <tbody>
        {vehiculos.map((vehiculo) => (
          <tr key={vehiculo.id}>
            <td>{vehiculo.patente}</td>
            <td>{vehiculo.tipo}</td>
            <td>{vehiculo.estado}</td>
            <td>
              {vehiculo.estado === "activo" && (
                <>
                  <button onClick={() => onBajaTemporal(vehiculo.id)}>Baja temporal</button>
                  <button onClick={() => onBajaDefinitiva(vehiculo.id)}>Baja definitiva</button>
                </>
              )}
              {vehiculo.estado === "baja_temporal" && (
                <>
                  <button onClick={() => onReactivar(vehiculo.id)}>Reactivar</button>
                  <button onClick={() => onBajaDefinitiva(vehiculo.id)}>Baja definitiva</button>
                </>
              )}
              {vehiculo.estado === "baja_definitiva" && <em>Baja definitiva (sin acciones)</em>}
            </td>
          </tr>
        ))}
      </tbody>
    </table>
  );
}
