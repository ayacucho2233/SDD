import { useEffect, useState } from "react";
import apiClient from "../services/apiClient";

export default function ReservaList({ estado, onCancelar }) {
  const [reservas, setReservas] = useState([]);
  const [cargando, setCargando] = useState(true);
  const [error, setError] = useState(null);
  const [legajoPorReserva, setLegajoPorReserva] = useState({});

  function cargar() {
    setCargando(true);
    apiClient
      .get("/reservas", { params: estado ? { estado } : {} })
      .then((response) => setReservas(response.data))
      .catch(() => setError("No se pudo cargar el listado de reservas."))
      .finally(() => setCargando(false));
  }

  useEffect(() => {
    cargar();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [estado]);

  async function cancelar(reserva) {
    const legajo = legajoPorReserva[reserva.id];
    if (!legajo) return;
    const resultado = await onCancelar(reserva.id, legajo);
    if (resultado?.ok) cargar();
  }

  if (cargando) return <p>Cargando reservas…</p>;
  if (error) return <p role="alert">{error}</p>;
  if (reservas.length === 0) return <p>No hay reservas para este filtro.</p>;

  return (
    <table>
      <thead>
        <tr>
          <th>Empleado</th>
          <th>Vehículo</th>
          <th>Inicio</th>
          <th>Fin</th>
          <th>Destino</th>
          <th>Estado</th>
          <th>Cancelar (ingresá tu legajo)</th>
        </tr>
      </thead>
      <tbody>
        {reservas.map((reserva) => (
          <tr key={reserva.id}>
            <td>{reserva.nombre_empleado}</td>
            <td>{reserva.vehiculo_id}</td>
            <td>{new Date(reserva.fecha_inicio).toLocaleString()}</td>
            <td>{new Date(reserva.fecha_fin).toLocaleString()}</td>
            <td>{reserva.destino}</td>
            <td>{reserva.cancelada ? "cancelada" : reserva.estado}</td>
            <td>
              {!reserva.cancelada && (
                <>
                  <input
                    placeholder="Legajo"
                    value={legajoPorReserva[reserva.id] ?? ""}
                    onChange={(e) =>
                      setLegajoPorReserva((prev) => ({ ...prev, [reserva.id]: e.target.value }))
                    }
                  />
                  <button onClick={() => cancelar(reserva)}>Cancelar</button>
                </>
              )}
            </td>
          </tr>
        ))}
      </tbody>
    </table>
  );
}
