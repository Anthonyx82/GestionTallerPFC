import requests
import serial
import serial.tools.list_ports
import time
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from tkinter import messagebox, Toplevel, StringVar, IntVar, Canvas, Label, Checkbutton, Button, Frame
from PIL import Image, ImageTk


API_URL = "https://anthonyx82.ddns.net/taller/api"
token = None
selected_port = None
revision_data = {}

partes_generales = ["Motor", "Chasis", "Caja de cambios"]
detalles_motor = ["Correa distribución", "Filtro aire", "Bujías", "Inyectores", "Radiador", "Aceite", "Refrigerante", "Batería", "Alternador", "Turbocompresor"]
detalles_chasis = ["Suspensión", "Frenos", "Rótulas", "Amortiguadores", "Discos", "Pastillas", "Dirección", "Eje delantero", "Eje trasero", "Ruedas"]
detalles_caja = ["Aceite transmisión", "Sincronizadores", "Embrague", "Convertidor par", "Engranajes", "Sensor velocidad", "Palanca", "Caja externa", "Sello junta", "Montura"]

def obtener_token():
    usuario = usuario_entry.get()
    password = password_entry.get()

    if not usuario or not password:
        messagebox.showwarning("Aviso", "Por favor, ingrese usuario y contraseña.")
        return

    response = requests.post(
        f"{API_URL}/login",
        json={"username": "test1", "password": "Ams1313*"}
    )
    
    if response.status_code == 200:
        global token
        token = response.json().get("access_token")
        login_frame.pack_forget()
        main_frame.pack(pady=20)
        cargar_puertos()
    else:
        messagebox.showerror("Error", f"Error en el login: {response.text}")

def cargar_puertos():
    ports = list(serial.tools.list_ports.comports())
    puerto_combo['values'] = [f"{p.device} - {p.description}" for p in ports]
    if ports:
        puerto_combo.current(0)
        btn_enviar.config(state=NORMAL)
    else:
        puerto_combo['values'] = ["No se detectaron dispositivos"]
        btn_enviar.config(state=DISABLED)

def leer_datos_obd2():
    port_info = puerto_combo.get()
    if " - " not in port_info:
        messagebox.showerror("Error", "Seleccione un puerto válido.")
        return

    PORT = port_info.split(" - ")[0]
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

            respuesta_vin = enviar_comando("0902")
            vin = interpretar_respuesta_vin(respuesta_vin)

            if not vin or vin == "DESCONOCIDO":
                vin = "1HGCM82633A123456"

            respuesta_rpm = enviar_comando("010C")
            rpm = interpretar_respuesta_rpm(respuesta_rpm)

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
            partes = linea.split(" ")[2:]
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

def mostrar_imagen(parent, ruta):
    try:
        img = Image.open(ruta)
        img_tk = ImageTk.PhotoImage(img)

        label_img = Label(parent, image=img_tk)
        label_img.image = img_tk
        label_img.pack()
        return label_img
    except Exception as e:
        print(f"No se pudo cargar la imagen: {e}")

def siguiente(modal, seleccion_general):
    global revision_data
    seleccionadas = [parte for parte, var in seleccion_general.items() if var.get()]
    if not seleccionadas:
        messagebox.showwarning("Aviso", "Debe seleccionar al menos una parte para continuar.")
        return
    revision_data = {parte: [] for parte in seleccionadas}
    modal.destroy()
    mostrar_modal_detalle()

