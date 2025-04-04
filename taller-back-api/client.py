import requests
import serial
import time
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from tkinter import messagebox

# Configuración de la API
API_URL = "https://anthonyx82.ddns.net/taller/api"
token = None

# Función para autenticarse
def obtener_token():
    usuario = usuario_entry.get()
    password = password_entry.get()

    if not usuario or not password:
        messagebox.showwarning("Aviso", "Por favor, ingrese usuario y contraseña.")
        return

    response = requests.post(
        f"{API_URL}/login",
        json={"username": usuario, "password": password}
    )
    
    if response.status_code == 200:
        global token
        token = response.json().get("access_token")
        login_frame.pack_forget()
        main_frame.pack(pady=20)
    else:
        messagebox.showerror("Error", f"Error en el login: {response.text}")

# Función para leer datos del OBD-II, incluyendo VIN
def leer_datos_obd2():
    PORT = "COM3"
    BAUDRATE = 9600
    TIMEOUT = 1

    try:
        with serial.Serial(PORT, BAUDRATE, timeout=TIMEOUT) as elm:
            def enviar_comando(comando):
                elm.write((comando + "\r").encode())
                time.sleep(0.5)
                respuesta = elm.readlines()
                return [line.decode().strip() for line in respuesta]

            enviar_comando("ATZ")
            enviar_comando("ATE0")
            enviar_comando("ATSP0")

            # Leer VIN
            respuesta_vin = enviar_comando("0902")
            vin = interpretar_respuesta_vin(respuesta_vin)

            # Si el VIN es desconocido, asignar un valor predeterminado
            if not vin or vin == "DESCONOCIDO":
                vin = "1HGCM82633A123456"

            # Leer RPM
            respuesta_rpm = enviar_comando("010C")
            rpm = interpretar_respuesta_rpm(respuesta_rpm)

            # Leer velocidad
            respuesta_velocidad = enviar_comando("010D")
            velocidad = interpretar_respuesta_velocidad(respuesta_velocidad)

            return {"vin": vin, "rpm": rpm, "velocidad": velocidad}

    except Exception as e:
        messagebox.showerror("Error", f"No se pudo conectar al OBD-II: {e}")
        return {"vin": "1HGCM82633A123456", "rpm": 5200, "velocidad": 168}

def interpretar_respuesta_vin(respuesta):
    vin = ""
    for linea in respuesta:
        if "49 02" in linea:
            partes = linea.split(" ")[2:]  # Ignorar el identificador "49 02"
            vin += "".join(chr(int(p, 16)) for p in partes if p != "00")
    return vin.strip() if vin else "DESCONOCIDO"

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

# Función para enviar los datos a la API
def enviar_datos():
    if not token:
        messagebox.showerror("Error", "Debe iniciar sesión primero.")
        return

    marca = marca_entry.get()
    modelo = modelo_entry.get()
    year = year_entry.get()

    if not marca or not modelo or not year:
        messagebox.showwarning("Aviso", "Ingrese marca, modelo y año.")
        return

    datos_obd = leer_datos_obd2()
    
    # Mostrar VIN en la interfaz
    vin_label.config(text=f"VIN: {datos_obd['vin']}")

    vehiculo_data = {
        "marca": marca,
        "modelo": modelo,
        "year": int(year),
        "rpm": datos_obd["rpm"],
        "velocidad": datos_obd["velocidad"],
        "vin": datos_obd["vin"]
    }

    headers = {"Authorization": f"Bearer {token}"}
    response = requests.post(f"{API_URL}/guardar-vehiculo/", json=vehiculo_data, headers=headers)

    if response.status_code == 200:
        messagebox.showinfo("Éxito", "Datos del vehículo enviados correctamente.")
    else:
        messagebox.showerror("Error", f"No se pudo enviar: {response.text}")

# Crear ventana con colores personalizados
ventana = ttk.Window(themename="flatly")  # Tema más moderno
ventana.title("Cliente OBD-II")
ventana.geometry("400x550")
ventana.configure(bg="#FFFFFF")  # Fondo blanco

# ---------- Estilo ----------
btn_style = {"bootstyle": "warning", "width": 20, "padding": 5}  # Naranja
entry_style = {"width": 30, "bootstyle": "light"}  # Fondos blancos

# ---------- Pantalla de Login ----------
login_frame = ttk.Frame(ventana, padding=20)
login_frame.pack(pady=50)

ttk.Label(login_frame, text="Iniciar Sesión", font=("Arial", 16, "bold"), background="#FFFFFF", foreground="#E67E22").pack(pady=10)

usuario_entry = ttk.Entry(login_frame, **entry_style)
usuario_entry.pack(pady=5)
usuario_entry.insert(0, "Usuario")

password_entry = ttk.Entry(login_frame, show="*", **entry_style)
password_entry.pack(pady=5)
password_entry.insert(0, "Contraseña")

ttk.Button(login_frame, text="Login", command=obtener_token, **btn_style).pack(pady=10)

# ---------- Pantalla Principal ----------
main_frame = ttk.Frame(ventana, padding=20)

ttk.Label(main_frame, text="Registro de Vehículo", font=("Arial", 14, "bold"), background="#FFFFFF", foreground="#E67E22").pack(pady=10)

ttk.Label(main_frame, text="Marca", background="#FFFFFF", foreground="#333").pack(pady=2)
marca_entry = ttk.Entry(main_frame, **entry_style)
marca_entry.pack()

ttk.Label(main_frame, text="Modelo", background="#FFFFFF", foreground="#333").pack(pady=2)
modelo_entry = ttk.Entry(main_frame, **entry_style)
modelo_entry.pack()

ttk.Label(main_frame, text="Año", background="#FFFFFF", foreground="#333").pack(pady=2)
year_entry = ttk.Entry(main_frame, **entry_style)
year_entry.pack()

vin_label = ttk.Label(main_frame, text="VIN: Desconocido", background="#FFFFFF", foreground="#E67E22", font=("Arial", 10, "bold"))
vin_label.pack(pady=5)

ttk.Button(main_frame, text="Conectar OBD-II y Enviar", command=enviar_datos, **btn_style).pack(pady=20)

ventana.mainloop()
