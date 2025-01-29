## Descripción del Proyecto
Este proyecto consiste en una API desarrollada en **Python con FastAPI** para procesar los datos de una **base de datos** y un **escáner OBD-II ELM327**. La API permitirá que una aplicación en **Angular** gestione la información de los vehículos en tiempo real, permitiendo la lectura de datos desde el escáner y el almacenamiento de información relevante en la base de datos.

## Características Principales
- **FastAPI** para una API rápida y eficiente.
- **Base de datos SQL (PostgreSQL/MySQL)** gestionada con SQLAlchemy.
- **Soporte para OBD-II** mediante librerías como `python-OBD`.
- **Operaciones CRUD** para gestionar los datos de los vehículos.
- **Integración con Angular** para consumir la API y mostrar la información al usuario.
- **Seguridad con autenticación JWT** si es necesario.

## Pasos para el Proyecto
1. **Creación de la API y pruebas iniciales**
   - Configurar FastAPI y la base de datos.
   - Implementar las rutas CRUD.
   - Habilitar CORS para la comunicación con Angular.
2. **Prueba del escáner OBD-II**
   - Conectar el escáner OBD-II ELM327.
   - Probar la lectura de datos en tiempo real.
   - Validar los datos recogidos y almacenarlos en la base de datos.
3. **Desarrollo de la aplicación en Angular**
   - Crear la interfaz de usuario.
   - Integrar la API con Angular para mostrar los datos.
   - Implementar funciones de gestión de vehículos y lectura en tiempo real.

## Requisitos del Proyecto
### Tecnologías Utilizadas
- **Backend**: Python, FastAPI, SQLAlchemy
- **Base de Datos**: PostgreSQL / MySQL
- **Frontend**: Angular
- **Hardware**: Escáner OBD-II ELM327

### Instalación y Configuración
#### 1. Clonar el repositorio:
```sh
git clone <URL_DEL_REPO>
cd <NOMBRE_DEL_PROYECTO>
```

#### 2. Configurar un entorno virtual y las dependencias:
```sh
python -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate
pip install -r requirements.txt
```

#### 3. Configurar variables de entorno:
Crea un archivo `.env` con los datos de conexión a la base de datos y configuración del OBD-II.

#### 4. Ejecutar la API:
```sh
uvicorn main:app --reload
```

#### 5. Probar la API:
Abre en el navegador: `http://127.0.0.1:8000/docs` para acceder a la documentación generada automáticamente.

---

Con esta estructura, el proyecto tendrá una API funcional y una aplicación en Angular que interactuará con ella para gestionar la información de los vehículos y los datos obtenidos del escáner OBD-II.

