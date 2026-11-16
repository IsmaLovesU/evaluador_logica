"""Nodos del árbol de sintaxis abstracta (AST) para términos y fórmulas."""

from __future__ import annotations

from dataclasses import dataclass, field


# ---------------------------------------------------------------- términos --
class Termino:
    """Clase base de todo término: variable, constante o aplicación funcional."""


@dataclass(frozen=True)
class VarTerm(Termino):
    nombre: str

    def __str__(self) -> str:
        return self.nombre


@dataclass(frozen=True)
class ConstTerm(Termino):
    nombre: str

    def __str__(self) -> str:
        return self.nombre


@dataclass(frozen=True)
class FuncTerm(Termino):
    nombre: str
    args: tuple[Termino, ...] = field(default_factory=tuple)

    def __str__(self) -> str:
        return f"{self.nombre}({', '.join(str(a) for a in self.args)})"


# ---------------------------------------------------------------- fórmulas --
class Formula:
    """Clase base de toda fórmula."""


@dataclass(frozen=True)
class PredAtom(Formula):
    nombre: str
    args: tuple[Termino, ...] = field(default_factory=tuple)

    def __str__(self) -> str:
        if not self.args:
            return self.nombre
        return f"{self.nombre}({', '.join(str(a) for a in self.args)})"


@dataclass(frozen=True)
class Neg(Formula):
    sub: Formula

    def __str__(self) -> str:
        return f"¬{self.sub}"


@dataclass(frozen=True)
class And(Formula):
    izq: Formula
    der: Formula

    def __str__(self) -> str:
        return f"({self.izq} ∧ {self.der})"


@dataclass(frozen=True)
class Or(Formula):
    izq: Formula
    der: Formula

    def __str__(self) -> str:
        return f"({self.izq} ∨ {self.der})"


@dataclass(frozen=True)
class Implica(Formula):
    ant: Formula
    cons: Formula

    def __str__(self) -> str:
        return f"({self.ant} → {self.cons})"


@dataclass(frozen=True)
class Syss(Formula):
    izq: Formula
    der: Formula

    def __str__(self) -> str:
        return f"({self.izq} ↔ {self.der})"


@dataclass(frozen=True)
class ParaTodo(Formula):
    var: str
    sub: Formula

    def __str__(self) -> str:
        return f"∀{self.var}{self.sub}"


@dataclass(frozen=True)
class Existe(Formula):
    var: str
    sub: Formula

    def __str__(self) -> str:
        return f"∃{self.var}{self.sub}"
