# 🚗 Proyecto Taller 82

**Proyecto Taller 82** es una solución informática completa para talleres mecánicos. Permite realizar diagnósticos a vehículos mediante conexión OBD, registrar revisiones visuales realizadas por el mecánico, almacenar los datos en la nube del taller y generar informes profesionales en PDF listos para ser enviados al cliente por correo electrónico.

---

## 📌 Descripción general

El sistema está dividido en tres componentes principales:

- 🔧 **Cliente OBD (Python + Tkinter)**: Aplicación gráfica que detecta automáticamente dispositivos conectados (USB/Bluetooth), se comunica con el lector ELM327 y permite realizar la lectura del vehículo. El mecánico puede marcar los puntos revisados (motor, chasis, transmisión y sus partes internas).
- 🧠 **API Backend (FastAPI + MySQL)**: Recibe los datos del cliente OBD, los valida y los almacena en una base de datos. También se encarga de generar el informe en PDF y enviarlo por correo al cliente.
- 🌐 **Frontend (Angular)**: Aplicación web donde se puede registrar e iniciar sesión, visualizar los vehículos revisados y generar el informe desde un modal que permite introducir el email del cliente.

---

## ✅ Funcionalidades principales

- Lectura OBD (VIN, RPM, velocidad, códigos de error)
- Registro visual de revisión (motor, chasis, transmisión y detalles como aceite, filtros, etc.)
- Envío automático de datos al backend
- Almacenamiento en base de datos MySQL
- Frontend responsive para gestión de vehículos
- Generación y envío de PDF con logo del vehículo por correo
- Interfaz clara y moderna tanto en cliente como en frontend

---

## 📄 Contenido del informe PDF

- Logotipo de la marca del vehículo
- Fecha y hora de la revisión
- VIN, RPM, velocidad, códigos de error
- Puntos revisados por el mecánico
- Se genera automáticamente tras cada revisión y se envía al email indicado

---

## 🔐 Acceso al sistema

- Registro y login de usuarios desde el frontend
- Panel de vehículos revisados
- Modal de generación de informe con input para el email del cliente

---

## 🛠️ Tecnologías utilizadas

- **Cliente OBD**: Python, Tkinter, ttkbootstrap, PySerial
- **API Backend**: Python, FastAPI, SQLAlchemy, MySQL
- **Frontend**: Angular 18
- **Infraestructura**: Docker, Docker Compose, Traefik, Let's Encrypt
- **Servidor**: Debian 12

---

## 📘 Documentación del Frontend Angular

El frontend de la aplicación está ubicado en la carpeta `taller-front`. Para detalles específicos sobre la instalación, desarrollo y despliegue del frontend, por favor consulta el archivo README que se encuentra en:

```
taller-front/README.md
```

Este documento contiene instrucciones y detalles específicos para trabajar con la aplicación Angular.

---

## ⚙️ Instalación y despliegue

1. Clona el repositorio:

```bash
git clone https://github.com/Anthonyx82/GestionTallerPFC
cd GestionTallerPFC
````

2. Edita tu archivo `.env` para quitar los datos por defecto.

3. Levanta los contenedores con Docker Compose:

```bash
docker-compose up -d --build
```

4. Accede al frontend desde el navegador en tu dominio (ej. `https://taller-front.web82.es/taller-front/`)

---

## 🌐 Producción con Traefik + Let's Encrypt

* La infraestructura está desplegada en producción con **Traefik** como proxy inverso, usando certificados SSL de Let's Encrypt.
* Todas las rutas están protegidas bajo HTTPS.
* Traefik escucha en la red externa `web` con el entrypoint `websecure`.

---

## 📁 Estructura del proyecto

```
Proyecto-Taller-82/
├── cliente-obd/              # Interfaz OBD en Python
├── backend-api/              # API con FastAPI
├── frontend-angular/         # Frontend Angular
├── docker-compose.yml
└── .env.example
```

---

## 🤝 Contribuciones

Se aceptan contribuciones en las tres partes del proyecto. Puedes:

* Mejorar el cliente (UI, compatibilidad con más dispositivos OBD)
* Ampliar el backend (nuevos endpoints, autenticación avanzada)
* Mejorar el frontend (diseño, filtros, exportaciones)

Para colaborar:

1. Haz un fork del proyecto.
2. Crea una rama para tu funcionalidad.
3. Abre un Pull Request describiendo los cambios.

---

## ❓ Preguntas frecuentes (FAQ)

**¿Puedo usar este sistema en mi propio taller?**
Sí. Solo necesitas un lector OBD ELM327 y configurar tu servidor o usar Docker.

**¿Puedo modificar el cliente para otro conector OBD?**
Sí, el cliente está en Python y es fácilmente adaptable a otros protocolos o dispositivos.

**¿El cliente funciona en Windows, Linux o ambos?**
Funciona perfectamente en ambos. Recomendado Python 3.10 o superior.

**¿Puedo añadir más puntos de revisión o modificar los existentes?**
Sí, tanto las categorías (motor, chasis, transmisión) como sus elementos internos se pueden modificar fácilmente desde el código del cliente.

---

## 📜 Licencia

Este proyecto se publica bajo licencia **MIT**, lo que te permite usarlo, modificarlo y distribuirlo libremente.

---

## 🎓 Créditos

Desarrollado por [Anthonyx82](https://github.com/Anthonyx82) como proyecto de **Fin de Ciclo de Desarrollo de Aplicaciones Multiplataforma** (DAM) en 2025.

🔗 Más información y documentación detallada del proyecto disponible en:
[https://anthonyx82.github.io/html/programacion/taller/taller.html](https://anthonyx82.github.io/html/programacion/taller/taller.html)
