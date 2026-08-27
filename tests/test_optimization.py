import pytest

from motodynamics.disciplines.spec import load_discipline
from motodynamics.dynamics.steady import evaluate_handling
from motodynamics.optimization.problem import optimize_geometry


@pytest.mark.parametrize("name", ["gp", "mx"])
def test_discipline_loads(name):
    spec = load_discipline(name)
    assert spec.free_names()
    assert len(spec.bounds_list()) == len(spec.free_names())


@pytest.mark.parametrize("name", ["gp", "mx"])
def test_optimize_stays_within_bounds(name):
    spec = load_discipline(name)
    result = optimize_geometry(spec, seed=0)
    assert result.success
    for n, (lo, hi) in zip(spec.free_names(), spec.bounds_list()):
        assert lo - 1e-6 <= result.free_values[n] <= hi + 1e-6


def test_handling_limits_are_physical():
    spec = load_discipline("gp")
    result = optimize_geometry(spec, seed=0)
    h = evaluate_handling(result.geometry)
    # limites de aceleracion/frenada en un rango razonable (m/s^2)
    assert 5.0 < h.accel_limit < 25.0
    assert 5.0 < h.brake_limit < 25.0
