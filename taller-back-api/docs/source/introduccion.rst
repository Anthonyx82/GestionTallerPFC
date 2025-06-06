Introducción
============

Bienvenido a la documentación técnica de la **API de gestión de vehículos e informes de diagnóstico**. Esta API permite:

- Registrar usuarios y autenticarlos mediante JWT.
- Añadir vehículos a la cuenta de usuario, junto con sus datos OBD-II en tiempo real.
- Almacenar y consultar errores OBD-II (códigos DTC) asociados a cada vehículo.
- Generar informes de diagnóstico y enviarlos por correo a los clientes.
- Compartir informes mediante enlaces públicos protegidos con un token UUID.

Público Objetivo
----------------

- Desarrolladores que estén integrando una solución de telemetría OBD-II.
- Equipos de soporte técnico que necesiten generar y enviar informes de fallos a clientes.
- Administradores de flotas que quieran mantener un registro de diagnósticos remotos.

Tecnologías Principales
-----------------------

- **FastAPI**: 
  - Framework web para construir APIs RESTful de alto rendimiento.
  - Documentación automática en Swagger (``/docs``) y ReDoc (``/redoc``).

- **SQLAlchemy**:
  - ORM para gestionar la base de datos relacional MySQL.
  - Modelado de entidades como ``Usuario``, ``Vehiculo``, ``ErrorVehiculo`` e ``InformeCompartido``.

- **Pydantic**:
  - Validación y serialización de datos en entradas y respuestas.

- **JWT (JSON Web Tokens)**:
  - Autenticación sin estado (stateless).
  - Expiración configurable.

- **FastAPI-Mail**:
  - Envío de correos electrónicos con plantillas HTML para los informes.
  - Compatible con TLS/SSL y validación de certificados.

- **MySQL**:
  - Sistema de gestión de base de datos relacional.
  - Se puede ajustar el motor/host/credenciales a través de ``DATABASE_URL``.

- **Sphinx**:
  - Generación de la documentación estática en formato HTML/Markdown/PDF.
  - Uso de directivas como ``.. automodule::`` para extraer docstrings de ``main.py``.

Estructura de la Documentación
------------------------------

Esta documentación se divide en:

1. **Introducción**: visión global, tecnologías y esquema de carpetas.
2. **Endpoints**: descripción detallada de cada ruta, sus parámetros y ejemplos.
3. **Modelos de Datos**: descripción de cada clase ORM y modelo Pydantic.
4. **Configuración**: variables de entorno necesarias y explicación de la configuración del proyecto.

Requisitos Previos
------------------

- Python 3.9+  
- MySQL (o servidor compatible)  
- Dependencias del proyecto definidas en ``requirements.txt`` (FastAPI, SQLAlchemy, Pydantic, FastAPI-Mail, python-dotenv, etc.)  

Para ejecutar localmente:

1. Clona el repositorio.
2. Crea un entorno virtual:

   .. code-block:: bash

      python3 -m venv venv
      source venv/bin/activate

3. Instala las dependencias del proyecto:

   .. code-block:: bash

      pip install -r requirements.txt

4. Configura las variables de entorno necesarias creando un archivo ``.env`` en la raíz del proyecto.  
   Puedes usar como base un archivo ``.env.example``.

5. Ejecuta la aplicación usando Uvicorn:

   .. code-block:: bash

      uvicorn main:app --reload

Buenas Prácticas
----------------

- Mantén las variables de entorno fuera del control de versiones (``.gitignore``).
- Usa HTTPS y certificados válidos en producción.
- Cambia la clave ``SECRET_KEY`` y el ``ALGORITHM`` antes de desplegar.
- Implementa control de errores en el frontend para manejar respuestas ``401``, ``403``, ``422``, etc.
- Revisa los logs para rastrear errores en endpoints como ``/crear-informe/``.

Licencia y Contribución
-----------------------

Este proyecto se entrega con fines educativos y está licenciado bajo los términos definidos en el archivo ``LICENSE``.

Si deseas contribuir:

- Realiza un fork del repositorio.
- Crea una rama para tu mejora o corrección:

  .. code-block:: bash

     git checkout -b feature/nombre

- Haz tus commits siguiendo buenas prácticas de formato y mensajes.
- Envía un Pull Request para revisión.

Contacto
--------

Para dudas, errores o sugerencias, puedes abrir un issue en GitHub o contactar directamente con el equipo de desarrollo a traves del repositorio de GitHub
