"""Identificación de variables libres de una fórmula (para pedir el entorno)."""

from __future__ import annotations

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


def variables_en_termino(termino: Termino) -> set[str]:
    if isinstance(termino, VarTerm):
        return {termino.nombre}
    if isinstance(termino, ConstTerm):
        return set()
    if isinstance(termino, FuncTerm):
        resultado: set[str] = set()
        for arg in termino.args:
            resultado |= variables_en_termino(arg)
        return resultado
    raise TypeError(f"Tipo de término desconocido: {termino!r}")


def variables_libres(formula: Formula, ligadas: frozenset[str] = frozenset()) -> set[str]:
    if isinstance(formula, PredAtom):
        libres: set[str] = set()
        for arg in formula.args:
            libres |= variables_en_termino(arg)
        return libres - ligadas
    if isinstance(formula, Neg):
        return variables_libres(formula.sub, ligadas)
    if isinstance(formula, (And, Or, Syss)):
        return variables_libres(formula.izq, ligadas) | variables_libres(formula.der, ligadas)
    if isinstance(formula, Implica):
        return variables_libres(formula.ant, ligadas) | variables_libres(formula.cons, ligadas)
    if isinstance(formula, (ParaTodo, Existe)):
        return variables_libres(formula.sub, ligadas | {formula.var})
    raise TypeError(f"Tipo de fórmula desconocido: {formula!r}")
