Configuración del Proyecto
==========================

En esta sección se describe la configuración general del proyecto, desde la conexión a la base de datos hasta los parámetros de correo y seguridad. Toda la configuración se basa en variables de entorno que puedes definir en un archivo `.env` o directamente en tu entorno.

.. contents::
   :local:
   :depth: 2

Configuración de Entorno
------------------------

Para que la aplicación funcione correctamente, debes definir las siguientes variables de entorno (pueden estar en un archivo `.env`):

.. list-table::
   :header-rows: 1
   :widths: 20 60

   * - Variable                  - Descripción
   * - ``DATABASE_URL``          - URL de conexión a la base de datos MySQL (p. ej.: ``mysql+pymysql://user:password@host:port/dbname``).
   * - ``MAIL_USERNAME``         - Usuario para SMTP (FastAPI-Mail).
   * - ``MAIL_PASSWORD``         - Contraseña para SMTP.
   * - ``MAIL_FROM``             - Correo desde el cual se enviarán los mensajes.
   * - ``MAIL_PORT``             - Puerto SMTP (por defecto: 587).
   * - ``MAIL_SERVER``           - Servidor SMTP (p. ej.: ``smtp.gmail.com``).
   * - ``MAIL_STARTTLS``         - ``True`` si se debe usar STARTTLS.
   * - ``MAIL_SSL_TLS``          - ``True`` si se debe usar SSL/TLS.
   * - ``USE_CREDENTIALS``       - ``True`` si se usan las credenciales definidas.
   * - ``VALIDATE_CERTS``        - ``True`` para validar certificados SSL.
   * - ``SECRET_KEY``            - Clave secreta para firmar JWT.
   * - ``ALGORITHM``             - Algoritmo JWT (p. ej.: ``HS256``).
   * - ``ACCESS_TOKEN_EXPIRE_MINUTES`` - Tiempo de expiración del token (en minutos).

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

## endpoints.rst

```rst
Endpoints de la API
===================

En este documento se describen todos los endpoints disponibles en la API, organizados por funcionalidad: autenticación, gestión de vehículos, errores y generación de informes.

.. contents::
   :local:
   :depth: 2

Autenticación y Usuarios
------------------------

### Registro de Usuario

.. http:post:: /register

   Registra un nuevo usuario en la base de datos.  

   **Request Body** (``UsuarioRegistro``):

   - ``username`` (string, obligatorio): nombre de usuario (mínimo 3 caracteres).
   - ``password`` (string, obligatorio): contraseña (mínimo 6 caracteres).

   **Responses**:

   - ``200 OK``  
     ```json
     {
       "mensaje": "Usuario registrado correctamente"
     }
     ```
   - ``400 Bad Request``:  
     - Cuando no se cumple la longitud mínima de ``username`` o ``password``.  
     - O si el ``username`` ya existe.

### Login / Obtención de Token

.. http:post:: /login

   Autentica al usuario y devuelve un token JWT.

   **Request Body** (``UsuarioLogin``):

   - ``username`` (string, obligatorio): nombre de usuario.
   - ``password`` (string, obligatorio): contraseña.

   **Responses**:

   - ``200 OK``  
     ```json
     {
       "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
       "token_type": "bearer"
     }
     ```
   - ``400 Bad Request``:  
     - Si ``username`` o ``password`` no cumplen con mínimos de longitud.
   - ``401 Unauthorized``:  
     - Usuario no registrado o contraseña incorrecta.
   - ``500 Internal Server Error``:  
     - Error al generar el token.

Gestión de Vehículos
--------------------

Todos los endpoints de esta sección requieren autenticación previa (token JWT en Header: ``Authorization: Bearer <token>``).

### Guardar Vehículo

.. http:post:: /guardar-vehiculo/

   Crea un nuevo vehículo asociado al usuario autenticado.

   **Request Body** (``VehiculoRegistro``):

   - ``marca`` (string, obligatorio)
   - ``modelo`` (string, obligatorio)
   - ``year`` (integer, obligatorio)
   - ``rpm`` (integer, obligatorio)
   - ``velocidad`` (integer, obligatorio)
   - ``vin`` (string de longitud 17, obligatorio)
   - ``revision`` (object JSON, obligatorio)  
     - Ejemplo:  
       ```json
       {
         "tipo": "General",
         "fecha": "2025-06-05",
         "observaciones": "Cambio de frenos"
       }
       ```

   **Responses**:

   - ``200 OK``  
     ```json
     {
       "mensaje": "Vehículo guardado correctamente",
       "id": 42
     }
     ```
   - ``400 Bad Request``:  
     - VIN inválido o campos obligatorios vacíos.  
     - VIN duplicado.
   - ``401 Unauthorized``:  
     - Token no válido o expirado.
   - ``500 Internal Server Error``:  
     - Error inesperado al guardar en la base de datos.

### Listar Vehículos del Usuario

.. http:get:: /mis-vehiculos/

   Obtiene la lista de vehículos registrados por el usuario autenticado.

   **Parameters**:  
   - No requiere parámetros en la URL.

   **Responses**:

   - ``200 OK``  
     Si hay vehículos registrados:
     ```json
     {
       "vehiculos": [
         {
           "id": 1,
           "marca": "Toyota",
           "modelo": "Corolla",
           "year": 2020,
           "rpm": 1500,
           "velocidad": 80,
           "vin": "JTDBL40E799017833",
           "revision": "{\"tipo\": \"General\", \"fecha\": \"2025-06-05\"}",
           "usuario_id": 5
         },
         ...
       ]
     }
     ```
     Si no hay vehículos:
     ```json
     {
       "mensaje": "No hay vehículos registrados para este usuario.",
       "vehiculos": []
     }
     ```
   - ``401 Unauthorized``  
     - Token no válido o expirado.
   - ``500 Internal Server Error``  
     - Error interno al consultar la base de datos.

### Obtener Vehículo Específico

.. http:get:: /mis-vehiculos/{vehiculo_id}

   Recupera la información de un único vehículo registrado por el usuario.

   **URL Parameters**:

   - ``vehiculo_id`` (integer, obligatorio): ID del vehículo.

   **Responses**:

   - ``200 OK``  
     ```json
     {
       "id": 1,
       "marca": "Toyota",
       "modelo": "Corolla",
       "year": 2020,
       "rpm": 1500,
       "velocidad": 80,
       "vin": "JTDBL40E799017833",
       "revision": "{\"tipo\": \"General\", \"fecha\": \"2025-06-05\"}",
       "usuario_id": 5
     }
     ```
   - ``404 Not Found``  
     - Vehículo no existe o no pertenece al usuario.
   - ``401 Unauthorized``  
     - Token no válido o expirado.

### Editar Vehículo

.. http:put:: /editar-vehiculo/{vehiculo_id}

   Actualiza los datos de un vehículo existente.

   **URL Parameters**:

   - ``vehiculo_id`` (integer, obligatorio): ID del vehículo.

   **Request Body** (``VehiculoEdicion``):

   - ``marca`` (string, obligatorio)
   - ``modelo`` (string, obligatorio)
   - ``year`` (integer, obligatorio)
   - ``rpm`` (integer, obligatorio)
   - ``velocidad`` (integer, obligatorio)
   - ``vin`` (string de longitud 17, obligatorio)

   **Responses**:

   - ``200 OK``  
     ```json
     {
       "mensaje": "Vehículo actualizado correctamente"
     }
     ```
   - ``400 Bad Request``  
     - VIN inválido o ya registrado en otro vehículo.
   - ``404 Not Found``  
     - Vehículo no existe o no pertenece al usuario.
   - ``401 Unauthorized``  
     - Token no válido o expirado.
   - ``500 Internal Server Error``  
     - Error interno al actualizar.

### Eliminar Vehículo

.. http:delete:: /eliminar-vehiculo/{vehiculo_id}

   Elimina un vehículo y sus errores asociados.

   **URL Parameters**:

   - ``vehiculo_id`` (integer, obligatorio): ID del vehículo.

   **Responses**:

   - ``200 OK``  
     ```json
     {
       "mensaje": "Vehículo eliminado correctamente",
       "errores_eliminados": 3
     }
     ```
     donde ``errores_eliminados`` es la cantidad de registros de errores borrados en cascada.
   - ``404 Not Found``  
     - Vehículo no existe o no pertenece al usuario.
   - ``401 Unauthorized``  
     - Token no válido o expirado.
   - ``500 Internal Server Error``  
     - Error interno al eliminar.

Gestión de Errores OBD-II
-------------------------

Todos los endpoints de esta sección requieren autenticación previa.

### Guardar Errores de Vehículo

.. http:post:: /guardar-errores/

   Registra una lista de códigos DTC (errores OBD-II) para un vehículo específico.

   **Request Body** (``ErrorVehiculoRegistro``):

   - ``vehiculo_id`` (integer, obligatorio)
   - ``codigo_dtc`` (array[string], obligatorio):  
     Lista de códigos OBD-II (p. ej.: ``["P0301","P0420","P0133"]``).

   **Validaciones**:

   - ``vehiculo_id`` debe ser entero positivo.
   - ``codigo_dtc`` no puede estar vacío ni contener valores en blanco.
   - No se permiten códigos duplicados en la misma lista.
   - El vehículo debe pertenecer al usuario autenticado.

   **Responses**:

   - ``200 OK``  
     ```json
     {
       "mensaje": "Errores del vehículo guardados correctamente"
     }
     ```
   - ``400 Bad Request``  
     - Formato o datos inválidos (ID negativo, lista vacía, duplicados, etc.).
   - ``404 Not Found``  
     - Vehículo no encontrado o no pertenece al usuario.
   - ``401 Unauthorized``  
     - Token no válido o expirado.
   - ``500 Internal Server Error``  
     - Error al guardar en la base de datos.

### Obtener Errores de un Vehículo

.. http:get:: /mis-errores/{vehiculo_id}

   Obtiene todos los errores DTC registrados para un vehículo del usuario autenticado.

   **URL Parameters**:

   - ``vehiculo_id`` (integer, obligatorio)

   **Responses**:

   - ``200 OK``  
     ```json
     ["P0301", "P0420", "P0133"]
     ```
   - ``404 Not Found``  
     - No hay errores registrados para ese vehículo o el vehículo no existe.
   - ``401 Unauthorized``  
     - Token no válido o expirado.
   - ``500 Internal Server Error``  
     - Error interno al consultar la base de datos.

Generación y Consulta de Informes
---------------------------------

### Crear Informe para un Vehículo

.. http:post:: /crear-informe/{vehiculo_id}

   Genera un informe HTML con todos los errores de un vehículo y lo envía por correo al cliente. Se crea un token único para acceso público al informe.

   **URL Parameters**:

   - ``vehiculo_id`` (integer, obligatorio)

   **Request Body** (``InformeRequest``):

   - ``email`` (string, obligatorio): email del cliente (debe contener “@”).

   **Flujo**:

   1. Se valida que el vehículo exista y pertenezca al usuario autenticado.
   2. Se genera un token UUID único y se guarda en la tabla ``informes_compartidos``.
   3. Se construye un correo HTML con un botón que apunta a ``/informe/{token}``.
   4. Se envía el correo usando FastAPI-Mail.

   **Responses**:

   - ``200 OK``  
     ```json
     {
       "mensaje": "Informe creado y enviado al email",
       "token": "550e8400-e29b-41d4-a716-446655440000",
       "enlace": "https://tudominio.com/taller-front/informe/550e8400-e29b-41d4-a716-446655440000"
     }
     ```
   - ``400 Bad Request``  
     - Email inválido (no contiene “@”).
   - ``404 Not Found``  
     - Vehículo no existe o no pertenece al usuario.
   - ``401 Unauthorized``  
     - Token no válido o expirado.
   - ``500 Internal Server Error``  
     - Error al guardar el informe o al enviar el correo.

### Ver Informe Público

.. http:get:: /informe/{token}

   Permite a cualquier usuario (no autenticado) ver el informe de diagnóstico de un vehículo, siempre y cuando se tenga el token correcto.

   **URL Parameters**:

   - ``token`` (string, obligatorio, longitud mínima: 10)

   **Flujo**:

   1. Se valida el largo del token.
   2. Se busca el registro en ``informes_compartidos``.
   3. Se obtienen los datos del vehículo y todos los códigos DTC asociados.
   4. Se devuelve un JSON con la información del vehículo y la lista de errores.

   **Responses**:

   - ``200 OK``  
     ```json
     {
       "vehiculo": {
         "marca": "Toyota",
         "modelo": "Corolla",
         "year": 2020,
         "vin": "JTDBL40E799017833",
         "rpm": 1500,
         "velocidad": 80,
         "revision": "{\"tipo\": \"General\", \"fecha\": \"2025-06-05\"}"
       },
       "errores": ["P0301", "P0420"]
     }
     ```
   - ``400 Bad Request``  
     - Token inválido (longitud < 10).
   - ``404 Not Found``  
     - Token no encontrado, vehículo no existe o ya no tiene errores asociados.
   - ``500 Internal Server Error``  
     - Error interno al procesar la solicitud.

Servicio de Imágenes de Vehículo
--------------------------------

### Obtener URL de Imagen de Vehículo

.. http:get:: /car-imagery/

   Recupera una URL de imagen representativa usando la API externa de **carimagery.com**.

   **Query Parameters**:

   - ``searchTerm`` (string, obligatorio): término de búsqueda (marca, modelo, año, etc.).

   **Ejemplo de uso**:

   .. sourcecode:: bash

      curl -X GET "https://tudominio.com/taller/api/car-imagery/?searchTerm=Toyota%20Corolla%202020"

   **Responses**:

   - ``200 OK``  
     - Devuelve el contenido XML o texto plano con la URL de la imagen.
   - ``500 Internal Server Error``  
     - Error al consultar la API externa.

Endpoint de Prueba / Salud
--------------------------

.. http:get:: /saludo

   Endpoint simple para verificar la conectividad y que la API está funcionando.

   **Responses**:

   - ``200 OK``  
     ```json
     {
       "mensaje": "¡La API está funcionando correctamente!"
     }
     ```
