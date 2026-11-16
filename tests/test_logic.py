"""Pruebas del núcleo lógico: lenguaje, interpretación, parser y semántica.

Se usa unittest (librería estándar) para no depender de paquetes externos.
Ejecutar con:  python -m unittest discover -s tests -v
"""

from __future__ import annotations

import unittest

from logic.errores import (
    ErrorAridad,
    ErrorDominio,
    ErrorEntorno,
    ErrorInterpretacion,
    ErrorLenguaje,
    ErrorLexico,
    ErrorSimbolo,
    ErrorSintactico,
)
from logic.interpretacion import Interpretacion
from logic.lenguaje import Lenguaje
from logic.parser import parsear
from logic.semantica import evaluar_formula
from logic.variables import variables_libres


def construir_mundo():
    """Lenguaje e interpretación de ejemplo sobre D = {0, 1, 2}:
    - predicado P(x): verdadero para 0 y 2.
    - predicado Mayor(x, y): verdadero si x > y como enteros.
    - función suc(x): sucesor cíclico módulo 3.
    - función cero(): constante 0.
    """
    lenguaje = Lenguaje()
    lenguaje.agregar_predicado("P", 1)
    lenguaje.agregar_predicado("Mayor", 2)
    lenguaje.agregar_funcion("suc", 1)
    lenguaje.agregar_funcion("cero", 0)

    interp = Interpretacion(lenguaje, ["0", "1", "2"])
    for a in ["0", "1", "2"]:
        for b in ["0", "1", "2"]:
            interp.fijar_predicado_tupla("Mayor", (a, b), int(a) > int(b))
    interp.fijar_predicado_tupla("P", ("0",), True)
    interp.fijar_predicado_tupla("P", ("1",), False)
    interp.fijar_predicado_tupla("P", ("2",), True)

    interp.fijar_funcion("suc", ("0",), "1")
    interp.fijar_funcion("suc", ("1",), "2")
    interp.fijar_funcion("suc", ("2",), "0")
    interp.fijar_funcion("cero", (), "0")

    interp.validar_completa()
    return lenguaje, interp


class TestLenguaje(unittest.TestCase):
    def test_nombre_invalido(self):
        lenguaje = Lenguaje()
        with self.assertRaises(ErrorLenguaje):
            lenguaje.agregar_predicado("1Malo", 1)

    def test_nombre_duplicado_entre_predicado_y_funcion(self):
        lenguaje = Lenguaje()
        lenguaje.agregar_predicado("f", 1)
        with self.assertRaises(ErrorLenguaje):
            lenguaje.agregar_funcion("f", 1)

    def test_lenguaje_sin_predicados_es_invalido(self):
        lenguaje = Lenguaje()
        lenguaje.agregar_funcion("c", 0)
        with self.assertRaises(ErrorLenguaje):
            lenguaje.validar_lenguaje_completo()


class TestInterpretacion(unittest.TestCase):
    def test_dominio_vacio(self):
        lenguaje = Lenguaje()
        lenguaje.agregar_predicado("P", 1)
        with self.assertRaises(ErrorDominio):
            Interpretacion(lenguaje, [])

    def test_dominio_duplicado(self):
        lenguaje = Lenguaje()
        lenguaje.agregar_predicado("P", 1)
        with self.assertRaises(ErrorDominio):
            Interpretacion(lenguaje, ["a", "b", "a"])

    def test_funcion_parcial_es_invalida(self):
        lenguaje = Lenguaje()
        lenguaje.agregar_predicado("P", 1)
        lenguaje.agregar_funcion("f", 1)
        interp = Interpretacion(lenguaje, ["a", "b"])
        interp.fijar_predicado_tupla("P", ("a",), True)
        interp.fijar_funcion("f", ("a",), "b")  # falta f(b)
        with self.assertRaises(ErrorInterpretacion):
            interp.validar_completa()

    def test_relacion_vacia_es_invalida(self):
        lenguaje = Lenguaje()
        lenguaje.agregar_predicado("P", 1)
        interp = Interpretacion(lenguaje, ["a", "b"])
        with self.assertRaises(ErrorInterpretacion):
            interp.validar_completa()

    def test_tupla_fuera_de_dominio(self):
        lenguaje = Lenguaje()
        lenguaje.agregar_predicado("P", 1)
        interp = Interpretacion(lenguaje, ["a", "b"])
        with self.assertRaises(ErrorInterpretacion):
            interp.fijar_predicado_tupla("P", ("z",), True)


