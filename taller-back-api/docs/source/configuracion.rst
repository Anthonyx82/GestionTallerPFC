Configuración del Proyecto
===========================

Este proyecto cuenta con una configuración flexible basada en variables de entorno y herramientas integradas para seguridad y mensajería.

Base de Datos
-------------

- URL: definida en `DATABASE_URL`.
- Motor: MySQL con PyMySQL.
- ORM: SQLAlchemy.
- Sesiones: `SessionLocal()`.

Correo Electrónico
------------------

- Envío mediante `FastAPI-Mail`.
- Configuración por variables de entorno:
  - Usuario, contraseña, puerto, servidor SMTP.
- Soporta TLS y SSL.

Seguridad
---------

- `JWT`: para autenticación de usuarios.
- `bcrypt`: para encriptar contraseñas.
- `OAuth2PasswordBearer`: extracción automática del token.

Dependencias reutilizables
--------------------------

- `get_db()`: genera una sesión DB por request.
- `obtener_usuario_actual()`: extrae el usuario desde el token JWT.

.. automodule:: main
   :members: get_db
