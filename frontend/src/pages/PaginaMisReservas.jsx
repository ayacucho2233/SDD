import { useState } from "react";
import FiltroEstado from "../components/FiltroEstado";
import ReservaList from "../components/ReservaList";
import apiClient from "../services/apiClient";

export default function PaginaMisReservas() {
  const [estado, setEstado] = useState("");
  const [mensaje, setMensaje] = useState(null);

  async function cancelarReserva(reservaId, legajo) {
    setMensaje(null);
    try {
      await apiClient.post(`/reservas/${reservaId}/cancelar`, { legajo });
      setMensaje({ tipo: "exito", texto: "Reserva cancelada." });
      return { ok: true };
    } catch (error) {
      const status = error.response?.status;
      if (status === 403) {
        setMensaje({ tipo: "error", texto: "Solo el legajo que creó la reserva puede cancelarla." });
      } else if (status === 409) {
        setMensaje({ tipo: "error", texto: "Esa reserva ya no admite cancelación." });
      } else {
        setMensaje({ tipo: "error", texto: "No se pudo cancelar la reserva." });
      }
      return { ok: false };
    }
  }

  return (
    <section>
      <h2>Mis reservas</h2>
      <FiltroEstado valor={estado} onChange={setEstado} />
      <ReservaList estado={estado} onCancelar={cancelarReserva} />
      {mensaje && <p role={mensaje.tipo === "error" ? "alert" : "status"}>{mensaje.texto}</p>}
    </section>
  );
}
