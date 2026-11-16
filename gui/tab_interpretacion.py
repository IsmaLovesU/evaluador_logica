"""Pestaña 2: dominio finito D, f^I para cada función y P^I para cada predicado."""

from __future__ import annotations

import tkinter as tk
from itertools import product
from tkinter import ttk

from logic.errores import ErrorEvaluador
from logic.interpretacion import Interpretacion

from .widgets import MarcoDesplazable, etiqueta_error


class TabInterpretacion(ttk.Frame):
    def __init__(self, master, app) -> None:
        super().__init__(master, padding=12)
        self.app = app
        self._vars_funciones: dict[str, dict[tuple[str, ...], tk.StringVar]] = {}
        self._vars_predicados: dict[str, dict[tuple[str, ...], tk.BooleanVar]] = {}

        encabezado = ttk.Frame(self)
        encabezado.pack(fill="x")
        ttk.Label(encabezado, text="Dominio D (elementos separados por comas):").pack(side="left")
        self.dominio_entry = ttk.Entry(encabezado, width=40)
        self.dominio_entry.pack(side="left", padx=6)
        ttk.Button(encabezado, text="Construir tablas de interpretación", command=self._construir_tablas).pack(
            side="left", padx=6
        )

        self.error_lbl = etiqueta_error(self)
        self.error_lbl.pack(fill="x", pady=(4, 4))

        self.marco_desplazable = MarcoDesplazable(self)
        self.marco_desplazable.pack(fill="both", expand=True, pady=(4, 4))
        self.area_tablas = self.marco_desplazable.interior

        pie = ttk.Frame(self)
        pie.pack(fill="x")
        self.boton_guardar = ttk.Button(
            pie, text="Guardar interpretación y continuar →", command=self._guardar, state="disabled"
        )
        self.boton_guardar.pack(side="left")

        self._mensaje_inicial()

    def _mensaje_inicial(self) -> None:
        ttk.Label(
            self.area_tablas,
            text="Primero declare el lenguaje y luego construya aquí las tablas de interpretación.",
            foreground="#555555",
        ).pack(anchor="w", padx=4, pady=8)

    # -- API invocada por AplicacionEvaluador -------------------------------------------------
    def reconstruir(self) -> None:
        """Se llama cuando cambia el lenguaje: hay que empezar de cero."""
        self.app.interpretacion = None
        self.dominio_entry.delete(0, tk.END)
        self._limpiar_area()
        self._mensaje_inicial()
        self.boton_guardar.config(state="disabled")
        self.error_lbl.config(text="")

    def _limpiar_area(self) -> None:
        for widget in self.area_tablas.winfo_children():
            widget.destroy()
        self._vars_funciones.clear()
        self._vars_predicados.clear()

    # -- construir tablas a partir del dominio ingresado -------------------------------------------------
    def _construir_tablas(self) -> None:
        self.error_lbl.config(text="")
        try:
            self.app.lenguaje.validar_lenguaje_completo()
        except ErrorEvaluador as e:
            self.error_lbl.config(text=f"Lenguaje inválido: {e}")
            return

        dominio = [x.strip() for x in self.dominio_entry.get().split(",") if x.strip() != ""]
        try:
            interpretacion = Interpretacion(self.app.lenguaje, dominio)
        except ErrorEvaluador as e:
            self.error_lbl.config(text=str(e))
            self.boton_guardar.config(state="disabled")
            return

        self.app.interpretacion = interpretacion
        self._limpiar_area()

        for nombre, aridad in self.app.lenguaje.funciones.items():
            self._construir_tabla_funcion(nombre, aridad, interpretacion.dominio)
        for nombre, aridad in self.app.lenguaje.predicados.items():
            self._construir_tabla_predicado(nombre, aridad, interpretacion.dominio)

        self.boton_guardar.config(state="normal")

    def _construir_tabla_funcion(self, nombre: str, aridad: int, dominio: list[str]) -> None:
        marco = ttk.LabelFrame(self.area_tablas, text=f"Función {nombre} (aridad {aridad})", padding=8)
        marco.pack(fill="x", padx=4, pady=6)

        self._vars_funciones[nombre] = {}
        tuplas = list(product(dominio, repeat=aridad)) if aridad > 0 else [()]
        for fila, tupla in enumerate(tuplas):
            etiqueta = f"{nombre}({', '.join(tupla)})" if tupla else f"{nombre}()  (constante)"
            ttk.Label(marco, text=f"{etiqueta}  =").grid(row=fila, column=0, sticky="w", pady=2)
            var = tk.StringVar(value="")
            combo = ttk.Combobox(marco, textvariable=var, values=dominio, width=10, state="readonly")
            combo.grid(row=fila, column=1, sticky="w", padx=6)
            self._vars_funciones[nombre][tupla] = var

    def _construir_tabla_predicado(self, nombre: str, aridad: int, dominio: list[str]) -> None:
        marco = ttk.LabelFrame(self.area_tablas, text=f"Predicado {nombre} (aridad {aridad})", padding=8)
        marco.pack(fill="x", padx=4, pady=6)

        self._vars_predicados[nombre] = {}
        tuplas = list(product(dominio, repeat=aridad)) if aridad > 0 else [()]
        columnas = 4
        for i, tupla in enumerate(tuplas):
            etiqueta = f"{nombre}({', '.join(tupla)})" if tupla else f"{nombre}  (proposición)"
            var = tk.BooleanVar(value=False)
            chk = ttk.Checkbutton(marco, text=etiqueta, variable=var)
            chk.grid(row=i // columnas, column=i % columnas, sticky="w", padx=6, pady=2)
            self._vars_predicados[nombre][tupla] = var

    # -- guardar -------------------------------------------------
    def _guardar(self) -> None:
        self.error_lbl.config(text="")
        interp = self.app.interpretacion
        if interp is None:
            self.error_lbl.config(text="Primero construya las tablas de interpretación.")
            return
        try:
            for nombre, tuplas in self._vars_funciones.items():
                for tupla, var in tuplas.items():
                    valor = var.get()
                    if not valor:
                        raise ErrorEvaluador(
                            f"Falta asignar el valor de la función '{nombre}' para la tupla {tupla or '()'}."
                        )
                    interp.fijar_funcion(nombre, tupla, valor)
            for nombre, tuplas in self._vars_predicados.items():
                for tupla, var in tuplas.items():
                    interp.fijar_predicado_tupla(nombre, tupla, bool(var.get()))
            interp.validar_completa()
        except ErrorEvaluador as e:
            self.error_lbl.config(text=str(e))
            return

        self.app.al_confirmar_interpretacion()
