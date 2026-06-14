import ssl 
import urllib.request
import threading
import time

# Bypass de seguridad para conexiones locales
try:
    ssl._create_default_https_context = ssl._create_unverified_context
except AttributeError:
    pass

import flet as ft
import requests
import json
import os
from datetime import datetime

# ==========================================
# ☁️ LLAVES DE LA BÓVEDA FIREBASE
# ==========================================
API_KEY = "AIzaSyAZ2hZQET0JUvFxUkyp-SrvZapaxh4xRw8"
DATABASE_URL = "https://eapp-rgrej-default-rtdb.firebaseio.com"

# ==========================================
# 🎙️ SPEECH RECOGNITION
# ==========================================
try:
    import speech_recognition as sr
    SR_AVAILABLE = True
except ImportError:
    SR_AVAILABLE = False

# ==========================================
# 📄 FÁBRICA DE PDF Y LIMPIEZA DE EMOJIS
# ==========================================
def limpiar_texto(texto):
    return str(texto).encode('latin-1', 'ignore').decode('latin-1').strip()

try:
    from fpdf import FPDF
    class PDFFirmado(FPDF):
        def footer(self):
            self.set_y(-15)
            self.set_font("Arial", "I", 10)
            self.set_text_color(128, 128, 128)
            self.cell(0, 10, limpiar_texto("EApp 6.5 by Rogelio Grej - rogeliogrej@gmail.com"), align="C")
    PDF_DISPONIBLE = True
except ImportError:
    PDF_DISPONIBLE = False

