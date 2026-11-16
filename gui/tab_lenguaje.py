"""Pestaña 1: declarar los símbolos de predicado y de función con su aridad."""

from __future__ import annotations

import tkinter as tk
from tkinter import ttk

from logic.errores import ErrorEvaluador

from .widgets import etiqueta_error


class TabLenguaje(ttk.Frame):
    def __init__(self, master, app) -> None:
        super().__init__(master, padding=12)
        self.app = app

        ttk.Label(
            self,
            text="Declare los símbolos del lenguaje: predicados y funciones, con su aridad (número de argumentos).",
            wraplength=940,
            font=("Segoe UI", 10, "bold"),
        ).pack(anchor="w", pady=(0, 10))

        contenedor = ttk.Frame(self)
        contenedor.pack(fill="both", expand=True)
        contenedor.columnconfigure(0, weight=1)
        contenedor.columnconfigure(1, weight=1)

        self._construir_bloque_predicados(contenedor).grid(row=0, column=0, sticky="nsew", padx=(0, 8))
        self._construir_bloque_funciones(contenedor).grid(row=0, column=1, sticky="nsew", padx=(8, 0))

        pie = ttk.Frame(self)
        pie.pack(fill="x", pady=(12, 0))
        ttk.Button(pie, text="Confirmar lenguaje y continuar →", command=self._confirmar).pack(side="left")
        self.error_lbl = etiqueta_error(pie)
        self.error_lbl.pack(side="left", padx=12)

        self._refrescar_listas()

    # -- bloque de predicados -------------------------------------------------
    def _construir_bloque_predicados(self, master) -> ttk.LabelFrame:
        marco = ttk.LabelFrame(master, text="Predicados", padding=10)

        formulario = ttk.Frame(marco)
        formulario.pack(fill="x")
        ttk.Label(formulario, text="Nombre:").grid(row=0, column=0, sticky="w")
        self.pred_nombre = ttk.Entry(formulario, width=14)
        self.pred_nombre.grid(row=0, column=1, padx=4)
        ttk.Label(formulario, text="Aridad:").grid(row=0, column=2, sticky="w")
        self.pred_aridad = ttk.Spinbox(formulario, from_=0, to=5, width=5)
        self.pred_aridad.set(1)
        self.pred_aridad.grid(row=0, column=3, padx=4)
        ttk.Button(formulario, text="Agregar", command=self._agregar_predicado).grid(row=0, column=4, padx=4)

        self.lista_pred = ttk.Treeview(marco, columns=("nombre", "aridad"), show="headings", height=8)
        self.lista_pred.heading("nombre", text="Nombre")
        self.lista_pred.heading("aridad", text="Aridad")
        self.lista_pred.column("nombre", width=140)
        self.lista_pred.column("aridad", width=60, anchor="center")
        self.lista_pred.pack(fill="both", expand=True, pady=(8, 4))

        ttk.Button(marco, text="Eliminar seleccionado", command=self._eliminar_predicado).pack(anchor="w")
        return marco

    # -- bloque de funciones -------------------------------------------------
    def _construir_bloque_funciones(self, master) -> ttk.LabelFrame:
        marco = ttk.LabelFrame(master, text="Funciones (aridad 0 = constante)", padding=10)

        formulario = ttk.Frame(marco)
        formulario.pack(fill="x")
        ttk.Label(formulario, text="Nombre:").grid(row=0, column=0, sticky="w")
        self.fun_nombre = ttk.Entry(formulario, width=14)
        self.fun_nombre.grid(row=0, column=1, padx=4)
        ttk.Label(formulario, text="Aridad:").grid(row=0, column=2, sticky="w")
        self.fun_aridad = ttk.Spinbox(formulario, from_=0, to=5, width=5)
        self.fun_aridad.set(1)
        self.fun_aridad.grid(row=0, column=3, padx=4)
        ttk.Button(formulario, text="Agregar", command=self._agregar_funcion).grid(row=0, column=4, padx=4)

        self.lista_fun = ttk.Treeview(marco, columns=("nombre", "aridad"), show="headings", height=8)
        self.lista_fun.heading("nombre", text="Nombre")
        self.lista_fun.heading("aridad", text="Aridad")
        self.lista_fun.column("nombre", width=140)
        self.lista_fun.column("aridad", width=60, anchor="center")
        self.lista_fun.pack(fill="both", expand=True, pady=(8, 4))

        ttk.Button(marco, text="Eliminar seleccionado", command=self._eliminar_funcion).pack(anchor="w")
        return marco

    # -- acciones -------------------------------------------------
    def _agregar_predicado(self) -> None:
        self.error_lbl.config(text="")
        try:
            self.app.lenguaje.agregar_predicado(self.pred_nombre.get(), int(self.pred_aridad.get()))
        except (ErrorEvaluador, ValueError) as e:
            self.error_lbl.config(text=str(e))
            return
        self.pred_nombre.delete(0, tk.END)
        self._refrescar_listas()

    def _agregar_funcion(self) -> None:
        self.error_lbl.config(text="")
        try:
            self.app.lenguaje.agregar_funcion(self.fun_nombre.get(), int(self.fun_aridad.get()))
        except (ErrorEvaluador, ValueError) as e:
            self.error_lbl.config(text=str(e))
            return
        self.fun_nombre.delete(0, tk.END)
        self._refrescar_listas()

    def _eliminar_predicado(self) -> None:
        seleccion = self.lista_pred.selection()
        if not seleccion:
            return
        nombre = self.lista_pred.item(seleccion[0], "values")[0]
        self.app.lenguaje.eliminar_predicado(nombre)
        self._refrescar_listas()

    def _eliminar_funcion(self) -> None:
        seleccion = self.lista_fun.selection()
        if not seleccion:
            return
        nombre = self.lista_fun.item(seleccion[0], "values")[0]
        self.app.lenguaje.eliminar_funcion(nombre)
        self._refrescar_listas()

    def _refrescar_listas(self) -> None:
        self.lista_pred.delete(*self.lista_pred.get_children())
        for nombre, aridad in self.app.lenguaje.predicados.items():
            self.lista_pred.insert("", tk.END, values=(nombre, aridad))
        self.lista_fun.delete(*self.lista_fun.get_children())
        for nombre, aridad in self.app.lenguaje.funciones.items():
            self.lista_fun.insert("", tk.END, values=(nombre, aridad))

    def _confirmar(self) -> None:
        self.error_lbl.config(text="")
        try:
            self.app.lenguaje.validar_lenguaje_completo()
        except ErrorEvaluador as e:
            self.error_lbl.config(text=str(e))
            return
        self.app.al_confirmar_lenguaje()
