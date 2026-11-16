"""Árbol de explicación: justifica recursivamente el valor de verdad obtenido."""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class Explicacion:
    texto: str
    hijos: list["Explicacion"] = field(default_factory=list)
    decisivo: bool = True  # si este nodo fue determinante para el resultado del padre

    def a_texto(self, nivel: int = 0) -> str:
        sangria = "  " * nivel
        marca = "➜ " if nivel > 0 and not self.decisivo else ""
        lineas = [f"{sangria}{marca}{self.texto}"]
        for hijo in self.hijos:
            lineas.append(hijo.a_texto(nivel + 1))
        return "\n".join(lineas)
