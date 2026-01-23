import flet as ft
import json
import os
from datetime import datetime
import time

# --- 1. PERSISTENCIA DE DATOS ---

def cargar_datos(nombre_archivo):
    ruta_base = os.path.dirname(__file__)
    ruta_archivo = os.path.join(ruta_base, 'data', nombre_archivo)
    try:
        if os.path.exists(ruta_archivo):
            with open(ruta_archivo, 'r', encoding='utf-8') as f:
                return json.load(f)
        return []
    except:
        return []

def guardar_datos_json(nombre_archivo, lista_datos):
    try:
        if not os.path.exists("data"): os.makedirs("data")
        ruta = os.path.join("data", nombre_archivo)
        with open(ruta, "w", encoding="utf-8") as f:
            json.dump(lista_datos, f, ensure_ascii=False, indent=4)
    except Exception as e:
        print(f"Error al guardar {nombre_archivo}: {e}")

# Carga global de datos
usuarios = cargar_datos('usuarios.json')
libros = cargar_datos('libros.json')
reseñas = cargar_datos('reseñas.json')
compartidos = cargar_datos('compartidos.json')

# --- 2. APLICACIÓN PRINCIPAL ---

def main(page: ft.Page):
    page.title = "Readers Bay"
    page.window_width = 450
    page.window_height = 800
    page.theme_mode = ft.ThemeMode.LIGHT

    # --- FUNCIONES DE UTILIDAD ---
    
    def cerrar_dialogo(dlg):
        dlg.open = False
        page.update()

    def mostrar_snack(texto):
        page.snack_bar = ft.SnackBar(ft.Text(texto))
        page.snack_bar.open = True
        page.update()

    # --- VISTA: LOGIN Y REGISTRO ---

    def mostrar_login():
        page.clean()
        page.vertical_alignment = ft.MainAxisAlignment.CENTER
        page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
        
        txt_user = ft.TextField(label="Usuario", width=300)
        txt_pass = ft.TextField(label="Contraseña", password=True, width=300)
        lbl_error = ft.Text("", color="red")

        def btn_login_click(e):
            encontrado = next((u for u in usuarios if u['nombre'].lower() == txt_user.value.lower() 
                             and str(u['password']) == str(txt_pass.value)), None)
            if encontrado:
                page.data = encontrado
                iniciar_biblioteca()
            else:
                lbl_error.value = "Datos incorrectos"; page.update()

        page.add(
            ft.Icon(ft.Icons.AUTO_STORIES, size=80, color="blue"),
            ft.Text("Readers Bay", size=30, weight="bold"),
            txt_user, txt_pass, lbl_error,
            ft.Button("Ingresar", on_click=btn_login_click, width=300),
            ft.TextButton("¿No tienes cuenta? Regístrate", on_click=abrir_registro)
        )
        page.update()

    def abrir_registro(e):
        t_u = ft.TextField(label="Nuevo Usuario"); t_p = ft.TextField(label="Contraseña", password=True)
        def reg(e):
            usuarios.append({"id": int(time.time()), "nombre": t_u.value, "password": t_p.value})
            guardar_datos_json("usuarios.json", usuarios)
            cerrar_dialogo(dlg); mostrar_snack("Registrado con éxito")
        dlg = ft.AlertDialog(title=ft.Text("Registro"), content=ft.Column([t_u, t_p], tight=True), actions=[ft.TextButton("OK", on_click=reg)])
        page.overlay.append(dlg); dlg.open = True; page.update()

    # --- VISTA: BIBLIOTECA ---

    def iniciar_biblioteca():
        page.clean()
        user_actual = page.data
        lista_libros_ui = ft.Column(scroll=ft.ScrollMode.ADAPTIVE, expand=True)

        # --- FUNCIÓN: BUZÓN DE CORREOS ---
        def abrir_buzon(e):
            mis_mensajes = [m for m in compartidos if m.get('destinatario') == user_actual['nombre']]
            if not mis_mensajes:
                contenido = ft.Text("No tienes mensajes nuevos.")
            else:
                filas = [ft.ListTile(leading=ft.Icon(ft.Icons.EMAIL), title=ft.Text(f"De: {m['remitente']}"), subtitle=ft.Text(f"Libro: {m['libro_titulo']}\n'{m['mensaje']}'"), is_three_line=True) for m in mis_mensajes]
                contenido = ft.Column(filas, scroll=True, height=400)

            dlg_buzon = ft.AlertDialog(title=ft.Text("Buzón de Entrada"), content=contenido, actions=[ft.TextButton("Cerrar", on_click=lambda _: cerrar_dialogo(dlg_buzon))])
            page.overlay.append(dlg_buzon); dlg_buzon.open = True; page.update()

        # --- FUNCIONES DE DETALLES DEL LIBRO ---
        def abrir_detalles(libro):
            dlg = ft.AlertDialog(
                title=ft.Text(libro['titulo']),
                content=ft.Text(f"ID: {libro['id']}\nAutor: {libro['autor']}\nGénero: {libro['genero']}\nAño: {libro['anio']}"),
                actions=[
                    ft.TextButton("Ver Reseñas", on_click=lambda _: ver_reseñas(libro)),
                    ft.TextButton("Añadir Reseña", on_click=lambda _: abrir_formulario_resena(libro)), # REINSTALADO
                    ft.TextButton("Compartir", on_click=lambda _: compartir_libro(libro)),
                    ft.TextButton("Cerrar", on_click=lambda _: cerrar_dialogo(dlg))
                ]
            )
            page.overlay.append(dlg); dlg.open = True; page.update()

        def ver_reseñas(libro):
            filtradas = [r for r in reseñas if r.get('libro_id') == libro['id']]
            cont = ft.Column([ft.ListTile(title=ft.Text(f"{r['rating']} ★"), subtitle=ft.Text(r['texto'])) for r in filtradas], height=300, scroll=True) if filtradas else ft.Text("Sin reseñas.")
            dlg_v = ft.AlertDialog(title=ft.Text("Reseñas"), content=cont, actions=[ft.TextButton("Cerrar", on_click=lambda _: cerrar_dialogo(dlg_v))])
            page.overlay.append(dlg_v); dlg_v.open = True; page.update()

        def abrir_formulario_resena(libro):
            t_rate = ft.TextField(label="Calificación (1-5)", width=100)
            t_com = ft.TextField(label="Tu comentario", multiline=True, min_lines=3)
            def guardar(e):
                if not t_rate.value or not t_com.value: return
                reseñas.append({
                    "id": int(time.time()), "libro_id": libro['id'], 
                    "rating": t_rate.value, "texto": t_com.value, 
                    "fecha": datetime.now().strftime("%d/%m/%Y")
                })
                guardar_datos_json("reseñas.json", reseñas)
                cerrar_dialogo(dlg_f); mostrar_snack("¡Reseña guardada!")

            dlg_f = ft.AlertDialog(title=ft.Text(f"Nueva reseña: {libro['titulo']}"), content=ft.Column([t_rate, t_com], tight=True), actions=[ft.TextButton("Guardar", on_click=guardar)])
            page.overlay.append(dlg_f); dlg_f.open = True; page.update()

        def compartir_libro(libro):
            ops = [ft.dropdown.Option(u['nombre']) for u in usuarios if u['nombre'] != user_actual['nombre']]
            dd = ft.Dropdown(label="Enviar a...", options=ops); txt = ft.TextField(label="Mensaje")
            def enviar(e):
                if not dd.value: return
                compartidos.append({
                    "remitente": user_actual['nombre'], "destinatario": dd.value,
                    "libro_titulo": libro['titulo'], "mensaje": txt.value, 
                    "fecha": datetime.now().strftime("%d/%m/%Y %H:%M")
                })
                guardar_datos_json("compartidos.json", compartidos)
                cerrar_dialogo(dlg_c); mostrar_snack(f"Enviado a {dd.value}")
            dlg_c = ft.AlertDialog(title=ft.Text("Compartir"), content=ft.Column([dd, txt], tight=True), actions=[ft.TextButton("Enviar", on_click=enviar)])
            page.overlay.append(dlg_c); dlg_c.open = True; page.update()

        # UI BIBLIOTECA
        def crear_card(l):
            return ft.Card(ft.Container(padding=15, content=ft.Row([
                ft.Icon(ft.Icons.BOOK_ROUNDED, color="blue"),
                ft.Column([ft.Text(l['titulo'], weight="bold"), ft.Text(l['autor'])], expand=True),
                ft.IconButton(ft.Icons.INFO_OUTLINE, on_click=lambda _: abrir_detalles(l))
            ])))

        buscador = ft.TextField(label="Buscar libro...", prefix_icon=ft.Icons.SEARCH, on_change=lambda e: filtrar())
        def filtrar():
            lista_libros_ui.controls.clear()
            for l in libros:
                if buscador.value.lower() in l['titulo'].lower() or buscador.value.lower() in l['autor'].lower():
                    lista_libros_ui.controls.append(crear_card(l))
            page.update()

        for l in libros: lista_libros_ui.controls.append(crear_card(l))

        page.add(
            ft.AppBar(
                title=ft.Text(f"Readers Bay - {user_actual['nombre']}"),
                bgcolor=ft.Colors.BLUE_50,
                actions=[
                    ft.IconButton(ft.Icons.EMAIL_OUTLINED, tooltip="Buzón", on_click=abrir_buzon),
                    ft.IconButton(ft.Icons.LOGOUT, on_click=lambda _: mostrar_login())
                ]
            ),
            ft.Text("Mi Biblioteca", size=24, weight="bold"),
            buscador,
            lista_libros_ui
        )
        page.update()

    mostrar_login()

if __name__ == "__main__":
    ft.run(main)