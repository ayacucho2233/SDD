import { useState } from "react";
import VehiculoList from "../components/VehiculoList";
import ReservaForm from "../components/ReservaForm";
import apiClient from "../services/apiClient";

export default function PaginaReservar() {
  const [vehiculoSeleccionado, setVehiculoSeleccionado] = useState(null);
  const [enviando, setEnviando] = useState(false);
  const [mensaje, setMensaje] = useState(null);

  async function handleSubmit(datosReserva) {
    setEnviando(true);
    setMensaje(null);
    try {
      await apiClient.post("/reservas", datosReserva);
      setMensaje({ tipo: "exito", texto: "Reserva confirmada." });
      setVehiculoSeleccionado(null);
    } catch (error) {
      const status = error.response?.status;
      if (status === 409) {
        setMensaje({
          tipo: "error",
          texto: "Ese vehículo ya tiene una reserva activa que se superpone con el período elegido.",
        });
      } else if (status === 400) {
        setMensaje({ tipo: "error", texto: error.response.data?.detail ?? "Datos inválidos." });
      } else {
        setMensaje({ tipo: "error", texto: "No se pudo crear la reserva. Intentá nuevamente." });
      }
    } finally {
      setEnviando(false);
    }
  }

  return (
    <section>
      <h2>Reservar un vehículo</h2>
      <VehiculoList onSelect={setVehiculoSeleccionado} selectedId={vehiculoSeleccionado?.id} />

      {vehiculoSeleccionado && (
        <>
          <p>
            Vehículo seleccionado: <strong>{vehiculoSeleccionado.patente}</strong> (
            {vehiculoSeleccionado.tipo})
          </p>
          <ReservaForm
            vehiculoId={vehiculoSeleccionado.id}
            onSubmit={handleSubmit}
            enviando={enviando}
          />
        </>
      )}

      {mensaje && <p role={mensaje.tipo === "error" ? "alert" : "status"}>{mensaje.texto}</p>}
    </section>
  );
}
