"""Calculadora grafica y evaluador seguro de expresiones."""

import ast
import math
import re
from numbers import Real

import flet as ft


_OPERADORES = {
    ast.Add: lambda left, right: left + right,
    ast.Sub: lambda left, right: left - right,
    ast.Mult: lambda left, right: left * right,
    ast.Div: lambda left, right: left / right,
    ast.Pow: lambda left, right: left**right,
    ast.USub: lambda value: -value,
    ast.UAdd: lambda value: value,
}


def evaluar(expresion: str) -> Real:
    """Evalua solo numeros y operadores aritmeticos permitidos."""
    expresion = expresion.replace("^", "**")
    expresion = re.sub(r"√(\d+(?:\.\d+)?)", r"sqrt(\1)", expresion)
    expresion = expresion.replace("√(", "sqrt(")

    def visitar(nodo: ast.AST) -> Real:
        if isinstance(nodo, ast.Expression):
            return visitar(nodo.body)
        if isinstance(nodo, ast.Constant) and isinstance(nodo.value, (int, float)):
            return nodo.value
        if isinstance(nodo, ast.BinOp) and type(nodo.op) in _OPERADORES:
            return _OPERADORES[type(nodo.op)](visitar(nodo.left), visitar(nodo.right))
        if isinstance(nodo, ast.UnaryOp) and type(nodo.op) in _OPERADORES:
            return _OPERADORES[type(nodo.op)](visitar(nodo.operand))
        if isinstance(nodo, ast.Call) and isinstance(nodo.func, ast.Name) and nodo.func.id == "sqrt":
            if len(nodo.args) != 1:
                raise ValueError("sqrt requiere un argumento")
            return math.sqrt(visitar(nodo.args[0]))
        raise ValueError("expresion no permitida")

    return visitar(ast.parse(expresion, mode="eval"))


def crear_app(page: ft.Page) -> None:
    page.title = "Calculadora"
    page.window_width = 400
    page.window_height = 650
    page.window_resizable = False
    page.bgcolor = "black"
    page.theme_mode = ft.ThemeMode.DARK
    page.padding = 20
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.vertical_alignment = ft.MainAxisAlignment.CENTER

    pantalla = ft.Text(value="", size=32, color="white", weight=ft.FontWeight.BOLD)

    def actualizar(valor: str) -> None:
        pantalla.value += valor
        page.update()

    def calcular(_event: ft.ControlEvent) -> None:
        try:
            resultado = str(evaluar(pantalla.value))
            pantalla.value = resultado[:-2] if resultado.endswith(".0") else resultado
        except (SyntaxError, ValueError, ZeroDivisionError, OverflowError):
            pantalla.value = "Error"
        page.update()

    def boton(texto: str, color: str = "grey800", accion=None) -> ft.Container:
        accion = accion or (lambda _event: actualizar(texto))
        if texto == "pi":
            accion = lambda _event: actualizar(str(math.pi))
        return ft.Container(
            content=ft.FilledButton(
                content=ft.Text(texto, color="white", size=18, weight=ft.FontWeight.BOLD),
                bgcolor=color,
                on_click=accion,
                style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=12)),
            ),
            expand=True,
            height=60,
        )

    def limpiar(_event: ft.ControlEvent) -> None:
        pantalla.value = ""
        page.update()

    def retroceder(_event: ft.ControlEvent) -> None:
        pantalla.value = pantalla.value[:-1]
        page.update()

    operador = "surfaceVariant"
    filas = [
        ft.Row([boton("C", "red700", limpiar), boton("⌫", "red700", retroceder), boton("("), boton(")")], spacing=8),
        ft.Row([boton("^", operador), boton("√", operador), boton("/", operador), boton("*", operador)], spacing=8),
        ft.Row([boton("7"), boton("8"), boton("9"), boton("-", operador)], spacing=8),
        ft.Row([boton("4"), boton("5"), boton("6"), boton("+", operador)], spacing=8),
        ft.Row([ft.Column([ft.Row([boton("1"), boton("2"), boton("3")], spacing=8), ft.Row([boton("0"), boton("."), boton("pi")], spacing=8)], expand=3, spacing=8), boton("=", "blue700", calcular)], spacing=8),
    ]
    page.add(ft.Container(ft.Column([ft.Container(ft.Row([pantalla], alignment=ft.MainAxisAlignment.END), bgcolor="grey900", padding=15, border_radius=15, height=80), ft.Column(filas, spacing=8)], spacing=10), width=350))


def main() -> None:
    """Inicia la interfaz grafica."""
    ft.run(crear_app)


if __name__ == "__main__":
    main()