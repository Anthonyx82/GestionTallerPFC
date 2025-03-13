# Proyecto Taller - Monitoreo de Vehículos con OBD-II

## Descripción
Este proyecto consiste en una arquitectura completa para la recolección, almacenamiento y visualización de datos obtenidos desde un vehículo a través del puerto OBD-II. Se compone de:

- **API Backend** (FastAPI + MySQL): Maneja la autenticación y almacenamiento de datos.
- **Cliente OBD-II** (Python): Se conecta al vehículo y envía los datos a la API.
- **Frontend** (Angular): Permite a los usuarios autenticados visualizar la información de sus vehículos.
- **Docker + Traefik**: Para la administración de contenedores y configuración de proxy inverso.

---

## Requisitos Previos

Antes de comenzar, asegúrate de tener instalado:
- [Docker](https://docs.docker.com/get-docker/)
- [Docker Compose](https://docs.docker.com/compose/install/)
- [Python 3.8+](https://www.python.org/downloads/)
- [Node.js y Angular CLI](https://angular.io/cli)

---

## Configuración
### 1. Crear archivo `.env`
Antes de ejecutar el proyecto, crea un archivo `.env` en la raíz con las siguientes variables:

```
# Configuración de la base de datos
MYSQL_DATABASE=talleres
MYSQL_USER=user
MYSQL_PASSWORD=password
MYSQL_ROOT_PASSWORD=rootpassword
DATABASE_URL=mysql+pymysql://user:password@db/talleres

# Clave secreta para JWT
SECRET_KEY=clave-secreta-super-segura
```

### 2. Configurar el Cliente OBD-II
Asegúrate de modificar el script del cliente para reflejar el puerto correcto de tu dispositivo OBD-II. Ejemplo en `cliente.py`:
```python
PORT = "COM3"  # En Windows, cambiar si es necesario
```

---

## Ejecución del Proyecto
### 1. Construcción y ejecución con Docker
Para ejecutar todo el proyecto con Docker y Traefik, usa el siguiente comando:
```sh
docker-compose up -d --build
```
Esto levantará los contenedores de MySQL, la API y el frontend.

### 2. Acceder a los Servicios
- **API Backend**: `https://anthonyx82.ddns.net/taller/api`
- **Frontend Angular**: `https://anthonyx82.ddns.net/taller-front`

### 3. Probar la API
Puedes probar los endpoints con [Postman](https://www.postman.com/) o `curl`:
```sh
curl -X POST "https://anthonyx82.ddns.net/taller/api/login" -H "Content-Type: application/json" -d '{"username":"user", "password":"password"}'
```

---

## Notas Adicionales
- Asegúrate de que el dominio `anthonyx82.ddns.net` esté correctamente configurado.
- Modifica `traefik.yml` si necesitas cambiar la configuración de red.
- Revisa los logs con:
  ```sh
  docker-compose logs -f
  ```

