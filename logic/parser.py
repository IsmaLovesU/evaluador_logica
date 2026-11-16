"""Analizador sintáctico descendente recursivo.

Gramática (de menor a mayor precedencia; ¬, ∀, ∃ ligan más fuerte):

    formula   ::= syss
    syss      ::= implica ( '↔' implica )*
    implica   ::= disy ( '→' implica )?            # asociativo a la derecha
    disy      ::= conj ( '∨' conj )*
    conj      ::= unaria ( '∧' unaria )*
    unaria    ::= '¬' unaria | '∀' ID unaria | '∃' ID unaria | primaria
    primaria  ::= '(' formula ')' | atomo
    atomo     ::= ID | ID '(' termino (',' termino)* ')'
    termino   ::= ID | ID '(' termino (',' termino)* ')'

El símbolo cabeza de un átomo debe estar declarado como predicado; el
símbolo cabeza de un término compuesto debe estar declarado como función.
Cualquier ID "suelto" que no sea función de aridad 0 ni predicado se
interpreta como variable.
"""

from __future__ import annotations

from .errores import ErrorAridad, ErrorSimbolo, ErrorSintactico
from .lenguaje import Lenguaje
from .lexer import Token, tokenizar
from .nodos import (
    And,
    ConstTerm,
    Existe,
    Formula,
    FuncTerm,
    Implica,
    Neg,
    Or,
    ParaTodo,
    PredAtom,
    Syss,
    Termino,
    VarTerm,
)


