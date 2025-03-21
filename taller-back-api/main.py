from fastapi import FastAPI, HTTPException, Depends
from sqlalchemy import create_engine, Column, Integer, String, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session, relationship
import os
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from jose import JWTError, jwt
from passlib.context import CryptContext
from datetime import datetime, timedelta
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.exc import IntegrityError
from pydantic import BaseModel
import requests


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

# Seguridad OAuth2 para manejar tokens
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

# Modelos de la base de datos
class Usuario(Base):
    __tablename__ = "usuarios"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(255), unique=True, index=True)
    password_hash = Column(String(255))

    # Relación con Vehículo (uno a muchos)
    vehiculos = relationship("Vehiculo", back_populates="usuario")

class Vehiculo(Base):
    __tablename__ = "vehiculos"
    id = Column(Integer, primary_key=True, index=True)
    marca = Column(String(255), index=True)
    modelo = Column(String(255))
    year = Column(Integer)
    rpm = Column(Integer)
    velocidad = Column(Integer)
    usuario_id = Column(Integer, ForeignKey('usuarios.id'))  # FK hacia Usuario

    # Relación con Usuario (muchos a uno)
    usuario = relationship("Usuario", back_populates="vehiculos")

    # Relación con ErrorVehiculo (uno a muchos)
    errores = relationship("ErrorVehiculo", back_populates="vehiculo")

class ErrorVehiculo(Base):
    __tablename__ = "errores_vehiculos"
    id = Column(Integer, primary_key=True, index=True)
    vehiculo_id = Column(Integer, ForeignKey('vehiculos.id'))  # FK hacia Vehiculo
    codigo_dtc = Column(String(255))

    # Relación con Vehículo (muchos a uno)
    vehiculo = relationship("Vehiculo", back_populates="errores")


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
def obtener_usuario_desde_token(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("sub")
        usuario = db.query(Usuario).filter(Usuario.username == username).first()
        if usuario is None:
            raise HTTPException(status_code=401, detail="Usuario no encontrado")
        return usuario
    except JWTError:
        raise HTTPException(status_code=401, detail="Token inválido o expirado")

# Modelos Pydantic para peticiones
class UsuarioRegistro(BaseModel):
    username: str
    password: str

class UsuarioLogin(BaseModel):
    username: str
    password: str

class VehiculoRegistro(BaseModel):
    marca: str
    modelo: str
    year: int
    rpm: int
    velocidad: int

class ErrorVehiculoRegistro(BaseModel):
    codigo_dtc: list[str]
    vehiculo_id: int

# Endpoint para registro de usuario
@app.post("/register")
def register(datos: UsuarioRegistro, db: Session = Depends(get_db)):
    hashed_password = pwd_context.hash(datos.password)
    usuario = Usuario(username=datos.username, password_hash=hashed_password)
    db.add(usuario)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail="El usuario ya existe")
    return {"mensaje": "Usuario registrado correctamente"}

# Endpoint para autenticación y obtención del token JWT
@app.post("/login")
def login(datos: UsuarioLogin, db: Session = Depends(get_db)):
    usuario = db.query(Usuario).filter(Usuario.username == datos.username).first()
    if not usuario or not verificar_password(datos.password, usuario.password_hash):
        raise HTTPException(status_code=401, detail="Credenciales incorrectas")
    
    token = crear_token({"sub": datos.username})
    return {"access_token": token, "token_type": "bearer"}

# Endpoint para que el cliente de Python envíe datos OBD-II
@app.post("/guardar-vehiculo/")
def guardar_vehiculo(datos: VehiculoRegistro, usuario: Usuario = Depends(obtener_usuario_desde_token), db: Session = Depends(get_db)):
    nuevo_vehiculo = Vehiculo(**datos.dict(), usuario_id=usuario.id)
    db.add(nuevo_vehiculo)
    db.commit()
    return {"mensaje": "Vehículo guardado correctamente", "id": nuevo_vehiculo.id}

