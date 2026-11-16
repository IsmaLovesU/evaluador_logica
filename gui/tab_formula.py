"""Pestaña 3: edición de la fórmula (botones + teclado), detección de
variables libres y captura del entorno que las fija en el dominio."""

from __future__ import annotations

import tkinter as tk
from tkinter import ttk

from logic.errores import ErrorEvaluador
from logic.parser import parsear
from logic.semantica import evaluar_formula
from logic.variables import variables_libres

from .widgets import etiqueta_error

BOTONES_SIMBOLOS = [
    ("¬", "Negación"),
    ("∧", "Conjunción"),
    ("∨", "Disyunción"),
    ("→", "Implicación"),
    ("↔", "Bicondicional"),
    ("∀", "Para todo"),
    ("∃", "Existe"),
    ("(", "Paréntesis izquierdo"),
    (")", "Paréntesis derecho"),
    (",", "Coma"),
]


class TabFormula(ttk.Frame):
    def __init__(self, master, app) -> None:
        super().__init__(master, padding=12)
        self.app = app
        self._vars_entorno: dict[str, tk.StringVar] = {}

        ttk.Label(
            self,
            text="Escriba la fórmula usando el teclado para letras, variables y dígitos; "
            "use los botones para insertar conectivos, cuantificadores y paréntesis.",
            wraplength=960,
        ).pack(anchor="w", pady=(0, 8))

        barra = ttk.Frame(self)
        barra.pack(fill="x", pady=(0, 6))
        for simbolo, descripcion in BOTONES_SIMBOLOS:
            ttk.Button(
                barra, text=simbolo, width=3, command=lambda s=simbolo: self._insertar(s)
            ).pack(side="left", padx=2)
        ttk.Button(barra, text="⌫", width=3, command=self._borrar_uno).pack(side="left", padx=(10, 2))
        ttk.Button(barra, text="Limpiar", command=self._limpiar_formula).pack(side="left", padx=2)

        self.formula_entry = tk.Entry(self, font=("Consolas", 16))
        self.formula_entry.pack(fill="x", pady=(0, 8), ipady=4)
        self.formula_entry.focus_set()

        ttk.Button(self, text="Analizar fórmula", command=self._analizar).pack(anchor="w")

        self.error_lbl = etiqueta_error(self)
        self.error_lbl.pack(fill="x", pady=(6, 6))

        self.marco_entorno = ttk.LabelFrame(self, text="Variables libres y entorno", padding=10)
        self.marco_entorno.pack(fill="x", pady=(0, 10))
        self._info_lbl = ttk.Label(self.marco_entorno, text="Analice una fórmula para ver sus variables libres.")
        self._info_lbl.pack(anchor="w")

        self.boton_evaluar = ttk.Button(self, text="Evaluar →", command=self._evaluar, state="disabled")
        self.boton_evaluar.pack(anchor="w")

    # -- edición -------------------------------------------------
    def _insertar(self, simbolo: str) -> None:
        pos = self.formula_entry.index(tk.INSERT)
        self.formula_entry.insert(pos, simbolo)
        self.formula_entry.icursor(pos + len(simbolo))
        self.formula_entry.focus_set()

    def _borrar_uno(self) -> None:
        pos = self.formula_entry.index(tk.INSERT)
        if pos > 0:
            self.formula_entry.delete(pos - 1, pos)
        self.formula_entry.focus_set()

    def _limpiar_formula(self) -> None:
        self.formula_entry.delete(0, tk.END)
        self.formula_entry.focus_set()

    # -- API invocada por AplicacionEvaluador -------------------------------------------------
    def reiniciar(self) -> None:
        self.app.formula_ast = None
        self._limpiar_entorno()
        self.boton_evaluar.config(state="disabled")
        self.error_lbl.config(text="")

    def _limpiar_entorno(self) -> None:
        for widget in self.marco_entorno.winfo_children():
            widget.destroy()
        self._vars_entorno.clear()
        self._info_lbl = ttk.Label(self.marco_entorno, text="Analice una fórmula para ver sus variables libres.")
        self._info_lbl.pack(anchor="w")

    # -- flujo principal -------------------------------------------------
    def _analizar(self) -> None:
        self.error_lbl.config(text="")
        self.app.formula_ast = None
        self.boton_evaluar.config(state="disabled")

        if self.app.interpretacion is None:
            self.error_lbl.config(text="Primero debe declarar el lenguaje y guardar la interpretación.")
            return

        texto = self.formula_entry.get()
        try:
            formula = parsear(texto, self.app.lenguaje)
        except ErrorEvaluador as e:
            self.error_lbl.config(text=str(e))
            self._limpiar_entorno()
            return

        self.app.formula_ast = formula
        self.app.formula_texto = texto
        libres = sorted(variables_libres(formula))
        self._construir_entorno(libres)
        self.boton_evaluar.config(state="normal")

    def _construir_entorno(self, libres: list[str]) -> None:
        for widget in self.marco_entorno.winfo_children():
            widget.destroy()
        self._vars_entorno.clear()

        if not libres:
            ttk.Label(self.marco_entorno, text="La fórmula es cerrada: no tiene variables libres.").pack(anchor="w")
            return

        ttk.Label(
            self.marco_entorno,
            text=f"Variables libres detectadas: {', '.join(libres)}. Asigne un valor de D a cada una:",
        ).pack(anchor="w", pady=(0, 6))
        for var in libres:
            fila = ttk.Frame(self.marco_entorno)
            fila.pack(fill="x", pady=2)
            ttk.Label(fila, text=f"{var} =", width=8).pack(side="left")
            sv = tk.StringVar(value="")
            combo = ttk.Combobox(fila, textvariable=sv, values=self.app.interpretacion.dominio, width=10, state="readonly")
            combo.pack(side="left")
            self._vars_entorno[var] = sv

    def _evaluar(self) -> None:
        self.error_lbl.config(text="")
        if self.app.formula_ast is None:
            self.error_lbl.config(text="Primero analice la fórmula.")
            return

        entorno: dict[str, str] = {}
        for var, sv in self._vars_entorno.items():
            valor = sv.get()
            if not valor:
                self.error_lbl.config(text=f"Debe asignar un valor del dominio a la variable libre '{var}'.")
                return
            entorno[var] = valor

        try:
            valor, explicacion = evaluar_formula(self.app.formula_ast, self.app.interpretacion, entorno)
        except ErrorEvaluador as e:
            self.error_lbl.config(text=str(e))
            return

        self.app.tab_resultado.mostrar(valor, explicacion, self.app.formula_texto, entorno)
        self.app.ir_a_resultado()
