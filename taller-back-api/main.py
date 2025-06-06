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
from dotenv import load_dotenv
load_dotenv()
import os

# Configuración de la base de datos
"""
Configuración de la base de datos:

- Se establece la conexión con el motor de base de datos (MySQL por defecto).
- Se define `SessionLocal` como el generador de sesiones SQLAlchemy.
- `Base` se utiliza como clase base para los modelos ORM declarativos.
"""
DATABASE_URL = os.getenv("DATABASE_URL", "mysql+pymysql://user:password@db/talleres")
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Configuracion del servidor de correo
"""
Configuración del sistema de envío de correos (FastAPI Mail):

- Las credenciales y parámetros se cargan desde variables de entorno.
- `FastMail` se instancia con esta configuración para ser usado en envíos.
"""
conf = ConnectionConfig(
    MAIL_USERNAME=os.getenv("MAIL_USERNAME"),
    MAIL_PASSWORD=os.getenv("MAIL_PASSWORD"),
    MAIL_FROM=os.getenv("MAIL_FROM"),
    MAIL_PORT=int(os.getenv("MAIL_PORT", 587)),
    MAIL_SERVER=os.getenv("MAIL_SERVER"),
    MAIL_STARTTLS=os.getenv("MAIL_STARTTLS", "True") == "True",
    MAIL_SSL_TLS=os.getenv("MAIL_SSL_TLS", "False") == "True",
    USE_CREDENTIALS=os.getenv("USE_CREDENTIALS", "True") == "True",
    VALIDATE_CERTS=os.getenv("VALIDATE_CERTS", "True") == "True"
)

fm = FastMail(conf)

# Clave secreta y configuración de JWT
"""
Configuración de seguridad:

- `SECRET_KEY`, `ALGORITHM` y tiempo de expiración definen la seguridad del JWT.
- `pwd_context` se usa para hashear contraseñas con bcrypt.
- `oauth2_scheme` se usa como dependencia para extraer el token del header Authorization.
"""
SECRET_KEY = "clave-secreta-super-segura"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 300

# Configuración de Hash para contraseñas
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Seguridad OAuth2 para manejar tokens
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

# Modelos de la base de datos
class Usuario(Base):
    """
    Modelo ORM que representa a los usuarios del sistema.

    Atributos:
        id (int): ID autoincremental (clave primaria).
        username (str): Nombre de usuario, único.
        password_hash (str): Contraseña hasheada con bcrypt.

    Relaciones:
        vehiculos (List[Vehiculo]): Lista de vehículos registrados por el usuario.
    """
    __tablename__ = "usuarios"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(255), unique=True, index=True)
    password_hash = Column(String(255))

    # Relación con Vehículo (uno a muchos)
    vehiculos = relationship("Vehiculo", back_populates="usuario")

class Vehiculo(Base):
    """
    Modelo ORM que representa un vehículo registrado.

    Atributos:
        id (int): ID del vehículo.
        marca (str): Marca del vehículo.
        modelo (str): Modelo del vehículo.
        year (int): Año de fabricación.
        rpm (int): Revoluciones por minuto.
        velocidad (int): Velocidad actual.
        vin (str): Número VIN único del vehículo.
        revision (str): Información de revisión técnica.
        usuario_id (int): ID del usuario al que pertenece el vehículo.

    Relaciones:
        usuario (Usuario): Usuario propietario.
        errores (List[ErrorVehiculo]): Lista de errores asociados.
        informes_compartidos (List[InformeCompartido]): Informes generados con token público.
    """
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
    errores = relationship("ErrorVehiculo", back_populates="vehiculo", cascade="all, delete-orphan")
    
    # Relación con InformeCompartido (uno a muchos)
    informes_compartidos = relationship("InformeCompartido", back_populates="vehiculo", cascade="all, delete-orphan")


class ErrorVehiculo(Base):
    """
    Modelo ORM que almacena los errores OBD-II (códigos DTC) de un vehículo.

    Atributos:
        id (int): ID del error.
        vehiculo_id (int): ID del vehículo asociado.
        codigo_dtc (str): Código de diagnóstico (ej. P0301).

    Relaciones:
        vehiculo (Vehiculo): Vehículo asociado.
    """
    __tablename__ = "errores_vehiculos"
    id = Column(Integer, primary_key=True, index=True)
    vehiculo_id = Column(Integer, ForeignKey('vehiculos.id'))  # FK hacia Vehiculo
    codigo_dtc = Column(String(255))

    # Relación con Vehículo (muchos a uno)
    vehiculo = relationship("Vehiculo", back_populates="errores")

