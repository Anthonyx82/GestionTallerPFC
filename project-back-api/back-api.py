from fastapi import FastAPI, HTTPException
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import serial
import time

# Base de datos
DATABASE_URL = "sqlite:///./vehiculos.db"  # Cambiar si necesitas otra base de datos
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

# Crear la app
app = FastAPI()

# Función para leer datos del lector OBD2
def leer_datos_obd2():
    PORT = "COM3"  # Cambia al puerto donde está tu lector OBD2
    BAUDRATE = 9600
    TIMEOUT = 1  # Tiempo de espera para recibir respuestas

    try:
        # Conectar con el lector OBD2
        elm = serial.Serial(PORT, BAUDRATE, timeout=TIMEOUT)
        print("Conexión con el lector OBD2 exitosa.")

        # Enviar comandos al lector OBD2
        def enviar_comando(comando):
            elm.write((comando + "\r").encode())  # Agregar retorno de carro al comando
            time.sleep(0.5)
            respuesta = elm.readlines()
            return [line.decode().strip() for line in respuesta]

        # Inicializar el ELM327
        enviar_comando("ATZ")  # Reinicio del ELM327
        enviar_comando("ATE0")  # Desactivar eco
        enviar_comando("ATSP0")  # Auto-detectar protocolo OBD2

        # Leer RPM
        rpm_respuesta = enviar_comando("010C")  # PID para RPM
        if rpm_respuesta:
            # Decodificar respuesta para RPM
            rpm_hex = rpm_respuesta[0].split()[2:4]
            rpm = (int(rpm_hex[0], 16) * 256 + int(rpm_hex[1], 16)) // 4
        else:
            rpm = 0

        # Leer velocidad
        velocidad_respuesta = enviar_comando("010D")  # PID para velocidad
        if velocidad_respuesta:
            # Decodificar respuesta para velocidad
            velocidad = int(velocidad_respuesta[0].split()[2], 16)
        else:
            velocidad = 0

        # Suponemos marca, modelo y año como ejemplo, puedes expandirlo
        return {
            "marca": "Desconocida",  # Puede venir de otros comandos si es compatible
            "modelo": "Desconocido",
            "year": 2000,
            "rpm": rpm,
            "velocidad": velocidad,
        }

    except Exception as e:
        print(f"Error al leer datos OBD2: {e}")
        raise HTTPException(status_code=500, detail="Error al leer datos del vehículo")

# Endpoint para guardar los datos del vehículo automáticamente
@app.post("/guardar-vehiculo/")
async def guardar_vehiculo():
    session = SessionLocal()
    try:
        # Llama a la función que lee los datos del lector OBD2
        datos = leer_datos_obd2()

        # Crear un nuevo registro en la base de datos
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
