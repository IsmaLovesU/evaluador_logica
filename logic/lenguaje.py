"""Declaración del lenguaje: símbolos de predicado y de función con su aridad.

Convención de resolución de símbolos dentro de una fórmula:
  - Un identificador declarado como función de aridad 0 es una CONSTANTE.
  - Un identificador declarado como función de aridad n>0 debe aparecer
    como f(t1,...,tn); es un TÉRMINO COMPUESTO.
  - Un identificador declarado como predicado solo puede aparecer como
    fórmula atómica P(t1,...,tn) (o sin paréntesis si su aridad es 0).
  - Cualquier otro identificador que aparezca donde se espera un término
    se interpreta como VARIABLE (no requiere declaración previa).
"""

from __future__ import annotations

import re

from .errores import ErrorLenguaje

_RE_IDENTIFICADOR = re.compile(r"^[A-Za-zÁÉÍÓÚÑÜáéíóúñü_][A-Za-zÁÉÍÓÚÑÜáéíóúñü0-9_]*$")


def validar_nombre(nombre: str, categoria: str) -> None:
    nombre = nombre.strip()
    if not nombre:
        raise ErrorLenguaje(f"El nombre de {categoria} no puede estar vacío.")
    if not _RE_IDENTIFICADOR.match(nombre):
        raise ErrorLenguaje(
            f"'{nombre}' no es un nombre válido para {categoria}: debe iniciar con una "
            "letra o '_' y seguir con letras, dígitos o '_' (sin espacios ni símbolos)."
        )


class Lenguaje:
    """Conjunto de símbolos funcionales y predicativos declarados por el usuario."""

    def __init__(self) -> None:
        self.predicados: dict[str, int] = {}
        self.funciones: dict[str, int] = {}

    # -- alta y baja de símbolos -------------------------------------------------
    def agregar_predicado(self, nombre: str, aridad: int) -> None:
        nombre = nombre.strip()
        validar_nombre(nombre, "un predicado")
        self._validar_aridad(aridad)
        self._validar_nombre_libre(nombre)
        self.predicados[nombre] = aridad

    def agregar_funcion(self, nombre: str, aridad: int) -> None:
        nombre = nombre.strip()
        validar_nombre(nombre, "una función")
        self._validar_aridad(aridad)
        self._validar_nombre_libre(nombre)
        self.funciones[nombre] = aridad

    def eliminar_predicado(self, nombre: str) -> None:
        self.predicados.pop(nombre, None)

    def eliminar_funcion(self, nombre: str) -> None:
        self.funciones.pop(nombre, None)

    # -- consultas ----------------------------------------------------------------
    def es_predicado(self, nombre: str) -> bool:
        return nombre in self.predicados

    def es_funcion(self, nombre: str) -> bool:
        return nombre in self.funciones

    def es_constante(self, nombre: str) -> bool:
        return self.funciones.get(nombre) == 0

    def validar_lenguaje_completo(self) -> None:
        """El lenguaje debe tener contenido: sin al menos un predicado no
        existe ninguna fórmula atómica posible."""
        if not self.predicados:
            raise ErrorLenguaje(
                "El lenguaje debe declarar al menos un símbolo de predicado; "
                "sin predicados no se puede construir ninguna fórmula atómica."
            )

    # -- privados -------------------------------------------------------------
    @staticmethod
    def _validar_aridad(aridad: int) -> None:
        if not isinstance(aridad, int) or aridad < 0:
            raise ErrorLenguaje("La aridad debe ser un entero mayor o igual a 0.")

    def _validar_nombre_libre(self, nombre: str) -> None:
        if nombre in self.predicados or nombre in self.funciones:
            raise ErrorLenguaje(
                f"El símbolo '{nombre}' ya está declarado; los nombres de predicados "
                "y funciones deben ser distintos entre sí."
            )
