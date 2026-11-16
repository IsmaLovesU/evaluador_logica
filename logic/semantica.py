"""Evaluación semántica de fórmulas de primer orden sobre una interpretación
finita, con generación de una explicación recursiva de las razones decisivas.

Reglas de justificación (requerimiento 6):
  - ∃x φ verdadero  -> se reporta un testigo (el primer elemento que satisface φ).
  - ∀x φ falso      -> se reporta un contraejemplo (el primer elemento que lo refuta).
  - ∀x φ verdadero  -> comprobación completa: se muestra el caso de cada elemento.
  - ∃x φ falso      -> comprobación completa: se muestra el caso de cada elemento.
"""

from __future__ import annotations

from .errores import ErrorEntorno
from .explicacion import Explicacion
from .interpretacion import Interpretacion
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
from .variables import variables_libres

Entorno = dict[str, str]


# ------------------------------------------------------------------ términos --
def evaluar_termino(termino: Termino, interp: Interpretacion, entorno: Entorno) -> str:
    if isinstance(termino, VarTerm):
        if termino.nombre not in entorno:
            raise ErrorEntorno(f"La variable '{termino.nombre}' no tiene un valor asignado en el entorno.")
        return entorno[termino.nombre]
    if isinstance(termino, ConstTerm):
        return interp.evaluar_funcion(termino.nombre, ())
    if isinstance(termino, FuncTerm):
        valores = tuple(evaluar_termino(a, interp, entorno) for a in termino.args)
        return interp.evaluar_funcion(termino.nombre, valores)
    raise TypeError(f"Tipo de término desconocido: {termino!r}")


def _texto_termino(termino: Termino, interp: Interpretacion, entorno: Entorno) -> str:
    if isinstance(termino, VarTerm):
        return f"{termino.nombre}={entorno.get(termino.nombre, '?')}"
    if isinstance(termino, ConstTerm):
        return f"{termino.nombre}={evaluar_termino(termino, interp, entorno)}"
    if isinstance(termino, FuncTerm):
        args_txt = ", ".join(_texto_termino(a, interp, entorno) for a in termino.args)
        valor = evaluar_termino(termino, interp, entorno)
        return f"{termino.nombre}({args_txt})={valor}"
    raise TypeError(f"Tipo de término desconocido: {termino!r}")


# ------------------------------------------------------------------ fórmulas --
def _evaluar(formula: Formula, interp: Interpretacion, entorno: Entorno) -> tuple[bool, Explicacion]:
    if isinstance(formula, PredAtom):
        return _evaluar_pred(formula, interp, entorno)
    if isinstance(formula, Neg):
        return _evaluar_neg(formula, interp, entorno)
    if isinstance(formula, And):
        return _evaluar_and(formula, interp, entorno)
    if isinstance(formula, Or):
        return _evaluar_or(formula, interp, entorno)
    if isinstance(formula, Implica):
        return _evaluar_implica(formula, interp, entorno)
    if isinstance(formula, Syss):
        return _evaluar_syss(formula, interp, entorno)
    if isinstance(formula, ParaTodo):
        return _evaluar_para_todo(formula, interp, entorno)
    if isinstance(formula, Existe):
        return _evaluar_existe(formula, interp, entorno)
    raise TypeError(f"Tipo de fórmula desconocido: {formula!r}")


def _evaluar_pred(formula: PredAtom, interp: Interpretacion, entorno: Entorno) -> tuple[bool, Explicacion]:
    valores = tuple(evaluar_termino(a, interp, entorno) for a in formula.args)
    pertenece = interp.pertenece_predicado(formula.nombre, valores)
    if formula.args:
        args_txt = ", ".join(_texto_termino(a, interp, entorno) for a in formula.args)
        cabecera = f"{formula.nombre}({args_txt})"
    else:
        cabecera = formula.nombre
    tupla_txt = "(" + ", ".join(valores) + ")" if valores else "()"
    estado = "VERDADERO" if pertenece else "FALSO"
    pertenece_txt = "pertenece" if pertenece else "no pertenece"
    texto = f"{cabecera} es {estado}: la tupla {tupla_txt} {pertenece_txt} a la relación {formula.nombre}."
    return pertenece, Explicacion(texto)


def _evaluar_neg(formula: Neg, interp: Interpretacion, entorno: Entorno) -> tuple[bool, Explicacion]:
    v, e = _evaluar(formula.sub, interp, entorno)
    resultado = not v
    estado = "VERDADERO" if resultado else "FALSO"
    sub_estado = "falsa" if not v else "verdadera"
    texto = f"¬φ es {estado} porque φ es {sub_estado}."
    return resultado, Explicacion(texto, [e])


