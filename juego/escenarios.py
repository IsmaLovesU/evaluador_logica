"""Las 4 salas precargadas del Escape Room Lógico.

Cada sala es un caso de prueba completo (lenguaje + interpretación + fórmula)
construido con el mismo motor del evaluador (logic/), pero elegido a propósito
para que la respuesta correcta no sea obvia a simple vista: cuantificadores
anidados, implicaciones con verdad vacía y funciones que "mueven" el testigo
lejos del primer elemento del dominio.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from logic.errores import ErrorEvaluador
from logic.interpretacion import Interpretacion
from logic.lenguaje import Lenguaje
from logic.nodos import Existe, Formula, ParaTodo
from logic.parser import parsear
from logic.semantica import evaluar_formula


@dataclass
class Escenario:
    numero: int
    titulo: str
    historia: str
    lenguaje: Lenguaje
    interpretacion: Interpretacion
    formula_texto: str
    glosario: dict[str, str]
    pista: str
    digito: str

    formula_ast: Formula = field(init=False)
    valor_real: bool = field(init=False)
    tipo_decisivo: str | None = field(init=False)  # "testigo" | "contraejemplo" | None
    variable_decisiva: str | None = field(init=False)
    elemento_decisivo: str | None = field(init=False)

    def __post_init__(self) -> None:
        self.formula_ast = parsear(self.formula_texto, self.lenguaje)
        self.valor_real, _ = evaluar_formula(self.formula_ast, self.interpretacion, {})
        self._calcular_elemento_decisivo()

    def _calcular_elemento_decisivo(self) -> None:
        raiz = self.formula_ast
        if isinstance(raiz, Existe) and self.valor_real:
            self.tipo_decisivo = "testigo"
            self.variable_decisiva = raiz.var
            self.elemento_decisivo = self._buscar(raiz, buscar_verdadero=True)
        elif isinstance(raiz, ParaTodo) and not self.valor_real:
            self.tipo_decisivo = "contraejemplo"
            self.variable_decisiva = raiz.var
            self.elemento_decisivo = self._buscar(raiz, buscar_verdadero=False)
        else:
            self.tipo_decisivo = None
            self.variable_decisiva = None
            self.elemento_decisivo = None

    def _buscar(self, raiz: Existe | ParaTodo, buscar_verdadero: bool) -> str:
        for d in self.interpretacion.dominio:
            v, _ = evaluar_formula(raiz.sub, self.interpretacion, {raiz.var: d})
            if v == buscar_verdadero:
                return d
        raise RuntimeError("No se encontró elemento decisivo; revisa el diseño de la sala.")

    def explicacion_completa(self):
        _, exp = evaluar_formula(self.formula_ast, self.interpretacion, {})
        return exp


def _sala_1() -> Escenario:
    lenguaje = Lenguaje()
    lenguaje.agregar_predicado("Vigila", 2)

    dominio = ["Ana", "Beto", "Caro", "Dani", "Eli"]
    interp = Interpretacion(lenguaje, dominio)
    pares_verdaderos = [
        ("Ana", "Beto"), ("Ana", "Caro"),
        ("Beto", "Ana"), ("Beto", "Caro"), ("Beto", "Dani"),
        ("Caro", "Ana"), ("Caro", "Beto"), ("Caro", "Caro"), ("Caro", "Dani"), ("Caro", "Eli"),
        ("Dani", "Ana"), ("Dani", "Eli"),
        ("Eli", "Caro"), ("Eli", "Dani"),
    ]
    for par in pares_verdaderos:
        interp.fijar_predicado_tupla("Vigila", par, True)
    interp.validar_completa()

    return Escenario(
        numero=1,
        titulo="La Sala de los Centinelas",
        historia=(
            "Cinco centinelas custodian la primera puerta. La puerta solo se abre si "
            "EXISTE un centinela que vigila a TODOS los demás (incluido a sí mismo)."
        ),
        lenguaje=lenguaje,
        interpretacion=interp,
        formula_texto="∃x ∀y Vigila(x,y)",
        glosario={"Vigila(x, y)": "el centinela x vigila al centinela y"},
        pista="Busca la fila de la tabla que tenga TODAS sus casillas marcadas: ese centinela vigila a todos.",
        digito="7",
    )


def _sala_2() -> Escenario:
    lenguaje = Lenguaje()
    lenguaje.agregar_predicado("EsPrimo", 1)
    lenguaje.agregar_predicado("Mayor", 2)
    lenguaje.agregar_funcion("tres", 0)

    dominio = [str(n) for n in range(8)]
    interp = Interpretacion(lenguaje, dominio)
    for n in (2, 3, 5, 7):
        interp.fijar_predicado_tupla("EsPrimo", (str(n),), True)
    for a in dominio:
        for b in dominio:
            interp.fijar_predicado_tupla("Mayor", (a, b), int(a) > int(b))
    interp.fijar_funcion("tres", (), "3")
    interp.validar_completa()

    return Escenario(
        numero=2,
        titulo="La Sala de los Números",
        historia=(
            "Un panel numérico del 0 al 7 bloquea el paso. Debes decidir si para TODO "
            "número, el ser primo obliga a ser mayor que tres."
        ),
        lenguaje=lenguaje,
        interpretacion=interp,
        formula_texto="∀x (EsPrimo(x) → Mayor(x, tres))",
        glosario={
            "EsPrimo(x)": "x es un número primo",
            "Mayor(x, y)": "x es mayor que y",
            "tres": "la constante 3",
        },
        pista="Revisa cuáles números son primos y compáralos uno por uno con el 3. El primero que falle es la clave.",
        digito="3",
    )


def _sala_3() -> Escenario:
    lenguaje = Lenguaje()
    lenguaje.agregar_predicado("Antes", 2)
    lenguaje.agregar_funcion("opuesto", 1)

    colores = ["rojo", "naranja", "amarillo", "verde", "azul", "violeta"]
    interp = Interpretacion(lenguaje, colores)
    for a in colores:
        for b in colores:
            interp.fijar_predicado_tupla("Antes", (a, b), colores.index(a) < colores.index(b))
    mapa_opuesto = {
        "rojo": "rojo", "naranja": "rojo", "amarillo": "naranja",
        "verde": "azul", "azul": "naranja", "violeta": "amarillo",
    }
    for k, v in mapa_opuesto.items():
        interp.fijar_funcion("opuesto", (k,), v)
    interp.validar_completa()

    return Escenario(
        numero=3,
        titulo="La Sala del Testigo Oculto",
        historia=(
            "Un arcoíris de seis colores guarda la tercera llave. Necesitas hallar un "
            "color que aparezca ANTES que su propio 'opuesto' en el orden del arcoíris."
        ),
        lenguaje=lenguaje,
        interpretacion=interp,
        formula_texto="∃x Antes(x, opuesto(x))",
        glosario={
            "Antes(x, y)": "x aparece antes que y en el orden rojo→naranja→amarillo→verde→azul→violeta",
            "opuesto(x)": "el color opuesto asignado a x (tabla de la sala)",
        },
        pista="El testigo no es el primer color. Sigue la función opuesto color por color, en orden, hasta que Antes se cumpla.",
        digito="9",
    )


def _sala_4() -> Escenario:
    lenguaje = Lenguaje()
    lenguaje.agregar_predicado("EsPrimo", 1)
    lenguaje.agregar_predicado("Mayor", 2)
    lenguaje.agregar_funcion("cuadrado", 1)

    dominio = [str(n) for n in range(1, 7)]
    interp = Interpretacion(lenguaje, dominio)
    for n in (2, 3, 5):
        interp.fijar_predicado_tupla("EsPrimo", (str(n),), True)
    for a in dominio:
        for b in dominio:
            interp.fijar_predicado_tupla("Mayor", (a, b), int(a) > int(b))
    mapa_cuadrado = {"1": "2", "2": "4", "3": "5", "4": "6", "5": "6", "6": "1"}
    for k, v in mapa_cuadrado.items():
        interp.fijar_funcion("cuadrado", (k,), v)
    interp.validar_completa()

    return Escenario(
        numero=4,
        titulo="La Sala Final: la Máquina de Funciones",
        historia=(
            "La última puerta combina todo lo aprendido: ¿EXISTE un número del 1 al 6 "
            "que NO sea primo y que sea mayor que el valor que le asigna la máquina 'cuadrado'?"
        ),
        lenguaje=lenguaje,
        interpretacion=interp,
        formula_texto="∃x (¬EsPrimo(x) ∧ Mayor(x, cuadrado(x)))",
        glosario={
            "EsPrimo(x)": "x es un número primo",
            "Mayor(x, y)": "x es mayor que y",
            "cuadrado(x)": "el valor que la máquina asigna a x (tabla de la sala, no es x al cuadrado real)",
        },
        pista="Los números primos quedan descartados de inmediato por el '¬EsPrimo'. Revisa los no-primos uno por uno, en orden, y compara cada uno con lo que le asigna la máquina.",
        digito="2",
    )


def construir_escenarios() -> list[Escenario]:
    try:
        return [_sala_1(), _sala_2(), _sala_3(), _sala_4()]
    except ErrorEvaluador as e:  # pragma: no cover - solo si se rompe el diseño de una sala
        raise RuntimeError(f"Error al construir las salas precargadas: {e}") from e
