"""Optimizacion de la geometria para una disciplina.

Formulacion actual: suma ponderada de objetivos (agilidad, estabilidad, limites
de aceleracion y frenada). Es un punto de partida; cuando haya objetivos en
conflicto claros (p. ej. agilidad vs estabilidad) conviene pasar a multiobjetivo
y devolver un frente de Pareto.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
from scipy.optimize import differential_evolution

from motodynamics.disciplines.spec import DisciplineSpec
from motodynamics.dynamics.steady import evaluate_handling
from motodynamics.geometry.frame import MotorcycleGeometry

# Metricas que se pueden ponderar desde el YAML de la disciplina.
OBJECTIVE_KEYS = ("agility", "stability", "accel_limit", "brake_limit")


@dataclass(frozen=True, slots=True)
class OptimizationResult:
    discipline: str
    geometry: MotorcycleGeometry
    free_values: dict[str, float]
    score: float
    metrics: dict[str, float]
    success: bool
    n_eval: int


def _score(metrics: dict[str, float], weights: dict[str, float]) -> float:
    """Suma ponderada. Pesos positivos => se maximiza esa metrica."""
    return sum(weights.get(k, 0.0) * metrics[k] for k in OBJECTIVE_KEYS)


def _metrics_dict(g: MotorcycleGeometry) -> dict[str, float]:
    h = evaluate_handling(g)
    return {
        "agility": h.agility,
        "stability": h.stability,
        "accel_limit": h.accel_limit,
        "brake_limit": h.brake_limit,
    }


def optimize_geometry(spec: DisciplineSpec, seed: int | None = 0) -> OptimizationResult:
    """Busca la geometria que maximiza la puntuacion ponderada de la disciplina."""
    free_names = spec.free_names()
    bounds = spec.bounds_list()
    if not bounds:
        raise ValueError(f"{spec.name}: no hay parametros libres que optimizar")

    def objective(x: np.ndarray) -> float:
        free_values = dict(zip(free_names, x, strict=True))
        g = spec.build_geometry(free_values)
        return -_score(_metrics_dict(g), spec.weights)  # minimizamos -score

    res = differential_evolution(
        objective,
        bounds,
        seed=seed,
        tol=1e-7,
        maxiter=500,
        polish=True,
    )

    free_values = dict(zip(free_names, res.x, strict=True))
    geometry = spec.build_geometry(free_values)
    metrics = _metrics_dict(geometry)
    return OptimizationResult(
        discipline=spec.name,
        geometry=geometry,
        free_values=free_values,
        score=-res.fun,
        metrics=metrics,
        success=bool(res.success),
        n_eval=int(res.nfev),
    )
