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
        params={"username": usuario, "password": password}
    )

    if response.status_code == 200:
        return response.json()["access_token"]
    else:
        messagebox.showerror("Error", f"Error en el login: {response.text}")
        return None

# Función para leer datos desde OBD-II
def leer_datos_obd2():
    PORT = "COM3"  # En Windows, cambia esto según el puerto del lector OBD-II
    BAUDRATE = 9600
    TIMEOUT = 1

    try:
        elm = serial.Serial(PORT, BAUDRATE, timeout=TIMEOUT)
        print("Conexión con OBD2 exitosa.")

        def enviar_comando(comando):
            elm.write((comando + "\r").encode())
            time.sleep(0.5)
            respuesta = elm.readlines()
            return [line.decode().strip() for line in respuesta]

        enviar_comando("ATZ")
        enviar_comando("ATE0")
        enviar_comando("ATSP0")

        return {
            "marca": "Toyota",
            "modelo": "Corolla",
            "year": 2015,
            "rpm": 3000,
            "velocidad": 80
        }
    except:
        messagebox.showerror("Error", "No se pudo conectar al OBD-II.")
        return None

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

    datos = leer_datos_obd2()
    if not datos:
        return

    headers = {"Authorization": f"Bearer {token}"}
    response = requests.post(f"{API_URL}/guardar-vehiculo/", json=datos, headers=headers)

    if response.status_code == 200:
        messagebox.showinfo("Éxito", "Datos enviados correctamente.")
    else:
        messagebox.showerror("Error", "No se pudieron enviar los datos.")

# Crear la ventana principal
ventana = tk.Tk()
ventana.title("Cliente OBD-II")
ventana.geometry("400x300")

# Etiquetas y campos de entrada
tk.Label(ventana, text="Usuario:").pack(pady=5)
usuario_entry = tk.Entry(ventana)
usuario_entry.pack()

tk.Label(ventana, text="Contraseña:").pack(pady=5)
password_entry = tk.Entry(ventana, show="*")
password_entry.pack()

# Botón para enviar los datos
tk.Button(ventana, text="Conectar y enviar datos", command=enviar_datos).pack(pady=20)

# Ejecutar la ventana
ventana.mainloop()