# Endpoint para que el cliente de Python envíe errores OBD-II
@app.post("/guardar-errores/")
def guardar_errores(datos: ErrorVehiculoRegistro, usuario: Usuario = Depends(obtener_usuario_desde_token), db: Session = Depends(get_db)):
    vehiculo = db.query(Vehiculo).filter(Vehiculo.id == datos.vehiculo_id, Vehiculo.usuario_id == usuario.id).first()
    if vehiculo is None:
        raise HTTPException(status_code=404, detail="Vehículo no encontrado para el usuario.")

    for codigo in datos.codigo_dtc:
        error = ErrorVehiculo(vehiculo_id=vehiculo.id, codigo_dtc=codigo)
        db.add(error)

    db.commit()
    return {"mensaje": "Errores del vehículo guardados correctamente"}

# Endpoint para obtener vehículos del usuario autenticado
@app.get("/mis-vehiculos/")
def obtener_vehiculos(usuario: Usuario = Depends(obtener_usuario_desde_token), db: Session = Depends(get_db)):
    vehiculos = db.query(Vehiculo).filter(Vehiculo.usuario_id == usuario.id).all()
    return vehiculos

# Endpoint para obtener un vehiculo especifico del usuario autenticado
@app.get("/mis-vehiculos/{vehiculo_id}")
def obtener_vehiculo(vehiculo_id: int, usuario: Usuario = Depends(obtener_usuario_desde_token), db: Session = Depends(get_db)):
    vehiculo = db.query(Vehiculo).filter(Vehiculo.id == vehiculo_id, Vehiculo.usuario_id == usuario.id).first()
    if vehiculo is None:
        raise HTTPException(status_code=404, detail="Vehículo no encontrado")
    return vehiculo

# Endpoint para obtener los errores de un vehículo específico del usuario autenticado
@app.get("/mis-errores/{vehiculo_id}")
def obtener_errores(vehiculo_id: int, usuario: Usuario = Depends(obtener_usuario_desde_token), db: Session = Depends(get_db)):
    errores = db.query(ErrorVehiculo).filter(ErrorVehiculo.vehiculo_id == vehiculo_id).all()
    if not errores:
        raise HTTPException(status_code=404, detail="No se encontraron errores para este vehículo.")
    return errores

@app.get("/car-imagery/")
def get_car_image(searchTerm: str):
    url = f"https://www.carimagery.com/api.asmx/GetImageUrl?searchTerm={searchTerm}"
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.text
    except requests.RequestException as e:
        raise HTTPException(status_code=500, detail=f"Error al obtener imagen: {e}")

# Endpoint para editar vehículo
@app.put("/editar-vehiculo/{vehiculo_id}")
def editar_vehiculo(vehiculo_id: int, datos: VehiculoRegistro, usuario: Usuario = Depends(obtener_usuario_desde_token), db: Session = Depends(get_db)):
    vehiculo = db.query(Vehiculo).filter(Vehiculo.id == vehiculo_id, Vehiculo.usuario_id == usuario.id).first()
    if vehiculo is None:
        raise HTTPException(status_code=404, detail="Vehículo no encontrado")
    
    # Actualizar los detalles del vehículo
    vehiculo.marca = datos.marca
    vehiculo.modelo = datos.modelo
    vehiculo.year = datos.year
    vehiculo.rpm = datos.rpm
    vehiculo.velocidad = datos.velocidad

    db.commit()
    return {"mensaje": "Vehículo actualizado correctamente"}

# Endpoint para eliminar vehículo
@app.delete("/eliminar-vehiculo/{vehiculo_id}")
def eliminar_vehiculo(vehiculo_id: int, usuario: Usuario = Depends(obtener_usuario_desde_token), db: Session = Depends(get_db)):
    vehiculo = db.query(Vehiculo).filter(Vehiculo.id == vehiculo_id, Vehiculo.usuario_id == usuario.id).first()
    if vehiculo is None:
        raise HTTPException(status_code=404, detail="Vehículo no encontrado")
    
    db.query(ErrorVehiculo).filter(ErrorVehiculo.vehiculo_id == vehiculo.id).delete()
    db.delete(vehiculo)
    db.commit()
    return {"mensaje": "Vehículo eliminado correctamente"}

# Endpoint de saludo
@app.get("/saludo")
async def saludo():
    return {"mensaje": "¡La API está funcionando correctamente!"}