def mostrar_modal_revision():
    modal = Toplevel(ventana)
    modal.attributes("-fullscreen", True)
    modal.title("Revisión de partes del vehículo")

    # Cargar imagen y escalarla al 80%
    img = Image.open("images/vehiculo_xray.png")
    original_width, original_height = img.size
    escala = 0.8
    nuevo_ancho = int(original_width * escala)
    nuevo_alto = int(original_height * escala)
    img = img.resize((nuevo_ancho, nuevo_alto), Image.Resampling.LANCZOS)
    img_tk = ImageTk.PhotoImage(img)

    # Crear canvas con el tamaño ajustado
    canvas = Canvas(modal, width=modal.winfo_screenwidth(), height=modal.winfo_screenheight(), bg="white")
    canvas.pack(fill="both", expand=True)
    canvas.background = img_tk

    # Calcular posición centrada con margen superior (ej. 50px)
    margen_superior = 50
    x_centro = (modal.winfo_screenwidth() - nuevo_ancho) // 2

    canvas.create_image(x_centro, margen_superior, image=img_tk, anchor="nw")

    seleccion_general = {}

    partes_info = {
        "Motor": {"pos": (100, 300), "flecha": (150, 150)},
        "Chasis": {"pos": (700, 150), "flecha": (10, 100)},
        "Caja de cambios": {"pos": (800, 750), "flecha": (-150, -150)}
    }
    
    for parte, datos in partes_info.items():
        x, y = datos["pos"]
        dx, dy = datos["flecha"]
    
        x_escalado = int(x * escala) + x_centro
        y_escalado = int(y * escala) + margen_superior
    
        var = IntVar()
        chk = Checkbutton(modal, text=parte, variable=var, bg="white")
        canvas.create_window(x_escalado, y_escalado, window=chk)
    
        canvas.create_line(
            x_escalado, y_escalado,
            x_escalado + dx, y_escalado + dy,
            arrow="last", width=2, fill="white"
        )
    
        seleccion_general[parte] = var

    btn_siguiente = Button(modal, text="Siguiente", command=lambda: siguiente(modal, seleccion_general))
    canvas.create_window(modal.winfo_screenwidth()//2, modal.winfo_screenheight() - 80, window=btn_siguiente)


def mostrar_modal_detalle():
    partes_detalle = {
        "Motor": detalles_motor,
        "Chasis": detalles_chasis,
        "Caja de cambios": detalles_caja
    }

    partes_a_mostrar = list(revision_data.keys())

    if not partes_a_mostrar:
        messagebox.showwarning("Aviso", "Debes seleccionar al menos una parte para continuar.")
        return

    idx = 0

    def mostrar_parte():
        nonlocal idx
        if idx >= len(partes_a_mostrar):
            enviar_datos()
            return

        parte = partes_a_mostrar[idx]
        detalles = partes_detalle[parte]

        modal = Toplevel(ventana)
        modal.attributes("-fullscreen", True)
        modal.title(f"Revisión de {parte}")

        # Cargar imagen y escalarla
        ruta_imagen = f"images/{parte.lower()}_xray.png"
        try:
            img = Image.open(ruta_imagen)
            original_width, original_height = img.size
            escala = 0.8
            nuevo_ancho = int(original_width * escala)
            nuevo_alto = int(original_height * escala)
            img = img.resize((nuevo_ancho, nuevo_alto), Image.Resampling.LANCZOS)
            img_tk = ImageTk.PhotoImage(img)
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo cargar la imagen para {parte}: {e}")
            modal.destroy()
            return

        canvas = Canvas(modal, width=modal.winfo_screenwidth(), height=modal.winfo_screenheight(), bg="white")
        canvas.pack(fill="both", expand=True)
        canvas.background = img_tk

        margen_superior = 50
        x_centro = (modal.winfo_screenwidth() - nuevo_ancho) // 2
        canvas.create_image(x_centro, margen_superior, image=img_tk, anchor="nw")

        detalle_vars = []

        # Coordenadas y flechas personalizadas para cada parte
        coordenadas_custom = {
            "Motor": {
                "Correa distribución": ((220, 280), (100, 50)),
                "Filtro aire": ((400, 320), (-80, -100)),
                "Bujías": ((600, 260), (-150, -120)),
                "Inyectores": ((780, 240), (-100, 100)),
                "Radiador": ((300, 180), (120, 60)),
                "Aceite": ((500, 400), (-60, -150)),
                "Refrigerante": ((620, 150), (-90, 120)),
                "Batería": ((150, 380), (100, 100)),
                "Alternador": ((360, 480), (80, -80)),
                "Turbocompresor": ((720, 360), (-150, -100))
            },
            "Chasis": {
                "Suspensión": ((200, 200), (60, 80)),
                "Frenos": ((400, 150), (-100, 100)),
                "Rótulas": ((600, 220), (-80, -50)),
                "Amortiguadores": ((800, 180), (-150, 50)),
                "Discos": ((300, 300), (100, -60)),
                "Pastillas": ((500, 260), (-90, -90)),
                "Dirección": ((700, 300), (-100, 100)),
                "Eje delantero": ((400, 400), (60, -60)),
                "Eje trasero": ((600, 420), (-60, -60)),
                "Ruedas": ((800, 400), (-100, -80))
            },
            "Caja de cambios": {
                "Aceite transmisión": ((200, 150), (100, 100)),
                "Sincronizadores": ((400, 180), (-100, 100)),
                "Embrague": ((600, 160), (-120, 60)),
                "Convertidor par": ((800, 140), (-150, 120)),
                "Engranajes": ((300, 260), (80, 80)),
                "Sensor velocidad": ((500, 240), (-60, -90)),
                "Palanca": ((700, 260), (-90, -100)),
                "Caja externa": ((400, 360), (60, -80)),
                "Sello junta": ((600, 340), (-100, -50)),
                "Montura": ((800, 320), (-120, -80))
            }
        }

        coords_detalles = coordenadas_custom.get(parte, {})

        for nombre in detalles:
            if nombre not in coords_detalles:
                continue  # Saltar si no tiene coordenadas

            (x, y), (dx, dy) = coords_detalles[nombre]
            x_escalado = int(x * escala) + x_centro
            y_escalado = int(y * escala) + margen_superior

            var = IntVar()
            chk = Checkbutton(modal, text=nombre, variable=var, bg="white")
            canvas.create_window(x_escalado, y_escalado, window=chk)

            # Flecha con dirección personalizada
            canvas.create_line(
                x_escalado, y_escalado,
                x_escalado + dx, y_escalado + dy,
                arrow="last", width=2, fill="white"
            )

            detalle_vars.append((nombre, var))

        def siguiente_parte():
            seleccionados = [el for el, v in detalle_vars if v.get()]
            revision_data[parte] = seleccionados
            modal.destroy()
            nonlocal idx
            idx += 1
            mostrar_parte()

        canvas.create_window(modal.winfo_screenwidth()//2, modal.winfo_screenheight() - 80, window=Button(modal, text="Siguiente", command=siguiente_parte))

    mostrar_parte()

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

    vin_label.config(text=f"VIN: {datos_obd['vin']}")

    vehiculo_data = {
        "marca": marca,
        "modelo": modelo,
        "year": int(year),
        "rpm": datos_obd["rpm"],
        "velocidad": datos_obd["velocidad"],
        "vin": datos_obd["vin"],
        "revision": revision_data
    }

    headers = {"Authorization": f"Bearer {token}"}
    response = requests.post(f"{API_URL}/guardar-vehiculo/", json=vehiculo_data, headers=headers)

    if response.status_code == 200:
        messagebox.showinfo("Éxito", "Datos del vehículo enviados correctamente.")
    else:
        messagebox.showerror("Error", f"No se pudo enviar: {response.text}")

# CONFIGURACIÓN UI PRINCIPAL
ventana = ttk.Window(themename="flatly")
ventana.attributes("-fullscreen", True)
ventana.iconbitmap(r"C:/Users/amartinsos/GestionTallerPFC/taller-front/public/favicon.ico")
ventana.title("Cliente OBD-II")
ventana.geometry("400x600")
ventana.configure(bg="#FFFFFF")

btn_style = {"bootstyle": "warning", "width": 20, "padding": 5}
entry_style = {"width": 30, "bootstyle": "light"}

login_frame = ttk.Frame(ventana, padding=20)
login_frame.pack(pady=50)

# LOGIN UI
ttk.Label(login_frame, text="Iniciar Sesión", font=("Arial", 16, "bold"), background="#FFFFFF", foreground="#E67E22").pack(pady=10)
usuario_entry = ttk.Entry(login_frame, **entry_style)
usuario_entry.pack(pady=5)
usuario_entry.insert(0, "Usuario")
password_entry = ttk.Entry(login_frame, show="*", **entry_style)
password_entry.pack(pady=5)
password_entry.insert(0, "Contraseña")
ttk.Button(login_frame, text="Login", command=obtener_token, **btn_style).pack(pady=10)

# MAIN FRAME
main_frame = ttk.Frame(ventana, padding=20)
ttk.Label(main_frame, text="Registro de Vehículo", font=("Arial", 14, "bold"), background="#FFFFFF", foreground="#E67E22").pack(pady=10)
ttk.Label(main_frame, text="Puerto OBD-II", background="#FFFFFF", foreground="#333").pack(pady=2)
puerto_combo = ttk.Combobox(main_frame, width=35)
puerto_combo.pack(pady=5)
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

btn_enviar = ttk.Button(main_frame, text="Revisión y Enviar", command=mostrar_modal_revision, **btn_style)
btn_enviar.pack(pady=20)
btn_enviar.config(state=DISABLED)

ventana.mainloop()
