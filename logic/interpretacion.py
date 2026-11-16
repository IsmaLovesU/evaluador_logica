"""Interpretación: dominio finito D, f^I: D^n -> D para cada función y
P^I subconjunto de D^n para cada predicado."""

from __future__ import annotations

from itertools import product

from .errores import ErrorDominio, ErrorInterpretacion
from .lenguaje import Lenguaje


class Interpretacion:
    def __init__(self, lenguaje: Lenguaje, dominio: list[str]):
        self._validar_dominio(dominio)
        self.lenguaje = lenguaje
        self.dominio: list[str] = list(dominio)
        self.funciones: dict[str, dict[tuple[str, ...], str]] = {
            nombre: {} for nombre in lenguaje.funciones
        }
        self.predicados: dict[str, set[tuple[str, ...]]] = {
            nombre: set() for nombre in lenguaje.predicados
        }

    @staticmethod
    def _validar_dominio(dominio: list[str]) -> None:
        if not dominio:
            raise ErrorDominio("El dominio no puede estar vacío.")
        vistos = set()
        for elemento in dominio:
            elemento = elemento.strip()
            if not elemento:
                raise ErrorDominio("Un elemento del dominio no puede ser una cadena vacía.")
            if elemento in vistos:
                raise ErrorDominio(f"El elemento '{elemento}' está repetido en el dominio.")
            vistos.add(elemento)

    # -- asignación de funciones -------------------------------------------------
    def fijar_funcion(self, nombre: str, tupla: tuple[str, ...], valor: str) -> None:
        if nombre not in self.funciones:
            raise ErrorInterpretacion(f"'{nombre}' no es un símbolo funcional declarado.")
        aridad = self.lenguaje.funciones[nombre]
        if len(tupla) != aridad:
            raise ErrorInterpretacion(
                f"La función '{nombre}' tiene aridad {aridad}, pero se dio una tupla de tamaño {len(tupla)}."
            )
        for elem in tupla:
            if elem not in self.dominio:
                raise ErrorInterpretacion(
                    f"El valor '{elem}' en la tupla {tupla} no pertenece al dominio {self.dominio}."
                )
        if valor not in self.dominio:
            raise ErrorInterpretacion(
                f"El valor de retorno '{valor}' para {nombre}{tupla} no pertenece al dominio {self.dominio}."
            )
        self.funciones[nombre][tupla] = valor

    # -- asignación de predicados -------------------------------------------------
    def fijar_predicado_tupla(self, nombre: str, tupla: tuple[str, ...], pertenece: bool) -> None:
        if nombre not in self.predicados:
            raise ErrorInterpretacion(f"'{nombre}' no es un símbolo de predicado declarado.")
        aridad = self.lenguaje.predicados[nombre]
        if len(tupla) != aridad:
            raise ErrorInterpretacion(
                f"El predicado '{nombre}' tiene aridad {aridad}, pero se dio una tupla de tamaño {len(tupla)}."
            )
        for elem in tupla:
            if elem not in self.dominio:
                raise ErrorInterpretacion(
                    f"El valor '{elem}' en la tupla {tupla} no pertenece al dominio {self.dominio}."
                )
        if pertenece:
            self.predicados[nombre].add(tupla)
        else:
            self.predicados[nombre].discard(tupla)

    # -- validación de completitud -------------------------------------------------
    def validar_completa(self) -> None:
        """No se admiten funciones parciales ("vacías" en alguna entrada) ni
        relaciones vacías: cada función debe quedar definida para toda tupla
        de D^n y cada predicado debe tener al menos una tupla verdadera."""
        for nombre, aridad in self.lenguaje.funciones.items():
            tabla = self.funciones[nombre]
            for tupla in product(self.dominio, repeat=aridad):
                if tupla not in tabla:
                    raise ErrorInterpretacion(
                        f"Falta asignar un valor para la función '{nombre}' en la tupla {tupla}."
                    )
        for nombre in self.lenguaje.predicados:
            if len(self.predicados[nombre]) == 0:
                raise ErrorInterpretacion(
                    f"La relación del predicado '{nombre}' no puede quedar vacía; "
                    "debe marcar al menos una tupla como verdadera."
                )

    # -- consultas usadas por la semántica -------------------------------------------------
    def evaluar_funcion(self, nombre: str, tupla: tuple[str, ...]) -> str:
        try:
            return self.funciones[nombre][tupla]
        except KeyError:
            raise ErrorInterpretacion(
                f"La función '{nombre}' no tiene un valor asignado para la tupla {tupla}."
            )

    def pertenece_predicado(self, nombre: str, tupla: tuple[str, ...]) -> bool:
        return tupla in self.predicados[nombre]
