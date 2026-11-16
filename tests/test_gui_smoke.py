"""Prueba de humo de la interfaz gráfica: recorre todo el flujo (lenguaje ->
interpretación -> fórmula -> resultado) manipulando los widgets reales de
Tkinter, sin mostrar la ventana. Requiere un entorno con Tk disponible.

Ejecutar con:  python -m unittest tests.test_gui_smoke -v
"""

from __future__ import annotations

import tkinter as tk
import unittest

from gui.app import AplicacionEvaluador


class TestFlujoCompletoGUI(unittest.TestCase):
    def setUp(self) -> None:
        try:
            self.app = AplicacionEvaluador()
        except tk.TclError as e:
            self.skipTest(f"No hay display de Tk disponible: {e}")
        self.app.withdraw()
        self.app.update_idletasks()

    def tearDown(self) -> None:
        self.app.destroy()

    def test_flujo_completo_existencial_verdadero(self) -> None:
        app = self.app
        tl = app.tab_lenguaje

        tl.pred_nombre.insert(0, "P")
        tl.pred_aridad.set(1)
        tl._agregar_predicado()
        tl.pred_nombre.insert(0, "Mayor")
        tl.pred_aridad.set(2)
        tl._agregar_predicado()
        tl.fun_nombre.insert(0, "suc")
        tl.fun_aridad.set(1)
        tl._agregar_funcion()
        tl.fun_nombre.insert(0, "cero")
        tl.fun_aridad.set(0)
        tl._agregar_funcion()
        self.assertEqual(tl.error_lbl.cget("text"), "")

        tl._confirmar()
        self.assertEqual(tl.error_lbl.cget("text"), "")

        ti = app.tab_interpretacion
        ti.dominio_entry.insert(0, "0, 1, 2")
        ti._construir_tablas()
        self.assertEqual(ti.error_lbl.cget("text"), "")
        self.assertIsNotNone(app.interpretacion)

        for a in ("0", "1", "2"):
            for b in ("0", "1", "2"):
                ti._vars_predicados["Mayor"][(a, b)].set(int(a) > int(b))
        ti._vars_predicados["P"][("0",)].set(True)
        ti._vars_predicados["P"][("1",)].set(False)
        ti._vars_predicados["P"][("2",)].set(True)
        ti._vars_funciones["suc"][("0",)].set("1")
        ti._vars_funciones["suc"][("1",)].set("2")
        ti._vars_funciones["suc"][("2",)].set("0")
        ti._vars_funciones["cero"][()].set("0")

        ti._guardar()
        self.assertEqual(ti.error_lbl.cget("text"), "")

        tf = app.tab_formula
        tf.formula_entry.insert(0, "∃x P(x)")
        tf._analizar()
        self.assertEqual(tf.error_lbl.cget("text"), "")
        self.assertIsNotNone(app.formula_ast)
        self.assertEqual(tf._vars_entorno, {})  # fórmula cerrada

        tf._evaluar()
        self.assertEqual(tf.error_lbl.cget("text"), "")

        tr = app.tab_resultado
        self.assertEqual(tr.resultado_lbl.cget("text"), "VERDADERO")

    def test_formula_abierta_pide_entorno_y_detecta_contraejemplo(self) -> None:
        app = self.app
        tl = app.tab_lenguaje
        tl.pred_nombre.insert(0, "P")
        tl.pred_aridad.set(1)
        tl._agregar_predicado()
        tl._confirmar()

        ti = app.tab_interpretacion
        ti.dominio_entry.insert(0, "0,1,2")
        ti._construir_tablas()
        ti._vars_predicados["P"][("0",)].set(True)
        ti._vars_predicados["P"][("1",)].set(False)
        ti._vars_predicados["P"][("2",)].set(True)
        ti._guardar()

        tf = app.tab_formula
        tf.formula_entry.insert(0, "∀x P(x)")
        tf._analizar()
        self.assertEqual(tf._vars_entorno, {})  # x está ligada por ∀, no es libre
        tf._evaluar()

        tr = app.tab_resultado
        self.assertEqual(tr.resultado_lbl.cget("text"), "FALSO")

        # ahora una fórmula abierta: pide entorno para la variable libre
        tf.formula_entry.delete(0, tk.END)
        tf.formula_entry.insert(0, "P(x)")
        tf._analizar()
        self.assertIn("x", tf._vars_entorno)
        tf._vars_entorno["x"].set("1")
        tf._evaluar()
        self.assertEqual(tr.resultado_lbl.cget("text"), "FALSO")

    def test_error_de_sintaxis_no_produce_resultado(self) -> None:
        app = self.app
        tl = app.tab_lenguaje
        tl.pred_nombre.insert(0, "P")
        tl.pred_aridad.set(1)
        tl._agregar_predicado()
        tl._confirmar()

        ti = app.tab_interpretacion
        ti.dominio_entry.insert(0, "0,1")
        ti._construir_tablas()
        ti._vars_predicados["P"][("0",)].set(True)
        ti._guardar()

        tf = app.tab_formula
        tf.formula_entry.insert(0, "(P(x)")
        tf._analizar()
        self.assertNotEqual(tf.error_lbl.cget("text"), "")
        self.assertIsNone(app.formula_ast)
        self.assertEqual(str(tf.boton_evaluar.cget("state")), "disabled")


if __name__ == "__main__":
    unittest.main()
