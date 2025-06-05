Modelos de Datos
================

Modelos ORM (SQLAlchemy)
-------------------------

Los modelos ORM representan las tablas en la base de datos. Están definidos con SQLAlchemy e incluyen relaciones entre entidades.

- `Usuario`: representa un usuario registrado.
- `Vehiculo`: vehículo asociado a un usuario.
- `ErrorVehiculo`: errores OBD-II asociados a un vehículo.
- `InformeCompartido`: informes generados para ser enviados por correo.

Modelos de validación (Pydantic)
--------------------------------

Los modelos Pydantic se utilizan para validar entradas y salidas en la API:

- `UsuarioRegistro`, `UsuarioLogin`: manejo de usuarios.
- `VehiculoRegistro`, `VehiculoEdicion`: datos de los vehículos.
- `ErrorVehiculoRegistro`: errores recibidos desde el cliente OBD.
- `InformeRequest`: datos para enviar el informe por email.

.. automodule:: main
   :members:
   :private-members:
   :show-inheritance:
   :exclude-members: get_db, app
