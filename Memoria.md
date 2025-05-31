# Proyecto Taller 82

## 1. Portada

**Título del proyecto:** Proyecto Taller 82
**Nombre del autor:** Antonio Martín Sosa
**Ciclo formativo:** Desarrollo de Aplicaciones Web
**Centro educativo:** IES Castelar
**Fecha de entrega:** 1 de junio de 2025

## 2. Análisis de contexto

### a. Detección de necesidades

Durante mi experiencia con talleres mecánicos, detecté una carencia significativa en la información que se proporciona al cliente y en la ausencia de procedimientos claros y estructurados para realizar operaciones paso a paso. Esto genera confusión, pérdida de tiempo y errores en los procesos. Sobre todo en talleres mecanicos mas humildes o baratos.

### b. Estudio de mercado

**Empresas objetivo:** talleres multimarca, concesionarios, talleres móviles, pequeños talleres independientes.
**Beneficios frente a la competencia:**

* Mayor simplicidad y usabilidad.
* Reducción de costes frente a software comercial.
* Adaptado a talleres pequeños con recursos limitados.
* Gestión clara y digitalizada de revisiones, clientes y vehículos.

### c. Coste de implantación (estimación)

* Servidor dedicado (gasto unico): 500€
* Dominio + DNS dinámico: 15€ (anual)
* Certificados SSL: 0€ (Let’s Encrypt)
* Equipamiento: uso de hardware ya existente (PC Xeon, lector ELM327)
* Coste total estimado: < 600€ para puesta en marcha en un entorno real pequeño-mediano. Y a partir de hay solo con 15€ al año para mantener el dominio.

### d. Plataforma de ejecución

* **Backend y Frontend:** ejecutables en cualquier SO compatible con Docker.
* **Cliente OBD:** ejecutable solo en Windows por dependencias con puertos COM y librerías gráficas (Tkinter + ttkbootstrap).
* **Requisitos mínimos:**

  * Cliente:Portatil basico, Windows, puerto serie o Bluetooth.
  * Servidor: Docker, 4 GB RAM mínimo, red con acceso público.

### e. Protección de datos

El sistema almacena datos personales (nombre, email, matrícula, etc.). Para cumplir con el RGPD:

* El acceso está protegido con usuario/contraseña.
* Se solicita consentimiento explícito para el tratamiento de datos.
* El backend implementa medidas de seguridad y cifrado.

### f. Metodología de desarrollo

* **Organización:** desarrollo por prioridades. Primero el servidor (entorno Docker), luego backend, frontend y cliente Python.
* **Fases del desarrollo:**

  1. Infraestructura y despliegue con Traefik y Docker Compose.
  2. API REST con FastAPI y base de datos MySQL.
  3. Frontend con Angular para visualizar y gestionar vehículos.
  4. Cliente gráfico Python para lectura OBD.

### g. Esquema de base de datos

```python
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
    errores = relationship("ErrorVehiculo", back_populates="vehiculo", cascade="all, delete-orphan")
    
    # Relación con InformeCompartido (uno a muchos)
    informes_compartidos = relationship("InformeCompartido", back_populates="vehiculo", cascade="all, delete-orphan")


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

    # Relación con Vehiculo (muchos a uno)
    vehiculo = relationship("Vehiculo", back_populates="informes_compartidos")
```

Relaciones:

* Un usuario tiene muchos vehículos.
* Un vehículo puede tener muchos errores y muchos informes compartidos.

## 3. Organización de la ejecución

### a. Planning marzo–junio

* **Marzo:** configuración del servidor, Traefik, Docker Compose, BBDD MySQL, Monitorizacion y Mantenimiento
* **Abril:** desarrollo del backend (FastAPI), endpoints, base de datos
* **Mayo:** frontend Angular, cliente Python, pruebas de integración
* **Última semana de mayo:** pruebas finales, documentación, empaquetado

### b. Recursos utilizados

* Servidor físico con procesador Intel Xeon
* Cliente con lector ELM327 (USB y Bluetooth)
* Docker y Docker Compose
* Traefik como proxy inverso
* Herramientas: FastAPI, Angular 18, Python 3.11, MySQL, Glances, Jaeger, Kuma, etc.

## 4. Anexos

### 1. Manual de usuario

Se desarrollará paso a paso con capturas. Incluirá:

* Inicio de sesión y registro
* Gestión de vehículos
* Visualización de revisiones e informes
* Uso del cliente OBD (conexión, escaneo, envío de datos)

### 2. Manual del programador

* Estructura modular dividida por responsabilidades:

  * `taller-back-api/`: API y cliente Python
  * `taller-front/`: Aplicación Angular con interfaz de gestión
  * `docker-compose.yml`: define el entorno de despliegue completo
  * Uso de imágenes base propias (Node, Python) en lugar de imágenes predefinidas
* Uso de UUIDs para compartir informes por token

### 3. Bibliografía

* Documentación oficial de:

  * [FastAPI](https://fastapi.tiangolo.com/)
  * [Uvicorn](https://www.uvicorn.org/)
  * [SQLAlchemy](https://docs.sqlalchemy.org/)
  * [PyMySQL](https://pymysql.readthedocs.io/en/latest/)
  * [pyserial](https://pyserial.readthedocs.io/en/latest/)
  * [requests](https://docs.python-requests.org/en/latest/)
  * [tkinter](https://docs.python.org/3/library/tkinter.html)
  * [PyInstaller](https://pyinstaller.readthedocs.io/en/stable/)
  * [python-jose](https://python-jose.readthedocs.io/en/latest/)
  * [passlib](https://passlib.readthedocs.io/en/stable/)
  * [fastapi-mail](https://github.com/sabuhish/fastapi-mail)
  * [pydantic](https://pydantic.dev/)
  * [python-dotenv](https://pypi.org/project/python-dotenv/)
  * [Angular](https://angular.io/)
  * [Angular Material](https://material.angular.io/)
  * [html2pdf.js](https://github.com/eKoopmans/html2pdf.js)
  * [jsPDF](https://github.com/parallax/jsPDF)
  * [RxJS](https://rxjs.dev/)
  * [TypeScript](https://www.typescriptlang.org/)
  * [MySQL 5.7](https://dev.mysql.com/doc/refman/5.7/en/)
  * [Docker](https://docs.docker.com/)
  * [Nginx](https://nginx.org/en/docs/)
  * [Traefik](https://doc.traefik.io/traefik/)
  * [Glances](https://glances.readthedocs.io/en/develop/)
  * [Kuma](https://github.com/louislam/uptime-kuma/wiki)
  * [Jaeger](https://www.jaegertracing.io/docs/1.6/getting-started/)
  * [Prometheus](https://doc.traefik.io/traefik/observability/metrics/prometheus/)
  * [Debian 12](https://www.debian.org/index.es.html)

* ChatGPT para resolver dudas técnicas y generar ejemplos de código

---

### Estructura del proyecto

```
Proyecto Taller 82/
├── .env
├── .gitignore
├── docker-compose.yml
├── Memoria.MD
├── README.md
│
├── taller-back-api/
│   ├── images/
│   ├── client.py
│   ├── Dockerfile
│   ├── main.py
│   └── requirements.txt
│
├── taller-front/
    ├── .vscode/
    ├── node_modules/
    ├── public/
    ├── src/
    ├── .editorconfig
    ├── .gitignore
    ├── angular.json
    ├── Dockerfile
    ├── nginx.conf
    ├── package.json
    ├── package-lock.json
    ├── README.md
    ├── tsconfig.app.json
    ├── tsconfig.json
    └── tsconfig.spec.json
```