class TestParser(unittest.TestCase):
    def setUp(self):
        self.lenguaje, _ = construir_mundo()

    def test_caracter_no_reconocido(self):
        with self.assertRaises(ErrorLexico):
            parsear("P(x) & P(y)", self.lenguaje)

    def test_parentesis_sin_cerrar(self):
        with self.assertRaises(ErrorSintactico):
            parsear("(P(x)", self.lenguaje)

    def test_predicado_no_declarado(self):
        with self.assertRaises(ErrorSimbolo):
            parsear("Q(x)", self.lenguaje)

    def test_aridad_incorrecta(self):
        with self.assertRaises(ErrorAridad):
            parsear("P(x, y)", self.lenguaje)

    def test_funcion_usada_como_predicado(self):
        with self.assertRaises(ErrorSimbolo):
            parsear("suc(x)", self.lenguaje)

    def test_predicado_usado_como_termino(self):
        with self.assertRaises(ErrorSimbolo):
            parsear("Mayor(P, x)", self.lenguaje)

    def test_variable_no_puede_llamarse_como_simbolo_declarado(self):
        with self.assertRaises(ErrorSimbolo):
            parsear("∀P P(x)", self.lenguaje)

    def test_formula_bien_formada_con_cuantificadores_y_funcion(self):
        formula = parsear("∀x ∃y (Mayor(suc(x), y) ∧ P(y))", self.lenguaje)
        self.assertEqual(str(formula).count("∀"), 1)

    def test_variables_libres(self):
        formula = parsear("Mayor(x, y) ∧ ∀y P(y)", self.lenguaje)
        self.assertEqual(variables_libres(formula), {"x", "y"})


class TestSemantica(unittest.TestCase):
    def setUp(self):
        self.lenguaje, self.interp = construir_mundo()

    def _eval(self, texto: str, entorno: dict[str, str] | None = None):
        formula = parsear(texto, self.lenguaje)
        return evaluar_formula(formula, self.interp, entorno or {})

    def test_existencial_verdadero_da_testigo(self):
        valor, exp = self._eval("∃x P(x)")
        self.assertTrue(valor)
        self.assertIn("testigo", exp.a_texto().lower())

    def test_universal_falso_da_contraejemplo(self):
        valor, exp = self._eval("∀x P(x)")
        self.assertFalse(valor)
        self.assertIn("contraejemplo", exp.a_texto().lower())

    def test_universal_verdadero_hace_comprobacion_completa(self):
        valor, exp = self._eval("∀x (P(x) ∨ ¬P(x))")
        self.assertTrue(valor)
        texto = exp.a_texto().lower()
        self.assertIn("comprobación completa", texto)
        for d in self.interp.dominio:
            self.assertIn(f"x = {d}", exp.a_texto())

    def test_existencial_falso_hace_comprobacion_completa(self):
        valor, exp = self._eval("∃x (P(x) ∧ ¬P(x))")
        self.assertFalse(valor)
        self.assertIn("comprobación completa", exp.a_texto().lower())

    def test_conjuncion_y_disyuncion(self):
        valor, _ = self._eval("Mayor(suc(cero), cero) ∧ P(cero)")
        self.assertTrue(valor)  # suc(0)=1, Mayor(1,0)=True, P(0)=True
        valor, _ = self._eval("Mayor(cero, suc(cero)) ∨ P(cero)")
        self.assertTrue(valor)  # Mayor(0,1) falso, pero P(0) verdadero

    def test_implicacion_vacuamente_verdadera(self):
        # Mayor(0,2) es falso -> la implicación es verdadera sin importar el consecuente.
        valor, exp = self._eval("Mayor(cero, x) → P(x)", {"x": "1"})
        self.assertTrue(valor)
        self.assertIn("verdad vacía", exp.a_texto())

    def test_bicondicional(self):
        valor, _ = self._eval("P(cero) ↔ Mayor(suc(cero), cero)")
        self.assertTrue(valor)  # P(0)=True, Mayor(1,0)=True -> coinciden

    def test_variable_libre_sin_entorno_falla(self):
        formula = parsear("P(x)", self.lenguaje)
        with self.assertRaises(ErrorEntorno):
            evaluar_formula(formula, self.interp, {})

    def test_valor_de_entorno_fuera_de_dominio_falla(self):
        formula = parsear("P(x)", self.lenguaje)
        with self.assertRaises(ErrorEntorno):
            evaluar_formula(formula, self.interp, {"x": "9"})

    def test_formula_cerrada_no_requiere_entorno(self):
        valor, _ = self._eval("∀x ∃y Mayor(y, x) ∨ P(cero)")
        self.assertTrue(valor)


if __name__ == "__main__":
    unittest.main()
