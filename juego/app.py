"""Escape Room Lógico: interfaz de juego independiente del evaluador.

Usa el mismo motor (logic/) para calcular la verdad y la explicación, pero
corre en su propia ventana, separada de gui/app.py.
"""

from __future__ import annotations

import random
import tkinter as tk
from .escenarios import Escenario, construir_escenarios

TIEMPO_TOTAL_SEGUNDOS = 360  # 6 minutos para las 4 salas
PENALIZACION_INTENTO_FALLIDO = 10
PENALIZACION_PISTA = 30

COLOR_FONDO = "#10121a"
COLOR_PANEL = "#1b1e2b"
COLOR_TEXTO = "#eef0f7"
COLOR_ACENTO = "#f2c744"
COLOR_OK = "#36d17a"
COLOR_MAL = "#ef4b5f"


class VentanaEscapeRoom(tk.Tk):
    def __init__(self) -> None:
        super().__init__()
        self.title("Escape Room Lógico — MM3032")
        self.geometry("1100x760")
        self.minsize(900, 640)
        self.configure(bg=COLOR_FONDO)

        self.escenarios: list[Escenario] = construir_escenarios()
        self.indice_sala = 0
        self.digitos_obtenidos: list[str] = []
        self.pistas_usadas = 0
        self.tiempo_restante = TIEMPO_TOTAL_SEGUNDOS
        self.atrapado = False
        self._despues_id: str | None = None

        self.contenedor = tk.Frame(self, bg=COLOR_FONDO)
        self.contenedor.pack(fill="both", expand=True)

        self._mostrar_pantalla_inicio()

    # ------------------------------------------------------------------ utilidades --
    def _limpiar_contenedor(self) -> None:
        for widget in self.contenedor.winfo_children():
            widget.destroy()

    def _iniciar_reloj(self) -> None:
        self._tick()

    def _tick(self) -> None:
        minutos, segundos = divmod(max(self.tiempo_restante, 0), 60)
        color = COLOR_MAL if self.tiempo_restante <= 30 else COLOR_ACENTO
        if hasattr(self, "reloj_lbl") and self.reloj_lbl.winfo_exists():
            self.reloj_lbl.config(text=f"⏱ {minutos:02d}:{segundos:02d}", fg=color)

        if self.tiempo_restante <= 0:
            self._despues_id = None
            self._mostrar_pantalla_atrapado()
            return

        self.tiempo_restante -= 1
        self._despues_id = self.after(1000, self._tick)

    # ------------------------------------------------------------------ pantalla inicio --
    def _mostrar_pantalla_inicio(self) -> None:
        self._limpiar_contenedor()
        marco = tk.Frame(self.contenedor, bg=COLOR_FONDO)
        marco.pack(expand=True)

        tk.Label(
            marco, text="🔒 ESCAPE ROOM LÓGICO", font=("Segoe UI", 32, "bold"),
            fg=COLOR_ACENTO, bg=COLOR_FONDO,
        ).pack(pady=(40, 10))
        tk.Label(
            marco,
            text=(
                "Cuatro salas. Cuatro fórmulas de lógica de primer orden.\n"
                "Cada sala te muestra un mundo (dominio + relaciones + funciones) y una fórmula.\n"
                "Decide si es VERDADERA o FALSA y, cuando se te pida, señala el elemento decisivo\n"
                "(el testigo que la hace verdadera, o el contraejemplo que la hace falsa).\n"
                "Cada sala resuelta libera un dígito del código final."
            ),
            font=("Segoe UI", 12), fg=COLOR_TEXTO, bg=COLOR_FONDO, justify="center",
        ).pack(pady=(0, 30))
        tk.Label(
            marco, text=f"Tienen {TIEMPO_TOTAL_SEGUNDOS // 60} minutos. ¡Que empiece el reto!",
            font=("Segoe UI", 11, "italic"), fg="#9aa0b4", bg=COLOR_FONDO,
        ).pack(pady=(0, 30))

        tk.Button(
            marco, text="COMENZAR", font=("Segoe UI", 14, "bold"), bg=COLOR_ACENTO, fg="#10121a",
            activebackground="#ffd966", relief="flat", padx=30, pady=10, command=self._comenzar_juego,
        ).pack()

    def _comenzar_juego(self) -> None:
        self.indice_sala = 0
        self.digitos_obtenidos = []
        self.pistas_usadas = 0
        self.tiempo_restante = TIEMPO_TOTAL_SEGUNDOS
        self.atrapado = False
        self._mostrar_sala()
        self._iniciar_reloj()

    # ------------------------------------------------------------------ pantalla de sala --
    def _mostrar_sala(self) -> None:
        self._limpiar_contenedor()
        escenario = self.escenarios[self.indice_sala]

        barra_superior = tk.Frame(self.contenedor, bg=COLOR_PANEL, height=50)
        barra_superior.pack(fill="x")
        tk.Label(
            barra_superior, text=f"Sala {escenario.numero}/4 — {escenario.titulo}",
            font=("Segoe UI", 14, "bold"), fg=COLOR_TEXTO, bg=COLOR_PANEL,
        ).pack(side="left", padx=16, pady=10)
        self.reloj_lbl = tk.Label(
            barra_superior, text="⏱ --:--", font=("Consolas", 14, "bold"), fg=COLOR_ACENTO, bg=COLOR_PANEL,
        )
        self.reloj_lbl.pack(side="right", padx=16)
        tk.Label(
            barra_superior, text="Código: " + " ".join(self.digitos_obtenidos + ["_"] * (4 - len(self.digitos_obtenidos))),
            font=("Consolas", 14, "bold"), fg=COLOR_OK, bg=COLOR_PANEL,
        ).pack(side="right", padx=16)

        cuerpo = tk.Frame(self.contenedor, bg=COLOR_FONDO)
        cuerpo.pack(fill="both", expand=True, padx=20, pady=14)

        tk.Label(
            cuerpo, text=escenario.historia, font=("Segoe UI", 11, "italic"),
            fg="#c7cbe0", bg=COLOR_FONDO, wraplength=1020, justify="left",
        ).pack(anchor="w", pady=(0, 10))

        panel_mundo = tk.Frame(cuerpo, bg=COLOR_PANEL)
        panel_mundo.pack(fill="both", expand=True, side="left", padx=(0, 10))
        self._dibujar_mundo(panel_mundo, escenario)

        panel_juego = tk.Frame(cuerpo, bg=COLOR_PANEL, width=360)
        panel_juego.pack(fill="y", side="left")
        panel_juego.pack_propagate(False)
        self._dibujar_panel_respuesta(panel_juego, escenario)

    # -- dibujo del "mundo" (dominio, relaciones, funciones) -------------------------------------------------
    def _dibujar_mundo(self, master: tk.Frame, escenario: Escenario) -> None:
        tk.Label(
            master, text=f"Dominio D = {{ {', '.join(escenario.interpretacion.dominio)} }}",
            font=("Consolas", 12, "bold"), fg=COLOR_ACENTO, bg=COLOR_PANEL,
        ).pack(anchor="w", padx=14, pady=(12, 6))

        tk.Label(
            master, text=f"Fórmula a resolver:\n{escenario.formula_texto}",
            font=("Consolas", 18, "bold"), fg=COLOR_TEXTO, bg=COLOR_PANEL, justify="left",
        ).pack(anchor="w", padx=14, pady=(0, 10))

        tk.Label(
            master, text="Glosario: " + "   |   ".join(f"{s}: {d}" for s, d in escenario.glosario.items()),
            font=("Segoe UI", 9), fg="#9aa0b4", bg=COLOR_PANEL, wraplength=680, justify="left",
        ).pack(anchor="w", padx=14, pady=(0, 14))

        lienzo = tk.Frame(master, bg=COLOR_PANEL)
        lienzo.pack(fill="both", expand=True, padx=14)

        for nombre, aridad in escenario.lenguaje.predicados.items():
            self._dibujar_predicado(lienzo, escenario, nombre, aridad)
        for nombre, aridad in escenario.lenguaje.funciones.items():
            self._dibujar_funcion(lienzo, escenario, nombre, aridad)

    def _dibujar_predicado(self, master: tk.Frame, escenario: Escenario, nombre: str, aridad: int) -> None:
        marco = tk.LabelFrame(
            master, text=nombre, font=("Segoe UI", 10, "bold"),
            fg=COLOR_TEXTO, bg=COLOR_PANEL, labelanchor="nw", bd=1, relief="groove",
        )
        marco.pack(fill="x", pady=6)
        dominio = escenario.interpretacion.dominio

        if aridad == 1:
            fila = tk.Frame(marco, bg=COLOR_PANEL)
            fila.pack(fill="x", padx=8, pady=6)
            for d in dominio:
                cumple = (d,) in escenario.interpretacion.predicados[nombre]
                tk.Label(
                    fila, text=d, font=("Segoe UI", 10, "bold"),
                    fg="#10121a" if cumple else COLOR_TEXTO,
                    bg=COLOR_OK if cumple else "#2a2e42",
                    padx=8, pady=3,
                ).pack(side="left", padx=3)
        elif aridad == 2:
            tabla = tk.Frame(marco, bg=COLOR_PANEL)
            tabla.pack(padx=8, pady=6)
            tk.Label(tabla, text="", bg=COLOR_PANEL).grid(row=0, column=0)
            for j, b in enumerate(dominio):
                tk.Label(tabla, text=b, font=("Segoe UI", 9, "bold"), fg=COLOR_ACENTO, bg=COLOR_PANEL).grid(
                    row=0, column=j + 1, padx=2
                )
            for i, a in enumerate(dominio):
                tk.Label(tabla, text=a, font=("Segoe UI", 9, "bold"), fg=COLOR_ACENTO, bg=COLOR_PANEL).grid(
                    row=i + 1, column=0, padx=2, sticky="e"
                )
                for j, b in enumerate(dominio):
                    cumple = (a, b) in escenario.interpretacion.predicados[nombre]
                    tk.Label(
                        tabla, text="✓" if cumple else "·", width=2,
                        fg="#10121a" if cumple else "#555a72",
                        bg=COLOR_OK if cumple else "#242842",
                    ).grid(row=i + 1, column=j + 1, padx=2, pady=2)

    def _dibujar_funcion(self, master: tk.Frame, escenario: Escenario, nombre: str, aridad: int) -> None:
        marco = tk.LabelFrame(
            master, text=f"{nombre} (función)", font=("Segoe UI", 10, "bold"),
            fg=COLOR_TEXTO, bg=COLOR_PANEL, labelanchor="nw", bd=1, relief="groove",
        )
        marco.pack(fill="x", pady=6)
        fila = tk.Frame(marco, bg=COLOR_PANEL)
        fila.pack(fill="x", padx=8, pady=6)
        tabla = escenario.interpretacion.funciones[nombre]
        if aridad == 0:
            tk.Label(
                fila, text=f"{nombre} = {tabla[()]}", font=("Consolas", 10),
                fg=COLOR_TEXTO, bg=COLOR_PANEL,
            ).pack(side="left")
        else:
            for tupla in escenario.interpretacion.dominio:
                valor = tabla[(tupla,)]
                tk.Label(
                    fila, text=f"{tupla}→{valor}", font=("Consolas", 10),
                    fg=COLOR_TEXTO, bg="#242842", padx=6, pady=2,
                ).pack(side="left", padx=3)

    # -- panel de respuesta -------------------------------------------------
    def _dibujar_panel_respuesta(self, master: tk.Frame, escenario: Escenario) -> None:
        self.panel_juego = master
        self._respuesta_valor: bool | None = None
        self._respuesta_elemento: str | None = None

        tk.Label(
            master, text="¿La fórmula es...?", font=("Segoe UI", 12, "bold"),
            fg=COLOR_TEXTO, bg=COLOR_PANEL,
        ).pack(anchor="w", padx=14, pady=(16, 8))

        fila_vf = tk.Frame(master, bg=COLOR_PANEL)
        fila_vf.pack(padx=14, fill="x")
        self.btn_verdadero = tk.Button(
            fila_vf, text="VERDADERO", font=("Segoe UI", 11, "bold"), bg="#2a2e42", fg=COLOR_OK,
            relief="flat", pady=8, command=lambda: self._elegir_valor(True),
        )
        self.btn_verdadero.pack(side="left", fill="x", expand=True, padx=(0, 4))
        self.btn_falso = tk.Button(
            fila_vf, text="FALSO", font=("Segoe UI", 11, "bold"), bg="#2a2e42", fg=COLOR_MAL,
            relief="flat", pady=8, command=lambda: self._elegir_valor(False),
        )
        self.btn_falso.pack(side="left", fill="x", expand=True, padx=(4, 0))

        self.marco_elemento = tk.Frame(master, bg=COLOR_PANEL)
        self.marco_elemento.pack(fill="x", padx=14, pady=(14, 0))
        self._botones_elemento: list[tk.Button] = []

        tk.Frame(master, bg=COLOR_PANEL, height=20).pack()

        self.btn_comprobar = tk.Button(
            master, text="COMPROBAR", font=("Segoe UI", 12, "bold"), bg=COLOR_ACENTO, fg="#10121a",
            relief="flat", pady=10, command=self._comprobar,
        )
        self.btn_comprobar.pack(fill="x", padx=14, pady=(10, 6))

        self.feedback_lbl = tk.Label(
            master, text="", font=("Segoe UI", 10, "bold"), fg=COLOR_TEXTO, bg=COLOR_PANEL,
            wraplength=320, justify="left",
        )
        self.feedback_lbl.pack(fill="x", padx=14, pady=(0, 6))

        tk.Button(
            master, text="💡 Pedir pista (-30s)", font=("Segoe UI", 9), bg=COLOR_PANEL, fg="#9aa0b4",
            relief="flat", command=self._pedir_pista,
        ).pack(anchor="w", padx=14, pady=(10, 0))

    def _elegir_valor(self, valor: bool) -> None:
        self._respuesta_valor = valor
        self.btn_verdadero.config(bg=COLOR_OK if valor else "#2a2e42", fg="#10121a" if valor else COLOR_OK)
        self.btn_falso.config(bg=COLOR_MAL if not valor else "#2a2e42", fg="#10121a" if not valor else COLOR_MAL)

        escenario = self.escenarios[self.indice_sala]
        for b in self._botones_elemento:
            b.destroy()
        self._botones_elemento.clear()
        self._respuesta_elemento = None

        necesita_elemento = (
            (escenario.tipo_decisivo == "testigo" and valor)
            or (escenario.tipo_decisivo == "contraejemplo" and not valor)
        )
        if necesita_elemento:
            etiqueta = "testigo" if escenario.tipo_decisivo == "testigo" else "contraejemplo"
            tk.Label(
                self.marco_elemento,
                text=f"¿Cuál es el {etiqueta}? (valor de {escenario.variable_decisiva})",
                font=("Segoe UI", 10, "bold"), fg=COLOR_ACENTO, bg=COLOR_PANEL,
            ).pack(anchor="w", pady=(0, 6))
            opciones = list(escenario.interpretacion.dominio)
            random.shuffle(opciones)
            fila = tk.Frame(self.marco_elemento, bg=COLOR_PANEL)
            fila.pack(fill="x")
            for i, d in enumerate(opciones):
                btn = tk.Button(
                    fila, text=d, font=("Segoe UI", 10), bg="#2a2e42", fg=COLOR_TEXTO,
                    relief="flat", padx=8, pady=4, command=lambda d=d: self._elegir_elemento(d),
                )
                btn.grid(row=i // 4, column=i % 4, padx=3, pady=3, sticky="ew")
                self._botones_elemento.append(btn)

    def _elegir_elemento(self, d: str) -> None:
        self._respuesta_elemento = d
        for b in self._botones_elemento:
            es_este = b.cget("text") == d
            b.config(bg=COLOR_ACENTO if es_este else "#2a2e42", fg="#10121a" if es_este else COLOR_TEXTO)

    def _pedir_pista(self) -> None:
        escenario = self.escenarios[self.indice_sala]
        self.pistas_usadas += 1
        self.tiempo_restante = max(0, self.tiempo_restante - PENALIZACION_PISTA)
        self.feedback_lbl.config(text=f"💡 Pista: {escenario.pista}", fg=COLOR_ACENTO)

    def _comprobar(self) -> None:
        escenario = self.escenarios[self.indice_sala]

        if self._respuesta_valor is None:
            self.feedback_lbl.config(text="Primero elige VERDADERO o FALSO.", fg=COLOR_MAL)
            return

        necesita_elemento = (
            (escenario.tipo_decisivo == "testigo" and self._respuesta_valor)
            or (escenario.tipo_decisivo == "contraejemplo" and not self._respuesta_valor)
        )
        if necesita_elemento and self._respuesta_elemento is None:
            self.feedback_lbl.config(text="Falta señalar el elemento decisivo.", fg=COLOR_MAL)
            return

        correcto = self._respuesta_valor == escenario.valor_real
        if correcto and necesita_elemento:
            correcto = self._respuesta_elemento == escenario.elemento_decisivo

        if correcto:
            self._resolver_sala(escenario)
        else:
            self.tiempo_restante = max(0, self.tiempo_restante - PENALIZACION_INTENTO_FALLIDO)
            self.feedback_lbl.config(
                text="❌ No es correcto. Revisa la tabla con calma, el tiempo sigue corriendo (-10s).",
                fg=COLOR_MAL,
            )

    def _resolver_sala(self, escenario: Escenario) -> None:
        self.digitos_obtenidos.append(escenario.digito)
        self.feedback_lbl.config(
            text=f"✅ ¡Correcto! Dígito liberado: {escenario.digito}",
            fg=COLOR_OK,
        )
        self.btn_comprobar.config(state="disabled")
        for b in self._botones_elemento:
            b.config(state="disabled")
        self.btn_verdadero.config(state="disabled")
        self.btn_falso.config(state="disabled")

        tk.Button(
            self.panel_juego,
            text="Siguiente sala →" if self.indice_sala < 3 else "Ver código final →",
            font=("Segoe UI", 11, "bold"), bg=COLOR_ACENTO, fg="#10121a", relief="flat", pady=8,
            command=self._avanzar,
        ).pack(fill="x", padx=14, pady=(4, 10))

    def _avanzar(self) -> None:
        if self.indice_sala < len(self.escenarios) - 1:
            self.indice_sala += 1
            self._mostrar_sala()
        else:
            self._mostrar_pantalla_final()

    # ------------------------------------------------------------------ pantalla final --
    def _mostrar_pantalla_final(self) -> None:
        if self._despues_id is not None:
            self.after_cancel(self._despues_id)
            self._despues_id = None
        self._limpiar_contenedor()
        tiempo_usado = TIEMPO_TOTAL_SEGUNDOS - self.tiempo_restante

        marco = tk.Frame(self.contenedor, bg=COLOR_FONDO)
        marco.pack(expand=True)

        tk.Label(
            marco, text="🏆 ¡SALA ESCAPADA!", font=("Segoe UI", 30, "bold"), fg=COLOR_OK, bg=COLOR_FONDO,
        ).pack(pady=(40, 20))
        tk.Label(
            marco, text="Código final:", font=("Segoe UI", 14), fg=COLOR_TEXTO, bg=COLOR_FONDO,
        ).pack()
        tk.Label(
            marco, text=" - ".join(self.digitos_obtenidos), font=("Consolas", 40, "bold"),
            fg=COLOR_ACENTO, bg=COLOR_FONDO,
        ).pack(pady=(4, 24))
        tk.Label(
            marco,
            text=f"Tiempo usado: {tiempo_usado // 60}m {tiempo_usado % 60}s   |   Pistas usadas: {self.pistas_usadas}",
            font=("Segoe UI", 12), fg="#9aa0b4", bg=COLOR_FONDO,
        ).pack(pady=(0, 30))

        tk.Button(
            marco, text="JUGAR DE NUEVO", font=("Segoe UI", 12, "bold"), bg=COLOR_ACENTO, fg="#10121a",
            relief="flat", padx=24, pady=10, command=self._mostrar_pantalla_inicio,
        ).pack()

    def _mostrar_pantalla_atrapado(self) -> None:
        """Se acabó el tiempo: el juego queda bloqueado, solo se puede reintentar."""
        self.atrapado = True
        self._limpiar_contenedor()

        marco = tk.Frame(self.contenedor, bg=COLOR_FONDO)
        marco.pack(expand=True)

        tk.Label(
            marco, text="🔒 ¡SE ACABÓ EL TIEMPO!", font=("Segoe UI", 30, "bold"), fg=COLOR_MAL, bg=COLOR_FONDO,
        ).pack(pady=(40, 10))
        tk.Label(
            marco, text="Se han quedado atrapados en la sala.", font=("Segoe UI", 16, "bold"),
            fg=COLOR_TEXTO, bg=COLOR_FONDO,
        ).pack(pady=(0, 20))
        tk.Label(
            marco,
            text=f"Salas escapadas: {len(self.digitos_obtenidos)} de {len(self.escenarios)}"
            + (f"   |   Código parcial: {' - '.join(self.digitos_obtenidos)}" if self.digitos_obtenidos else ""),
            font=("Segoe UI", 12), fg="#9aa0b4", bg=COLOR_FONDO,
        ).pack(pady=(0, 30))

        tk.Button(
            marco, text="INTENTAR DE NUEVO", font=("Segoe UI", 12, "bold"), bg=COLOR_ACENTO, fg="#10121a",
            relief="flat", padx=24, pady=10, command=self._mostrar_pantalla_inicio,
        ).pack()


def ejecutar() -> None:
    app = VentanaEscapeRoom()
    app.mainloop()
