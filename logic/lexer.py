"""Analizador léxico: convierte el texto de una fórmula en una lista de tokens."""

from __future__ import annotations

from dataclasses import dataclass

from .errores import ErrorLexico

# Símbolos lógicos aceptados (se insertan por botón, pero también se
# reconocen si llegan pegados/escritos directamente).
SIMBOLOS = {
    "¬": "NOT",
    "∧": "AND",
    "∨": "OR",
    "→": "IMPLICA",
    "↔": "SYSS",
    "∀": "PARA_TODO",
    "∃": "EXISTE",
    "(": "LPAREN",
    ")": "RPAREN",
    ",": "COMA",
}

@dataclass
class Token:
    tipo: str
    valor: str
    posicion: int


def _es_inicio_identificador(c: str) -> bool:
    return c.isalpha() or c == "_"


def _es_continuacion_identificador(c: str) -> bool:
    return c.isalnum() or c == "_"


def tokenizar(texto: str) -> list[Token]:
    tokens: list[Token] = []
    i = 0
    n = len(texto)
    while i < n:
        c = texto[i]

        if c.isspace():
            i += 1
            continue

        if c in SIMBOLOS:
            tokens.append(Token(SIMBOLOS[c], c, i))
            i += 1
            continue

        if _es_inicio_identificador(c):
            inicio = i
            i += 1
            while i < n and _es_continuacion_identificador(texto[i]):
                i += 1
            tokens.append(Token("ID", texto[inicio:i], inicio))
            continue

        raise ErrorLexico(f"Carácter no reconocido: '{c}'. Use los botones para los conectivos y cuantificadores.", i)

    tokens.append(Token("EOF", "", n))
    return tokens
