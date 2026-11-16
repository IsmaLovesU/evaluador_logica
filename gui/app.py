"""Ventana principal: organiza las cuatro pestañas del flujo de trabajo."""

from __future__ import annotations

import tkinter as tk
from tkinter import ttk

from logic.interpretacion import Interpretacion
from logic.lenguaje import Lenguaje

from .tab_formula import TabFormula
from .tab_interpretacion import TabInterpretacion
from .tab_lenguaje import TabLenguaje
from .tab_resultado import TabResultado


class AplicacionEvaluador(tk.Tk):
    def __init__(self) -> None:
        super().__init__()
        self.title("Evaluador semántico — Lógica de primer orden (MM3032)")
        self.geometry("1040x720")
        self.minsize(860, 600)

        self.lenguaje = Lenguaje()
        self.interpretacion: Interpretacion | None = None
        self.formula_ast = None
        self.formula_texto: str = ""

        estilo = ttk.Style(self)
        try:
            estilo.theme_use("vista" if "vista" in estilo.theme_names() else estilo.theme_use())
        except tk.TclError:
            pass

        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill="both", expand=True, padx=6, pady=6)

        self.tab_lenguaje = TabLenguaje(self.notebook, self)
        self.tab_interpretacion = TabInterpretacion(self.notebook, self)
        self.tab_formula = TabFormula(self.notebook, self)
        self.tab_resultado = TabResultado(self.notebook, self)

        self.notebook.add(self.tab_lenguaje, text="1. Lenguaje")
        self.notebook.add(self.tab_interpretacion, text="2. Interpretación")
        self.notebook.add(self.tab_formula, text="3. Fórmula y entorno")
        self.notebook.add(self.tab_resultado, text="4. Resultado")

    # -- notificaciones entre pestañas -------------------------------------------------
    def al_confirmar_lenguaje(self) -> None:
        self.interpretacion = None
        self.formula_ast = None
        self.tab_interpretacion.reconstruir()
        self.tab_formula.reiniciar()
        self.tab_resultado.limpiar()
        self.notebook.select(self.tab_interpretacion)

    def al_confirmar_interpretacion(self) -> None:
        self.formula_ast = None
        self.tab_formula.reiniciar()
        self.tab_resultado.limpiar()
        self.notebook.select(self.tab_formula)

    def ir_a_resultado(self) -> None:
        self.notebook.select(self.tab_resultado)


def ejecutar() -> None:
    app = AplicacionEvaluador()
    app.mainloop()
