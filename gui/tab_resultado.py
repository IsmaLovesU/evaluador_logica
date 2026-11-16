"""Pestaña 4: Verdadero/Falso y el árbol de explicación de las razones decisivas."""

from __future__ import annotations

import tkinter as tk
from tkinter import ttk

from logic.explicacion import Explicacion


class TabResultado(ttk.Frame):
    def __init__(self, master, app) -> None:
        super().__init__(master, padding=12)
        self.app = app

        self.resultado_lbl = ttk.Label(self, text="—", font=("Segoe UI", 28, "bold"))
        self.resultado_lbl.pack(anchor="w")

        self.subtitulo_lbl = ttk.Label(self, text="Todavía no se ha evaluado ninguna fórmula.", wraplength=960)
        self.subtitulo_lbl.pack(anchor="w", pady=(2, 10))

        ttk.Label(self, text="Explicación de las razones decisivas:", font=("Segoe UI", 10, "bold")).pack(anchor="w")

        marco_arbol = ttk.Frame(self)
        marco_arbol.pack(fill="both", expand=True, pady=(4, 0))

        self.arbol = ttk.Treeview(marco_arbol, show="tree")
        scrollbar = ttk.Scrollbar(marco_arbol, orient="vertical", command=self.arbol.yview)
        self.arbol.configure(yscrollcommand=scrollbar.set)
        self.arbol.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        self.arbol.tag_configure("decisivo", foreground="#0a5d00", font=("Segoe UI", 9, "bold"))
        self.arbol.tag_configure("no_decisivo", foreground="#555555")

    def limpiar(self) -> None:
        self.resultado_lbl.config(text="—", foreground="black")
        self.subtitulo_lbl.config(text="Todavía no se ha evaluado ninguna fórmula.")
        self.arbol.delete(*self.arbol.get_children())

    def mostrar(self, valor: bool, explicacion: Explicacion, formula_texto: str, entorno: dict[str, str]) -> None:
        self.resultado_lbl.config(
            text="VERDADERO" if valor else "FALSO",
            foreground="#0a5d00" if valor else "#b00020",
        )
        if entorno:
            entorno_txt = ", ".join(f"{k} = {v}" for k, v in entorno.items())
            subtitulo = f"Fórmula: {formula_texto}        Entorno: {entorno_txt}"
        else:
            subtitulo = f"Fórmula: {formula_texto}        (fórmula cerrada, sin entorno)"
        self.subtitulo_lbl.config(text=subtitulo)

        self.arbol.delete(*self.arbol.get_children())
        self._insertar_nodo("", explicacion)

    def _insertar_nodo(self, padre: str, explicacion: Explicacion) -> None:
        tag = "decisivo" if explicacion.decisivo else "no_decisivo"
        nodo = self.arbol.insert(padre, "end", text=explicacion.texto, open=True, tags=(tag,))
        for hijo in explicacion.hijos:
            self._insertar_nodo(nodo, hijo)
