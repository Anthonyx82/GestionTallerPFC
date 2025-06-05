Modelos de Datos
================

En esta sección se describen en detalle los **modelos ORM** (SQLAlchemy) y los **modelos de validación** (Pydantic) definidos en `main.py`. Se incluyen tablas con atributos, tipos, relaciones y ejemplos de uso.

.. contents::
   :local:
   :depth: 2

Modelos ORM (SQLAlchemy)
-------------------------

Los modelos ORM representan las tablas de la base de datos, heredan de `Base` y están definidos en `main.py`. A continuación se listan sus atributos principales, tipos y descripciones.

.. list-table::
   :header-rows: 1
   :widths: 15 20 20 45

   * - **Clase**
     - **Atributo**
     - **Tipo**
     - **Descripción**
   * - ``Usuario``
     - ``id``
     - Integer (PK)
     - Identificador único autoincremental.
   * - ``Usuario``
     - ``username``
     - String(255), único
     - Nombre de usuario (único).
   * - ``Usuario``
     - ``password_hash``
     - String(255)
     - Contraseña almacenada (hash bcrypt).
   * - ``Usuario``
     - ``vehiculos``
     - Relationship
     - Relación uno-a-muchos con ``Vehiculo``.
   * - ``Vehiculo``
     - ``id``
     - Integer (PK)
     - Identificador del vehículo.
   * - ``Vehiculo``
     - ``marca``
     - String(255)
     - Marca del vehículo.
   * - ``Vehiculo``
     - ``modelo``
     - String(255)
     - Modelo del vehículo.
   * - ``Vehiculo``
     - ``year``
     - Integer
     - Año de fabricación (YYYY).
   * - ``Vehiculo``
     - ``rpm``
     - Integer
     - Revoluciones por minuto.
   * - ``Vehiculo``
     - ``velocidad``
     - Integer
     - Velocidad actual en km/h.
   * - ``Vehiculo``
     - ``vin``
     - String(17), único
     - Número VIN (único, 17 caracteres).
   * - ``Vehiculo``
     - ``revision``
     - String(255)
     - JSON serializado con detalles de la revisión.
   * - ``Vehiculo``
     - ``usuario_id``
     - Integer (FK)
     - Clave foránea a ``Usuario.id``.
   * - ``Vehiculo``
     - ``errores``
     - Relationship
     - Relación uno-a-muchos con ``ErrorVehiculo``.
   * - ``Vehiculo``
     - ``informes_compartidos``
     - Relationship
     - Relación uno-a-muchos con ``InformeCompartido``.
   * - ``ErrorVehiculo``
     - ``id``
     - Integer (PK)
     - Identificador del error DTC.
   * - ``ErrorVehiculo``
     - ``vehiculo_id``
     - Integer (FK)
     - Clave foránea a ``Vehiculo.id``.
   * - ``ErrorVehiculo``
     - ``codigo_dtc``
     - String(255)
     - Código OBD-II (p. ej., "P0301").
   * - ``ErrorVehiculo``
     - ``vehiculo``
     - Relationship
     - Vínculo inverso a ``Vehiculo``.
   * - ``InformeCompartido``
     - ``id``
     - Integer (PK)
     - Identificador del informe.
   * - ``InformeCompartido``
     - ``token``
     - String(100), único
     - Token UUID público para compartir.
   * - ``InformeCompartido``
     - ``vehiculo_id``
     - Integer (FK)
     - Clave foránea a ``Vehiculo.id``.
   * - ``InformeCompartido``
     - ``email_cliente``
     - String(255)
     - Email del destinatario.
   * - ``InformeCompartido``
     - ``creado_en``
     - DateTime
     - Fecha y hora de creación (UTC).

**Relaciones entre Tablas**:

- ``Usuario`` ↔ ``Vehiculo``
   - Uno a muchos:
      - En `Usuario`:
         ```python 
         vehiculos = relationship("Vehiculo", back_populates="usuario", cascade="all, delete-orphan")
         ``` 
      - En `Vehiculo`:
         ```python
         usuario = relationship("Usuario", back_populates="vehiculos")
         ```

- ``Vehiculo`` ↔ ``ErrorVehiculo``  
   - Uno a muchos:  
      - En `Vehiculo`:  
      ```python 
      errores = relationship("ErrorVehiculo", back_populates="vehiculo", cascade="all, delete-orphan")
      ```  
      - En `ErrorVehiculo`:  
      ```python
      vehiculo = relationship("Vehiculo", back_populates="errores")
      ```

- ``Vehiculo`` ↔ ``InformeCompartido``  
   - Uno a muchos:  
      - En `Vehiculo`:  
      ```python 
      informes_compartidos = relationship("InformeCompartido", back_populates="vehiculo", cascade="all, delete-orphan")
      ```  
    - En `InformeCompartido`: 
      ```python
      vehiculo = relationship("Vehiculo", back_populates="informes_compartidos")
      ```

Ejemplo de Esquema en SQL
~~~~~~~~~~~~~~~~~~~~~~~~~

A modo de referencia, a continuación se muestra un esquema simplificado en SQL que refleja la estructura anterior:

