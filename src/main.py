import flet as ft
import requests
import asyncio
import os
import time
import random
from faker import Faker

#API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000")
API_BASE_URL = os.getenv("API_BASE_URL", "http://64.181.166.239")

fake = Faker("es_ES")

# ------------------- Generadores Random -------------------
def generar_nombre_random():
    return fake.first_name()

def generar_email_random():
    numero = random.randint(1, 999)
    dominio = random.choice(["example.com", "correo.com", "gmail.com"])
    return f"{fake.first_name()}{numero}@{dominio}"

def generar_contraseña_random():
    letras = "".join(random.choices("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ", k=4))
    numeros = "".join(random.choices("0123456789", k=2))
    return letras + numeros

# ------------------- API -------------------
async def cargar_datos(page: ft.Page, usuarios_tabla: ft.DataTable, salida: ft.Text):
    while True:
        try:
            response = await asyncio.to_thread(requests.get, f"{API_BASE_URL}/usuarios_get")
            if response.status_code == 200:
                data = response.json()
                usuarios_tabla.rows.clear()
                for u in data:
                    usuarios_tabla.rows.append(
                        ft.DataRow(
                            cells=[
                                ft.DataCell(ft.Text(u["nombre"])),
                                ft.DataCell(ft.Text(u["correo"])),
                                ft.DataCell(ft.Text(u.get("rol", "jugador"))),
                                ft.DataCell(ft.Text("Activo" if u.get("activo", True) else "Inactivo")),
                                ft.DataCell(
                                    ft.Row(
                                        [
                                            ft.IconButton(
                                                ft.Icons.EDIT,
                                                tooltip="Editar",
                                                on_click=lambda e, user=u.copy(): abrir_modal_editar(page, user)
                                            ),
                                            ft.IconButton(
                                                ft.Icons.DELETE,
                                                tooltip="Eliminar",
                                                on_click=lambda e, user_id=u["id"]: eliminar_usuario(page, user_id)
                                            ),
                                        ]
                                    )
                                ),
                            ]
                        )
                    )
                salida.value = f"Última actualización: {time.strftime('%H:%M:%S')}"
                page.update()
            else:
                salida.value = f"Error al cargar datos: {response.status_code}"
                page.update()
        except requests.exceptions.RequestException as e:
            salida.value = f"Excepción al conectar con la API: {e}"
            page.update()
        await asyncio.sleep(2)

def crear_usuario(page, nombre_usuario, email_usuario, password_usuario, rol_usuario, activo_usuario):
    if not nombre_usuario.value.strip().replace(" ", "").isalpha():
        page.open(ft.SnackBar(ft.Text("❌ El nombre solo puede contener letras")))
        return

    if len(password_usuario.value) < 6 or not any(c.isdigit() for c in password_usuario.value) or not any(c.isalpha() for c in password_usuario.value):
        page.open(ft.SnackBar(ft.Text("❌ La contraseña debe tener al menos 6 caracteres, letras y números")))
        return

    payload = {
        "nombre": nombre_usuario.value.strip(),
        "correo": email_usuario.value.strip(),
        "password": password_usuario.value,
        "rol": rol_usuario.value,
        "activo": activo_usuario.value,
    }

    try:
        response = requests.post(f"{API_BASE_URL}/usuarios", json=payload)
        print(payload)
        print(response)
        if response.status_code in (200, 201):
            page.open(ft.SnackBar(ft.Text("✅ Usuario creado!"), bgcolor=ft.Colors.GREEN_700))
            Limpiar(nombre_usuario, email_usuario, password_usuario)
        elif response.status_code == 422:
            page.open(ft.SnackBar(ft.Text("⚠️ Error de validación")))
        else:
            page.open(ft.SnackBar(ft.Text(f"⚠️ Error {response.status_code}: {response.text}")))
    except requests.exceptions.RequestException as e:
        page.open(ft.SnackBar(ft.Text(f"❌ Error de conexión: {e}")))
    page.update()

def Limpiar(nombre_usuario, email_usuario, password_usuario):
    nombre_usuario.value = ""
    email_usuario.value = ""
    password_usuario.value = ""
    nombre_usuario.page.update()

def eliminar_usuario(page, user_id: int):
    try:
        response = requests.delete(f"{API_BASE_URL}/usuarios/{user_id}")
        if response.status_code == 200:
            page.open(ft.SnackBar(ft.Text("✅ Usuario eliminado"), bgcolor=ft.Colors.RED_700))
        else:
            page.open(ft.SnackBar(ft.Text(f"⚠️ Error al eliminar: {response.status_code}")))
    except requests.exceptions.RequestException as e:
        page.open(ft.SnackBar(ft.Text(f"❌ Error de conexión: {e}")))
    page.update()

