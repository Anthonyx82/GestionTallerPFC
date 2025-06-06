===================
Endpoints de la API
===================

En este documento se describen todos los endpoints disponibles en la API, organizados por funcionalidad. Para cada ruta se indica método HTTP, URL, esquema de datos de entrada/salida, validaciones y ejemplos de uso.

Autenticación y Usuarios
------------------------

Registro de Usuario
~~~~~~~~~~~~~~~~~~~

.. http:post:: /register

   Registra un nuevo usuario en la base de datos.

   **Request Body** (``UsuarioRegistro``):

   - ``username`` (string, obligatorio, mínimo 3 caracteres)  
   - ``password`` (string, obligatorio, mínimo 6 caracteres)  

   **Ejemplo**:

   .. code-block:: http

      POST /register HTTP/1.1
      Host: api.ejemplo.com
      Content-Type: application/json

      {
        "username": "juanperez",
        "password": "secreto123"
      }

   **Responses**:

   - **200 OK**

     .. code-block:: json

        {
          "mensaje": "Usuario registrado correctamente"
        }

   - **400 Bad Request**

     - Cuando ``username`` o ``password`` no cumplen longitud mínima.  
     - Si el ``username`` ya existe.

     .. code-block:: json

        {
          "detail": "El usuario ya existe"
        }

   - **500 Internal Server Error**

     - Error inesperado al guardar en la base de datos.

Login / Obtención de Token
~~~~~~~~~~~~~~~~~~~~~~~~~~

.. http:post:: /login

   Autentica al usuario y devuelve un token JWT.

   **Request Body** (``UsuarioLogin``):

   - ``username`` (string, obligatorio)  
   - ``password`` (string, obligatorio)  

   **Ejemplo**:

   .. code-block:: http

      POST /login HTTP/1.1
      Host: api.ejemplo.com
      Content-Type: application/json

      {
        "username": "juanperez",
        "password": "secreto123"
      }

   **Responses**:

   - **200 OK**

     .. code-block:: json

        {
          "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
          "token_type": "bearer"
        }

   - **400 Bad Request**

     - Si ``username`` o ``password`` no cumplen requisitos (longitud).

     .. code-block:: json

        {
          "detail": "Las credenciales no cumplen los requisitos mínimos"
        }

   - **401 Unauthorized**

     - Usuario no registrado o contraseña incorrecta.

     .. code-block:: json

        {
          "detail": "Credenciales inválidas"
        }

   - **500 Internal Server Error**

     - Error al generar el token.

Gestión de Vehículos
--------------------

.. note::

   Todos los endpoints de esta sección requieren que el header ``Authorization: Bearer <token>`` contenga un JWT válido.

Guardar Vehículo
~~~~~~~~~~~~~~~~

.. http:post:: /guardar-vehiculo/

   Crea un nuevo vehículo y lo asocia al usuario autenticado.

   **Request Body** (``VehiculoRegistro``):

   - ``marca`` (string, obligatorio)  
   - ``modelo`` (string, obligatorio)  
   - ``year`` (integer, obligatorio, p. ej., 2023)  
   - ``rpm`` (integer, obligatorio)  
   - ``velocidad`` (integer, obligatorio)  
   - ``vin`` (string, obligatorio, longitud = 17)  
   - ``revision`` (dict JSON, obligatorio)  
     - ``tipo`` (string, obligatorio)  
     - ``fecha`` (string, formato ISO YYYY-MM-DD, obligatorio)  
     - ``observaciones`` (string, opcional)

   **Ejemplo**:

   .. code-block:: http

      POST /guardar-vehiculo/ HTTP/1.1
      Host: api.ejemplo.com
      Authorization: Bearer eyJhbGciOi...
      Content-Type: application/json

      {
        "marca": "Ford",
        "modelo": "Focus",
        "year": 2020,
        "rpm": 1200,
        "velocidad": 60,
        "vin": "1HGCM82633A004352",
        "revision": {
          "tipo": "General",
          "fecha": "2025-06-05",
          "observaciones": "Cambio aceite"
        }
      }

   **Responses**:

   - **200 OK**

     .. code-block:: json

        {
          "mensaje": "Vehículo guardado correctamente",
          "id": 10
        }

   - **400 Bad Request**

     - VIN inválido (no 17 caracteres) o campos faltantes.  
     - VIN duplicado.

     .. code-block:: json

        {
          "detail": "VIN inválido o ya registrado"
        }

   - **401 Unauthorized**

     - Token ausente, inválido o expirado.

     .. code-block:: json

        {
          "detail": "No autenticado"
        }

   - **500 Internal Server Error**

     - Error interno al persistir datos.