.. code-block:: sql

   CREATE TABLE usuarios (
       id INT AUTO_INCREMENT PRIMARY KEY,
       username VARCHAR(255) UNIQUE NOT NULL,
       password_hash VARCHAR(255) NOT NULL
   );

   CREATE TABLE vehiculos (
       id INT AUTO_INCREMENT PRIMARY KEY,
       marca VARCHAR(255) NOT NULL,
       modelo VARCHAR(255) NOT NULL,
       year INT NOT NULL,
       rpm INT NOT NULL,
       velocidad INT NOT NULL,
       vin VARCHAR(17) UNIQUE NOT NULL,
       revision TEXT NOT NULL,
       usuario_id INT NOT NULL,
       FOREIGN KEY (usuario_id) REFERENCES usuarios(id) ON DELETE CASCADE
   );

   CREATE TABLE error_vehiculo (
       id INT AUTO_INCREMENT PRIMARY KEY,
       vehiculo_id INT NOT NULL,
       codigo_dtc VARCHAR(255) NOT NULL,
       FOREIGN KEY (vehiculo_id) REFERENCES vehiculos(id) ON DELETE CASCADE
   );

   CREATE TABLE informes_compartidos (
       id INT AUTO_INCREMENT PRIMARY KEY,
       token VARCHAR(100) UNIQUE NOT NULL,
       vehiculo_id INT NOT NULL,
       email_cliente VARCHAR(255) NOT NULL,
       creado_en DATETIME NOT NULL,
       FOREIGN KEY (vehiculo_id) REFERENCES vehiculos(id) ON DELETE CASCADE
   );

Modelos de Validación (Pydantic)
--------------------------------

Los modelos Pydantic garantizan que las peticiones entrantes y salidas cumplan con un esquema específico. Se utilizan en los endpoints para validar datos de usuario, vehículo, errores e informes.

.. list-table::
   :header-rows: 1
   :widths: 20 50 50

   * - **Clase**
     - **Campos**
     - **Descripción**
   * - ``UsuarioRegistro``
     - ``username`` (string, obligatorio, mínimo 3 caracteres)
     - Nombre de usuario.
   * - ``UsuarioRegistro``
     - ``password`` (string, obligatorio, mínimo 6 caracteres)
     - Contraseña.
   * - ``UsuarioLogin``
     - ``username`` (string, obligatorio)
     - Nombre de usuario.
   * - ``UsuarioLogin``
     - ``password`` (string, obligatorio)
     - Contraseña.
   * - ``VehiculoRegistro``
     - ``marca`` (string, obligatorio)
     - Marca del vehículo.
   * - ``VehiculoRegistro``
     - ``modelo`` (string, obligatorio)
     - Modelo del vehículo.
   * - ``VehiculoRegistro``
     - ``year`` (integer, obligatorio, YYYY)
     - Año de fabricación.
   * - ``VehiculoRegistro``
     - ``rpm`` (integer, obligatorio)
     - Revoluciones por minuto.
   * - ``VehiculoRegistro``
     - ``velocidad`` (integer, obligatorio)
     - Velocidad actual en km/h.
   * - ``VehiculoRegistro``
     - ``vin`` (string de longitud 17, obligatorio)
     - Número VIN único.
   * - ``VehiculoRegistro``
     - ``revision`` (dict con claves obligatorias y opcionales)
     - Detalles de revisión: ``tipo``, ``fecha``, ``observaciones``.
   * - ``VehiculoEdicion``
     - (mismos campos que ``VehiculoRegistro`` excepto ``revision``)
     - Usado para actualizar vehículos existentes.
   * - ``ErrorVehiculoRegistro``
     - ``vehiculo_id`` (integer, obligatorio)
     - ID del vehículo.
   * - ``ErrorVehiculoRegistro``
     - ``codigo_dtc`` (list[string], obligatorio)
     - Lista de códigos DTC.
   * - ``InformeRequest``
     - ``email`` (string, obligatorio, debe contener "@")
     - Email del cliente.

Validaciones Clave
~~~~~~~~~~~~~~~~~~

- En ``UsuarioRegistro`` y ``UsuarioLogin`` se verifica longitud mínima de `username` y `password`.  
- En ``VehiculoRegistro`` y ``VehiculoEdicion`` se exige que `vin` sea exactamente 17 caracteres y único en la base de datos.  
- En ``ErrorVehiculoRegistro`` se valida que `vehiculo_id` exista y que la lista `codigo_dtc` no esté vacía ni tenga duplicados.  
- En ``InformeRequest`` se comprueba que `email` contenga el carácter “@”.

Ejemplo de Uso en un Endpoint
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Por ejemplo, en el endpoint `/guardar-vehiculo/`:

.. code-block:: python

   @app.post("/guardar-vehiculo/")
   def crear_vehiculo(
       vehiculo: VehiculoRegistro,
       db: Session = Depends(get_db),
       usuario: Usuario = Depends(obtener_usuario_desde_token)
   ):
       # Aquí 'vehiculo' ya está validado por Pydantic:
       #   vehiculo.marca (str), vehiculo.modelo (str), vehiculo.vin (str de 17 chars), etc.
       nuevo = models.Vehiculo(
           marca=vehiculo.marca,
           modelo=vehiculo.modelo,
           year=vehiculo.year,
           rpm=vehiculo.rpm,
           velocidad=vehiculo.velocidad,
           vin=vehiculo.vin,
           revision=json.dumps(vehiculo.revision),
           usuario_id=usuario.id
       )
       db.add(nuevo)
       db.commit()
       db.refresh(nuevo)
       return {"mensaje": "Vehículo guardado correctamente", "id": nuevo.id}

Referencia Automática
~~~~~~~~~~~~~~~~~~~~~

Para revisar el código completo de cada clase (atributos adicionales, métodos, relaciones, validaciones), se ha añadido la directiva `.. automodule:: main` más abajo:

.. automodule:: main
   :members:
   :exclude-members: get_db, app
   :show-inheritance:
   :undoc-members:
