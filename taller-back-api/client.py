import requests
import serial
import time
import tkinter as tk
from tkinter import messagebox

# Configuración de la API
API_URL = "https://anthonyx82.ddns.net/taller/api"

# Función para autenticarse y obtener el token
def obtener_token(usuario, password):
    response = requests.post(
        f"{API_URL}/login",
        json={"username": usuario, "password": password}
    )
    
    if response.status_code == 200:
        return response.json().get("access_token")
    else:
        messagebox.showerror("Error", f"Error en el login: {response.text}")
        return None

# Función para leer datos desde OBD-II
def leer_datos_obd2():
    PORT = "COM3"  # Ajusta según el sistema operativo
    BAUDRATE = 9600
    TIMEOUT = 1

    try:
        with serial.Serial(PORT, BAUDRATE, timeout=TIMEOUT) as elm:
            print("Conexión con OBD2 exitosa.")

            def enviar_comando(comando):
                elm.write((comando + "\r").encode())
                time.sleep(0.5)
                respuesta = elm.readlines()
                return [line.decode().strip() for line in respuesta]

            enviar_comando("ATZ")
            enviar_comando("ATE0")
            enviar_comando("ATSP0")

            # Leer RPM
            respuesta_rpm = enviar_comando("010C")
            rpm = interpretar_respuesta_rpm(respuesta_rpm)

            # Leer velocidad
            respuesta_velocidad = enviar_comando("010D")
            velocidad = interpretar_respuesta_velocidad(respuesta_velocidad)

            # Leer códigos de error (DTCs)
            respuesta_errores = enviar_comando("03")
            codigos_dtc = interpretar_codigos_dtc(respuesta_errores)

            return {
                "rpm": rpm,
                "velocidad": velocidad,
                "errores": codigos_dtc
            }

    except Exception as e:
        messagebox.showerror("Error", f"No se pudo conectar al OBD-II: {e}")
        # Datos por defecto si ocurre un error
        return {
            "rpm": 5200,  # RPM del Peugeot 206 HDi de 2002
            "velocidad": 168,  # Velocidad máxima del Peugeot 206 HDi de 2002
            "errores": ["P0300", "P0400"]  # Errores básicos por defecto
        }

# Funciones para interpretar los datos OBD-II
def interpretar_respuesta_rpm(respuesta):
    for linea in respuesta:
        if "41 0C" in linea:
            partes = linea.split(" ")
            if len(partes) >= 4:
                A = int(partes[2], 16)
                B = int(partes[3], 16)
                return ((A * 256) + B) / 4
    return 0

def interpretar_respuesta_velocidad(respuesta):
    for linea in respuesta:
        if "41 0D" in linea:
            partes = linea.split(" ")
            if len(partes) >= 3:
                return int(partes[2], 16)
    return 0

def interpretar_codigos_dtc(respuesta):
    dtcs = []
    for linea in respuesta:
        if "43" in linea or "47" in linea:
            partes = linea.split(" ")[1:]
            for i in range(0, len(partes), 2):
                if len(partes) > i + 1:
                    codigo = partes[i] + partes[i + 1]
                    dtcs.append(codigo)
    return dtcs

# Función para enviar los datos a la API
def enviar_datos():
    usuario = usuario_entry.get()
    password = password_entry.get()

    if not usuario or not password:
        messagebox.showwarning("Aviso", "Por favor, ingrese usuario y contraseña.")
        return

    token = obtener_token(usuario, password)
    if not token:
        return

    datos_obd = leer_datos_obd2()
    if not datos_obd:
        return

    # Solicitar marca, modelo y año
    marca = marca_entry.get()
    modelo = modelo_entry.get()
    year = year_entry.get()

    if not marca or not modelo or not year:
        messagebox.showwarning("Aviso", "Ingrese marca, modelo y año.")
        return

    # Guardar datos del vehículo
    vehiculo_data = {
        "marca": marca if marca else "Peugeot",
        "modelo": modelo if modelo else "206 HDi",
        "year": int(year) if year else 2002,
        "rpm": datos_obd["rpm"],
        "velocidad": datos_obd["velocidad"]
    }
    
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.post(f"{API_URL}/guardar-vehiculo/", json=vehiculo_data, headers=headers)
    
    if response.status_code == 200:
        vehiculo_id = response.json()["id"]
        messagebox.showinfo("Éxito", "Datos del vehículo enviados correctamente.")
        
        if datos_obd["errores"]:
            errores_data = {"codigo_dtc": datos_obd["errores"], "vehiculo_id": vehiculo_id}
            response = requests.post(f"{API_URL}/guardar-errores/", json=errores_data, headers=headers)
            if response.status_code == 200:
                messagebox.showinfo("Éxito", "Errores enviados correctamente.")
            else:
                messagebox.showerror("Error", f"No se pudieron enviar los errores: {response.text}")
        else:
            messagebox.showinfo("Info", "No se encontraron errores en el vehículo.")

# Crear la ventana principal
ventana = tk.Tk()
ventana.title("Cliente OBD-II")
ventana.geometry("400x400")

# Etiquetas y campos de entrada
tk.Label(ventana, text="Usuario:").pack(pady=5)
usuario_entry = tk.Entry(ventana)
usuario_entry.pack()

tk.Label(ventana, text="Contraseña:").pack(pady=5)
password_entry = tk.Entry(ventana, show="*")
password_entry.pack()

tk.Label(ventana, text="Marca:").pack(pady=5)
marca_entry = tk.Entry(ventana)
marca_entry.pack()

tk.Label(ventana, text="Modelo:").pack(pady=5)
modelo_entry = tk.Entry(ventana)
modelo_entry.pack()

tk.Label(ventana, text="Año:").pack(pady=5)
year_entry = tk.Entry(ventana)
year_entry.pack()

# Botón para enviar los datos
tk.Button(ventana, text="Conectar y enviar datos", command=enviar_datos).pack(pady=20)

# Ejecutar la ventana
ventana.mainloop()
