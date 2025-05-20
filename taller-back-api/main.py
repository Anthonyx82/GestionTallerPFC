# Standard library
import os
import uuid
from datetime import datetime, timedelta

# Third-party libraries
import requests
from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic import BaseModel
from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.security import OAuth2PasswordBearer
from fastapi_mail import FastMail, MessageSchema, ConnectionConfig
from sqlalchemy import create_engine, Column, Integer, String, ForeignKey
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session, relationship

# Configuración de la base de datos
DATABASE_URL = os.getenv("DATABASE_URL", "mysql+pymysql://user:password@db/talleres")
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Configuracion del servidor de correo
#conf = ConnectionConfig(
#    MAIL_USERNAME="tucorreo@example.com",
#    MAIL_PASSWORD="tu_contraseña",
#    MAIL_FROM="tucorreo@example.com",
#    MAIL_PORT=587,
#    MAIL_SERVER="smtp.tu-servidor.com",
#    MAIL_TLS=True,
#    MAIL_SSL=False,
#    USE_CREDENTIALS=True
#)

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
    vin = Column(String(17), unique=True, nullable=False)
    revision = Column(String(255))
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

class InformeCompartido(Base):
    __tablename__ = "informes_compartidos"
    id = Column(Integer, primary_key=True)
    token = Column(String(100), unique=True, index=True, default=lambda: str(uuid.uuid4()))
    vehiculo_id = Column(Integer, ForeignKey("vehiculos.id"))
    email_cliente = Column(String(255))
    creado_en = Column(String(255), default=lambda: datetime.utcnow().isoformat())

    vehiculo = relationship("Vehiculo")

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
    vin: str
    revision: dict

class ErrorVehiculoRegistro(BaseModel):
    codigo_dtc: list[str]
    vehiculo_id: int
    
class InformeRequest(BaseModel):
    email: str
    
class VehiculoEdicion(BaseModel):
    marca: str
    modelo: str
    year: int
    rpm: int
    velocidad: int
    vin: str

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
def guardar_vehiculo(
    datos: VehiculoRegistro, 
    usuario: Usuario = Depends(obtener_usuario_desde_token), 
    db: Session = Depends(get_db)
):
    # Verificar si el VIN ya está registrado
    if db.query(Vehiculo).filter(Vehiculo.vin == datos.vin).first():
        raise HTTPException(status_code=400, detail="El VIN ya está registrado en otro vehículo.")
    
    # Agregar los datos de revisión al vehículo
    nuevo_vehiculo = Vehiculo(
        marca=datos.marca,
        modelo=datos.modelo,
        year=datos.year,
        rpm=datos.rpm,
        velocidad=datos.velocidad,
        vin=datos.vin,
        revision=str(datos.revision),
        usuario_id=usuario.id
    )
    
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

@app.post("/crear-informe/{vehiculo_id}")
def crear_informe(vehiculo_id: int, request: InformeRequest, usuario: Usuario = Depends(obtener_usuario_desde_token), db: Session = Depends(get_db)):
    vehiculo = db.query(Vehiculo).filter_by(id=vehiculo_id, usuario_id=usuario.id).first()
    if not vehiculo:
        raise HTTPException(status_code=404, detail="Vehículo no encontrado")

    token = str(uuid.uuid4())
    informe = InformeCompartido(token=token, vehiculo_id=vehiculo.id, email_cliente=request.email)
    db.add(informe)
    db.commit()

    enlace = f"https://anthonyx82.ddns.net/taller-front/informe/{token}"
    mensaje = MessageSchema(
        subject="Tu informe del vehículo",
        recipients=[request.email],
        body=f"Hola, aquí tienes el informe de tu vehículo: {enlace}",
        subtype="plain"
    )
    # Descomentar una vez configurado el correo
    # fm.send_message(mensaje)

    return {"mensaje": "Informe creado y enviado al email", "token": token, "enlace": enlace}


@app.get("/informe/{token}")
def ver_informe(token: str, db: Session = Depends(get_db)):
    informe = db.query(InformeCompartido).filter_by(token=token).first()
    if not informe:
        raise HTTPException(status_code=404, detail="Informe no encontrado")

    vehiculo = db.query(Vehiculo).filter_by(id=informe.vehiculo_id).first()
    errores = db.query(ErrorVehiculo).filter_by(vehiculo_id=vehiculo.id).all()

    return {
        "vehiculo": {
            "marca": vehiculo.marca,
            "modelo": vehiculo.modelo,
            "year": vehiculo.year,
            "vin": vehiculo.vin,
            "rpm": vehiculo.rpm,
            "velocidad": vehiculo.velocidad,
            "revision": vehiculo.revision
        },
        "errores": [e.codigo_dtc for e in errores]
    }

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
def editar_vehiculo(
    vehiculo_id: int, 
    datos: VehiculoEdicion,
    usuario: Usuario = Depends(obtener_usuario_desde_token), 
    db: Session = Depends(get_db)
):
    vehiculo = db.query(Vehiculo).filter(Vehiculo.id == vehiculo_id, Vehiculo.usuario_id == usuario.id).first()
    
    if vehiculo is None:
        raise HTTPException(status_code=404, detail="Vehículo no encontrado")
    
    # Verificar que el nuevo VIN no esté en otro vehículo
    if vehiculo.vin != datos.vin and db.query(Vehiculo).filter(Vehiculo.vin == datos.vin).first():
        raise HTTPException(status_code=400, detail="El VIN ya está registrado en otro vehículo.")

    # Actualizar solo los campos permitidos
    vehiculo.marca = datos.marca
    vehiculo.modelo = datos.modelo
    vehiculo.year = datos.year
    vehiculo.rpm = datos.rpm
    vehiculo.velocidad = datos.velocidad
    vehiculo.vin = datos.vin

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
