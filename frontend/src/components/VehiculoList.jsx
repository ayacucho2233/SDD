import { useEffect, useState } from "react";
import apiClient from "../services/apiClient";

export default function VehiculoList({ onSelect, selectedId }) {
  const [vehiculos, setVehiculos] = useState([]);
  const [cargando, setCargando] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    let activo = true;
    setCargando(true);
    apiClient
      .get("/vehiculos")
      .then((response) => {
        if (activo) setVehiculos(response.data);
      })
      .catch(() => {
        if (activo) setError("No se pudo cargar el listado de vehículos.");
      })
      .finally(() => {
        if (activo) setCargando(false);
      });
    return () => {
      activo = false;
    };
  }, []);

  if (cargando) return <p>Cargando vehículos…</p>;
  if (error) return <p role="alert">{error}</p>;
  if (vehiculos.length === 0) return <p>No hay vehículos cargados en el pool.</p>;

  return (
    <table>
      <thead>
        <tr>
          <th>Patente</th>
          <th>Tipo</th>
          <th>Estado</th>
        </tr>
      </thead>
      <tbody>
        {vehiculos.map((vehiculo) => (
          <tr
            key={vehiculo.id}
            aria-selected={vehiculo.id === selectedId}
            onClick={() => onSelect?.(vehiculo)}
          >
            <td>{vehiculo.patente}</td>
            <td>{vehiculo.tipo}</td>
            <td>{vehiculo.estado}</td>
          </tr>
        ))}
      </tbody>
    </table>
  );
}
