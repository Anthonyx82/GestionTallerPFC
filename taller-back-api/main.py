from fastapi import FastAPI, HTTPException, Depends
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
import os
import serial
import time
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

# Obtener configuración desde variables de entorno
DATABASE_URL = os.getenv("DATABASE_URL", "mysql+pymysql://user:password@db/talleres")

# Crear conexión a la base de datos
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Modelo de la base de datos
Base = declarative_base()

class Vehiculo(Base):
    __tablename__ = "vehiculos"
    id = Column(Integer, primary_key=True, index=True)
    marca = Column(String(255), index=True)
    modelo = Column(String(255))
    year = Column(Integer)
    rpm = Column(Integer)
    velocidad = Column(Integer)

# Crear tablas en la base de datos si no existen
Base.metadata.create_all(bind=engine)

# Crear la app FastAPI
app = FastAPI(root_path="/taller/api")  # Para funcionar en la subruta con Traefik

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Dependencia para obtener la sesión de la base de datos
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Función para leer datos del lector OBD2
def leer_datos_obd2():
    PORT = "/dev/ttyUSB0"  # Cambiar según el entorno
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
        rpm = int(rpm_respuesta[0].split()[2], 16) if rpm_respuesta else 0

        velocidad_respuesta = enviar_comando("010D")
        velocidad = int(velocidad_respuesta[0].split()[2], 16) if velocidad_respuesta else 0

        return {"marca": "Desconocida", "modelo": "Desconocido", "year": 2000, "rpm": rpm, "velocidad": velocidad}

    except Exception as e:
        print(f"Error al leer datos OBD2: {e}")
        raise HTTPException(status_code=500, detail="Error al leer datos del vehículo")

# Endpoint para manejar OPTIONS (preflight request)
@app.options("/guardar-vehiculo/")
async def options_guardar_vehiculo():
    return JSONResponse(content={}, status_code=200)

# Endpoint para guardar los datos del vehículo en la BBDD
@app.post("/guardar-vehiculo/")
async def guardar_vehiculo(db: Session = Depends(get_db)):
    try:
        datos = leer_datos_obd2()
        nuevo_vehiculo = Vehiculo(**datos)
        db.add(nuevo_vehiculo)
        db.commit()
        db.refresh(nuevo_vehiculo)
        return {"mensaje": "Vehículo guardado correctamente", "id": nuevo_vehiculo.id}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

# Endpoint de saludo para comprobar si la API está funcionando
@app.get("/saludo")
async def saludo():
    return {"mensaje": "¡La API está funcionando correctamente!"}