import flet as ft
import json
import os
from datetime import datetime

# --- 1. CARGA DE DATOS ---
def cargar_datos(nombre_archivo):
    ruta_base = os.path.dirname(__file__)
    ruta_archivo = os.path.join(ruta_base, 'data', nombre_archivo)
    try:
        if os.path.exists(ruta_archivo):
            with open(ruta_archivo, 'r', encoding='utf-8') as f:
                return json.load(f)
        return []
    except: return []

def guardar_datos(nombre_archivo, datos):
    ruta_base = os.path.dirname(__file__)
    ruta_archivo = os.path.join(ruta_base, 'data', nombre_archivo)
    with open(ruta_archivo, 'w', encoding='utf-8') as f:
        json.dump(datos, f, indent=4)

usuarios = cargar_datos('usuarios.json')
libros = cargar_datos('libros.json')
reseñas = cargar_datos('reseñas.json')

# --- 2. APLICACIÓN PRINCIPAL ---
def main(page: ft.Page):
    page.title = "Readers Bay"
    page.window_width = 450
    page.window_height = 800
    page.theme_mode = ft.ThemeMode.LIGHT

    # --- FUNCIONES DE APOYO ---
    
    def cerrar_sesion(e):
        page.data = None
        mostrar_login()

    # --- VISTA: BIBLIOTECA (CON BUSCADOR Y CLIC) ---
    def iniciar_biblioteca():
        page.clean()
        user = page.data
        
        lista_libros_ui = ft.Column(scroll=ft.ScrollMode.ADAPTIVE, expand=True)

        # --- FUNCIÓN PARA ABRIR EL DIÁLOGO DE RESEÑA ---
        def abrir_resena(libro):
            txt_comentario = ft.TextField(
                label="Escribe tu opinión aquí...", 
                multiline=True, 
                min_lines=3,
                border_radius=10
            )
            
            # Definimos el diálogo primero
            dlg = ft.AlertDialog(
                title=ft.Text(f"Reseñar: {libro['titulo']}"),
                content=ft.Column([
                    ft.Text(f"Autor: {libro['autor']}", italic=True),
                    txt_comentario,
                ], tight=True),
                actions=[
                    ft.TextButton("Cancelar", on_click=lambda _: page.close(dlg)),
                    ft.ElevatedButton("Enviar Reseña", on_click=lambda _: guardar_resena_click(libro, txt_comentario, dlg))
                ],
            )

            # --- LA CLAVE PARA QUE APAREZCA ---
            page.open(dlg) 

        def guardar_resena_click(libro, campo_texto, dialogo):
            if not campo_texto.value:
                campo_texto.error_text = "La reseña no puede estar vacía"
                page.update()
                return

            nueva_resena = {
                "usuario": user['nombre'],
                "libro": libro['titulo'],
                "texto": campo_texto.value,
                "fecha": datetime.now().strftime("%d/%m/%Y %H:%M")
            }
            
            # Guardar en la lista y en el archivo
            reseñas.append(nueva_resena)
            guardar_datos('reseñas.json', reseñas)
            
            # Cerrar el diálogo y avisar al usuario
            page.close(dialogo)
            page.snack_bar = ft.SnackBar(ft.Text(f"¡Gracias por tu reseña de {libro['titulo']}!"))
            page.snack_bar.open = True
            page.update()

        # --- RESTO DE LA LÓGICA (Buscador y Tarjetas) ---
        def filtrar_libros(e):
            termino = buscador.value.lower()
            lista_libros_ui.controls.clear()
            for libro in libros:
                if termino in libro['titulo'].lower() or termino in libro['autor'].lower():
                    lista_libros_ui.controls.append(crear_tarjeta_libro(libro))
            page.update()

        def crear_tarjeta_libro(libro):
            return ft.Card(
                content=ft.Container(
                    padding=15,
                    content=ft.Row([
                        ft.Icon(ft.Icons.BOOK_ROUNDED, color=ft.Colors.BLUE_700, size=30),
                        ft.Column([
                            ft.Text(libro['titulo'], weight="bold", size=16, overflow=ft.TextOverflow.ELLIPSIS),
                            ft.Text(libro['autor'], size=13, color=ft.Colors.GREY_700),
                        ], expand=True),
                        # Este botón ahora sí disparará el diálogo
                        ft.IconButton(
                            icon=ft.Icons.RATE_REVIEW_ROUNDED,
                            icon_color=ft.Colors.BLUE_ACCENT_700,
                            tooltip="Escribir reseña",
                            on_click=lambda _: abrir_resena(libro)
                        )
                    ])
                )
            )

        buscador = ft.TextField(
            label="Buscar por título o autor...",
            prefix_icon=ft.Icons.SEARCH,
            on_change=filtrar_libros,
            border_radius=15,
            bgcolor=ft.Colors.GREY_50
        )

        for l in libros:
            lista_libros_ui.controls.append(crear_tarjeta_libro(l))

        page.add(
            ft.AppBar(
                title=ft.Text(f"Readers Bay - {user['nombre']}"),
                bgcolor=ft.Colors.BLUE_50,
                actions=[ft.IconButton(ft.Icons.LOGOUT, on_click=lambda _: mostrar_login())]
            ),
            ft.Container(height=10),
            ft.Text("Mi Biblioteca", size=24, weight="bold"),
            buscador,
            ft.Divider(height=20, color=ft.Colors.TRANSPARENT),
            lista_libros_ui
        )
        page.update()

    # --- VISTA: LOGIN (YA FUNCIONAL) ---
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
                lbl_error.value = "Datos incorrectos"
                page.update()

        page.add(
            ft.Icon(ft.Icons.AUTO_STORIES, size=80, color="blue"),
            ft.Text("Readers Bay", size=30, weight="bold"),
            txt_user, txt_pass, lbl_error,
            ft.ElevatedButton("Ingresar", on_click=btn_login_click, width=300)
        )
        page.update()

    mostrar_login()

if __name__ == "__main__":
    ft.app(target=main)