def abrir_modal_editar(page, user):
    nombre_edit = ft.TextField(label="Nombre", value=user["nombre"])
    email_edit = ft.TextField(label="Correo", value=user["correo"])
    rol_edit = ft.Dropdown(label="Rol", options=[ft.dropdown.Option("jugador"), ft.dropdown.Option("admin"), ft.dropdown.Option("moderador")], value=user.get("rol", "jugador"))
    activo_edit = ft.Checkbox(label="Activo", value=user.get("activo", True))
    password_edit = ft.TextField(label="Nueva contraseña", password=True, can_reveal_password=True, value="Temp123")

    def guardar_edicion(e):
        payload = {
            "nombre": nombre_edit.value.strip(),
            "correo": email_edit.value.strip(),
            "rol": rol_edit.value,
            "activo": activo_edit.value,
            "password": password_edit.value
        }
        try:
            response = requests.put(f"{API_BASE_URL}/usuarios/{user['id']}", json=payload)
            if response.status_code == 200:
                page.open(ft.SnackBar(ft.Text("✅ Usuario actualizado"), bgcolor=ft.Colors.GREEN_700))
            else:
                page.open(ft.SnackBar(ft.Text(f"⚠️ Error {response.status_code}: {response.text}")))
        except requests.exceptions.RequestException as e:
            page.open(ft.SnackBar(ft.Text(f"❌ Error de conexión: {e}")))
        cerrar_modal()
    def cerrar_modal():
        page.close(dialog)
        page.update()
    dialog = ft.AlertDialog(
        title=ft.Text("Editar Usuario"),
        content=ft.Column([nombre_edit, email_edit, rol_edit, activo_edit, password_edit], spacing=10),
        actions=[ft.ElevatedButton("Guardar", on_click=guardar_edicion),
                 ft.TextButton("Cancelar", on_click=lambda e: cerrar_modal())],
        actions_alignment=ft.MainAxisAlignment.END
    )
    page.open(dialog)
    page.update()



def generar_datos_random(nombre_field, email_field, password_field):
    nombre_field.value = generar_nombre_random()
    email_field.value = generar_email_random()
    password_field.value = generar_contraseña_random()
    nombre_field.page.update()

# ------------------- UI -------------------
def main(page: ft.Page):
    page.title = "Gestión de Usuarios - Flet & FastAPI"
    page.theme_mode = ft.ThemeMode.LIGHT
    page.scroll = ft.ScrollMode.AUTO
    page.padding = 20
    page.bgcolor = ft.Colors.BLUE_GREY_50

    nombre_usuario = ft.TextField(col=6,label="Nombre", value=generar_nombre_random())
    email_usuario = ft.TextField(col=6,label="Correo Electrónico",  keyboard_type=ft.KeyboardType.EMAIL, value=generar_email_random())
    password_usuario = ft.TextField(col=3,label="Contraseña",  password=True, can_reveal_password=True, value=generar_contraseña_random())
    rol_usuario = ft.Dropdown(col=3,label="Rol",  options=[ft.dropdown.Option("jugador"), ft.dropdown.Option("admin"), ft.dropdown.Option("moderador")])
    activo_usuario = ft.Checkbox(label="Activo", value=True)

    usuarios_tabla = ft.DataTable(
        columns=[ft.DataColumn(ft.Text("Nombre")), ft.DataColumn(ft.Text("Correo")), ft.DataColumn(ft.Text("Rol")), ft.DataColumn(ft.Text("Estado")), ft.DataColumn(ft.Text("Acciones"))],
        rows=[],
        border=ft.border.all(1, ft.Colors.BLUE_GREY_100),
        border_radius=10,
        column_spacing=25,
        heading_row_color=ft.Colors.BLUE_GREY_100,
        expand=True,
        sort_ascending=True,
        
    )

    salida = ft.Text("Esperando datos...")

    contenedor_form = ft.Container(
        content=ft.Column([
            ft.Text("Crear Usuario", size=24, weight=ft.FontWeight.BOLD),
            ft.ResponsiveRow(controls=[nombre_usuario, email_usuario, password_usuario,rol_usuario]),
            activo_usuario,
            ft.Row([
                ft.ElevatedButton("Crear Usuario", on_click=lambda e: crear_usuario(page, nombre_usuario, email_usuario, password_usuario, rol_usuario, activo_usuario)),
                ft.ElevatedButton("Generar datos random", on_click=lambda e: generar_datos_random(nombre_usuario, email_usuario, password_usuario)),
                ft.OutlinedButton("Limpiar", on_click=lambda e: Limpiar(nombre_usuario, email_usuario, password_usuario))
            ], spacing=10),
            
        ], spacing=10),
        padding=20,
        border=ft.border.all(1, ft.Colors.BLUE_GREY_200),
        border_radius=10,
        bgcolor=ft.Colors.WHITE
    )

    page.add(contenedor_form, ft.Column(height=450,scroll=ft.ScrollMode.AUTO, controls=[usuarios_tabla, salida],  expand=True,horizontal_alignment=ft.CrossAxisAlignment.STRETCH))
    page.run_task(cargar_datos, page, usuarios_tabla, salida)

if __name__ == "__main__":
    ft.app(target=main, view=ft.WEB_BROWSER, port=8550)