Listar Vehículos del Usuario
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. http:get:: /mis-vehiculos/

   Recupera todos los vehículos asociados al usuario autenticado.

   **Headers**:

   - ``Authorization: Bearer <token>`` (string, obligatorio)

   **Ejemplo**:

   .. code-block:: http

      GET /mis-vehiculos/ HTTP/1.1
      Host: api.ejemplo.com
      Authorization: Bearer eyJhbGciOi...

   **Responses**:

   - **200 OK**

     - Si existen vehículos:

       .. code-block:: json

          {
            "vehiculos": [
              {
                "id": 1,
                "marca": "Toyota",
                "modelo": "Corolla",
                "year": 2018,
                "rpm": 1500,
                "velocidad": 80,
                "vin": "JTDBL40E799017833",
                "revision": {"tipo": "Anual", "fecha": "2025-01-10"},
                "usuario_id": 5
              },
              {
                "id": 2,
                "marca": "Honda",
                "modelo": "Civic",
                "year": 2021,
                "rpm": 1300,
                "velocidad": 70,
                "vin": "2HGFC2F59MH123456",
                "revision": {"tipo": "Cambio llantas", "fecha": "2025-03-20"},
                "usuario_id": 5
              }
            ]
          }

     - Si no hay vehículos:

       .. code-block:: json

          {
            "mensaje": "No hay vehículos registrados para este usuario.",
            "vehiculos": []
          }

   - **401 Unauthorized**

     - Token inválido o expirado.

   - **500 Internal Server Error**

     - Error al recuperar datos.

Obtener Vehículo Específico
~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. http:get:: /mis-vehiculos/{vehiculo_id}

   Recupera la información de un único vehículo (``vehiculo_id``) si pertenece al usuario.

   **URL Parameters**:

   - ``vehiculo_id`` (integer, obligatorio)

   **Ejemplo**:

   .. code-block:: http

      GET /mis-vehiculos/2 HTTP/1.1
      Host: api.ejemplo.com
      Authorization: Bearer eyJhbGciOi...

   **Responses**:

   - **200 OK**

     .. code-block:: json

        {
          "id": 2,
          "marca": "Honda",
          "modelo": "Civic",
          "year": 2021,
          "rpm": 1300,
          "velocidad": 70,
          "vin": "2HGFC2F59MH123456",
          "revision": {"tipo": "Cambio llantas", "fecha": "2025-03-20"},
          "usuario_id": 5
        }

   - **404 Not Found**

     - El vehículo no existe o no pertenece al usuario.

     .. code-block:: json

        {
          "detail": "Vehículo no encontrado"
        }

   - **401 Unauthorized**

     - Token inválido o expirado.

Editar Vehículo
~~~~~~~~~~~~~~~

.. http:put:: /editar-vehiculo/{vehiculo_id}

   Actualiza los datos de un vehículo existente.

   **URL Parameters**:

   - ``vehiculo_id`` (integer, obligatorio)

   **Request Body** (``VehiculoEdicion``):

   - ``marca`` (string, obligatorio)  
   - ``modelo`` (string, obligatorio)  
   - ``year`` (integer, obligatorio)  
   - ``rpm`` (integer, obligatorio)  
   - ``velocidad`` (integer, obligatorio)  
   - ``vin`` (string, obligatorio, longitud = 17)  

   **Ejemplo**:

   .. code-block:: http

      PUT /editar-vehiculo/2 HTTP/1.1
      Host: api.ejemplo.com
      Authorization: Bearer eyJhbGciOi...
      Content-Type: application/json

      {
        "marca": "Honda",
        "modelo": "Civic LX",
        "year": 2022,
        "rpm": 1400,
        "velocidad": 75,
        "vin": "2HGFC2F59MH123456"
      }

   **Responses**:

   - **200 OK**

     .. code-block:: json

        {
          "mensaje": "Vehículo actualizado correctamente"
        }

   - **400 Bad Request**

     - VIN inválido o ya registrado en otro vehículo.

     .. code-block:: json

        {
          "detail": "VIN duplicado"
        }

   - **404 Not Found**

     - Vehículo no existe o no pertenece al usuario.

     .. code-block:: json

        {
          "detail": "Vehículo no encontrado"
        }

   - **401 Unauthorized**

     - Token inválido o expirado.

   - **500 Internal Server Error**

     - Error interno al actualizar.

