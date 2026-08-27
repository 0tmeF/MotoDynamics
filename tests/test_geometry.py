import math

import pytest

from motodynamics.geometry.frame import MotorcycleGeometry


@pytest.fixture
def ref() -> MotorcycleGeometry:
    return MotorcycleGeometry(
        wheelbase=1.44,
        rake=math.radians(24.0),
        triple_offset=0.030,
        front_radius=0.30,
        rear_radius=0.32,
        cg_height=0.58,
        cg_x_from_front=0.50,
        mass=240.0,
        swingarm_length=0.58,
        swingarm_angle=math.radians(8.0),
    )


def test_trail_formula(ref):
    expected_normal = ref.front_radius * math.sin(ref.rake) - ref.triple_offset
    assert ref.normal_trail == pytest.approx(expected_normal)
    assert ref.trail == pytest.approx(expected_normal / math.cos(ref.rake))
    assert ref.trail > 0


def test_load_fractions_sum_to_one(ref):
    assert ref.front_load_fraction + ref.rear_load_fraction == pytest.approx(1.0)
    total = ref.static_front_load + ref.static_rear_load
    assert total == pytest.approx(ref.mass * MotorcycleGeometry.G)


def test_with_returns_modified_copy(ref):
    other = ref.with_(wheelbase=1.50)
    assert other.wheelbase == 1.50
    assert ref.wheelbase == 1.44  # el original no cambia