class _Parser:
    def __init__(self, tokens: list[Token], lenguaje: Lenguaje):
        self.tokens = tokens
        self.lenguaje = lenguaje
        self.pos = 0

    # -- utilidades de recorrido -------------------------------------------------
    @property
    def actual(self) -> Token:
        return self.tokens[self.pos]

    def avanzar(self) -> Token:
        tok = self.tokens[self.pos]
        if tok.tipo != "EOF":
            self.pos += 1
        return tok

    def esperar(self, tipo: str, descripcion: str) -> Token:
        if self.actual.tipo != tipo:
            raise ErrorSintactico(
                f"Se esperaba {descripcion}, pero se encontró "
                f"{self._describir(self.actual)}.",
                self.actual.posicion,
            )
        return self.avanzar()

    @staticmethod
    def _describir(tok: Token) -> str:
        if tok.tipo == "EOF":
            return "el final de la fórmula"
        return f"'{tok.valor}'"

    # -- producción principal -------------------------------------------------
    def parsear_formula_completa(self) -> Formula:
        formula = self.parse_syss()
        if self.actual.tipo != "EOF":
            raise ErrorSintactico(
                f"Entrada inesperada {self._describir(self.actual)} después de una fórmula completa.",
                self.actual.posicion,
            )
        return formula

    def parse_syss(self) -> Formula:
        izq = self.parse_implica()
        while self.actual.tipo == "SYSS":
            self.avanzar()
            der = self.parse_implica()
            izq = Syss(izq, der)
        return izq

    def parse_implica(self) -> Formula:
        izq = self.parse_disy()
        if self.actual.tipo == "IMPLICA":
            self.avanzar()
            der = self.parse_implica()  # asociativo a la derecha
            return Implica(izq, der)
        return izq

    def parse_disy(self) -> Formula:
        izq = self.parse_conj()
        while self.actual.tipo == "OR":
            self.avanzar()
            der = self.parse_conj()
            izq = Or(izq, der)
        return izq

    def parse_conj(self) -> Formula:
        izq = self.parse_unaria()
        while self.actual.tipo == "AND":
            self.avanzar()
            der = self.parse_unaria()
            izq = And(izq, der)
        return izq

    def parse_unaria(self) -> Formula:
        if self.actual.tipo == "NOT":
            self.avanzar()
            return Neg(self.parse_unaria())
        if self.actual.tipo == "PARA_TODO":
            self.avanzar()
            var = self._leer_variable_cuantificada("∀")
            return ParaTodo(var, self.parse_unaria())
        if self.actual.tipo == "EXISTE":
            self.avanzar()
            var = self._leer_variable_cuantificada("∃")
            return Existe(var, self.parse_unaria())
        return self.parse_primaria()

    def _leer_variable_cuantificada(self, simbolo: str) -> str:
        if self.actual.tipo != "ID":
            raise ErrorSintactico(
                f"Se esperaba una variable después de '{simbolo}', pero se encontró "
                f"{self._describir(self.actual)}.",
                self.actual.posicion,
            )
        nombre = self.avanzar().valor
        if self.lenguaje.es_predicado(nombre) or self.lenguaje.es_funcion(nombre):
            raise ErrorSimbolo(
                f"'{nombre}' ya está declarado como símbolo del lenguaje y no puede "
                "usarse como variable cuantificada."
            )
        return nombre

    def parse_primaria(self) -> Formula:
        if self.actual.tipo == "LPAREN":
            self.avanzar()
            formula = self.parse_syss()
            self.esperar("RPAREN", "')' que cierre el paréntesis")
            return formula
        return self.parse_atomo()

    def parse_atomo(self) -> Formula:
        if self.actual.tipo != "ID":
            raise ErrorSintactico(
                f"Se esperaba una fórmula atómica, un '¬', un cuantificador o '(', "
                f"pero se encontró {self._describir(self.actual)}.",
                self.actual.posicion,
            )
        tok = self.avanzar()
        nombre = tok.valor

        if self.lenguaje.es_funcion(nombre):
            raise ErrorSimbolo(
                f"'{nombre}' está declarado como símbolo funcional, no como predicado; "
                "no puede usarse como fórmula atómica."
            )
        if not self.lenguaje.es_predicado(nombre):
            raise ErrorSimbolo(
                f"'{nombre}' no está declarado como predicado del lenguaje."
            )

        aridad = self.lenguaje.predicados[nombre]
        args = self._parsear_argumentos_opcionales(nombre, tok.posicion)
        if len(args) != aridad:
            raise ErrorAridad(
                f"El predicado '{nombre}' tiene aridad {aridad}, pero se le dieron "
                f"{len(args)} argumento(s)."
            )
        return PredAtom(nombre, tuple(args))

    def parse_termino(self) -> Termino:
        if self.actual.tipo != "ID":
            raise ErrorSintactico(
                f"Se esperaba un término (variable, constante o función), pero se "
                f"encontró {self._describir(self.actual)}.",
                self.actual.posicion,
            )
        tok = self.avanzar()
        nombre = tok.valor

        if self.lenguaje.es_predicado(nombre):
            raise ErrorSimbolo(
                f"'{nombre}' está declarado como predicado, no puede usarse como término."
            )

        if self.lenguaje.es_funcion(nombre):
            aridad = self.lenguaje.funciones[nombre]
            args = self._parsear_argumentos_opcionales(nombre, tok.posicion)
            if len(args) != aridad:
                raise ErrorAridad(
                    f"La función '{nombre}' tiene aridad {aridad}, pero se le dieron "
                    f"{len(args)} argumento(s)."
                )
            if aridad == 0:
                return ConstTerm(nombre)
            return FuncTerm(nombre, tuple(args))

        # No declarado como función ni predicado: es una variable.
        if self.actual.tipo == "LPAREN":
            raise ErrorSimbolo(
                f"'{nombre}' no está declarado como símbolo funcional, no puede aplicarse "
                "a argumentos entre paréntesis."
            )
        return VarTerm(nombre)

    def _parsear_argumentos_opcionales(self, nombre: str, posicion: int) -> list[Termino]:
        """Lee '(' t1, ..., tn ')' si está presente; si no hay '(', se asume aridad 0."""
        if self.actual.tipo != "LPAREN":
            return []
        self.avanzar()
        args: list[Termino] = []
        if self.actual.tipo != "RPAREN":
            args.append(self.parse_termino())
            while self.actual.tipo == "COMA":
                self.avanzar()
                args.append(self.parse_termino())
        self.esperar("RPAREN", f"')' que cierre los argumentos de '{nombre}'")
        return args


def parsear(texto: str, lenguaje: Lenguaje) -> Formula:
    """Convierte el texto de una fórmula en su AST, validando contra el lenguaje."""
    if not texto or not texto.strip():
        raise ErrorSintactico("La fórmula está vacía.")
    tokens = tokenizar(texto)
    parser = _Parser(tokens, lenguaje)
    return parser.parsear_formula_completa()
