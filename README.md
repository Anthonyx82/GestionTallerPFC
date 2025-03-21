# Proyecto Taller

## Descripción
Este proyecto es una plataforma que permite la recopilación y visualización de datos OBD-II de un vehículo. La arquitectura incluye una API desarrollada en FastAPI, un cliente en Python para la conexión con el puerto OBD-II y un frontend en Angular. Todo el proyecto está dockerizado y configurado con Traefik como proxy inverso.

## Características
- **Monitoreo de datos del vehículo**: RPM, velocidad, marca, modelo y año.
- **Autenticación segura**: Uso de tokens JWT.
- **Interfaz web en Angular**: Visualización de la información del vehículo.
- **Despliegue con Docker y Traefik**: Infraestructura lista para producción.

## Configuración y Ejecución
### Prerrequisitos
Asegúrate de tener instalado:
- Docker & Docker Compose
- Un dispositivo OBD-II compatible
- Python 3.x y Node.js (para desarrollo local)

### Variables de Entorno
Antes de iniciar, configura un archivo `.env` con las siguientes variables:
```env
MYSQL_DATABASE=talleres
MYSQL_USER=user
MYSQL_PASSWORD=password
MYSQL_ROOT_PASSWORD=rootpassword
DATABASE_URL=mysql+pymysql://user:password@db/talleres
```

### Despliegue del Proyecto
Ejecuta el siguiente comando para iniciar todos los servicios:
```sh
docker-compose up -d --build
```
Esto lanzará:
- **Base de datos MySQL**
- **API FastAPI**
- **Cliente Angular**

### Acceso
- **API Backend:** `https://anthonyx82.ddns.net/taller/api`
- **Frontend Angular:** `https://anthonyx82.ddns.net/taller-front`

## Contribución
Las contribuciones son bienvenidas. Para reportar errores o proponer mejoras, abre un issue en este repositorio.

## Contacto
- **Autor:** Antonio Martín Sosa  
- **Email:** [antoniomartinmanzanares2004@gmail.com](mailto:antoniomartinmanzanares2004@gmail.com)  
- **LinkedIn:** [linkedin.com/in/antoniomartinsosa](https://www.linkedin.com/in/antoniomartinsosa)  
- **Portfolio Web:** [anthonyx82.github.io](https://anthonyx82.github.io)  

