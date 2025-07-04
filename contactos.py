import pandas as pd
import tkinter as tk
from tkinter import Button, Entry, Label, ttk, messagebox
import json
import os
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from tkinter import messagebox

check_vars = []  # lista de variables de checkboxes
modo_mensaje = False
checkbox_vars_por_id = {}
archivesubi=""
boton_enviar_masivo = None

CSV_FILE = os.path.join(archivesubi, "contactos.csv")


# Si no existe el archivo, crear uno con encabezados
if not os.path.exists(CSV_FILE):
    pd.DataFrame(columns=["Nombre", "Cumpleaños", "Ocupación", "Correo", "Teléfono", "Empresa", "Dirección"]).to_csv(CSV_FILE, index=False)

# Cargar dataset<
def cargar_datos():
    return pd.read_csv(CSV_FILE)

# Guardar dataset
def guardar_datos(df):
    df.to_csv(CSV_FILE, index=False)

# Aplicar filtros
def aplicar_filtros():
    global root
    global buscar_var
    global ocupacion_var
    nombre_filtro = buscar_var.get().lower()
    ocupacion_filtro = ocupacion_var.get()

    filtrado = df[df['Nombre'].str.lower().str.contains(nombre_filtro)]
    if ocupacion_filtro and ocupacion_filtro != "Todos":
        filtrado = filtrado[filtrado['Ocupación'] == ocupacion_filtro]
    
    mostrar_resultados(filtrado)

# Mostrar resultados
def mostrar_resultados(filtrado):
    global resultados_frame
    for widget in resultados_frame.winfo_children():
        widget.destroy()

    for _, fila in filtrado.iterrows():
        contenedor = ttk.Frame(resultados_frame)
        contenedor.pack(fill="x", pady=2)

        texto = f"{fila['Nombre']} | {fila['Teléfono']} | {fila['Correo']} | {fila['Empresa']} | {fila['Ocupación']}"
        ttk.Label(contenedor, text=texto).pack(side="left")

        ttk.Button(contenedor, text="Ver más", command=lambda f=fila: ver_detalles(f)).pack(side="right")

# Ver más detalles
def ver_detalles(fila):
    global root
    ventana = tk.Toplevel(root)
    ventana.title(f"Detalles de {fila['Nombre']}")

    ttk.Label(ventana, text=f"Cumpleaños: {fila['Cumpleaños']}").pack()
    ttk.Label(ventana, text=f"Dirección: {fila['Dirección']}").pack()

    ttk.Button(ventana, text="Eliminar", command=lambda: eliminar_registro(fila, ventana)).pack(pady=5)
    ttk.Button(ventana, text="Editar", command=lambda: editar_registro(fila, ventana)).pack()

# Eliminar
def eliminar_registro(fila, ventana):
    global df
    df = df[df['Correo'] != fila['Correo']]
    guardar_datos(df)
    aplicar_filtros()
    ventana.destroy()
    messagebox.showinfo("Eliminado", "Registro eliminado.")

# Editar
def editar_registro(fila, ventana):
    global root
    ventana_editar = tk.Toplevel(root)
    ventana_editar.title(f"Editar {fila['Nombre']}")
    entradas = {}

    for campo in df.columns:
        ttk.Label(ventana_editar, text=campo).pack()
        entrada = ttk.Entry(ventana_editar)
        entrada.insert(0, fila[campo])
        entrada.pack()
        entradas[campo] = entrada

    def guardar_edicion():
        global df
        df = df[df['Correo'] != fila['Correo']]  # Eliminar antiguo
        nuevo = {k: v.get() for k, v in entradas.items()}
        df = pd.concat([df, pd.DataFrame([nuevo])], ignore_index=True)
        guardar_datos(df)
        aplicar_filtros()
        ventana_editar.destroy()
        ventana.destroy()
        messagebox.showinfo("Editado", "Registro actualizado.")

    ttk.Button(ventana_editar, text="Guardar", command=guardar_edicion).pack(pady=5)

# Agregar nuevo
def agregar_nuevo():
    global root
    ventana_nuevo = tk.Toplevel(root)
    ventana_nuevo.title("Agregar persona")
    entradas = {}

    for campo in df.columns:
        ttk.Label(ventana_nuevo, text=campo).pack()
        entrada = ttk.Entry(ventana_nuevo)
        entrada.pack()
        entradas[campo] = entrada

    def guardar_nuevo():
        global df
        nuevo = {k: v.get() for k, v in entradas.items()}
        df = pd.concat([df, pd.DataFrame([nuevo])], ignore_index=True)
        guardar_datos(df)
        aplicar_filtros()
        actualizar_opciones_ocupacion()
        ventana_nuevo.destroy()
        messagebox.showinfo("Agregado", "Persona agregada.")

    ttk.Button(ventana_nuevo, text="Guardar", command=guardar_nuevo).pack(pady=5)

