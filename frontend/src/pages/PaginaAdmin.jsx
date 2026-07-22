import { useEffect, useState } from "react";
import AdminVehiculoForm from "../components/AdminVehiculoForm";
import AdminVehiculoList from "../components/AdminVehiculoList";
import apiClient from "../services/apiClient";

export default function PaginaAdmin() {
  const [usuario, setUsuario] = useState("");
  const [password, setPassword] = useState("");
  const [autenticado, setAutenticado] = useState(false);
  const [vehiculos, setVehiculos] = useState([]);
  const [enviando, setEnviando] = useState(false);
  const [mensaje, setMensaje] = useState(null);

  const auth = { username: usuario, password };

  function cargarVehiculos() {
    apiClient
      .get("/vehiculos")
      .then((response) => setVehiculos(response.data))
      .catch(() => setMensaje({ tipo: "error", texto: "No se pudo cargar el listado de vehículos." }));
  }

  useEffect(() => {
    if (autenticado) cargarVehiculos();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [autenticado]);

  async function ejecutarAccionAdmin(promesa, mensajeExito) {
    setEnviando(true);
    setMensaje(null);
    try {
      await promesa;
      setMensaje({ tipo: "exito", texto: mensajeExito });
      cargarVehiculos();
    } catch (error) {
      const status = error.response?.status;
      if (status === 401) {
        setAutenticado(false);
        setMensaje({ tipo: "error", texto: "Credenciales de administrador inválidas." });
      } else if (status === 409) {
        setMensaje({ tipo: "error", texto: error.response.data?.detail ?? "Conflicto." });
      } else if (status === 400) {
        setMensaje({ tipo: "error", texto: error.response.data?.detail ?? "Datos inválidos." });
      } else {
        setMensaje({ tipo: "error", texto: "No se pudo completar la operación." });
      }
    } finally {
      setEnviando(false);
    }
  }

  function handleLogin(event) {
    event.preventDefault();
    setAutenticado(true);
  }

  function handleAlta(datos) {
    ejecutarAccionAdmin(
      apiClient.post("/admin/vehiculos", datos, { auth }),
      "Vehículo agregado al pool.",
    );
  }

  function handleBajaTemporal(vehiculoId) {
    ejecutarAccionAdmin(
      apiClient.post(`/admin/vehiculos/${vehiculoId}/baja-temporal`, null, { auth }),
      "Vehículo dado de baja temporal.",
    );
  }

  function handleBajaDefinitiva(vehiculoId) {
    ejecutarAccionAdmin(
      apiClient.post(`/admin/vehiculos/${vehiculoId}/baja-definitiva`, null, { auth }),
      "Vehículo dado de baja definitiva.",
    );
  }

  function handleReactivar(vehiculoId) {
    ejecutarAccionAdmin(
      apiClient.post(`/admin/vehiculos/${vehiculoId}/reactivar`, null, { auth }),
      "Vehículo reactivado.",
    );
  }

  if (!autenticado) {
    return (
      <section>
        <h2>Administración</h2>
        <form onSubmit={handleLogin}>
          <label>
            Usuario
            <input value={usuario} onChange={(e) => setUsuario(e.target.value)} />
          </label>
          <label>
            Contraseña
            <input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
            />
          </label>
          <button type="submit">Ingresar</button>
        </form>
        {mensaje && <p role="alert">{mensaje.texto}</p>}
      </section>
    );
  }

  return (
    <section>
      <h2>Administración del pool de vehículos</h2>
      <AdminVehiculoForm onSubmit={handleAlta} enviando={enviando} />
      <AdminVehiculoList
        vehiculos={vehiculos}
        onBajaTemporal={handleBajaTemporal}
        onBajaDefinitiva={handleBajaDefinitiva}
        onReactivar={handleReactivar}
      />
      {mensaje && <p role={mensaje.tipo === "error" ? "alert" : "status"}>{mensaje.texto}</p>}
    </section>
  );
}
