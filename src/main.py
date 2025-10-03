import flet as ft
import requests
import json
import time

import asyncio

# --- Configuración ---
# **IMPORTANTE**: Asegúrate de que tu servidor FastAPI esté corriendo en esta URL.
API_BASE_URL = "http://127.0.0.1:8000"


# --------------------------------------------------------------------------------
# --- Lógica de Manejo de API ---
# --------------------------------------------------------------------------------
async def cargar_datos(page: ft.Page, usuarios_tabla: ft.DataTable, salida: ft.Text):
    while True:
        try:
            response = requests.get(f"{API_BASE_URL}/usuarios_get/")
            if response.status_code == 200:
                data = response.json()
                print("Datos recibidos:", data)

                # limpiar filas previas
                usuarios_tabla.rows.clear()

                # agregar nuevas filas
                for u in data:
                    usuarios_tabla.rows.append(
                        ft.DataRow(
                            cells=[
                                ft.DataCell(ft.Text(str(u["id"]))),
                                ft.DataCell(ft.Text(u["nombre"])),
                                ft.DataCell(ft.Text(u["correo"])),
                            ]
                        )
                    )

                salida.value = f"Última actualización: {time.strftime('%H:%M:%S')}"
                page.update()
            else:
                salida.value = f"Error al cargar datos: {response.status_code}"
                page.update()

            await asyncio.sleep(3)
        except requests.exceptions.RequestException as e:
            salida.value = f"Excepción al conectar con la API: {e}"
            page.update()
            await asyncio.sleep(5)


def crear_usuario(
    page: ft.Page,
    idusuario: ft.TextField,
    nombre_usuario: ft.TextField,
    email_usuario: ft.TextField,
):
    """Maneja la lógica para enviar una solicitud POST a la API de FastAPI."""

    # 1. Validar y obtener el ID
    try:
        user_id = int(idusuario.value)
    except ValueError:
        page.open(
            ft.SnackBar(
                ft.Text("El ID debe ser un número entero válido."),
                bgcolor=ft.Colors.RED_700,
            )
        )
        page.update()
        return

    # 2. Crear el payload
    payload = {
        "id": user_id,
        "nombre": nombre_usuario.value,
        "correo": email_usuario.value,
    } 
    # 3. Realizar la solicitud POST
    try:
        # Aquí se realiza la solicitud a tu API de FastAPI
        response = requests.post(f"{API_BASE_URL}/usuarios/", json=payload)

        print("Payload a enviar:", payload)
        # 4. Mostrar mensaje de éxito y limpiar campos
        page.open(
            ft.SnackBar(
                ft.Text(f"Usuario {user_id} creado exitosamente!"),
                bgcolor=ft.Colors.GREEN_700,
            )
        )

        idusuario.value = ""
        nombre_usuario.value = ""
        email_usuario.value = ""

        page.update()

    except requests.exceptions.RequestException as e:
        # 5. Manejar errores de la solicitud (conexión o respuesta de la API)
        error_message = f"Error: No se pudo conectar a la API ({API_BASE_URL})."
        if response.status_code == 422:
            error_message = "Error de validación (422): Revise los datos de entrada."
        elif response.status_code == 400:
            error_message = "Error 400: Usuario con ese ID ya existe."
        else:
            error_message = (
                f"Error al crear usuario: {response.status_code} - {response.text}"
            )

        page.open(ft.SnackBar(ft.Text(error_message), bgcolor=ft.Colors.RED_700))
        page.update()


def main(page: ft.Page):
    """
    Función principal de Flet. Recibe la instancia de Page.
    """
    # Configuración de la página (usando la instancia 'page')
    page.title = "Cliente Flet para API de Usuarios (FastAPI)"
    page.theme_mode = ft.ThemeMode.LIGHT
    page.vertical_alignment = ft.MainAxisAlignment.START
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.scroll = ft.ScrollMode.AUTO
    page.padding = 20
    page.bgcolor = ft.Colors.BLUE_GREY_50

    # --- Componentes de Formulario ---
    idusuario = ft.TextField(
        col={"sm": 12, "md": 3},
        label="ID (Entero)",
        keyboard_type=ft.KeyboardType.NUMBER,
        max_length=5,
        width=150,
        hint_text="Ej: 101",
    )
    nombre_usuario = ft.TextField(
        col={"sm": 12, "md": 5}, label="Nombre", max_length=50, hint_text="Ej: Jane Doe"
    )
    email_usuario = ft.TextField(
        value="jane@example.com",
        col={"sm": 12, "md": 4},
        label="Correo Electrónico",
        max_length=100,
        keyboard_type=ft.KeyboardType.EMAIL,
        hint_text="Ej: jane@example.com",
    )
    usuarios_tabla = ft.DataTable(
        columns=[
            ft.DataColumn(ft.Text("ID", weight=ft.FontWeight.BOLD)),
            ft.DataColumn(ft.Text("Nombre", weight=ft.FontWeight.BOLD)),
            ft.DataColumn(ft.Text("Correo Electrónico", weight=ft.FontWeight.BOLD)),
        ],
        rows=[],
        border=ft.border.all(1, ft.Colors.BLUE_GREY_100),
        border_radius=10,
        vertical_lines=ft.border.BorderSide(1, ft.Colors.BLUE_GREY_50),
        horizontal_lines=ft.border.BorderSide(1, ft.Colors.BLUE_GREY_50),
        column_spacing=25,
        heading_row_color=ft.Colors.BLUE_GREY_50,
        data_row_min_height=40,
    )
    contenedor_Entrada = ft.Container( 
        padding=30,
        content=ft.Column(
            controls=[
                ft.Text("Gestión de Usuarios", size=24, weight=ft.FontWeight.BOLD),
                ft.Divider(height=10),
                ft.ResponsiveRow(
                    controls=[idusuario, nombre_usuario, email_usuario],
                    spacing=15,
                    run_spacing=15,
                ),
                ft.Row(
                    controls=[
                        ft.ElevatedButton(
                            "Crear Usuario (POST)",
                            icon=ft.Icons.PERSON_ADD,
                            # La función ahora recibe la instancia 'page'
                            on_click=lambda e: crear_usuario(
                                page, idusuario, nombre_usuario, email_usuario
                            ),
                        ),
                        ft.OutlinedButton(
                            "Limpiar",
                            icon=ft.Icons.REFRESH,
                            on_click=lambda e: Limpiar(),
                        ),
                    ],
                    spacing=15,
                    alignment=ft.MainAxisAlignment.START,
                ),
            ],
            spacing=20,
        ),
        margin=ft.margin.only(bottom=20),
        border=ft.border.all(1, ft.Colors.BLUE_GREY_200),
        border_radius=12,
        bgcolor=ft.Colors.WHITE,
        shadow=ft.BoxShadow(0, 5, ft.Colors.with_opacity(0.1, ft.Colors.BLACK)),
    )

    salida = ft.Text("Esperando datos...")
    page.add(contenedor_Entrada, usuarios_tabla, salida)

    page.run_task(cargar_datos, page, usuarios_tabla, salida)

    page.update()

    def Limpiar():
        idusuario.value = ""
        nombre_usuario.value = ""
        email_usuario.value = ""
        page.update()


# Ejecutar la aplicación Flet
if __name__ == "__main__":
    ft.app(target=main, view=ft.WEB_BROWSER, port=8550)
