from fastapi import FastAPI, HTTPException
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import serial
import time
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

# Crear la app
app = FastAPI()

# Configurar CORS correctamente
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Puedes cambiarlo a ["http://127.0.0.1:5500"] si lo necesitas
    allow_credentials=True,
    allow_methods=["*"],  # Permite todos los métodos (incluyendo OPTIONS)
    allow_headers=["*"],  # Permite todos los headers
)

# Base de datos
DATABASE_URL = "sqlite:///./vehiculos.db"
engine = create_engine(DATABASE_URL)
Base = declarative_base()

# Modelo de la base de datos
class Vehiculo(Base):
    __tablename__ = "vehiculos"
    id = Column(Integer, primary_key=True, index=True)
    marca = Column(String, index=True)
    modelo = Column(String)
    year = Column(Integer)
    rpm = Column(Integer)
    velocidad = Column(Integer)

Base.metadata.create_all(bind=engine)

# Sesión de la base de datos
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Función para leer datos del lector OBD2
def leer_datos_obd2():
    PORT = "COM3"  # Cambia al puerto donde está tu lector OBD2
    BAUDRATE = 9600
    TIMEOUT = 1

    try:
        elm = serial.Serial(PORT, BAUDRATE, timeout=TIMEOUT)
        print("Conexión con el lector OBD2 exitosa.")

        def enviar_comando(comando):
            elm.write((comando + "\r").encode())
            time.sleep(0.5)
            respuesta = elm.readlines()
            return [line.decode().strip() for line in respuesta]

        enviar_comando("ATZ")
        enviar_comando("ATE0")
        enviar_comando("ATSP0")

        rpm_respuesta = enviar_comando("010C")
        if rpm_respuesta:
            rpm_hex = rpm_respuesta[0].split()[2:4]
            rpm = (int(rpm_hex[0], 16) * 256 + int(rpm_hex[1], 16)) // 4
        else:
            rpm = 0

        velocidad_respuesta = enviar_comando("010D")
        if velocidad_respuesta:
            velocidad = int(velocidad_respuesta[0].split()[2], 16)
        else:
            velocidad = 0

        return {
            "marca": "Desconocida",
            "modelo": "Desconocido",
            "year": 2000,
            "rpm": rpm,
            "velocidad": velocidad,
        }

    except Exception as e:
        print(f"Error al leer datos OBD2: {e}")
        raise HTTPException(status_code=500, detail="Error al leer datos del vehículo")

# Endpoint para manejar OPTIONS (preflight request)
@app.options("/guardar-vehiculo/")
async def options_guardar_vehiculo():
    return JSONResponse(content={}, status_code=200)

# Endpoint para guardar los datos del vehículo automáticamente
@app.post("/guardar-vehiculo/")
async def guardar_vehiculo():
    session = SessionLocal()
    try:
        datos = leer_datos_obd2()
        nuevo_vehiculo = Vehiculo(
            marca=datos["marca"],
            modelo=datos["modelo"],
            year=datos["year"],
            rpm=datos["rpm"],
            velocidad=datos["velocidad"],
        )
        session.add(nuevo_vehiculo)
        session.commit()
        session.refresh(nuevo_vehiculo)
        return {"mensaje": "Vehículo guardado correctamente", "id": nuevo_vehiculo.id}
    except Exception as e:
        session.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        session.close()