def activar_mensaje_masivo():
    global modo_mensaje
    modo_mensaje = not modo_mensaje
    if not modo_mensaje:
        checkbox_vars_por_id.clear()
    aplicar_filtros()


def mostrar_resultados(filtrado):
    global root
    global resultados_frame
    global boton_enviar_masivo

    for widget in resultados_frame.winfo_children():
        widget.destroy()

    check_vars.clear()

    for _, fila in filtrado.iterrows():
        contenedor = ttk.Frame(resultados_frame)
        contenedor.pack(fill="x", pady=2)

        correo_id = fila["Correo"]

        if modo_mensaje:
            if correo_id not in checkbox_vars_por_id:
                checkbox_vars_por_id[correo_id] = tk.BooleanVar()
            var = checkbox_vars_por_id[correo_id]
            chk = ttk.Checkbutton(contenedor, variable=var)
            chk.pack(side="left")
            check_vars.append((var, fila))

        texto = f"{fila['Nombre']} | {fila['Teléfono']} | {fila['Correo']} | {fila['Empresa']} | {fila['Ocupación']}"
        ttk.Label(contenedor, text=texto).pack(side="left")

        if not modo_mensaje:
            ttk.Button(contenedor, text="Ver más", command=lambda f=fila: ver_detalles(f)).pack(side="right")

    # Eliminar botón previo si existe
    if boton_enviar_masivo and boton_enviar_masivo.winfo_exists():
        boton_enviar_masivo.destroy()
        boton_enviar_masivo = None

    if modo_mensaje:
        boton_enviar_masivo = ttk.Button(root, text="Enviar mensaje", command=abrir_ventana_mensaje)
        boton_enviar_masivo.pack(pady=10)




def abrir_ventana_mensaje():
    global root
    seleccionados = [
        fila for correo, var in checkbox_vars_por_id.items()
        if var.get() and not df[df['Correo'] == correo].empty
        for _, fila in df[df['Correo'] == correo].iterrows()
    ]

    if not seleccionados:
        messagebox.showwarning("Sin selección", "No seleccionaste a nadie.")
        return

    ventana_mensaje = tk.Toplevel(root)
    ventana_mensaje.title("Enviar mensaje masivo")

    ttk.Label(ventana_mensaje, text=f"Personas seleccionadas: {len(seleccionados)}").pack(pady=5)
    mensaje_var = tk.Text(ventana_mensaje, width=60, height=10)
    mensaje_var.pack(padx=10)

    def enviar_whatsapp():
        errores = []

        # Inicializar navegador con Selenium (usa ChromeDriver)
        from selenium.webdriver.chrome.options import Options
        chrome_options = Options()
        chrome_options.add_argument("user-data-dir=./perfil_whatsapp")  # Carpeta donde se guarda la sesión
        driver = webdriver.Chrome(options=chrome_options)
        driver.get("https://web.whatsapp.com")

        # Esperar escaneo de código QR
        input("Escanea el código QR y presiona Enter para continuar...")

        for persona in seleccionados:
            try:
                numero = persona["Telefono"].replace("+", "").replace(" ", "")
                url = f"https://web.whatsapp.com/send?phone={numero}&text={mensaje_var}"
                driver.get(url)
                time.sleep(10)  # espera a que cargue el chat (ajustable según tu red)

                # Buscar y hacer clic en el botón de enviar
                enviar_btn = driver.find_element(By.XPATH, '//span[@data-icon="send"]')
                enviar_btn.click()
                time.sleep(2)  # breve pausa entre mensajes

            except Exception as e:
                errores.append((persona["Telefono"], str(e)))

        driver.quit()

        if errores:
            errores_str = "\n".join([f"{tel}: {err}" for tel, err in errores])
            messagebox.showerror("Errores al enviar", errores_str)
        else:
            messagebox.showinfo("Éxito", "Mensajes de WhatsApp enviados correctamente.")


    def mostrar_formulario_correo():
        formulario = tk.Toplevel(ventana_mensaje)
        formulario.title("Credenciales de correo")
        formulario.geometry("300x150")

        ttk.Label(formulario, text="Correo Gmail:").pack(pady=5)
        correo_entry = ttk.Entry(formulario)
        correo_entry.pack()

        ttk.Label(formulario, text="Contraseña (App Password):").pack(pady=5)
        contra_entry = ttk.Entry(formulario, show="*")
        contra_entry.pack()

        def autenticar_y_enviar():
            remitente = correo_entry.get()
            password = contra_entry.get()
            mensaje = mensaje_var.get("1.0", "end").strip()

            if not remitente or not password:
                messagebox.showwarning("Campos vacíos", "Completa ambos campos.")
                return

            import smtplib
            from email.mime.text import MIMEText

            errores = []
            for persona in seleccionados:
                try:
                    msg = MIMEText(mensaje)
                    msg["Subject"] = "Mensaje Masivo"
                    msg["From"] = remitente
                    msg["To"] = persona["Correo"]

                    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
                        server.login(remitente, password)
                        server.send_message(msg)
                except Exception as e:
                    errores.append((persona["Correo"], str(e)))

            if errores:
                errores_str = "\n".join([f"{c}: {err}" for c, err in errores])
                messagebox.showerror("Errores al enviar", errores_str)
            else:
                messagebox.showinfo("Éxito", "Correos enviados correctamente.")
            formulario.destroy()

        ttk.Button(formulario, text="Enviar correos", command=autenticar_y_enviar).pack(pady=10)

    # Botones de envío
    ttk.Button(ventana_mensaje, text="Enviar por WhatsApp", command=enviar_whatsapp).pack(pady=5)
    ttk.Button(ventana_mensaje, text="Enviar por correo", command=mostrar_formulario_correo).pack(pady=5)


