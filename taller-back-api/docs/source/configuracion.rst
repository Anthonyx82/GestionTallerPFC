==========================
Configuración del Proyecto
==========================

En esta sección se describe la configuración general del proyecto, desde la conexión a la base de datos hasta los parámetros de correo y seguridad. Toda la configuración se basa en variables de entorno que puedes definir en un archivo `.env` o directamente en tu entorno.

Configuración de Entorno
---------------------

Para que la aplicación funcione correctamente, debes definir las siguientes variables de entorno (pueden estar en un archivo `.env`):

.. list-table::
   :header-rows: 1
   :widths: 20 60

   * - Variable
     - Descripción
   * - ``DATABASE_URL``
     - URL de conexión a la base de datos MySQL (p. ej.: ``mysql+pymysql://user:password@host:port/dbname``).
   * - ``MAIL_USERNAME``
     - Usuario para SMTP (FastAPI-Mail).
   * - ``MAIL_PASSWORD``
     - Contraseña para SMTP.
   * - ``MAIL_FROM``
     - Correo desde el cual se enviarán los mensajes.
   * - ``MAIL_PORT``
     - Puerto SMTP (por defecto: 587).
   * - ``MAIL_SERVER``
     - Servidor SMTP (p. ej.: ``smtp.gmail.com``).
   * - ``MAIL_STARTTLS``
     - ``True`` si se debe usar STARTTLS.
   * - ``MAIL_SSL_TLS``
     - ``True`` si se debe usar SSL/TLS.
   * - ``USE_CREDENTIALS``
     - ``True`` si se usan las credenciales definidas.
   * - ``VALIDATE_CERTS``
     - ``True`` para validar certificados SSL.
   * - ``SECRET_KEY``
     - Clave secreta para firmar JWT.
   * - ``ALGORITHM``
     - Algoritmo JWT (p. ej.: ``HS256``).
   * - ``ACCESS_TOKEN_EXPIRE_MINUTES``
     - Tiempo de expiración del token (en minutos).

Base de Datos
-------------

- **URL**: obtenida desde ``DATABASE_URL``.
- **Motor**: MySQL con el driver PyMySQL.
- **ORM**: SQLAlchemy.
- **Sesiones**: se genera con ``SessionLocal()`` por request.

Declaración en código (``main.py``):

.. code-block:: python

   # Configuración de la base de datos
   DATABASE_URL = os.getenv("DATABASE_URL", "mysql+pymysql://user:password@db/talleres")
   engine = create_engine(DATABASE_URL)
   SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
   Base = declarative_base()

Correo Electrónico
------------------

La aplicación utiliza **FastAPI-Mail** para el envío de correos electrónicos (por ejemplo, para enviar informes generados).  

- Se configuran las credenciales y parámetros de SMTP en la clase ``ConnectionConfig``.
- Se soporta TLS y SSL según las variables ``MAIL_STARTTLS`` y ``MAIL_SSL_TLS``.
- Ejemplo de uso en ``main.py``:

.. code-block:: python

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

Seguridad
---------

La autenticación y autorización se basan en JWT. A continuación se detallan los componentes clave:

- **SECRET_KEY**: clave secreta para firmar y verificar tokens JWT. Defínela en la variable de entorno ``SECRET_KEY`` o déjala en el código como fallback.
- **ALGORITHM**: algoritmo para JWT, por defecto ``HS256``.
- **ACCESS_TOKEN_EXPIRE_MINUTES**: tiempo de expiración del token (en minutos). Se obtiene de la variable de entorno ``ACCESS_TOKEN_EXPIRE_MINUTES`` o usa 300 por defecto.

- Para hashear contraseñas se utiliza ``bcrypt`` a través de ``passlib``:

  .. code-block:: python

     pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

- Para extraer el token de las peticiones, se usa ``OAuth2PasswordBearer(tokenUrl="login")``.

Flujo de autenticación en ``main.py``:

1. **Registro**: el endpoint ``/register`` recibe un ``UsuarioRegistro`` (username + password), hashea la contraseña y la almacena.
2. **Login**: el endpoint ``/login`` recibe un ``UsuarioLogin``, verifica credenciales y, si es válido, genera un JWT con ``crear_token``.
3. **Dependencia ``obtener_usuario_desde_token``**: se encarga de decodificar el JWT, extraer el ``sub`` (username) y cargar el usuario desde la base de datos. Si no encuentra usuario o el token está expirado, lanza ``HTTPException(401)``.

Dependencias reutilizables
--------------------------

A continuación se listan las funciones que puedes reusar en tus endpoints:

.. automodule:: main
   :members: get_db, obtener_usuario_desde_token
   :undoc-members:

- ``get_db()``:  
  - Abre una sesión de base de datos (SQLAlchemy) y la cierra automáticamente al salir del contexto.
  - Uso típico:
  
    .. code-block:: python

       @app.get("/ruta_ejemplo")
       def ejemplo(db: Session = Depends(get_db)):
           # db es una sesión válida
           ...

- ``obtener_usuario_desde_token``:  
  - Extrae el token JWT del encabezado ``Authorization`` y devuelve la instancia de ``Usuario`` correspondiente.
  - Uso típico:

    .. code-block:: python

       @app.get("/ruta_protegida")
       def protegida(usuario: Usuario = Depends(obtener_usuario_desde_token)):
           # usuario es el objeto Usuario autenticado
           ...

---