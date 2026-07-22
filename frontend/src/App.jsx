import { useState } from "react";
import PaginaReservar from "./pages/PaginaReservar";
import PaginaMisReservas from "./pages/PaginaMisReservas";
import PaginaAdmin from "./pages/PaginaAdmin";

export default function App() {
  const [vista, setVista] = useState("menu");
  const [subVistaEmpleado, setSubVistaEmpleado] = useState("nueva");

  function volverAlMenu() {
    setVista("menu");
    setSubVistaEmpleado("nueva");
  }

  return (
    <div>
      <header className="app-header">
        <h1 onClick={volverAlMenu}>Reserva de Vehículos Corporativos</h1>
        {vista !== "menu" && (
          <button className="volver-btn" onClick={volverAlMenu}>
            ← Volver al menú
          </button>
        )}
      </header>

      <main className="app-main">
        {vista === "menu" && (
          <div className="menu-principal">
            <div className="menu-card" onClick={() => setVista("empleado")}>
              <span className="icono">🚗</span>
              <h2>Reservar</h2>
              <p>Consultá vehículos disponibles, reservá uno o gestioná tus reservas.</p>
            </div>
            <div className="menu-card" onClick={() => setVista("admin")}>
              <span className="icono">🛠️</span>
              <h2>Administración</h2>
              <p>Alta, edición y baja de vehículos del pool (requiere credenciales).</p>
            </div>
          </div>
        )}

        {vista === "empleado" && (
          <>
            <nav className="subnav">
              <button
                className={subVistaEmpleado === "nueva" ? "activo" : ""}
                onClick={() => setSubVistaEmpleado("nueva")}
              >
                Nueva reserva
              </button>
              <button
                className={subVistaEmpleado === "mis" ? "activo" : ""}
                onClick={() => setSubVistaEmpleado("mis")}
              >
                Mis reservas
              </button>
            </nav>
            {subVistaEmpleado === "nueva" && <PaginaReservar />}
            {subVistaEmpleado === "mis" && <PaginaMisReservas />}
          </>
        )}

        {vista === "admin" && <PaginaAdmin />}
      </main>
    </div>
  );
}