class InformeCompartido(Base):
    """
    Modelo ORM que representa un informe compartido con un cliente por email.

    Atributos:
        id (int): ID del informe.
        token (str): Token único para acceder al informe.
        vehiculo_id (int): ID del vehículo relacionado.
        email_cliente (str): Email al que se envía el informe.
        creado_en (str): Fecha y hora de creación del informe (ISO format).

    Relaciones:
        vehiculo (Vehiculo): Vehículo asociado.
    """
    __tablename__ = "informes_compartidos"
    id = Column(Integer, primary_key=True)
    token = Column(String(100), unique=True, index=True, default=lambda: str(uuid.uuid4()))
    vehiculo_id = Column(Integer, ForeignKey("vehiculos.id"))
    email_cliente = Column(String(255))
    creado_en = Column(String(255), default=lambda: datetime.utcnow().isoformat())

    # Relación con Vehiculo (muchos a uno)
    vehiculo = relationship("Vehiculo", back_populates="informes_compartidos")

# Crear tablas si no existen
if __name__ == "__main__":
    Base.metadata.create_all(bind=engine)

# Iniciar FastAPI
app = FastAPI(root_path="/taller/api")

app.mount("/docs_html", StaticFiles(directory="docs/build/html"), name="docs_html")

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
    """
    Dependencia de FastAPI para obtener una sesión de base de datos.

    Se utiliza con `Depends(get_db)` para abrir una sesión, cederla al endpoint y cerrarla automáticamente.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Función para verificar contraseña
def verificar_password(plain_password, hashed_password):
    """
    Verifica si una contraseña en texto plano coincide con su hash almacenado.

    Args:
        password_plano (str): Contraseña proporcionada por el usuario.
        password_hash (str): Hash almacenado en la base de datos.

    Returns:
        bool: True si coinciden, False si no.
    """
    return pwd_context.verify(plain_password, hashed_password)

# Función para generar tokens
def crear_token(data: dict, expira_en: int = ACCESS_TOKEN_EXPIRE_MINUTES):
    """
    Genera un token JWT con los datos proporcionados y un tiempo de expiración opcional.

    Args:
        datos (dict): Datos a incluir en el payload del token.
        tiempo_expiracion (Optional[timedelta]): Tiempo personalizado de expiración. Si no se especifica, se usarán 30 minutos por defecto.

    Returns:
        str: Token JWT firmado.

    Raises:
        Exception: Si hay un error al codificar el token.
    """
    to_encode = data.copy()
    to_encode.update({"exp": datetime.utcnow() + timedelta(minutes=expira_en)})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

# Función para verificar token
def obtener_usuario_desde_token(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    """
    Extrae y valida el usuario actual a partir del token JWT proporcionado.

    Args:
        token (str): Token JWT incluido en el encabezado de autorización.
        db (Session): Sesión de base de datos.

    Returns:
        Usuario: Instancia del usuario autenticado.

    Raises:
        HTTPException 401: Si el token es inválido o ha expirado.
    """
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
    """
    Modelo de solicitud para registrar un nuevo usuario.

    Atributos:
        username (str): Nombre de usuario.
        password (str): Contraseña en texto plano.
    """
    username: str
    password: str

class UsuarioLogin(BaseModel):
    """
    Modelo de solicitud para iniciar sesión de usuario.

    Atributos:
        username (str): Nombre de usuario.
        password (str): Contraseña en texto plano.
    """
    username: str
    password: str

class VehiculoRegistro(BaseModel):
    """
    Modelo de solicitud para registrar un nuevo vehículo.

    Atributos:
        marca (str): Marca del vehículo.
        modelo (str): Modelo del vehículo.
        year (int): Año del vehículo.
        rpm (int): RPM del motor.
        velocidad (int): Velocidad del vehículo.
        vin (str): Número VIN único del vehículo.
        revision (dict): Detalles de la revisión técnica (estructura flexible).
    """
    marca: str
    modelo: str
    year: int
    rpm: int
    velocidad: int
    vin: str
    revision: dict

class VehiculoEdicion(BaseModel):
    """
    Modelo de solicitud para editar un vehículo existente.

    Atributos:
        marca (str): Marca del vehículo.
        modelo (str): Modelo del vehículo.
        year (int): Año de fabricación.
        rpm (int): Revoluciones por minuto.
        velocidad (int): Velocidad actual.
        vin (str): Número VIN del vehículo.
    """
    marca: str
    modelo: str
    year: int
    rpm: int
    velocidad: int
    vin: str

class ErrorVehiculoRegistro(BaseModel):
    """
    Modelo de solicitud para registrar errores OBD-II de un vehículo.

    Atributos:
        codigo_dtc (list[str]): Lista de códigos DTC (códigos de diagnóstico).
        vehiculo_id (int): ID del vehículo al que se le asocian los errores.
    """
    codigo_dtc: list[str]
    vehiculo_id: int
    
class InformeRequest(BaseModel):
    """
    Modelo de solicitud para generar y enviar un informe por correo.

    Atributos:
        email (str): Dirección de email del cliente destinatario.
    """
    email: str
    

# Endpoint para registro de usuario
@app.post("/register")
def register(datos: UsuarioRegistro, db: Session = Depends(get_db)):
    """
    **POST** ``/register``
    
    Registra un nuevo usuario en la base de datos.
    
    **Parámetros**:
    - ``datos`` (UsuarioRegistro): Objeto que contiene el nombre de usuario y la contraseña.
    - ``db`` (Session): Sesión activa de la base de datos, proporcionada por FastAPI.
    
    **Retorna**:
    - ``dict``: Un mensaje indicando si el usuario fue registrado exitosamente.
    
    **Errores**:
    - ``400``: Si los campos son inválidos o el nombre de usuario ya existe.
    """
    if not datos.username or len(datos.username.strip()) < 3:
        raise HTTPException(status_code=400, detail="El nombre de usuario es obligatorio y debe tener al menos 3 caracteres.")
    if not datos.password or len(datos.password) < 6:
        raise HTTPException(status_code=400, detail="La contraseña debe tener al menos 6 caracteres.")

    hashed_password = pwd_context.hash(datos.password)
    usuario = Usuario(username=datos.username.strip(), password_hash=hashed_password)
    db.add(usuario)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail="El nombre de usuario ya está registrado. Por favor elige otro.")
    return {"mensaje": "Usuario registrado correctamente"}

# Endpoint para autenticación y obtención del token JWT
@app.post("/login")
def login(datos: UsuarioLogin, db: Session = Depends(get_db)):
    """
    Autentica al usuario y devuelve un token JWT válido.

    Args:
        datos (UsuarioLogin): Credenciales de usuario.
        db (Session): Sesión activa de la base de datos.

    Returns:
        dict: Token JWT si la autenticación fue exitosa.

    Raises:
        HTTPException 400: Datos inválidos.
        HTTPException 401: Usuario no encontrado o contraseña incorrecta.
        HTTPException 500: Error al generar el token.
    """
    if not datos.username or len(datos.username.strip()) < 3:
        raise HTTPException(status_code=400, detail="Debes ingresar un nombre de usuario válido.")
    
    if not datos.password or len(datos.password) < 6:
        raise HTTPException(status_code=400, detail="Debes ingresar una contraseña válida de al menos 6 caracteres.")

    usuario = db.query(Usuario).filter(Usuario.username == datos.username.strip()).first()
    
    if not usuario:
        raise HTTPException(status_code=401, detail="El nombre de usuario no está registrado.")
    
    if not verificar_password(datos.password, usuario.password_hash):
        raise HTTPException(status_code=401, detail="La contraseña es incorrecta.")

    try:
        token = crear_token({"sub": usuario.username})
    except Exception as e:
        raise HTTPException(status_code=500, detail="Hubo un error al generar el token. Intenta nuevamente.")

    return {"access_token": token, "token_type": "bearer"}

# Endpoint para que el cliente de Python envíe datos OBD-II
@app.post("/guardar-vehiculo/")
def guardar_vehiculo(datos: VehiculoRegistro, usuario: Usuario = Depends(obtener_usuario_desde_token), db: Session = Depends(get_db)):
    """
    Guarda un nuevo vehículo en la base de datos asociado al usuario autenticado.

    Args:
        vehiculo (VehiculoBase): Datos del vehículo (marca, modelo, año, color, etc.).
        db (Session): Sesión de base de datos.
        usuario (Usuario): Usuario autenticado, extraído desde el token JWT.

    Returns:
        dict: Mensaje de confirmación.

    Raises:
        HTTPException 401: Si no se proporciona un token válido.
    """
    # Validaciones básicas
    if not datos.vin or len(datos.vin.strip()) != 17:
        raise HTTPException(status_code=400, detail="El VIN debe contener exactamente 17 caracteres.")

    campos_requeridos = {
        "marca": datos.marca,
        "modelo": datos.modelo,
        "year": datos.year,
        "rpm": datos.rpm,
        "velocidad": datos.velocidad
    }
    for campo, valor in campos_requeridos.items():
        if not valor and valor != 0:
            raise HTTPException(status_code=400, detail=f"El campo '{campo}' es obligatorio.")

    if not isinstance(datos.revision, dict):
        raise HTTPException(status_code=400, detail="El campo 'revision' debe ser un objeto JSON.")

    # Verificar si el VIN ya está registrado
    if db.query(Vehiculo).filter(Vehiculo.vin == datos.vin.strip()).first():
        raise HTTPException(status_code=400, detail="El número de VIN ya está registrado. Debe ser único por vehículo.")

    try:
        nuevo_vehiculo = Vehiculo(
            marca=datos.marca.strip(),
            modelo=datos.modelo.strip(),
            year=datos.year,
            rpm=datos.rpm,
            velocidad=datos.velocidad,
            vin=datos.vin.strip(),
            revision=str(datos.revision),
            usuario_id=usuario.id
        )
        db.add(nuevo_vehiculo)
        db.commit()
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error al guardar el vehículo: {str(e)}")

    return {"mensaje": "Vehículo guardado correctamente", "id": nuevo_vehiculo.id}

# Endpoint para que el cliente de Python envíe errores OBD-II
@app.post("/guardar-errores/")
def guardar_errores(datos: ErrorVehiculoRegistro, usuario: Usuario = Depends(obtener_usuario_desde_token), db: Session = Depends(get_db)):
    """
    Guarda una lista de códigos de error OBD-II (DTC) asociados a un vehículo del usuario autenticado.

    Este endpoint es utilizado por el cliente Python que recibe errores del escáner OBD-II y los envía al backend para su almacenamiento.

    Args:
        datos (ErrorVehiculoRegistro): Objeto que contiene el ID del vehículo y una lista de códigos DTC.
        usuario (Usuario): Usuario autenticado, obtenido desde el token JWT.
        db (Session): Sesión activa de la base de datos.

    Returns:
        dict: Mensaje de confirmación si los errores fueron guardados correctamente.

    Raises:
        HTTPException 400:
            - Si el ID del vehículo no es válido (no entero o negativo).
            - Si la lista de códigos está vacía o contiene valores vacíos.
            - Si hay códigos DTC duplicados.
        HTTPException 404: Si el vehículo no pertenece al usuario autenticado.
        HTTPException 500: Si ocurre un error inesperado al guardar en la base de datos.
    """
    # Validar el ID del vehículo
    if not isinstance(datos.vehiculo_id, int) or datos.vehiculo_id <= 0:
        raise HTTPException(status_code=400, detail="El ID del vehículo debe ser un número entero positivo.")

    # Validar lista de códigos
    if not isinstance(datos.codigo_dtc, list) or len(datos.codigo_dtc) == 0:
        raise HTTPException(status_code=400, detail="Debe proporcionar al menos un código DTC.")
    
    codigos_limpios = [c.strip() for c in datos.codigo_dtc if c and c.strip()]
    if not codigos_limpios:
        raise HTTPException(status_code=400, detail="Todos los códigos DTC están vacíos o en blanco.")
    
    if len(set(codigos_limpios)) != len(codigos_limpios):
        raise HTTPException(status_code=400, detail="Hay códigos DTC duplicados en la lista.")

    # Verificar propiedad del vehículo
    vehiculo = db.query(Vehiculo).filter(
        Vehiculo.id == datos.vehiculo_id, 
        Vehiculo.usuario_id == usuario.id
    ).first()

    if vehiculo is None:
        raise HTTPException(status_code=404, detail="No se encontró un vehículo con ese ID para el usuario autenticado.")

    try:
        for codigo in codigos_limpios:
            error = ErrorVehiculo(vehiculo_id=vehiculo.id, codigo_dtc=codigo)
            db.add(error)
        db.commit()
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"No se pudieron guardar los errores del vehículo: {str(e)}")

    return {"mensaje": "Errores del vehículo guardados correctamente"}

# Endpoint para obtener vehículos del usuario autenticado
@app.get("/mis-vehiculos/")
def obtener_vehiculos(usuario: Usuario = Depends(obtener_usuario_desde_token), db: Session = Depends(get_db)):
    """
    Obtiene todos los vehículos registrados por el usuario autenticado.

    Args:
        db (Session): Sesión de base de datos.
        usuario (Usuario): Usuario autenticado mediante JWT.

    Returns:
        List[VehiculoBase]: Lista de vehículos asociados al usuario.
    """
    try:
        vehiculos = db.query(Vehiculo).filter(Vehiculo.usuario_id == usuario.id).all()
        if not vehiculos:
            return {"mensaje": "No hay vehículos registrados para este usuario.", "vehiculos": []}
        return {"vehiculos": vehiculos}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al obtener los vehículos: {str(e)}")

# Endpoint para obtener un vehiculo especifico del usuario autenticado
@app.get("/mis-vehiculos/{vehiculo_id}")
def obtener_vehiculo(vehiculo_id: int, usuario: Usuario = Depends(obtener_usuario_desde_token), db: Session = Depends(get_db)):
    """
    Recupera la información de un vehículo específico registrado por el usuario autenticado.

    Args:
        vehiculo_id (int): ID del vehículo a consultar.
        usuario (Usuario): Usuario autenticado mediante JWT.
        db (Session): Sesión activa de la base de datos.

    Returns:
        Vehiculo: Objeto del vehículo solicitado.

    Raises:
        HTTPException 404: Si el vehículo no pertenece al usuario o no existe.
    """
    vehiculo = db.query(Vehiculo).filter(Vehiculo.id == vehiculo_id, Vehiculo.usuario_id == usuario.id).first()
    if vehiculo is None:
        raise HTTPException(status_code=404, detail="Vehículo no encontrado")
    return vehiculo

# Endpoint para obtener los errores de un vehículo específico del usuario autenticado
@app.get("/mis-errores/{vehiculo_id}")
def obtener_errores(vehiculo_id: int, usuario: Usuario = Depends(obtener_usuario_desde_token), db: Session = Depends(get_db)):
    """
    Devuelve todos los errores DTC (códigos OBD-II) asociados a un vehículo del usuario autenticado.

    Args:
        vehiculo_id (int): ID del vehículo para el que se desean consultar los errores.
        usuario (Usuario): Usuario autenticado mediante JWT.
        db (Session): Sesión activa de la base de datos.

    Returns:
        List[ErrorVehiculo]: Lista de errores registrados.

    Raises:
        HTTPException 404: Si no existen errores para ese vehículo.
    """
    errores = db.query(ErrorVehiculo).filter(ErrorVehiculo.vehiculo_id == vehiculo_id).all()
    if not errores:
        raise HTTPException(status_code=404, detail="No se encontraron errores para este vehículo.")
    return errores

@app.post("/crear-informe/{vehiculo_id}")
async def crear_informe(vehiculo_id: int, request: InformeRequest, usuario: Usuario = Depends(obtener_usuario_desde_token), db: Session = Depends(get_db)):
    """
    Crea un informe de errores del vehículo y lo envía al email del cliente.

    Este endpoint genera un enlace único que da acceso a una vista del informe de diagnóstico del vehículo. Se envía un correo al cliente con dicho enlace.

    Args:
        vehiculo_id (int): ID del vehículo del que se desea generar el informe.
        request (InformeRequest): Objeto que contiene el email del cliente.
        usuario (Usuario): Usuario autenticado mediante JWT.
        db (Session): Sesión activa de la base de datos.

    Returns:
        dict: Mensaje de éxito, token generado y enlace de acceso.

    Raises:
        HTTPException 400: Si el email no es válido.
        HTTPException 404: Si el vehículo no pertenece al usuario.
        HTTPException 500: Si ocurre un error al guardar el informe o enviar el correo.
    """
    if not request.email or "@" not in request.email:
        raise HTTPException(status_code=400, detail="Debe proporcionar un email válido para enviar el informe.")

    try:
        vehiculo = db.query(Vehiculo).filter_by(id=vehiculo_id, usuario_id=usuario.id).first()
        if not vehiculo:
            raise HTTPException(status_code=404, detail="No se encontró un vehículo con ese ID para el usuario autenticado.")

        token = str(uuid.uuid4())
        informe = InformeCompartido(
            token=token,
            vehiculo_id=vehiculo.id,
            email_cliente=request.email
        )
        db.add(informe)
        db.commit()

        enlace = f"https://anthonyx82.ddns.net/taller-front/informe/{token}"

        mensaje = MessageSchema(
        subject="Tu informe del vehículo",
        recipients=[request.email],
        body=f"""
        <html>
        <head>
          <style>
            @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600&display=swap');
            body {{
              font-family: 'Poppins', sans-serif;
              background-color: #ffffff;
              color: #333333;
              padding: 20px;
            }}
            .container {{
              max-width: 600px;
              margin: 0 auto;
              border: 1px solid #e0e0e0;
              border-radius: 8px;
              padding: 30px;
              background-color: #fafafa;
            }}
            .titulo {{
              color: #ff6f00;
              font-size: 24px;
              font-weight: 600;
              margin-bottom: 20px;
            }}
            .boton {{
              display: inline-block;
              margin-top: 20px;
              padding: 12px 24px;
              background-color: #ff6f00;
              color: white;
              text-decoration: none;
              border-radius: 6px;
              font-weight: 500;
            }}
            .footer {{
              margin-top: 40px;
              font-size: 12px;
              color: #999;
              text-align: center;
            }}
          </style>
        </head>
        <body>
          <div class="container">
            <div class="titulo">Informe de tu vehículo</div>
            <p>Hola,</p>
            <p>Has solicitado acceder al informe de tu vehículo. Puedes visualizarlo en el siguiente enlace seguro:</p>
            <a href="{enlace}" class="boton">Ver Informe</a>
            <p style="margin-top: 20px;">Gracias por confiar en nosotros.</p>
            <div class="footer">
              Para cualquier duda puede contestar a este correo electronico.
            </div>
          </div>
        </body>
        </html>
        """,
        subtype="html"
        )
        
        # Enviar correo solo si el sistema está configurado
        await fm.send_message(mensaje)

        return {"mensaje": "Informe creado y enviado al email", "token": token, "enlace": enlace}

    except HTTPException:
        raise  # Relevantar tal cual si ya se lanzó arriba
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error al crear el informe: {str(e)}")

# Acceso al informe generado
@app.get("/informe/{token}")
def ver_informe(token: str, db: Session = Depends(get_db)):
    """
    Devuelve los datos del informe generado a partir de un token único.

    Este endpoint permite el acceso público a un informe de diagnóstico de vehículo mediante un enlace con token generado previamente. No requiere autenticación, pero valida que el token sea legítimo.

    Args:
        token (str): Token único del informe generado.

    Returns:
        dict: Información del vehículo (marca, modelo, año, etc.) y lista de errores DTC.

    Raises:
        HTTPException 400: Si el token no es válido o demasiado corto.
        HTTPException 404: Si no se encuentra el informe, el vehículo o los errores asociados.
        HTTPException 500: Si ocurre un error inesperado al procesar la solicitud.
    """
    try:
        if not token or len(token) < 10:
            raise HTTPException(status_code=400, detail="El token proporcionado no es válido.")

        informe = db.query(InformeCompartido).filter_by(token=token).first()
        if not informe:
            raise HTTPException(status_code=404, detail="No se encontró un informe con el token proporcionado.")

        vehiculo = db.query(Vehiculo).filter_by(id=informe.vehiculo_id).first()
        if not vehiculo:
            raise HTTPException(status_code=404, detail="El vehículo relacionado con este informe ya no existe.")

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
            "errores": [e.codigo_dtc for e in errores] if errores else []
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error interno al obtener el informe: {str(e)}")

@app.get("/car-imagery/")
def get_car_image(searchTerm: str):
    """
    Obtiene una URL de imagen representativa de un vehículo usando el término de búsqueda proporcionado.

    Este endpoint consulta la API externa de carimagery.com para devolver la URL de una imagen que coincida con el término (por ejemplo, "Toyota Corolla 2020").

    Args:
        searchTerm (str): Término de búsqueda del vehículo (marca, modelo, año, etc.).

    Returns:
        str: URL de la imagen del vehículo.

    Raises:
        HTTPException 500: Si hay un error al consultar la API externa.
    """
    url = f"https://www.carimagery.com/api.asmx/GetImageUrl?searchTerm={searchTerm}"
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.text
    except requests.RequestException as e:
        raise HTTPException(status_code=500, detail=f"Error al obtener imagen: {e}")

# Endpoint para editar vehículo
@app.put("/editar-vehiculo/{vehiculo_id}")
def editar_vehiculo(vehiculo_id: int, datos: VehiculoEdicion, usuario: Usuario = Depends(obtener_usuario_desde_token), db: Session = Depends(get_db)):
    """
    Actualiza los datos de un vehículo existente del usuario autenticado.

    Args:
        vehiculo_id (int): ID del vehículo a modificar.
        datos_actualizados (VehiculoBase): Nuevos datos del vehículo.
        db (Session): Sesión de base de datos.
        usuario (Usuario): Usuario autenticado.

    Returns:
        dict: Mensaje de éxito.

    Raises:
        HTTPException 404: Si el vehículo no existe o no pertenece al usuario.
    """
    try:
        # Validación básica
        if not datos.vin or len(datos.vin) != 17:
            raise HTTPException(status_code=400, detail="El VIN debe tener exactamente 17 caracteres.")

        vehiculo = db.query(Vehiculo).filter(
            Vehiculo.id == vehiculo_id,
            Vehiculo.usuario_id == usuario.id
        ).first()

        if vehiculo is None:
            raise HTTPException(status_code=404, detail="No se encontró un vehículo con ese ID asociado al usuario.")

        if vehiculo.vin != datos.vin:
            vin_existente = db.query(Vehiculo).filter(Vehiculo.vin == datos.vin).first()
            if vin_existente:
                raise HTTPException(status_code=400, detail="El VIN proporcionado ya está registrado en otro vehículo.")

        # Actualizar campos
        vehiculo.marca = datos.marca
        vehiculo.modelo = datos.modelo
        vehiculo.year = datos.year
        vehiculo.rpm = datos.rpm
        vehiculo.velocidad = datos.velocidad
        vehiculo.vin = datos.vin

        db.commit()
        return {"mensaje": "Vehículo actualizado correctamente"}

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ocurrió un error al editar el vehículo: {str(e)}")

# Endpoint para eliminar vehículo
@app.delete("/eliminar-vehiculo/{vehiculo_id}")
def eliminar_vehiculo(vehiculo_id: int, usuario: Usuario = Depends(obtener_usuario_desde_token), db: Session = Depends(get_db)):
    """
    Elimina un vehículo registrado por el usuario autenticado.

    Args:
        vehiculo_id (int): ID del vehículo a eliminar.
        db (Session): Sesión de base de datos.
        usuario (Usuario): Usuario autenticado mediante JWT.

    Returns:
        dict: Mensaje de éxito.

    Raises:
        HTTPException 404: Si el vehículo no existe o no pertenece al usuario.
    """
    try:
        vehiculo = db.query(Vehiculo).filter(
            Vehiculo.id == vehiculo_id,
            Vehiculo.usuario_id == usuario.id
        ).first()

        if vehiculo is None:
            raise HTTPException(
                status_code=404,
                detail="No se encontró un vehículo con ese ID asociado al usuario."
            )

        # Eliminar errores asociados primero
        errores_eliminados = db.query(ErrorVehiculo).filter(
            ErrorVehiculo.vehiculo_id == vehiculo.id
        ).delete()

        db.delete(vehiculo)
        db.commit()

        return {
            "mensaje": "Vehículo eliminado correctamente",
            "errores_eliminados": errores_eliminados
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Ocurrió un error al eliminar el vehículo: {str(e)}"
        )

# Endpoint de saludo
@app.get("/saludo")
async def saludo():
    """
    Devuelve un mensaje simple para verificar que la API está activa.

    Este endpoint puede utilizarse para pruebas de conectividad o para confirmar que el backend está desplegado correctamente.

    Returns:
        dict: Mensaje de saludo indicando que la API funciona.
    """
    return {"mensaje": "¡La API está funcionando correctamente!"}
