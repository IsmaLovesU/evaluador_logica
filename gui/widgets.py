"""Widgets auxiliares reutilizados por varias pestañas de la interfaz."""

from __future__ import annotations

import tkinter as tk
from tkinter import ttk


class MarcoDesplazable(ttk.Frame):
    """Un ttk.Frame con scroll vertical, útil cuando las tablas de
    interpretación (tuplas de D^n) crecen más de lo que cabe en pantalla."""

    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self.canvas = tk.Canvas(self, borderwidth=0, highlightthickness=0)
        self.scrollbar = ttk.Scrollbar(self, orient="vertical", command=self.canvas.yview)
        self.interior = ttk.Frame(self.canvas)

        self.interior.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")),
        )
        self.canvas_window = self.canvas.create_window((0, 0), window=self.interior, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        self.canvas.bind("<Configure>", self._ajustar_ancho_interior)
        self.canvas.bind("<Enter>", lambda e: self.canvas.bind_all("<MouseWheel>", self._en_rueda_raton))
        self.canvas.bind("<Leave>", lambda e: self.canvas.unbind_all("<MouseWheel>"))

        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")

    def _ajustar_ancho_interior(self, evento) -> None:
        self.canvas.itemconfig(self.canvas_window, width=evento.width)

    def _en_rueda_raton(self, evento) -> None:
        self.canvas.yview_scroll(int(-1 * (evento.delta / 120)), "units")


def etiqueta_error(master, texto: str = "") -> ttk.Label:
    return ttk.Label(master, text=texto, foreground="#b00020", wraplength=560, justify="left")
