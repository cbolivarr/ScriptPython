import flet as ft
import math

def main(page: ft.Page):
    # --- Configuración de la Ventana Principal ---
    page.title = "Calculadora Flet Pro"
    page.window_width = 400
    page.window_height = 650
    page.window_resizable = False
    page.bgcolor = "black"  
    page.theme_mode = ft.ThemeMode.DARK 
    page.padding = 20
    # Centramos todo el contenido en la pantalla
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.vertical_alignment = ft.MainAxisAlignment.CENTER

    # --- Estado de la pantalla (Reactivo) ---
    pantalla_texto = ft.Text(value="", size=32, color="white", weight=ft.FontWeight.BOLD)

    # --- Funciones de la calculadora ---
    def click_boton(e):
        valor = e.control.data  
        pantalla_texto.value += str(valor)
        page.update()  

    def borrar(e):
        pantalla_texto.value = ""
        page.update()

    def retroceder(e):
        pantalla_texto.value = pantalla_texto.value[:-1]
        page.update()

    def calcular(e):
        try:
            expresion = pantalla_texto.value
            expresion = expresion.replace('^', '**').replace('√', 'math.sqrt')
            resultado = str(eval(expresion))
            
            if resultado.endswith('.0'):
                resultado = resultado[:-2]
                
            pantalla_texto.value = resultado
        except Exception:
            pantalla_texto.value = "Error"
        page.update()

    # --- Componente de Pantalla ---
    pantalla_container = ft.Container(
        content=ft.Row([pantalla_texto], alignment=ft.MainAxisAlignment.END), 
        bgcolor="grey900", 
        padding=15,
        border_radius=15,
        height=80,
        alignment=ft.Alignment(1, 0) 
    )

    # --- Función para construir un botón estandarizado ---
    def crear_boton(texto, bg_col="grey800", text_col="white", accion=click_boton, expand=True, height=60):
        texto_interior = ft.Text(value=texto, color=text_col, size=18, weight=ft.FontWeight.BOLD)
        
        if texto == 'π':
            on_click_func = lambda e: [pantalla_texto.__setattr__('value', pantalla_texto.value + str(math.pi)), page.update()]
        else:
            on_click_func = accion

        return ft.Container(
            content=ft.FilledButton(
                content=texto_interior,
                bgcolor=bg_col,
                style=ft.ButtonStyle(
                    shape=ft.RoundedRectangleBorder(radius=12),
                    # CORREGIDO: Usamos ft.Padding con los 4 lados en 0 para evitar errores de atributo
                    padding=ft.Padding(0, 0, 0, 0) 
                ), 
                on_click=on_click_func,
                data=texto
            ),
            expand=expand,
            height=height
        )

    # --- Distribución del Teclado usando Filas y Columnas ---
    r1 = ft.Row([
        crear_boton("C", bg_col="red700"),
        crear_boton("⌫", bg_col="red700", accion=retroceder),
        crear_boton("(", bg_col="surfaceVariant", text_col="cyanAccent"),
        crear_boton(")", bg_col="surfaceVariant", text_col="cyanAccent"),
    ], spacing=8)

    r2 = ft.Row([
        crear_boton("^", bg_col="surfaceVariant", text_col="cyanAccent"),
        crear_boton("√", bg_col="surfaceVariant", text_col="cyanAccent"),
        crear_boton("/", bg_col="surfaceVariant", text_col="cyanAccent"),
        crear_boton("*", bg_col="surfaceVariant", text_col="cyanAccent"),
    ], spacing=8)

    r3 = ft.Row([
        crear_boton("7"), crear_boton("8"), crear_boton("9"),
        crear_boton("-", bg_col="surfaceVariant", text_col="cyanAccent"),
    ], spacing=8)

    r4 = ft.Row([
        crear_boton("4"), crear_boton("5"), crear_boton("6"),
        crear_boton("+", bg_col="surfaceVariant", text_col="cyanAccent"),
    ], spacing=8)

    bloque_izquierdo = ft.Column([
        ft.Row([crear_boton("1"), crear_boton("2"), crear_boton("3")], spacing=8),
        ft.Row([crear_boton("0"), crear_boton("."), crear_boton("π")], spacing=8)
    ], spacing=8, expand=3) 

    bloque_derecho = ft.Column([
        crear_boton("=", bg_col="blue700", accion=calcular, height=128) 
    ], expand=1) 

    r5_6 = ft.Row([bloque_izquierdo, bloque_derecho], spacing=8)

    # --- Contenedor del Teclado Completo ---
    teclado = ft.Column([r1, r2, r3, r4, r5_6], spacing=8)

    # --- Encapsulamos todo en un contenedor central con ancho fijo ---
    calculadora_layout = ft.Container(
        content=ft.Column([
            pantalla_container,
            ft.Container(height=5), 
            teclado
        ], spacing=10),
        width=350, 
    )

    # --- Agregar el diseño final a la página ---
    page.add(calculadora_layout)

ft.run(main)