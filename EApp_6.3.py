import ssl 
import urllib.request

# Bypass de seguridad para conexiones locales
try:
    ssl._create_default_https_context = ssl._create_unverified_context
except AttributeError:
    pass

import flet as ft
import requests
import json
import os

# ==========================================
# 🛡️ ADAPTADOR DE ENTORNO (NUBE vs ESCRITORIO)
# ==========================================
try:
    import tkinter as tk
    from tkinter import filedialog
    ENTORNO_ESCRITORIO = True
except ImportError:
    # Si estamos en Render (Linux sin pantalla), tkinter fallará.
    ENTORNO_ESCRITORIO = False

# ==========================================
# ☁️ LLAVES DE LA BÓVEDA FIREBASE
# ==========================================
API_KEY = "AIzaSyAZ2hZQET0JUvFxUkyp-SrvZapaxh4xRw8"
DATABASE_URL = "https://eapp-rgrej-default-rtdb.firebaseio.com"

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
            self.cell(0, 10, limpiar_texto("EApp 6.4 by Rogelio Grej - rogeliogrej@gmail.com"), align="C")
    PDF_DISPONIBLE = True
except ImportError:
    PDF_DISPONIBLE = False

def main(page: ft.Page):
    # --- CONFIGURACIÓN GENERAL ---
    page.title = "EApp 6.4 by Rogelio Grej"
    page.theme_mode = "light"
    page.scroll = "adaptive"
    page.bgcolor = "#F8FAFC"
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER

    LANG = ["ES"]
    USER_TOKEN = [""]
    USER_ID = [""]
    tareas = []
    tarea_a_restaurar = [""]

    TXT = {
        "ES": {
            "appbar": "EApp 6.4 by Rogelio Grej",
            "login_title": "EApp 6.4 Cloud",
            "login_sub": "Inicia sesión en tu bóveda en la nube",
            "correo": "Correo electrónico",
            "pass": "Contraseña",
            "olvide": "¿Olvidaste tu contraseña?",
            "entrar": "ENTRAR A LA NUBE ☁️",
            "crear_acc": "Crear una cuenta nueva",
            "tab_m": "⚡ Matriz",
            "tab_h": "✅ Historial",
            "pdf_m": "Generar PDF de Pendientes 📄",
            "pdf_h": "Generar PDF de Historial 📄",
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
            "back": "⬅️ Volver al inicio de sesión",
            "reg_title": "Crear Cuenta ⚡",
            "reg_sub": "Tu cuenta se protegerá en Firebase",
            "reg_btn": "REGISTRARME",
            "empty": "(Sin tareas)",
            "empty_h": "Aún no has finalizado tareas.",
            "gen_date": "Reporte generado el:",
            "creacion": "Creada:",
            "fin": "Fin:",
            "new_task_btn": "➕ NUEVA TAREA"
        },
        "EN": {
            "appbar": "EApp 6.4 by Rogelio Grej",
            "login_title": "EApp 6.4 Cloud",
            "login_sub": "Log in to your cloud vault",
            "correo": "Email Address",
            "pass": "Password",
            "olvide": "Forgot your password?",
            "entrar": "ENTER CLOUD ☁️",
            "crear_acc": "Create a new account",
            "tab_m": "⚡ Matrix",
            "tab_h": "✅ History",
            "pdf_m": "Generate Pending PDF 📄",
            "pdf_h": "Generate History PDF 📄",
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
            "new_task_btn": "➕ NEW TASK"
        }
    }

    lbl_appbar = ft.Text("EApp 6.4 by Rogelio Grej", weight="bold", color="#FFFFFF")
    lbl_login_title = ft.Text("EApp 6.4 Cloud", size=32, weight="extrabold", color="#1E293B")
    lbl_login_sub = ft.Text("Inicia sesión en tu bóveda en la nube", size=14, color="#64748B")
    campo_correo = ft.TextField(label="Correo electrónico", width=300, border_radius=10)
    campo_pass = ft.TextField(label="Contraseña", password=True, width=300, border_radius=10)
    
    btn_olvide = ft.TextButton("¿Olvidaste tu contraseña?", style=ft.ButtonStyle(color="#64748B"))
    btn_login = ft.ElevatedButton("ENTRAR A LA NUBE ☁️", bgcolor="#F59E0B", color="white", width=300, height=50)
    btn_crear = ft.TextButton("Crear una cuenta nueva", style=ft.ButtonStyle(color="#2196F3"))
    
    lbl_reg_title = ft.Text("Crear Cuenta ⚡", size=28, weight="bold", color="#1E293B")
    lbl_reg_sub = ft.Text("Tu cuenta se protegerá en Firebase", color="#64748B")
    reg_correo = ft.TextField(label="Nuevo Correo", width=300, border_radius=10)
    reg_pass = ft.TextField(label="Nueva Contraseña", password=True, width=300, border_radius=10)
    
    btn_reg_confirm = ft.ElevatedButton("REGISTRARME", bgcolor="#4CAF50", color="white", width=300, height=50)
    btn_reg_volver = ft.TextButton("⬅️ Volver al inicio de sesión")

    lbl_rec_title = ft.Text("Recuperar Cuenta 🔐", size=28, weight="bold", color="#1E293B")
    lbl_rec_sub = ft.Text("Firebase te enviará las instrucciones", color="#64748B")
    recup_correo = ft.TextField(label="Tu correo registrado", width=300, border_radius=10)
    btn_rec_enviar = ft.ElevatedButton("ENVIAR ENLACE", bgcolor="#2196F3", color="white", width=300, height=50)
    btn_rec_volver = ft.TextButton("⬅️ Volver al inicio de sesión")

    txt_tab_matriz = ft.Text("⚡ Matriz", weight="bold", size=16)
    txt_tab_hist = ft.Text("✅ Historial", weight="bold", size=16)
    
    btn_pdf_m = ft.ElevatedButton("Generar PDF de Pendientes 📄", bgcolor="#FF5722", color="white")
    btn_pdf_h = ft.ElevatedButton("Generar PDF de Historial 📄", bgcolor="#FF5722", color="white")

    txt_q1 = ft.Text("HACER (SS)", size=18, weight="bold", color="#FFFFFF")
    txt_q2 = ft.Text("PLANIFICAR (NS)", size=18, weight="bold", color="#FFFFFF")
    txt_q3 = ft.Text("DELEGAR (SN)", size=18, weight="bold", color="#FFFFFF")
    txt_q4 = ft.Text("ELIMINAR (NN)", size=18, weight="bold", color="#FFFFFF")

    lbl_form_title = ft.Text("Nueva Tarea ⚡", weight="bold", size=20, color="#1E293B")
    input_tarea = ft.TextField(label="Nombre de la tarea")
    input_rubro = ft.TextField(label="Rubro (ej. Ofimática)")
    dd_urgente = ft.Dropdown(label="¿Urgente?", width=120)
    dd_importante = ft.Dropdown(label="¿Importante?", width=120)
    btn_cancelar = ft.TextButton("Cancelar")
    btn_guardar = ft.ElevatedButton("Guardar en Nube ☁️", bgcolor="#4CAF50", color="white")

    lbl_rest_title = ft.Text("♻️ Restaurar a Matriz", weight="bold", size=18, color="#1E293B")
    lbl_rest_sub = ft.Text("¿A qué cuadrante deseas enviar esta tarea?")
    dd_cuad_rest = ft.Dropdown(label="Elige el nuevo cuadrante")
    btn_rest_cancel = ft.TextButton("Cancelar")
    btn_rest_confirm = ft.ElevatedButton("Restaurar", bgcolor="#F59E0B", color="white")

    btn_nueva_tarea = ft.ElevatedButton(
        "➕ NUEVA TAREA", 
        bgcolor="#F59E0B", 
        color="white", 
        height=50,
        on_click=lambda e: (setattr(panel_ingreso, 'visible', True), page.update())
    )

    btn_lang = ft.TextButton(
        "🌍", 
        tooltip="English / Español", 
        style=ft.ButtonStyle(color="white", text_style=ft.TextStyle(size=24))
    )

    lista_hacer = ft.Column()
    lista_planificar = ft.Column()
    lista_delegar = ft.Column()
    lista_eliminar = ft.Column()
    lista_historial = ft.Column(spacing=10)

    from datetime import datetime
    def obtener_fecha(): return datetime.now().strftime("%d/%m/%Y %I:%M %p")

    def cargar_datos():
        if not USER_ID[0]: return
        url = f"{DATABASE_URL}/users/{USER_ID[0]}/tareas.json?auth={USER_TOKEN[0]}"
        try:
            res = requests.get(url)
            if res.status_code == 200 and res.text != 'null':
                data = res.json()
                tareas.clear()
                if isinstance(data, list): tareas.extend([t for t in data if t is not None])
                elif isinstance(data, dict): tareas.extend(list(data.values()))
        except Exception as e: print("Error cargando:", e)

    def guardar_datos():
        if not USER_ID[0]: return
        url = f"{DATABASE_URL}/users/{USER_ID[0]}/tareas.json?auth={USER_TOKEN[0]}"
        try: requests.put(url, json=tareas)
        except Exception as e: print("Error guardando:", e)

    def finalizar_tarea(e):
        for t in tareas:
            if t["nombre"] == e.control.data and t.get("estado") == "pendiente":
                t["estado"] = "finalizada"
                t["fecha_fin"] = obtener_fecha()
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
        tareas.append({"nombre": input_tarea.value, "rubro": input_rubro.value or "General", "cuadrante": c, "estado": "pendiente", "fecha_ingreso": obtener_fecha()})
        guardar_datos()
        input_tarea.value = ""
        input_rubro.value = ""
        panel_ingreso.visible = False
        actualizar_vistas()

    def pedir_ruta_guardado(nombre_por_defecto, titulo):
        # 🧠 INTELIGENCIA ADAPTATIVA
        if ENTORNO_ESCRITORIO:
            root = tk.Tk()
            root.withdraw()
            root.attributes('-topmost', True) 
            ruta = filedialog.asksaveasfilename(defaultextension=".pdf", initialfile=nombre_por_defecto, title=titulo, filetypes=[("Archivos PDF", "*.pdf")])
            root.destroy()
            return ruta
        else:
            # En la web, el archivo se guarda temporalmente en la raíz para enviarlo al navegador
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
            
            # MAGIA EN LA NUBE: Si estamos en celular, abrimos el PDF para descargarlo
            if not ENTORNO_ESCRITORIO:
                page.launch_url(f"/{ruta_elegida}")
                
            page.snack_bar = ft.SnackBar(ft.Text("¡PDF procesado con éxito! 📄", color="white"), bgcolor="#4CAF50")
            page.snack_bar.open = True
            page.update()

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
            
            if not ENTORNO_ESCRITORIO:
                page.launch_url(f"/{ruta_elegida}")
                
            page.snack_bar = ft.SnackBar(ft.Text("¡PDF procesado con éxito! 📄", color="white"), bgcolor="#4CAF50")
            page.snack_bar.open = True
            page.update()

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
            bgcolor=color_fondo, border_radius=15, padding=20, shadow=ft.BoxShadow(spread_radius=1, blur_radius=8, color="#CBD5E1")
        )

    tarjeta_hacer = crear_tarjeta_dinamica(txt_q1, "#E53935", lista_hacer)
    tarjeta_planificar = crear_tarjeta_dinamica(txt_q2, "#2196F3", lista_planificar)
    tarjeta_delegar = crear_tarjeta_dinamica(txt_q3, "#FB8C00", lista_delegar)
    tarjeta_eliminar = crear_tarjeta_dinamica(txt_q4, "#64748B", lista_eliminar)

    def actualizar_vistas():
        t_lang = TXT[LANG[0]]
        lista_hacer.controls.clear(); lista_planificar.controls.clear(); lista_delegar.controls.clear(); lista_eliminar.controls.clear(); lista_historial.controls.clear()
        
        pendientes = [t for t in tareas if t.get("estado", "pendiente") == "pendiente"]
        finalizadas = [t for t in tareas if t.get("estado") == "finalizada"]
        q_map_en = {"HACER": "DO", "PLANIFICAR": "SCHEDULE", "DELEGAR": "DELEGATE", "ELIMINAR": "DELETE"}

        for t in pendientes:
            item = ft.Container(
                content=ft.Row([
                    ft.TextButton("✔️", data=t["nombre"], on_click=finalizar_tarea, style=ft.ButtonStyle(color="#FFFFFF")),
                    ft.Text(f"[{t.get('rubro', 'General')}] {t['nombre']}", color="#FFFFFF", size=14, weight="w500", expand=True)
                ]), padding=2
            )
            q = t.get("cuadrante", "")
            if q == "HACER": lista_hacer.controls.append(item)
            elif q == "PLANIFICAR": lista_planificar.controls.append(item)
            elif q == "DELEGAR": lista_delegar.controls.append(item)
            elif q == "ELIMINAR": lista_eliminar.controls.append(item)

        for lista in [lista_hacer, lista_planificar, lista_delegar, lista_eliminar]:
            if not lista.controls: lista.controls.append(ft.Text(t_lang["empty"], color="#FFFFFF", opacity=0.7))

        for t in reversed(finalizadas):
            c_text = t['cuadrante'] if LANG[0] == "ES" else q_map_en.get(t['cuadrante'], t['cuadrante'])
            item_historial = ft.Container(
                content=ft.Row([
                    ft.Text("✅", size=18),
                    ft.Column([
                        ft.Text(t["nombre"], weight="bold", size=14),
                        ft.Text(f"{c_text} | {t_lang['fin']} {t.get('fecha_fin', '')}", size=11, color="#64748B")
                    ], expand=True), 
                    ft.TextButton("♻️", data=t["nombre"], on_click=abrir_panel_restaurar),
                    ft.TextButton("🗑️", data=t["nombre"], on_click=eliminar_tarea_definitiva)
                ]), bgcolor="#FFFFFF", padding=10, border_radius=10
            )
            lista_historial.controls.append(item_historial)
            
        if not lista_historial.controls: lista_historial.controls.append(ft.Text(t_lang["empty_h"], color="#64748B"))
        page.update()

    def ocultar_panel(e=None):
        panel_ingreso.visible = False
        page.update()

    btn_cancelar.on_click = ocultar_panel
    btn_guardar.on_click = agregar_tarea_submit
    btn_rest_cancel.on_click = ocultar_panel_restaurar
    btn_rest_confirm.on_click = confirmar_restauracion

    panel_ingreso = ft.Container(
        content=ft.Column([
            lbl_form_title, input_tarea, input_rubro,
            ft.Row([dd_urgente, dd_importante], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
            ft.Row([btn_cancelar, btn_guardar], alignment=ft.MainAxisAlignment.END)
        ]), bgcolor="#FFFFFF", padding=20, border_radius=15, shadow=ft.BoxShadow(spread_radius=1, blur_radius=10, color="#CBD5E1"), visible=False, margin=15
    )

    panel_restaurar = ft.Container(
        content=ft.Column([
            lbl_rest_title,
            lbl_rest_sub,
            dd_cuad_rest,
            ft.Row([btn_rest_cancel, btn_rest_confirm], alignment=ft.MainAxisAlignment.END)
        ]), bgcolor="#FFFFFF", padding=20, border_radius=15, shadow=ft.BoxShadow(spread_radius=1, blur_radius=10, color="#CBD5E1"), visible=False, margin=15
    )

    row_botones_matriz = ft.Row([btn_nueva_tarea, btn_pdf_m], alignment=ft.MainAxisAlignment.END)
    row_botones_historial = ft.Row([btn_pdf_h], alignment=ft.MainAxisAlignment.END)

    vista_matriz = ft.Column([row_botones_matriz, panel_ingreso, tarjeta_hacer, tarjeta_planificar, tarjeta_delegar, tarjeta_eliminar], spacing=15, visible=True)
    vista_historial = ft.Column([row_botones_historial, panel_restaurar, ft.Divider(), lista_historial], spacing=15, visible=False)

    def click_matriz(e): vista_matriz.visible, vista_historial.visible, btn_matriz.bgcolor, btn_historial.bgcolor = True, False, "#E2E8F0", "#FFFFFF"; page.update()
    def click_historial(e): vista_matriz.visible, vista_historial.visible, btn_matriz.bgcolor, btn_historial.bgcolor = False, True, "#FFFFFF", "#E2E8F0"; page.update()

    btn_matriz = ft.Container(content=ft.Row([txt_tab_matriz], alignment=ft.MainAxisAlignment.CENTER), on_click=click_matriz, padding=15, bgcolor="#E2E8F0", border_radius=10, expand=1)
    btn_historial = ft.Container(content=ft.Row([txt_tab_hist], alignment=ft.MainAxisAlignment.CENTER), on_click=click_historial, padding=15, bgcolor="#FFFFFF", border_radius=10, expand=1)

    appbar_principal = ft.AppBar(
        leading=ft.Container(content=ft.Image(src="R Logo.png", width=40, height=40), padding=5), 
        title=lbl_appbar, 
        bgcolor="#1E293B", 
        center_title=True,
        actions=[btn_lang]
    )
    
    contenedor_app = ft.Container(content=ft.Column([ft.Row([btn_matriz, btn_historial], alignment=ft.MainAxisAlignment.CENTER), ft.Divider(color="transparent", height=5), vista_matriz, vista_historial]), padding=20, visible=False)

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
        try:
            res = requests.post(url, json=payload); data = res.json()
            if "error" in data: page.snack_bar = ft.SnackBar(ft.Text(f"⚠️ Error: {data['error']['message']}", color="white"), bgcolor="#E53935")
            else:
                page.snack_bar = ft.SnackBar(ft.Text("✅ Cuenta creada en la nube.", color="white"), bgcolor="#4CAF50")
                volver_al_login()
        except: page.snack_bar = ft.SnackBar(ft.Text("⚠️ Error de conexión a Firebase.", color="white"), bgcolor="#E53935")
        page.snack_bar.open = True; page.update()
    
    btn_reg_confirm.on_click = registrar_usuario

    def enviar_recuperacion(e):
        if not recup_correo.value: return
        url = f"https://identitytoolkit.googleapis.com/v1/accounts:sendOobCode?key={API_KEY}"
        payload = {"requestType": "PASSWORD_RESET", "email": recup_correo.value}
        try:
            res = requests.post(url, json=payload); data = res.json()
            if "error" in data: page.snack_bar = ft.SnackBar(ft.Text("⚠️ Error verificando correo.", color="white"), bgcolor="#E53935")
            else:
                page.snack_bar = ft.SnackBar(ft.Text("📧 ¡Enlace enviado! (Revisa tu carpeta de Spam).", color="white"), bgcolor="#4CAF50")
                volver_al_login()
        except: page.snack_bar = ft.SnackBar(ft.Text("⚠️ Error de conexión a Firebase.", color="white"), bgcolor="#E53935")
        page.snack_bar.open = True; page.update()
    
    btn_rec_enviar.on_click = enviar_recuperacion

    def iniciar_sesion(e):
        url = f"https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key={API_KEY}"
        payload = {"email": campo_correo.value, "password": campo_pass.value, "returnSecureToken": True}
        try:
            res = requests.post(url, json=payload); data = res.json()
            if "error" in data: page.snack_bar = ft.SnackBar(ft.Text("⚠️ Credenciales incorrectas.", color="white"), bgcolor="#E53935")
            else:
                USER_TOKEN[0], USER_ID[0] = data["idToken"], data["localId"]
                cargar_datos()
                contenedor_login.visible, contenedor_app.visible = False, True
                page.appbar = appbar_principal
                page.snack_bar = ft.SnackBar(ft.Text("¡Conectado a la Nube! ☁️⚡", color="white"), bgcolor="#4CAF50")
                actualizar_vistas()
        except: page.snack_bar = ft.SnackBar(ft.Text("⚠️ Error de conexión.", color="white"), bgcolor="#E53935")
        page.snack_bar.open = True; page.update()

    btn_login.on_click = iniciar_sesion

    logo_pantallas = ft.Image(src="R Logo.png", width=120, height=120)

    contenedor_login = ft.Container(content=ft.Column([ft.Divider(color="transparent", height=30), logo_pantallas, lbl_login_title, lbl_login_sub, ft.Divider(color="transparent", height=10), campo_correo, campo_pass, btn_olvide, btn_login, btn_crear], alignment=ft.MainAxisAlignment.CENTER, horizontal_alignment=ft.CrossAxisAlignment.CENTER), expand=True, visible=True)
    contenedor_registro = ft.Container(content=ft.Column([ft.Divider(color="transparent", height=30), ft.Image(src="R Logo.png", width=100, height=100), lbl_reg_title, lbl_reg_sub, ft.Divider(color="transparent", height=10), reg_correo, reg_pass, btn_reg_confirm, btn_reg_volver], alignment=ft.MainAxisAlignment.CENTER, horizontal_alignment=ft.CrossAxisAlignment.CENTER), expand=True, visible=False)
    contenedor_recuperar = ft.Container(content=ft.Column([ft.Divider(color="transparent", height=30), ft.Image(src="R Logo.png", width=100, height=100), lbl_rec_title, lbl_rec_sub, ft.Divider(color="transparent", height=10), recup_correo, btn_rec_enviar, btn_rec_volver], alignment=ft.MainAxisAlignment.CENTER, horizontal_alignment=ft.CrossAxisAlignment.CENTER), expand=True, visible=False)

    aplicar_idioma()
    page.add(contenedor_login, contenedor_registro, contenedor_recuperar, contenedor_app)

# ALERTA DE NUBE: assets_dir="." permite que el servidor web entregue los PDFs al navegador
ft.app(target=main, assets_dir=".")