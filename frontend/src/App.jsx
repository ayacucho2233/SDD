import { useState } from "react";
import PaginaReservar from "./pages/PaginaReservar";
import PaginaMisReservas from "./pages/PaginaMisReservas";
import PaginaAdmin from "./pages/PaginaAdmin";

export default function App() {
  const [tab, setTab] = useState("reservar");

  return (
    <div>
      <header>
        <h1>Reserva de Vehículos Corporativos</h1>
        <nav>
          <button onClick={() => setTab("reservar")}>Reservar</button>
          <button onClick={() => setTab("mis-reservas")}>Mis reservas</button>
          <button onClick={() => setTab("admin")}>Administración</button>
        </nav>
      </header>
      <main>
        {tab === "reservar" && <PaginaReservar />}
        {tab === "mis-reservas" && <PaginaMisReservas />}
        {tab === "admin" && <PaginaAdmin />}
      </main>
    </div>
  );
}