def main(page: ft.Page):
    # --- CONFIGURACIÓN GENERAL ---
    page.title = "EApp 6.5 by Rogelio Grej"
    page.theme_mode = "light"
    page.scroll = "adaptive"
    page.padding = 0
    # Fondo con gradiente para resaltar el Glassmorphism
    page.bgcolor = "#0F172A"
    
    # Audio elements
    # Removed flet_audio since it causes unknown control error on Desktop

    LANG = ["ES"]
    USER_TOKEN = [""]
    USER_ID = [""]
    tareas = []
    tarea_a_restaurar = [""]
    alarm_task_id = [""]

    TXT = {
        "ES": {
            "appbar": "EApp 6.5 by Rogelio Grej",
            "login_title": "EApp 6.5 Cloud",
            "login_sub": "Inicia sesión en tu bóveda en la nube",
            "correo": "Correo electrónico",
            "pass": "Contraseña",
            "olvide": "¿Olvidaste tu contraseña?",
            "entrar": "ENTRAR A LA NUBE ☁️",
            "crear_acc": "Crear una cuenta nueva",
            "tab_m": "Matriz",
            "tab_h": "Historial",
            "pdf_m": "Generar PDF Pendientes 📄",
            "pdf_h": "Generar PDF Historial 📄",
            "q1": "HACER (SS)", "q2": "PLANIFICAR (NS)", "q3": "DELEGAR (SN)", "q4": "ELIMINAR (NN)",
            "form_title": "Nueva Tarea ⚡",
            "lbl_tarea": "Nombre de la tarea",
            "lbl_rubro": "Rubro (ej. Ofimática)",
            "lbl_urg": "¿Urgente?",
            "lbl_imp": "¿Importante?",
            "cancel": "Cancelar",
            "save": "Guardar en Nube ☁️",
            "rest_title": "♻️ Restaurar a Matriz",
            "rest_sub": "¿A qué cuadrante deseas enviar esta tarea?",
            "rest_btn": "Restaurar",
            "rec_title": "Recuperar Cuenta 🔐",
            "rec_sub": "Firebase te enviará las instrucciones",
            "send_link": "ENVIAR ENLACE",
            "back": "⬅️ Volver al inicio",
            "reg_title": "Crear Cuenta ⚡",
            "reg_sub": "Tu cuenta se protegerá en Firebase",
            "reg_btn": "REGISTRARME",
            "empty": "(Sin tareas)",
            "empty_h": "Aún no has finalizado tareas.",
            "gen_date": "Reporte generado el:",
            "creacion": "Creada:",
            "fin": "Fin:",
            "new_task_btn": "NUEVA TAREA"
        },
        "EN": {
            "appbar": "EApp 6.5 by Rogelio Grej",
            "login_title": "EApp 6.5 Cloud",
            "login_sub": "Log in to your cloud vault",
            "correo": "Email Address",
            "pass": "Password",
            "olvide": "Forgot your password?",
            "entrar": "ENTER CLOUD ☁️",
            "crear_acc": "Create a new account",
            "tab_m": "Matrix",
            "tab_h": "History",
            "pdf_m": "Pending PDF 📄",
            "pdf_h": "History PDF 📄",
            "q1": "DO (YY)", "q2": "SCHEDULE (NY)", "q3": "DELEGATE (YN)", "q4": "DELETE (NN)",
            "form_title": "New Task ⚡",
            "lbl_tarea": "Task Name",
            "lbl_rubro": "Category (e.g. Office)",
            "lbl_urg": "Urgent?",
            "lbl_imp": "Important?",
            "cancel": "Cancel",
            "save": "Save to Cloud ☁️",
            "rest_title": "♻️ Restore to Matrix",
            "rest_sub": "Which quadrant do you want to send this task to?",
            "rest_btn": "Restore",
            "rec_title": "Recover Account 🔐",
            "rec_sub": "Firebase will send you instructions",
            "send_link": "SEND LINK",
            "back": "⬅️ Back to login",
            "reg_title": "Create Account ⚡",
            "reg_sub": "Your account is secured by Firebase",
            "reg_btn": "REGISTER",
            "empty": "(No tasks)",
            "empty_h": "No finished tasks yet.",
            "gen_date": "Report generated on:",
            "creacion": "Created:",
            "fin": "Done:",
            "new_task_btn": "NEW TASK"
        }
    }

    # Glassmorphism helpers
    def border_all(w, c): return ft.Border(ft.BorderSide(w, c), ft.BorderSide(w, c), ft.BorderSide(w, c), ft.BorderSide(w, c))

    def glass_container(content, padding=20):
        return ft.Container(
            content=content,
            bgcolor="#1AFFFFFF",
            border_radius=20,
            padding=padding,
            blur=ft.Blur(15, 15, ft.BlurTileMode.MIRROR),
            border=border_all(1, "#4DFFFFFF"),
            shadow=ft.BoxShadow(blur_radius=20, color="#20000000")
        )

    lbl_appbar = ft.Text("EApp 6.5 by Rogelio Grej", weight="bold", color="#FFFFFF")
    lbl_login_title = ft.Text("EApp 6.5 Cloud", size=32, weight="extrabold", color="#FFFFFF")
    lbl_login_sub = ft.Text("Inicia sesión en tu bóveda en la nube", size=14, color="#CBD5E1")
    campo_correo = ft.TextField(label="Correo electrónico", width=300, border_radius=10, color="white", border_color="#FFFFFF", cursor_color="white")
    campo_pass = ft.TextField(label="Contraseña", password=True, width=300, border_radius=10, color="white", border_color="#FFFFFF", cursor_color="white")
    
    btn_olvide = ft.TextButton("¿Olvidaste tu contraseña?", style=ft.ButtonStyle(color="#93C5FD"))
    btn_login = ft.ElevatedButton("ENTRAR A LA NUBE ☁️", bgcolor="#F59E0B", color="white", width=300, height=50)
    btn_crear = ft.TextButton("Crear una cuenta nueva", style=ft.ButtonStyle(color="#60A5FA"))
    
    lbl_reg_title = ft.Text("Crear Cuenta ⚡", size=28, weight="bold", color="#FFFFFF")
    lbl_reg_sub = ft.Text("Tu cuenta se protegerá en Firebase", color="#CBD5E1")
    reg_correo = ft.TextField(label="Nuevo Correo", width=300, border_radius=10, color="white", border_color="#FFFFFF")
    reg_pass = ft.TextField(label="Nueva Contraseña", password=True, width=300, border_radius=10, color="white", border_color="#FFFFFF")
    
    btn_reg_confirm = ft.ElevatedButton("REGISTRARME", bgcolor="#4CAF50", color="white", width=300, height=50)
    btn_reg_volver = ft.TextButton("⬅️ Volver al inicio", style=ft.ButtonStyle(color="white"))

    lbl_rec_title = ft.Text("Recuperar Cuenta 🔐", size=28, weight="bold", color="#FFFFFF")
    lbl_rec_sub = ft.Text("Firebase te enviará las instrucciones", color="#CBD5E1")
    recup_correo = ft.TextField(label="Tu correo registrado", width=300, border_radius=10, color="white", border_color="#FFFFFF")
    btn_rec_enviar = ft.ElevatedButton("ENVIAR ENLACE", bgcolor="#2196F3", color="white", width=300, height=50)
    btn_rec_volver = ft.TextButton("⬅️ Volver al inicio", style=ft.ButtonStyle(color="white"))

    txt_tab_matriz = ft.Text("Matriz", weight="bold", size=16, color="white")
    txt_tab_hist = ft.Text("Historial", weight="bold", size=16, color="white")
    
    btn_pdf_m = ft.ElevatedButton("Generar PDF Pendientes 📄", bgcolor="#FF5722", color="white")
    btn_pdf_h = ft.ElevatedButton("Generar PDF Historial 📄", bgcolor="#FF5722", color="white")

    txt_q1 = ft.Text("HACER (SS)", size=18, weight="bold", color="#FFFFFF")
    txt_q2 = ft.Text("PLANIFICAR (NS)", size=18, weight="bold", color="#FFFFFF")
    txt_q3 = ft.Text("DELEGAR (SN)", size=18, weight="bold", color="#FFFFFF")
    txt_q4 = ft.Text("ELIMINAR (NN)", size=18, weight="bold", color="#FFFFFF")

    lbl_form_title = ft.Text("Nueva Tarea ⚡", weight="bold", size=20, color="#FFFFFF")
    input_tarea = ft.TextField(label="Nombre de la tarea", label_style=ft.TextStyle(color="#B3FFFFFF"), expand=True, color="white", border_color="white")
    
    input_rubro = ft.TextField(label="Rubro (ej. Ofimática)", label_style=ft.TextStyle(color="#B3FFFFFF"), color="white", border_color="white")
    dd_urgente = ft.Dropdown(label="¿Urgente?", label_style=ft.TextStyle(color="#B3FFFFFF"), text_size=14, width=120, color="black", bgcolor="white")
    dd_importante = ft.Dropdown(label="¿Importante?", label_style=ft.TextStyle(color="#B3FFFFFF"), text_size=14, width=120, color="black", bgcolor="white")
    
    # Selector de alarma manual temporal
    input_alarma = ft.TextField(label="Alarma (YYYY-MM-DD HH:MM)", hint_text="Ej: 2026-06-13 18:30", label_style=ft.TextStyle(color="#B3FFFFFF"), color="white", border_color="white", expand=True)

    btn_cancelar = ft.TextButton("Cancelar", style=ft.ButtonStyle(color="white"))
    btn_guardar = ft.ElevatedButton("Guardar en Nube ☁️", bgcolor="#4CAF50", color="white")

    lbl_rest_title = ft.Text("♻️ Restaurar a Matriz", weight="bold", size=18, color="#FFFFFF")
    lbl_rest_sub = ft.Text("¿A qué cuadrante deseas enviar esta tarea?", color="white")
    dd_cuad_rest = ft.Dropdown(label="Elige el nuevo cuadrante", color="black", bgcolor="white")
    btn_rest_cancel = ft.TextButton("Cancelar", style=ft.ButtonStyle(color="white"))
    btn_rest_confirm = ft.ElevatedButton("Restaurar", bgcolor="#F59E0B", color="white")

    btn_nueva_tarea = ft.ElevatedButton("NUEVA TAREA", bgcolor="#F59E0B", color="white", height=50, on_click=lambda e: (setattr(panel_ingreso, 'visible', True), page.update()))
    btn_lang = ft.TextButton("🌍", tooltip="English / Español", style=ft.ButtonStyle(color="white", text_style=ft.TextStyle(size=24)))

    lista_hacer = ft.Column()
    lista_planificar = ft.Column()
    lista_delegar = ft.Column()
    lista_eliminar = ft.Column()
    lista_historial = ft.Column(spacing=10)



    # ===============================
    # MANEJO DE ESTADO Y RED ASINCRONO
    # ===============================
    def obtener_fecha(): return datetime.now().strftime("%d/%m/%Y %I:%M %p")

    def cargar_datos():
        if not USER_ID[0]: return
        url = f"{DATABASE_URL}/users/{USER_ID[0]}/tareas.json?auth={USER_TOKEN[0]}"
        def run():
            try:
                res = requests.get(url, timeout=10)
                if res.status_code == 200 and res.text != 'null':
                    data = res.json()
                    tareas.clear()
                    if isinstance(data, list): tareas.extend([t for t in data if t is not None])
                    elif isinstance(data, dict): tareas.extend(list(data.values()))
                actualizar_vistas()
            except Exception as e: 
                print("Error cargando:", e)
                page.snack_bar = ft.SnackBar(ft.Text("Error al cargar datos. Comprueba tu conexión.", color="white"), bgcolor="red")
                page.snack_bar.open = True; page.update()
        threading.Thread(target=run).start()

    def guardar_datos():
        if not USER_ID[0]: return
        url = f"{DATABASE_URL}/users/{USER_ID[0]}/tareas.json?auth={USER_TOKEN[0]}"
        def run():
            try: 
                requests.put(url, json=tareas, timeout=10)
            except Exception as e: 
                print("Error guardando:", e)
                page.snack_bar = ft.SnackBar(ft.Text("Error al guardar en la nube.", color="white"), bgcolor="red")
                page.snack_bar.open = True; page.update()
        threading.Thread(target=run).start()

    def finalizar_tarea(e):
        for t in tareas:
            if t["nombre"] == e.control.data and t.get("estado") == "pendiente":
                t["estado"] = "finalizada"
                t["fecha_fin"] = obtener_fecha()
                t["alarm_active"] = False
                break
        guardar_datos()
        actualizar_vistas()

    def eliminar_tarea_definitiva(e):
        nombre_tarea = e.control.data
        tareas[:] = [t for t in tareas if t["nombre"] != nombre_tarea]
        guardar_datos()
        actualizar_vistas()
        page.snack_bar = ft.SnackBar(ft.Text("🗑️ Tarea eliminada", color="white"), bgcolor="#E53935")
        page.snack_bar.open = True; page.update()

    def abrir_panel_restaurar(e):
        tarea_a_restaurar[0] = e.control.data
        panel_restaurar.visible = True; page.update()

    def ocultar_panel_restaurar(e=None):
        panel_restaurar.visible = False; page.update()

    def confirmar_restauracion(e):
        val = dd_cuad_rest.value
        mapa_en_es = {"DO": "HACER", "SCHEDULE": "PLANIFICAR", "DELEGATE": "DELEGAR", "DELETE": "ELIMINAR"}
        nuevo_cuadrante = mapa_en_es.get(val, val)
        for t in tareas:
            if t["nombre"] == tarea_a_restaurar[0] and t.get("estado") == "finalizada":
                t["estado"] = "pendiente"
                t["cuadrante"] = nuevo_cuadrante
                t["fecha_fin"] = ""
                break
        guardar_datos()
        ocultar_panel_restaurar()
        actualizar_vistas()
        page.snack_bar = ft.SnackBar(ft.Text(f"✅ Tarea restaurada a {nuevo_cuadrante}", color="white"), bgcolor="#4CAF50")
        page.snack_bar.open = True; page.update()

    def agregar_tarea_submit(e):
        if not input_tarea.value: return
        u, i = dd_urgente.value, dd_importante.value
        is_urg = u in ["SÍ", "YES"]
        is_imp = i in ["SÍ", "YES"]
        c = "HACER" if is_urg and is_imp else "PLANIFICAR" if not is_urg and is_imp else "DELEGAR" if is_urg and not is_imp else "ELIMINAR"
        
        tareas.append({
            "nombre": input_tarea.value, 
            "rubro": input_rubro.value or "General", 
            "cuadrante": c, 
            "estado": "pendiente", 
            "fecha_ingreso": obtener_fecha(),
            "alarm_time": input_alarma.value,
            "alarm_active": True if input_alarma.value else False
        })
        guardar_datos()
        input_tarea.value = ""
        input_rubro.value = ""
        input_alarma.value = ""
        panel_ingreso.visible = False
        actualizar_vistas()

    # ===============================
    # SISTEMA DE ALARMAS BACKGROUND
    # ===============================
    def revisar_alarmas():
        while True:
            try:
                if USER_ID[0]:
                    ahora = datetime.now()
                    for t in tareas:
                        if t.get("estado") == "pendiente" and t.get("alarm_active") and t.get("alarm_time"):
                            # Parsear la hora
                            alarm_dt = None
                            time_str = t["alarm_time"].strip()
                            try:
                                if len(time_str) <= 5 and ":" in time_str:
                                    dt_t = datetime.strptime(time_str, "%H:%M")
                                    alarm_dt = ahora.replace(hour=dt_t.hour, minute=dt_t.minute, second=0)
                                else:
                                    alarm_dt = datetime.strptime(time_str, "%Y-%m-%d %H:%M")
                            except: pass

                            if alarm_dt and (ahora >= alarm_dt) and (ahora - alarm_dt).total_seconds() < 300:
                                t["alarm_active"] = False
                                
                                # Reproducir audio nativo Flet y vibración
                                try:
                                    page.window_to_front()
                                except: pass
                                
                                try:
                                    alarm_audio.play()
                                    haptic_fb.heavy_impact()
                                except Exception as ex: 
                                    print("Error reproduciendo alarma:", ex)
                                
                                # Show notification
                                page.snack_bar = ft.SnackBar(ft.Text(f"⏰ ALARMA: {t['nombre']}", size=20, weight="bold", color="white"), bgcolor="red", duration=8000)
                                page.snack_bar.open = True
                                page.update()
                                guardar_datos()
            except Exception as e: pass
            time.sleep(10) # Revisa cada 10 segundos
            
    threading.Thread(target=revisar_alarmas, daemon=True).start()

    # ==========================================
    # 📄 GENERADORES DE PDF (LAZY IMPORT TKINTER)
    # ==========================================
    def pedir_ruta_guardado(nombre_por_defecto, titulo):
        if not page.web:
            try:
                import tkinter as tk
                from tkinter import filedialog
                root = tk.Tk()
                root.withdraw()
                root.attributes('-topmost', True) 
                ruta = filedialog.asksaveasfilename(defaultextension=".pdf", initialfile=nombre_por_defecto, title=titulo, filetypes=[("Archivos PDF", "*.pdf")])
                root.destroy()
                return ruta
            except:
                return nombre_por_defecto
        else:
            return nombre_por_defecto

    def generar_pdf_matriz(e):
        if not PDF_DISPONIBLE: return
        ruta_elegida = pedir_ruta_guardado("Matriz_Pendientes.pdf", "Guardar Matriz")
        if ruta_elegida:
            t_lang = TXT[LANG[0]]
            pdf = PDFFirmado() 
            pdf.add_page()
            pdf.set_font("Arial", 'B', 16)
            titulo_limpio = limpiar_texto(f"{t_lang['appbar']} - {t_lang['tab_m']}")
            pdf.cell(0, 10, titulo_limpio, ln=True, align="C")
            pdf.set_font("Arial", 'I', 10)
            fecha_limpia = limpiar_texto(f"{t_lang['gen_date']} {obtener_fecha()}")
            pdf.cell(0, 10, fecha_limpia, ln=True, align="C")
            pdf.ln(5)
            
            pendientes = [t for t in tareas if t.get("estado", "pendiente") == "pendiente"]
            cuadrantes = {"HACER": [], "PLANIFICAR": [], "DELEGAR": [], "ELIMINAR": []}
            q_map_en = {"HACER": "DO", "PLANIFICAR": "SCHEDULE", "DELEGAR": "DELEGATE", "ELIMINAR": "DELETE"}
            
            for t in pendientes:
                c = t.get("cuadrante", "HACER")
                if c in cuadrantes: cuadrantes[c].append(t)
            
            for cuad, lista in cuadrantes.items():
                if lista:
                    c_text = cuad if LANG[0] == "ES" else q_map_en.get(cuad, cuad)
                    pdf.set_font("Arial", 'B', 12)
                    pdf.set_fill_color(230, 230, 230)
                    pdf.cell(0, 8, limpiar_texto(f"  {c_text}  "), ln=True, fill=True)
                    pdf.set_font("Arial", '', 10)
                    for t in lista:
                        texto = f"   - [{t.get('rubro', 'General')}] {t['nombre']} | {t_lang['creacion']} {t.get('fecha_ingreso', 'N/A')}"
                        pdf.cell(0, 8, limpiar_texto(texto), ln=True)
                    pdf.ln(5)
            pdf.output(ruta_elegida) 
            if page.web: page.launch_url(f"/{ruta_elegida}")
            page.snack_bar = ft.SnackBar(ft.Text("¡PDF procesado con éxito! 📄", color="white"), bgcolor="#4CAF50")
            page.snack_bar.open = True; page.update()

    def generar_pdf_historial(e):
        if not PDF_DISPONIBLE: return
        ruta_elegida = pedir_ruta_guardado("Historial_Tareas.pdf", "Guardar Historial")
        if ruta_elegida:
            t_lang = TXT[LANG[0]]
            pdf = PDFFirmado() 
            pdf.add_page()
            pdf.set_font("Arial", 'B', 16)
            titulo_limpio = limpiar_texto(f"{t_lang['appbar']} - {t_lang['tab_h']}")
            pdf.cell(0, 10, titulo_limpio, ln=True, align="C")
            pdf.set_font("Arial", 'I', 10)
            fecha_limpia = limpiar_texto(f"{t_lang['gen_date']} {obtener_fecha()}")
            pdf.cell(0, 10, fecha_limpia, ln=True, align="C")
            pdf.ln(5)
            
            finalizadas = [t for t in tareas if t.get("estado") == "finalizada"]
            cuadrantes = {"HACER": [], "PLANIFICAR": [], "DELEGAR": [], "ELIMINAR": []}
            q_map_en = {"HACER": "DO", "PLANIFICAR": "SCHEDULE", "DELEGAR": "DELEGATE", "ELIMINAR": "DELETE"}
            
            for t in finalizadas:
                c = t.get("cuadrante", "HACER")
                if c in cuadrantes: cuadrantes[c].append(t)
                
            for cuad, lista in cuadrantes.items():
                if lista:
                    c_text = cuad if LANG[0] == "ES" else q_map_en.get(cuad, cuad)
                    pdf.set_font("Arial", 'B', 12)
                    pdf.set_fill_color(230, 230, 230)
                    pdf.cell(0, 8, limpiar_texto(f"  {c_text}  "), ln=True, fill=True)
                    pdf.set_font("Arial", '', 10)
                    for t in lista:
                        texto = f"   - [{t.get('rubro', 'General')}] {t['nombre']} | {t_lang['creacion']} {t.get('fecha_ingreso', 'N/A')} | {t_lang['fin']} {t.get('fecha_fin', '')}"
                        pdf.cell(0, 8, limpiar_texto(texto), ln=True)
                    pdf.ln(5)
            pdf.output(ruta_elegida)
            if page.web: page.launch_url(f"/{ruta_elegida}")
            page.snack_bar = ft.SnackBar(ft.Text("¡PDF procesado con éxito! 📄", color="white"), bgcolor="#4CAF50")
            page.snack_bar.open = True; page.update()

    btn_pdf_m.on_click = generar_pdf_matriz
    btn_pdf_h.on_click = generar_pdf_historial

    def aplicar_idioma():
        try:
            t = TXT[LANG[0]]
            lbl_appbar.value = t["appbar"]
            lbl_login_title.value = t["login_title"]
            lbl_login_sub.value = t["login_sub"]
            campo_correo.label = t["correo"]
            campo_pass.label = t["pass"]
            btn_olvide.text = t["olvide"]
            btn_login.text = t["entrar"]
            btn_crear.text = t["crear_acc"]
            txt_tab_matriz.value = t["tab_m"]
            txt_tab_hist.value = t["tab_h"]
            btn_pdf_m.text = t["pdf_m"]
            btn_pdf_h.text = t["pdf_h"]
            btn_nueva_tarea.text = t["new_task_btn"]
            txt_q1.value = t["q1"]
            txt_q2.value = t["q2"]
            txt_q3.value = t["q3"]
            txt_q4.value = t["q4"]
            lbl_form_title.value = t["form_title"]
            input_tarea.label = t["lbl_tarea"]
            input_rubro.label = t["lbl_rubro"]
            dd_urgente.label = t["lbl_urg"]
            dd_importante.label = t["lbl_imp"]
            btn_cancelar.text = t["cancel"]
            btn_guardar.text = t["save"]
            lbl_rest_title.value = t["rest_title"]
            lbl_rest_sub.value = t["rest_sub"]
            btn_rest_cancel.text = t["cancel"]
            btn_rest_confirm.text = t["rest_btn"]
            lbl_rec_title.value = t["rec_title"]
            lbl_rec_sub.value = t["rec_sub"]
            recup_correo.label = t["correo"]
            btn_rec_enviar.text = t["send_link"]
            btn_rec_volver.text = t["back"]
            lbl_reg_title.value = t["reg_title"]
            lbl_reg_sub.value = t["reg_sub"]
            reg_correo.label = t["correo"]
            reg_pass.label = t["pass"]
            btn_reg_confirm.text = t["reg_btn"]
            btn_reg_volver.text = t["back"]

            if LANG[0] == "EN":
                dd_urgente.options = [ft.dropdown.Option("YES"), ft.dropdown.Option("NO")]
                dd_importante.options = [ft.dropdown.Option("YES"), ft.dropdown.Option("NO")]
                dd_cuad_rest.options = [ft.dropdown.Option("DO"), ft.dropdown.Option("SCHEDULE"), ft.dropdown.Option("DELEGATE"), ft.dropdown.Option("DELETE")]
                if dd_urgente.value == "SÍ": dd_urgente.value = "YES"
                if dd_importante.value == "SÍ": dd_importante.value = "YES"
            else:
                dd_urgente.options = [ft.dropdown.Option("SÍ"), ft.dropdown.Option("NO")]
                dd_importante.options = [ft.dropdown.Option("SÍ"), ft.dropdown.Option("NO")]
                dd_cuad_rest.options = [ft.dropdown.Option("HACER"), ft.dropdown.Option("PLANIFICAR"), ft.dropdown.Option("DELEGAR"), ft.dropdown.Option("ELIMINAR")]
                if dd_urgente.value == "YES": dd_urgente.value = "SÍ"
                if dd_importante.value == "YES": dd_importante.value = "SÍ"
        except Exception as e: pass
        actualizar_vistas()
        page.update()

    def toggle_lang(e):
        LANG[0] = "EN" if LANG[0] == "ES" else "ES"
        aplicar_idioma()
        
    btn_lang.on_click = toggle_lang

    def crear_tarjeta_dinamica(txt_control, color_fondo, contenedor):
        return ft.Container(
            content=ft.Column([txt_control, ft.Divider(color="#FFFFFF", opacity=0.3), contenedor]),
            bgcolor=color_fondo, border_radius=20, padding=20, 
            shadow=ft.BoxShadow(spread_radius=1, blur_radius=15, color="#30000000"),
            border=border_all(1, "#33FFFFFF") # Detalle glassmorphism
        )

    tarjeta_hacer = crear_tarjeta_dinamica(txt_q1, "#CCB91C1C", lista_hacer) # Rojo translucido
    tarjeta_planificar = crear_tarjeta_dinamica(txt_q2, "#CC1D4ED8", lista_planificar) # Azul
    tarjeta_delegar = crear_tarjeta_dinamica(txt_q3, "#CCB45309", lista_delegar) # Naranja
    tarjeta_eliminar = crear_tarjeta_dinamica(txt_q4, "#CC334155", lista_eliminar) # Gris

    def actualizar_vistas():
        t_lang = TXT[LANG[0]]
        lista_hacer.controls.clear(); lista_planificar.controls.clear(); lista_delegar.controls.clear(); lista_eliminar.controls.clear(); lista_historial.controls.clear()
        
        pendientes = [t for t in tareas if t.get("estado", "pendiente") == "pendiente"]
        finalizadas = [t for t in tareas if t.get("estado") == "finalizada"]
        q_map_en = {"HACER": "DO", "PLANIFICAR": "SCHEDULE", "DELEGAR": "DELEGATE", "ELIMINAR": "DELETE"}

        for t in pendientes:
            alarma_icon = f" ⏰ {t['alarm_time']}" if t.get("alarm_active") else ""
            item = ft.Container(
                content=ft.Row([
                    ft.TextButton("✔️", data=t["nombre"], on_click=finalizar_tarea, style=ft.ButtonStyle(color="#FFFFFF")),
                    ft.Text(value=f"[{t.get('rubro', 'General')}] {t['nombre']}{alarma_icon}", color="#FFFFFF", size=14, weight="w500", expand=True)
                ]), padding=2
            )
            q = t.get("cuadrante", "")
            if q == "HACER": lista_hacer.controls.append(item)
            elif q == "PLANIFICAR": lista_planificar.controls.append(item)
            elif q == "DELEGAR": lista_delegar.controls.append(item)
            elif q == "ELIMINAR": lista_eliminar.controls.append(item)

        for lista in [lista_hacer, lista_planificar, lista_delegar, lista_eliminar]:
            if not lista.controls: lista.controls.append(ft.Text(value=t_lang["empty"], color="#FFFFFF", opacity=0.7))

        for t in reversed(finalizadas):
            c_text = t['cuadrante'] if LANG[0] == "ES" else q_map_en.get(t['cuadrante'], t['cuadrante'])
            item_historial = ft.Container(
                content=ft.Row([
                    ft.Text("✅", size=18),
                    ft.Column([
                        ft.Text(value=t["nombre"], weight="bold", size=14, color="white"),
                        ft.Text(value=f"{c_text} | {t_lang['fin']} {t.get('fecha_fin', '')}", size=11, color="#CBD5E1")
                    ], expand=True), 
                    ft.TextButton("♻️", data=t["nombre"], on_click=abrir_panel_restaurar),
                    ft.TextButton("🗑️", data=t["nombre"], on_click=eliminar_tarea_definitiva)
                ]), bgcolor="#20FFFFFF", padding=10, border_radius=10, border=border_all(1, "#33FFFFFF")
            )
            lista_historial.controls.append(item_historial)
            
        if not lista_historial.controls: lista_historial.controls.append(ft.Text(value=t_lang["empty_h"], color="#CBD5E1"))
        page.update()

    def ocultar_panel(e=None):
        panel_ingreso.visible = False
        page.update()

    btn_cancelar.on_click = ocultar_panel
    btn_guardar.on_click = agregar_tarea_submit
    btn_rest_cancel.on_click = ocultar_panel_restaurar
    btn_rest_confirm.on_click = confirmar_restauracion

    panel_ingreso = glass_container(
        ft.Column([
            lbl_form_title, 
            input_tarea, 
            input_rubro,
            input_alarma,
            ft.Row([dd_urgente, dd_importante], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
            ft.Row([btn_cancelar, btn_guardar], alignment=ft.MainAxisAlignment.END)
        ])
    )
    panel_ingreso.visible = False
    panel_ingreso.margin = 15

    panel_restaurar = glass_container(
        ft.Column([
            lbl_rest_title,
            lbl_rest_sub,
            dd_cuad_rest,
            ft.Row([btn_rest_cancel, btn_rest_confirm], alignment=ft.MainAxisAlignment.END)
        ])
    )
    panel_restaurar.visible = False
    panel_restaurar.margin = 15

    row_botones_matriz = ft.Row([btn_nueva_tarea, btn_pdf_m], alignment=ft.MainAxisAlignment.END)
    row_botones_historial = ft.Row([btn_pdf_h], alignment=ft.MainAxisAlignment.END)

    vista_matriz = ft.Column([row_botones_matriz, panel_ingreso, tarjeta_hacer, tarjeta_planificar, tarjeta_delegar, tarjeta_eliminar], spacing=15, visible=True)
    vista_historial = ft.Column([row_botones_historial, panel_restaurar, ft.Divider(color="#33FFFFFF"), lista_historial], spacing=15, visible=False)

    def click_matriz(e): vista_matriz.visible, vista_historial.visible, btn_matriz.bgcolor, btn_historial.bgcolor = True, False, "#33FFFFFF", "#10FFFFFF"; page.update()
    def click_historial(e): vista_matriz.visible, vista_historial.visible, btn_matriz.bgcolor, btn_historial.bgcolor = False, True, "#10FFFFFF", "#33FFFFFF"; page.update()

    btn_matriz = ft.Container(content=ft.Row([txt_tab_matriz], alignment=ft.MainAxisAlignment.CENTER), on_click=click_matriz, padding=15, bgcolor="#33FFFFFF", border_radius=10, expand=1)
    btn_historial = ft.Container(content=ft.Row([txt_tab_hist], alignment=ft.MainAxisAlignment.CENTER), on_click=click_historial, padding=15, bgcolor="#10FFFFFF", border_radius=10, expand=1)

    appbar_principal = ft.AppBar(
        leading=ft.Container(content=ft.Image(src="assets/logo.png", width=30, height=30, fit=ft.BoxFit.CONTAIN), padding=10), 
        title=lbl_appbar, 
        bgcolor="#0F172A", 
        center_title=True,
        actions=[btn_lang]
    )
    
    contenedor_app = ft.Container(
        content=ft.Column([
            ft.Row([btn_matriz, btn_historial], alignment=ft.MainAxisAlignment.CENTER), 
            ft.Divider(color="transparent", height=5), 
            vista_matriz, vista_historial
        ]), 
        padding=20, visible=False, expand=True
    )

    def mostrar_pantalla_registro(e): contenedor_login.visible, contenedor_recuperar.visible, contenedor_registro.visible = False, False, True; page.update()
    def mostrar_pantalla_recuperar(e): contenedor_login.visible, contenedor_registro.visible, contenedor_recuperar.visible = False, False, True; page.update()
    def volver_al_login(e=None):
        contenedor_registro.visible, contenedor_recuperar.visible, contenedor_login.visible = False, False, True
        reg_correo.value, reg_pass.value, recup_correo.value = "", "", ""
        page.update()

    btn_olvide.on_click = mostrar_pantalla_recuperar
    btn_crear.on_click = mostrar_pantalla_registro
    btn_rec_volver.on_click = volver_al_login
    btn_reg_volver.on_click = volver_al_login

    def registrar_usuario(e):
        if not reg_correo.value or not reg_pass.value: return
        url = f"https://identitytoolkit.googleapis.com/v1/accounts:signUp?key={API_KEY}"
        payload = {"email": reg_correo.value, "password": reg_pass.value, "returnSecureToken": True}
        def run():
            try:
                res = requests.post(url, json=payload, timeout=10); data = res.json()
                if "error" in data: page.snack_bar = ft.SnackBar(ft.Text(value=f"⚠️ Error: {data['error']['message']}", color="white"), bgcolor="#E53935")
                else:
                    page.snack_bar = ft.SnackBar(ft.Text(value="✅ Cuenta creada en la nube.", color="white"), bgcolor="#4CAF50")
                    volver_al_login()
            except Exception as ex: 
                page.snack_bar = ft.SnackBar(ft.Text(value="⚠️ Error de conexión a Firebase.", color="white"), bgcolor="#E53935")
            page.snack_bar.open = True; page.update()
        threading.Thread(target=run).start()
    
    btn_reg_confirm.on_click = registrar_usuario

    def enviar_recuperacion(e):
        if not recup_correo.value: return
        url = f"https://identitytoolkit.googleapis.com/v1/accounts:sendOobCode?key={API_KEY}"
        payload = {"requestType": "PASSWORD_RESET", "email": recup_correo.value}
        def run():
            try:
                res = requests.post(url, json=payload, timeout=10); data = res.json()
                if "error" in data: page.snack_bar = ft.SnackBar(ft.Text(value="⚠️ Error verificando correo.", color="white"), bgcolor="#E53935")
                else:
                    page.snack_bar = ft.SnackBar(ft.Text(value="📧 ¡Enlace enviado! (Revisa tu carpeta de Spam).", color="white"), bgcolor="#4CAF50")
                    volver_al_login()
            except: page.snack_bar = ft.SnackBar(ft.Text(value="⚠️ Error de conexión a Firebase.", color="white"), bgcolor="#E53935")
            page.snack_bar.open = True; page.update()
        threading.Thread(target=run).start()
    
    btn_rec_enviar.on_click = enviar_recuperacion

    def iniciar_sesion(e):
        url = f"https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key={API_KEY}"
        payload = {"email": campo_correo.value, "password": campo_pass.value, "returnSecureToken": True}
        def run():
            try:
                res = requests.post(url, json=payload, timeout=10); data = res.json()
                if "error" in data: page.snack_bar = ft.SnackBar(ft.Text(value="⚠️ Credenciales incorrectas.", color="white"), bgcolor="#E53935")
                else:
                    USER_TOKEN[0], USER_ID[0] = data["idToken"], data["localId"]
                    cargar_datos()
                    contenedor_login.visible, contenedor_app.visible = False, True
                    page.appbar = appbar_principal
                    page.snack_bar = ft.SnackBar(ft.Text(value="¡Conectado a la Nube! ☁️⚡", color="white"), bgcolor="#4CAF50")
                    actualizar_vistas()
            except: page.snack_bar = ft.SnackBar(ft.Text(value="⚠️ Error de conexión.", color="white"), bgcolor="#E53935")
            page.snack_bar.open = True; page.update()
        threading.Thread(target=run).start()

    btn_login.on_click = iniciar_sesion

    # Sustituir iconos de nube por logo de usuario
    icono_nube_1 = ft.Image(src="assets/logo.png", width=120, height=120, fit=ft.BoxFit.CONTAIN)
    icono_nube_2 = ft.Image(src="assets/logo.png", width=120, height=120, fit=ft.BoxFit.CONTAIN)
    icono_nube_3 = ft.Image(src="assets/logo.png", width=120, height=120, fit=ft.BoxFit.CONTAIN)

    # Convertir pantallas de login a Glassmorphism
    contenedor_login = ft.Container(
        content=glass_container(ft.Column([icono_nube_1, lbl_login_title, lbl_login_sub, ft.Divider(color="transparent", height=10), campo_correo, campo_pass, btn_olvide, btn_login, btn_crear], alignment=ft.MainAxisAlignment.CENTER, horizontal_alignment=ft.CrossAxisAlignment.CENTER)),
        expand=True, visible=True, padding=40, alignment=ft.Alignment.CENTER
    )
    contenedor_registro = ft.Container(
        content=glass_container(ft.Column([icono_nube_2, lbl_reg_title, lbl_reg_sub, ft.Divider(color="transparent", height=10), reg_correo, reg_pass, btn_reg_confirm, btn_reg_volver], alignment=ft.MainAxisAlignment.CENTER, horizontal_alignment=ft.CrossAxisAlignment.CENTER)),
        expand=True, visible=False, padding=40, alignment=ft.Alignment.CENTER
    )
    contenedor_recuperar = ft.Container(
        content=glass_container(ft.Column([icono_nube_3, lbl_rec_title, lbl_rec_sub, ft.Divider(color="transparent", height=10), recup_correo, btn_rec_enviar, btn_rec_volver], alignment=ft.MainAxisAlignment.CENTER, horizontal_alignment=ft.CrossAxisAlignment.CENTER)),
        expand=True, visible=False, padding=40, alignment=ft.Alignment.CENTER
    )

    aplicar_idioma()
    # Usar una imagen de fondo difuminada    # Fondo de pantalla
    img_bg = ft.Image(src="https://images.unsplash.com/photo-1618005182384-a83a8bd57fbe?q=80&w=2564&auto=format&fit=crop", fit=ft.BoxFit.COVER, expand=True, opacity=0.3)
    
    # Agregar componentes de hardware para móviles (Alarma y Vibración)
    alarm_audio = ft.Audio(src="alarm.mp3", autoplay=False)
    haptic_fb = ft.HapticFeedback()
    page.overlay.extend([alarm_audio, haptic_fb])
    
    stack = ft.Stack([
        img_bg,
        ft.Column([contenedor_login, contenedor_registro, contenedor_recuperar, contenedor_app], expand=True)
    ], expand=True)

    page.add(stack)

if __name__ == "__main__":
    ft.run(main, assets_dir=".")
