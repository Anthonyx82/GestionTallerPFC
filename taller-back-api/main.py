from fastapi import FastAPI, HTTPException, Depends
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
import os
import time
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from jose import JWTError, jwt
from passlib.context import CryptContext
from datetime import datetime, timedelta

# Configuración de la base de datos
DATABASE_URL = os.getenv("DATABASE_URL", "mysql+pymysql://user:password@db/talleres")
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Clave secreta y configuración de JWT
SECRET_KEY = "clave-secreta-super-segura"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 300

# Configuración de Hash para contraseñas
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Modelo de la base de datos
class Usuario(Base):
    __tablename__ = "usuarios"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(255), unique=True, index=True)
    password_hash = Column(String(255))

class Vehiculo(Base):
    __tablename__ = "vehiculos"
    id = Column(Integer, primary_key=True, index=True)
    marca = Column(String(255), index=True)
    modelo = Column(String(255))
    year = Column(Integer)
    rpm = Column(Integer)
    velocidad = Column(Integer)
    usuario_id = Column(Integer)  # Relación con el usuario

# Crear tablas si no existen
Base.metadata.create_all(bind=engine)

# Iniciar FastAPI
app = FastAPI(root_path="/taller/api")

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

# Función para verificar contraseña
def verificar_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

# Función para generar tokens
def crear_token(data: dict, expira_en: int = ACCESS_TOKEN_EXPIRE_MINUTES):
    to_encode = data.copy()
    to_encode.update({"exp": datetime.utcnow() + timedelta(minutes=expira_en)})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

# Función para verificar token
def obtener_usuario_desde_token(token: str, db: Session):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("sub")
        usuario = db.query(Usuario).filter(Usuario.username == username).first()
        if usuario is None:
            raise HTTPException(status_code=401, detail="Usuario no encontrado")
        return usuario
    except JWTError:
        raise HTTPException(status_code=401, detail="Token inválido o expirado")

# Endpoint para registro de usuario
@app.post("/register")
def register(username: str, password: str, db: Session = Depends(get_db)):
    hashed_password = pwd_context.hash(password)
    usuario = Usuario(username=username, password_hash=hashed_password)
    db.add(usuario)
    db.commit()
    return {"mensaje": "Usuario registrado correctamente"}

# Endpoint para autenticación y obtención del token JWT
@app.post("/login")
def login(username: str, password: str, db: Session = Depends(get_db)):
    usuario = db.query(Usuario).filter(Usuario.username == username).first()
    if not usuario or not verificar_password(password, usuario.password_hash):
        raise HTTPException(status_code=401, detail="Credenciales incorrectas")
    
    token = crear_token({"sub": username})
    return {"access_token": token, "token_type": "bearer"}

# Endpoint para que el cliente de Python envíe datos OBD-II
@app.post("/guardar-vehiculo/")
def guardar_vehiculo(marca: str, modelo: str, year: int, rpm: int, velocidad: int, token: str, db: Session = Depends(get_db)):
    usuario = obtener_usuario_desde_token(token, db)
    nuevo_vehiculo = Vehiculo(marca=marca, modelo=modelo, year=year, rpm=rpm, velocidad=velocidad, usuario_id=usuario.id)
    db.add(nuevo_vehiculo)
    db.commit()
    return {"mensaje": "Vehículo guardado correctamente", "id": nuevo_vehiculo.id}

# Endpoint para obtener vehículos del usuario autenticado
@app.get("/mis-vehiculos/")
def obtener_vehiculos(token: str, db: Session = Depends(get_db)):
    usuario = obtener_usuario_desde_token(token, db)
    vehiculos = db.query(Vehiculo).filter(Vehiculo.usuario_id == usuario.id).all()
    return vehiculos

# Endpoint de saludo
@app.get("/saludo")
async def saludo():
    return {"mensaje": "¡La API está funcionando correctamente!"}