def _evaluar_and(formula: And, interp: Interpretacion, entorno: Entorno) -> tuple[bool, Explicacion]:
    vi, ei = _evaluar(formula.izq, interp, entorno)
    vd, ed = _evaluar(formula.der, interp, entorno)
    resultado = vi and vd
    ei.decisivo = True if resultado else (not vi)
    ed.decisivo = True if resultado else (not vd)
    motivo = "ambos operandos son verdaderos" if resultado else "al menos un operando es falso"
    estado = "VERDADERO" if resultado else "FALSO"
    texto = f"φ ∧ ψ es {estado} porque {motivo}."
    return resultado, Explicacion(texto, [ei, ed])


def _evaluar_or(formula: Or, interp: Interpretacion, entorno: Entorno) -> tuple[bool, Explicacion]:
    vi, ei = _evaluar(formula.izq, interp, entorno)
    vd, ed = _evaluar(formula.der, interp, entorno)
    resultado = vi or vd
    ei.decisivo = (not resultado) or vi
    ed.decisivo = (not resultado) or vd
    motivo = "al menos un operando es verdadero" if resultado else "ambos operandos son falsos"
    estado = "VERDADERO" if resultado else "FALSO"
    texto = f"φ ∨ ψ es {estado} porque {motivo}."
    return resultado, Explicacion(texto, [ei, ed])


def _evaluar_implica(formula: Implica, interp: Interpretacion, entorno: Entorno) -> tuple[bool, Explicacion]:
    va, ea = _evaluar(formula.ant, interp, entorno)
    if not va:
        texto = (
            "φ → ψ es VERDADERO porque el antecedente es falso "
            "(verdad vacía); no es necesario evaluar el consecuente."
        )
        return True, Explicacion(texto, [ea])
    vc, ec = _evaluar(formula.cons, interp, entorno)
    resultado = vc
    estado = "VERDADERO" if resultado else "FALSO"
    cons_estado = "verdadero" if vc else "falso"
    texto = f"φ → ψ es {estado} porque el antecedente es verdadero y el consecuente es {cons_estado}."
    return resultado, Explicacion(texto, [ea, ec])


def _evaluar_syss(formula: Syss, interp: Interpretacion, entorno: Entorno) -> tuple[bool, Explicacion]:
    vi, ei = _evaluar(formula.izq, interp, entorno)
    vd, ed = _evaluar(formula.der, interp, entorno)
    resultado = vi == vd
    estado = "VERDADERO" if resultado else "FALSO"
    motivo = "ambos lados tienen el mismo valor de verdad" if resultado else "los dos lados difieren en su valor de verdad"
    texto = f"φ ↔ ψ es {estado} porque {motivo}."
    return resultado, Explicacion(texto, [ei, ed])


def _evaluar_para_todo(formula: ParaTodo, interp: Interpretacion, entorno: Entorno) -> tuple[bool, Explicacion]:
    var = formula.var
    casos: list[Explicacion] = []
    for d in interp.dominio:
        entorno2 = dict(entorno)
        entorno2[var] = d
        v, e = _evaluar(formula.sub, interp, entorno2)
        if not v:
            texto = f"∀{var} φ es FALSO: se encontró un contraejemplo con {var} = {d}."
            caso = Explicacion(f"Contraejemplo: {var} = {d}", [e])
            return False, Explicacion(texto, [caso])
        casos.append(Explicacion(f"Caso {var} = {d}: se cumple.", [e]))
    texto = (
        f"∀{var} φ es VERDADERO: comprobación completa sobre el dominio {interp.dominio}; "
        f"φ se cumple para cada valor de {var}."
    )
    return True, Explicacion(texto, casos)


def _evaluar_existe(formula: Existe, interp: Interpretacion, entorno: Entorno) -> tuple[bool, Explicacion]:
    var = formula.var
    casos: list[Explicacion] = []
    for d in interp.dominio:
        entorno2 = dict(entorno)
        entorno2[var] = d
        v, e = _evaluar(formula.sub, interp, entorno2)
        if v:
            texto = f"∃{var} φ es VERDADERO: testigo {var} = {d}."
            caso = Explicacion(f"Testigo: {var} = {d}", [e])
            return True, Explicacion(texto, [caso])
        casos.append(Explicacion(f"Caso {var} = {d}: no se cumple.", [e]))
    texto = (
        f"∃{var} φ es FALSO: comprobación completa sobre el dominio {interp.dominio}; "
        f"ningún valor de {var} satisface φ."
    )
    return False, Explicacion(texto, casos)


# ------------------------------------------------------------------ entrada pública --
def evaluar_formula(formula: Formula, interp: Interpretacion, entorno: Entorno) -> tuple[bool, Explicacion]:
    """Valida el entorno frente a las variables libres y el dominio, y evalúa."""
    libres = variables_libres(formula)
    faltantes = libres - entorno.keys()
    if faltantes:
        raise ErrorEntorno(
            f"Faltan valores en el entorno para las variables libres: {sorted(faltantes)}."
        )
    for var, val in entorno.items():
        if var in libres and val not in interp.dominio:
            raise ErrorEntorno(
                f"El valor '{val}' asignado a la variable '{var}' no pertenece al dominio {interp.dominio}."
            )
    return _evaluar(formula, interp, entorno)
