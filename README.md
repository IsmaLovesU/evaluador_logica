# Evaluador de Lógica de Primer Orden (MM3032)

Herramienta para declarar un lenguaje de primer orden, construir una interpretación
(dominio, predicados y funciones) y evaluar fórmulas sobre esa interpretación, con
explicación paso a paso del resultado (testigos para `∃`, contraejemplos para `∀`).

Incluye además un "Escape Room Lógico": un juego que usa el mismo motor para plantear
acertijos de lógica resueltos contra el reloj.

## Requisitos

- Python 3.11+ (usa `tkinter`, incluido en la instalación estándar de Python en Windows).
- No se requieren dependencias externas (no hay `requirements.txt`).

## Estructura

- `logic/`: motor del evaluador (lexer, parser, semántica, interpretación, explicación). No depende de la interfaz gráfica.
- `gui/`: interfaz del evaluador, organizada en 4 pestañas: Lenguaje → Interpretación → Fórmula y entorno → Resultado.
- `juego/`: interfaz del Escape Room Lógico, construida sobre `logic/`.
- `tests/`: pruebas unitarias del motor y pruebas de humo de ambas interfaces.

## Cómo ejecutar

Evaluador semántico (GUI principal):

```
python main.py
```

Escape Room Lógico:

```
python juego_escape.py
```

## Cómo probar

Ejecutar toda la batería de pruebas:

```
python -m unittest discover -s tests
```

- `tests/test_logic.py`: valida el lenguaje, el parser y la semántica (conjunción, disyunción, implicación, bicondicional, cuantificadores `∀`/`∃`, errores esperados).
- `tests/test_gui_smoke.py` y `tests/test_juego_smoke.py`: pruebas de humo que abren las ventanas de Tkinter para confirmar que arrancan sin errores.
