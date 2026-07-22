from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import get_settings
from app.routers import admin_vehiculos, reservas, vehiculos

settings = get_settings()

app = FastAPI(title="Reserva de Vehículos Corporativos")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.frontend_origin],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(vehiculos.router)
app.include_router(reservas.router)
app.include_router(admin_vehiculos.router)