Eliminar Vehículo
~~~~~~~~~~~~~~~~~

.. http:delete:: /eliminar-vehiculo/{vehiculo_id}

   Elimina un vehículo y todos sus errores OBD-II asociados (cascade).

   **URL Parameters**:

   - ``vehiculo_id`` (integer, obligatorio)

   **Ejemplo**:

   .. code-block:: http

      DELETE /eliminar-vehiculo/2 HTTP/1.1
      Host: api.ejemplo.com
      Authorization: Bearer eyJhbGciOi...

   **Responses**:

   - **200 OK**

     .. code-block:: json

        {
          "mensaje": "Vehículo eliminado correctamente",
          "errores_eliminados": 4
        }

     - ``errores_eliminados``: cantidad de registros de errores borrados.

   - **404 Not Found**

     - Vehículo no existe o no pertenece al usuario.

     .. code-block:: json

        {
          "detail": "Vehículo no encontrado"
        }

   - **401 Unauthorized**

     - Token inválido o expirado.

   - **500 Internal Server Error**

     - Error interno al eliminar.

Gestión de Errores OBD-II
-------------------------

.. note::

   Estos endpoints también requieren token válido en ``Authorization``.

Guardar Errores de Vehículo
~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. http:post:: /guardar-errores/

   Registra múltiples códigos DTC para un vehículo del usuario.

   **Request Body** (``ErrorVehiculoRegistro``):

   - ``vehiculo_id`` (integer, obligatorio)  
   - ``codigo_dtc`` (array[string], obligatorio)  
     - Lista de códigos OBD-II (p. ej.: ``["P0301", "P0420", "P0133"]``)

   **Validaciones**:

   - ``vehiculo_id`` debe ser entero positivo y corresponder a un vehículo del usuario.  
   - ``codigo_dtc`` no puede estar vacío ni contener duplicados o valores en blanco.  

   **Ejemplo**:

   .. code-block:: http

      POST /guardar-errores/ HTTP/1.1
      Host: api.ejemplo.com
      Authorization: Bearer eyJhbGciOi...
      Content-Type: application/json

      {
        "vehiculo_id": 1,
        "codigo_dtc": ["P0301", "P0420", "P0171"]
      }

   **Responses**:

   - **200 OK**

     .. code-block:: json

        {
          "mensaje": "Errores del vehículo guardados correctamente"
        }

   - **400 Bad Request**

     - Formato inválido, lista vacía, duplicados, vehiculo_id negativo.

     .. code-block:: json

        {
          "detail": "Lista de códigos vacía o contiene duplicados"
        }

   - **404 Not Found**

     - Vehículo no encontrado o no pertenece al usuario.

     .. code-block:: json

        {
          "detail": "Vehículo no encontrado"
        }

   - **401 Unauthorized**

     - Token inválido o expirado.

   - **500 Internal Server Error**

     - Error interno al guardar.

Obtener Errores de un Vehículo
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. http:get:: /mis-errores/{vehiculo_id}

   Obtiene todos los códigos DTC registrados para un vehículo.

   **URL Parameters**:

   - ``vehiculo_id`` (integer, obligatorio)

   **Ejemplo**:

   .. code-block:: http

      GET /mis-errores/1 HTTP/1.1
      Host: api.ejemplo.com
      Authorization: Bearer eyJhbGciOi...

   **Responses**:

   - **200 OK**

     .. code-block:: json

        ["P0301", "P0420", "P0171"]

   - **404 Not Found**

     - Vehículo no existente o no tiene errores registrados.

     .. code-block:: json

        {
          "detail": "No se encontraron errores para este vehículo"
        }

   - **401 Unauthorized**

     - Token inválido o expirado.

   - **500 Internal Server Error**

     - Error interno al consultar la base de datos.

Generación y Consulta de Informes
---------------------------------

.. note::

   La creación del informe envía un correo con un enlace público (token UUID).  
   Ver también en “Modelos” la tabla ``InformeCompartido``.

