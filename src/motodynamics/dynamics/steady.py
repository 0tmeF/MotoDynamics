"""Metricas de comportamiento en regimen cuasi-estatico.

Este modulo es deliberadamente simple: mezcla resultados exactos de mecanica
(transferencia de carga longitudinal, limites de caballito y stoppie) con
indices heuristicos de agilidad y estabilidad que sirven como funcion objetivo
provisional para la optimizacion.

Los indices heuristicos deben sustituirse por modelos con respaldo teorico
(estabilidad de weave/wobble, indices de maniobrabilidad de Cossalter) a medida
que se traslade la teoria del libro. Ver docs/theory.md.
"""

from __future__ import annotations

from dataclasses import dataclass

from motodynamics.geometry.frame import MotorcycleGeometry

G = 9.81


@dataclass(frozen=True, slots=True)
class HandlingMetrics:
    """Resultados de :func:`evaluate_handling`.

    agility: mayor = mas agil (cambia de direccion con menos esfuerzo).
    stability: mayor = mas estable en recta y a alta velocidad.
    accel_limit: aceleracion longitudinal maxima antes del caballito [m/s^2].
    brake_limit: deceleracion maxima antes del stoppie [m/s^2].
    """

    agility: float
    stability: float
    accel_limit: float
    brake_limit: float


def _agility_index(g: MotorcycleGeometry) -> float:
    """Indice heuristico de agilidad.

    Penaliza distancia entre ejes larga, mucho avance y momento de inercia
    (aproximado por masa * altura_cg^2). Normalizado a valores O(1) para una
    moto de referencia.
    """
    inertia_proxy = g.mass * g.cg_height**2
    return 1.0 / (g.wheelbase * (1.0 + 4.0 * g.trail) * inertia_proxy) * 1.0e3


def _stability_index(g: MotorcycleGeometry) -> float:
    """Indice heuristico de estabilidad direccional.

    Crece con el avance y la distancia entre ejes; decrece si el centro de
    masas esta muy alto respecto a la distancia entre ejes.
    """
    return (g.trail * g.wheelbase) / (0.2 + g.cg_height / g.wheelbase)


def evaluate_handling(g: MotorcycleGeometry) -> HandlingMetrics:
    """Calcula las metricas de comportamiento para una geometria dada."""
    accel_limit = g.front_load_fraction * G * g.wheelbase / g.cg_height
    brake_limit = g.rear_load_fraction * G * g.wheelbase / g.cg_height
    return HandlingMetrics(
        agility=_agility_index(g),
        stability=_stability_index(g),
        accel_limit=accel_limit,
        brake_limit=brake_limit,
    )
