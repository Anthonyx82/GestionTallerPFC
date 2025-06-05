Introducción
============

Bienvenido a la documentación técnica de la API de gestión de vehículos e informes de diagnóstico.

Este sistema permite registrar usuarios, añadir vehículos, capturar errores OBD-II (DTC), generar informes personalizados y compartirlos mediante enlaces públicos enviados por correo electrónico.

Tecnologías utilizadas:

- **FastAPI**: para la creación de endpoints RESTful modernos.
- **SQLAlchemy**: ORM para gestión de base de datos relacional.
- **Pydantic**: validación de datos.
- **JWT (JSON Web Tokens)**: autenticación y autorización.
- **FastAPI-Mail**: envío de correos con informes.
- **MySQL**: base de datos principal.
- **Sphinx**: generación de esta documentación.

Esta documentación se divide en las siguientes secciones:

- Descripción de los endpoints disponibles.
- Modelos de datos (ORM y Pydantic).
- Configuración del sistema (DB, correo, JWT, etc.).