Crear Informe para un Vehículo
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. http:post:: /crear-informe/{vehiculo_id}

   Genera un informe HTML con todos los errores de un vehículo y lo envía por correo al cliente.  
   Se crea un token único para acceso público.

   **URL Parameters**:

   - ``vehiculo_id`` (integer, obligatorio)

   **Request Body** (``InformeRequest``):

   - ``email`` (string, obligatorio, debe contener "@").

   **Flujo Interno**:

   1. Verificar que ``vehiculo_id`` existe y pertenece al usuario.  
   2. Recuperar lista de códigos DTC asociados.  
   3. Generar un token UUID único (``uuid4()``) y guardar en tabla ``informes_compartidos``.  
   4. Crear plantilla HTML (botón con enlace a ``/informe/{token}``).  
   5. Enviar correo con FastAPI-Mail.  

   **Ejemplo**:

   .. code-block:: http

      POST /crear-informe/1 HTTP/1.1
      Host: api.ejemplo.com
      Authorization: Bearer eyJhbGciOi...
      Content-Type: application/json

      {
        "email": "cliente@dominio.com"
      }

   **Responses**:

   - **200 OK**

     .. code-block:: json

        {
          "mensaje": "Informe creado y enviado al email",
          "token": "550e8400-e29b-41d4-a716-446655440000",
          "enlace": "https://tudominio.com/taller-front/informe/550e8400-e29b-41d4-a716-446655440000"
        }

   - **400 Bad Request**

     - Email inválido (no contiene "@") o faltan datos.

     .. code-block:: json

        {
          "detail": "Formato de email inválido"
        }

   - **404 Not Found**

     - Vehículo no existe o no pertenece al usuario.

     .. code-block:: json

        {
          "detail": "Vehículo no encontrado"
        }

   - **401 Unauthorized**

     - Token inválido o expirado.

   - **500 Internal Server Error**

     - Error al guardar token o enviar correo.

Ver Informe Público
-------------------

.. http:get:: /informe/{token}

   Permite a cualquier usuario (sin autenticación) ver el informe de diagnóstico de un vehículo, siempre que posea el token correcto.

   **URL Parameters**:

   - ``token`` (string, obligatorio, longitud mínima 10)

   **Flujo Interno**:

   1. Validar longitud mínima de ``token`` (10 caracteres).  
   2. Buscar registro en tabla ``informes_compartidos``.  
   3. Recuperar datos de vehículo e historial de errores.  
   4. Devolver JSON con datos del vehículo y lista de errores.

   **Ejemplo**:

   .. code-block:: http

      GET /informe/550e8400-e29b-41d4-a716-446655440000 HTTP/1.1
      Host: api.ejemplo.com

   **Responses**:

   - **200 OK**

     .. code-block:: json

        {
          "vehiculo": {
            "marca": "Toyota",
            "modelo": "Corolla",
            "year": 2020,
            "vin": "JTDBL40E799017833",
            "rpm": 1500,
            "velocidad": 80,
            "revision": {"tipo": "Anual", "fecha": "2025-01-10"}
          },
          "errores": ["P0301", "P0420"]
        }

   - **400 Bad Request**

     - Token inválido (longitud < 10).

     .. code-block:: json

        {
          "detail": "Token inválido"
        }

   - **404 Not Found**

     - Token no encontrado o informe expirado.

     .. code-block:: json

        {
          "detail": "Informe no encontrado"
        }

   - **500 Internal Server Error**

     - Error interno al procesar la solicitud.

Servicio de Imágenes de Vehículo
--------------------------------

Obtener URL de Imagen de Vehículo
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. http:get:: /car-imagery/

   Recupera una URL de imagen de vehículo usando la API externa de **carimagery.com**.

   **Query Parameters**:

   - ``searchTerm`` (string, obligatorio)  
     Ejemplo: ``searchTerm=Toyota%20Corolla%202020``

   **Ejemplo**:

   .. code-block:: http

      GET /car-imagery/?searchTerm=Toyota%20Corolla%202020 HTTP/1.1
      Host: api.ejemplo.com

   **Responses**:

   - **200 OK**

     Devuelve texto o XML con la URL de la imagen, por ejemplo:

     .. code-block:: xml

        <CarImagery>
          <ImageUrl>https://imagenes.com/ford_focus_2020.jpg</ImageUrl>
        </CarImagery>

   - **400 Bad Request**

     - Si falta ``searchTerm`` o está vacío.

     .. code-block:: json

        {
          "detail": "searchTerm es obligatorio"
        }

   - **500 Internal Server Error**

     - Error al conectar con la API externa.

Endpoint de Prueba / Salud
--------------------------

Salud / Ping
~~~~~~~~~~~~

.. http:get:: /saludo

   Endpoint simple para verificar que la API está en funcionamiento.

   **Ejemplo**:

   .. code-block:: http

      GET /saludo HTTP/1.1
      Host: api.ejemplo.com

   **Responses**:

   - **200 OK**

     .. code-block:: json

        {
          "mensaje": "¡La API está funcionando correctamente!"
        }