def actualizar_opciones_ocupacion():
    global ocupacion_var
    global ocupacion_menu
    ocupaciones_actuales = ["Todos"] + sorted(set(df['Ocupación'].dropna().unique()))
    menu =  ocupacion_menu["menu"]
    menu.delete(0, "end")
    for ocupacion in ocupaciones_actuales:
        menu.add_command(label=ocupacion, command=lambda v=ocupacion: ocupacion_var.set(v))



def pantallaprincipal():
    # === INTERFAZ PRINCIPAL ===
    global df
    df = cargar_datos()
    global root 
    root= tk.Tk()
    root.title("Gestión de Contactos")
    root.geometry("900x600")
    root.minsize(800, 500)

    # Frame para filtros en horizontal
    filtros_frame = ttk.Frame(root)
    filtros_frame.pack(fill="x", padx=10, pady=5)

    # Filtro por nombre
    global buscar_var
    buscar_var = tk.StringVar()
    ttk.Label(filtros_frame, text="Buscar por nombre:").grid(row=0, column=0, padx=5)
    ttk.Entry(filtros_frame, textvariable=buscar_var, width=30).grid(row=0, column=1, padx=5)

    # Filtro por ocupación
    ocupaciones = ["Todos"] + sorted(set(df['Ocupación'].dropna().unique()))
    global ocupacion_var
    ocupacion_var = tk.StringVar(value="Todos")
    ttk.Label(filtros_frame, text="Filtrar por ocupación:").grid(row=0, column=2, padx=5)
    global ocupacion_menu
    ocupacion_menu = ttk.OptionMenu(filtros_frame, ocupacion_var, ocupacion_var.get(), *ocupaciones)
    ocupacion_menu.grid(row=0, column=3, padx=5)

    # Botón aplicar
    ttk.Button(filtros_frame, text="Aplicar filtros", command=aplicar_filtros).grid(row=0, column =4, padx=5)

    # Lista de resultados con scroll
    canvas = tk.Canvas(root)
    scroll = ttk.Scrollbar(root, orient="vertical", command=canvas.yview)
    global resultados_frame
    resultados_frame = ttk.Frame(canvas)

    resultados_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
    canvas.create_window((0, 0), window=resultados_frame, anchor="nw")
    canvas.configure(yscrollcommand=scroll.set)

    canvas.pack(side="left", fill="both", expand=True, padx=10, pady=5)
    scroll.pack(side="right", fill="y")

    # Botón agregar
    ttk.Button(root, text="Agregar persona", command=agregar_nuevo).pack(pady=10)
    ttk.Button(root, text="Mensaje Masivo", command=activar_mensaje_masivo).pack(pady=10)


    aplicar_filtros()
    root.mainloop()


def first_time_execution():
    global config_file
    global archivesubi
    config_file = "first_run.txt"
    if not os.path.exists(config_file):
        # Code to be executed only once
        print("es mi primera vez")

        # Create the configuration file with a flag
        with open(config_file, "w") as file:
            file.write("")
        popup = tk.Tk()
        popup.title("info")
        direccionarch = Entry(popup)
        direccionarchlabel = Label(popup, text="direccion donde se guardan los archivos", fg="gray")
        direccionarchlabel.grid(row=2, column=2)
        direccionarch.grid(row=3, column=2)

        def guardarubi2():
            archubi = direccionarch.get()
            with open(config_file, "w") as file:
                file.write(archubi)
            print("se guardo la nueva ubicacion de los archivos")

        archivesboton = Button(popup, text="guardar", command=guardarubi2)
        archivesboton.grid(row=3, column=3)

        close_button = Button(popup, text="Close", command=popup.destroy)
        close_button.grid(row=4, column=2)
        popup.mainloop()
        try:
            with open('data.json', 'r') as file:
                data = json.load(file)  # Load the existing data as a Python object
        except FileNotFoundError:
            data = []
    else:
        with open(config_file, "r") as file:
            print("no es la primera vez")
            content = file.read()
            archivesubi = content 
        pantallaprincipal()


first_time_execution()