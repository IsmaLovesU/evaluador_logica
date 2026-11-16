"""Jerarquía de errores del evaluador semántico.

Todas las entradas inválidas (sintaxis, símbolos, aridades, dominio,
tuplas o asignaciones) deben producir una de estas excepciones en vez
de un valor de verdad, tal como exige el requerimiento de validación.
"""


class ErrorEvaluador(Exception):
    """Clase base para cualquier error controlado del evaluador."""


class ErrorLexico(ErrorEvaluador):
    """Carácter o token no reconocido al leer la fórmula."""

    def __init__(self, mensaje: str, posicion: int | None = None):
        self.posicion = posicion
        if posicion is not None:
            mensaje = f"{mensaje} (posición {posicion})"
        super().__init__(mensaje)


class ErrorSintactico(ErrorEvaluador):
    """La secuencia de tokens no corresponde a una fórmula bien formada."""

    def __init__(self, mensaje: str, posicion: int | None = None):
        self.posicion = posicion
        if posicion is not None:
            mensaje = f"{mensaje} (posición {posicion})"
        super().__init__(mensaje)


class ErrorSimbolo(ErrorEvaluador):
    """Uso de un símbolo no declarado, o uso incorrecto de su categoría
    (predicado usado como función, función usada como predicado, etc.)."""


class ErrorAridad(ErrorEvaluador):
    """Un símbolo se usó con un número de argumentos distinto al declarado."""


class ErrorDominio(ErrorEvaluador):
    """El dominio es vacío, tiene elementos repetidos o un nombre inválido."""


class ErrorInterpretacion(ErrorEvaluador):
    """La interpretación es inválida: función parcial, relación vacía,
    tupla con elementos fuera del dominio, etc."""


class ErrorEntorno(ErrorEvaluador):
    """El entorno no fija todas las variables libres, o asigna un valor
    que no pertenece al dominio."""


class ErrorLenguaje(ErrorEvaluador):
    """El lenguaje declarado es inválido (nombre repetido, aridad inválida,
    ningún predicado declarado, etc.)."""
