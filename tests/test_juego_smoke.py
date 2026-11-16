"""Prueba de humo del Escape Room Lógico: recorre las 4 salas manipulando los
widgets reales (sin mostrar la ventana), para asegurar que el flujo completo
de juego (elegir valor, elegir elemento decisivo, comprobar, avanzar, pantalla
final) funciona con el motor real.

Ejecutar con:  python -m unittest tests.test_juego_smoke -v
"""

from __future__ import annotations

import tkinter as tk
import unittest

from juego.app import VentanaEscapeRoom


class TestEscapeRoomGUI(unittest.TestCase):
    def setUp(self) -> None:
        try:
            self.app = VentanaEscapeRoom()
        except tk.TclError as e:
            self.skipTest(f"No hay display de Tk disponible: {e}")
        self.app.withdraw()
        self.app.update_idletasks()

    def tearDown(self) -> None:
        self.app.destroy()

    def test_recorrido_completo_con_respuestas_correctas(self) -> None:
        app = self.app
        app._comenzar_juego()

        for i in range(4):
            escenario = app.escenarios[i]
            self.assertEqual(app.indice_sala, i)

            app._elegir_valor(escenario.valor_real)
            if escenario.tipo_decisivo is not None:
                app._elegir_elemento(escenario.elemento_decisivo)

            app._comprobar()
            self.assertIn("Correcto", app.feedback_lbl.cget("text"))
            self.assertEqual(app.digitos_obtenidos[-1], escenario.digito)

            app._avanzar()

        self.assertEqual(app.digitos_obtenidos, [e.digito for e in app.escenarios])

    def test_respuesta_incorrecta_penaliza_y_no_avanza(self) -> None:
        app = self.app
        app._comenzar_juego()
        escenario = app.escenarios[0]
        tiempo_antes = app.tiempo_restante

        app._elegir_valor(not escenario.valor_real)
        app._comprobar()

        self.assertIn("No es correcto", app.feedback_lbl.cget("text"))
        self.assertEqual(app.indice_sala, 0)
        self.assertEqual(app.digitos_obtenidos, [])
        self.assertLess(app.tiempo_restante, tiempo_antes)

    def test_comprobar_sin_elegir_valor_pide_que_elija(self) -> None:
        app = self.app
        app._comenzar_juego()
        app._comprobar()
        self.assertIn("Primero elige", app.feedback_lbl.cget("text"))

    def test_sala_con_elemento_decisivo_exige_elegirlo(self) -> None:
        app = self.app
        app._comenzar_juego()
        escenario = app.escenarios[0]  # sala 1 siempre pide testigo
        self.assertEqual(escenario.tipo_decisivo, "testigo")

        app._elegir_valor(escenario.valor_real)
        app._comprobar()  # sin elegir elemento todavia
        self.assertIn("elemento decisivo", app.feedback_lbl.cget("text"))
        self.assertEqual(app.digitos_obtenidos, [])

    def test_tiempo_agotado_bloquea_el_juego(self) -> None:
        app = self.app
        app._comenzar_juego()
        self.assertFalse(app.atrapado)

        app.tiempo_restante = 0
        app._tick()

        self.assertTrue(app.atrapado)
        # ya no quedan botones de la sala (VERDADERO/FALSO/COMPROBAR) para seguir jugando
        self.assertFalse(hasattr(app, "btn_comprobar") and app.btn_comprobar.winfo_exists())
        # el único control disponible es el de reintentar
        textos = self._textos_botones(app.contenedor)
        self.assertIn("INTENTAR DE NUEVO", textos)

    def test_reintentar_despues_de_atrapado_reinicia_el_juego(self) -> None:
        app = self.app
        app._comenzar_juego()
        app.tiempo_restante = 0
        app._tick()

        app._mostrar_pantalla_inicio()
        self.assertEqual(app.digitos_obtenidos, [])
        textos = self._textos_botones(app.contenedor)
        self.assertIn("COMENZAR", textos)

    @staticmethod
    def _textos_botones(widget) -> list[str]:
        textos = []
        for hijo in widget.winfo_children():
            if isinstance(hijo, tk.Button):
                textos.append(hijo.cget("text"))
            textos.extend(TestEscapeRoomGUI._textos_botones(hijo))
        return textos

    def test_elemento_decisivo_incorrecto_no_resuelve_sala(self) -> None:
        app = self.app
        app._comenzar_juego()
        escenario = app.escenarios[0]
        otro = next(d for d in escenario.interpretacion.dominio if d != escenario.elemento_decisivo)

        app._elegir_valor(escenario.valor_real)
        app._elegir_elemento(otro)
        app._comprobar()

        self.assertIn("No es correcto", app.feedback_lbl.cget("text"))
        self.assertEqual(app.digitos_obtenidos, [])


if __name__ == "__main__":
    unittest.main()
