"""Definicion de una disciplina (GP, MX) como problema de optimizacion.

Una disciplina fija algunos parametros de la moto, deja otros libres dentro de
unos limites y asigna pesos a los objetivos de comportamiento. El YAML asociado
vive en configs/<nombre>.yaml.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from motodynamics.geometry.frame import MotorcycleGeometry
from motodynamics.io.config import load_yaml

CONFIG_DIR = Path(__file__).resolve().parents[3] / "configs"

# Parametros que puede optimizar el modelo (el resto se toman como fijos).
FREE_PARAMETERS = (
    "wheelbase",
    "rake",
    "triple_offset",
    "cg_height",
    "cg_x_from_front",
    "swingarm_length",
    "swingarm_angle",
)


@dataclass(frozen=True, slots=True)
class DisciplineSpec:
    name: str
    fixed: dict[str, float]
    bounds: dict[str, tuple[float, float]]
    weights: dict[str, float]

    def free_names(self) -> list[str]:
        """Nombres de los parametros libres, en orden estable."""
        return [p for p in FREE_PARAMETERS if p in self.bounds]

    def bounds_list(self) -> list[tuple[float, float]]:
        return [self.bounds[n] for n in self.free_names()]

    def build_geometry(self, free_values: dict[str, float]) -> MotorcycleGeometry:
        """Construye la geometria combinando parametros fijos y libres."""
        params = {**self.fixed, **free_values}
        return MotorcycleGeometry(**params)


def load_discipline(name: str, config_dir: Path | None = None) -> DisciplineSpec:
    """Carga configs/<name>.yaml y lo valida a un DisciplineSpec."""
    directory = config_dir or CONFIG_DIR
    data = load_yaml(directory / f"{name}.yaml")

    fixed = {k: float(v) for k, v in data.get("fixed", {}).items()}
    bounds = {
        k: (float(v["min"]), float(v["max"])) for k, v in data.get("bounds", {}).items()
    }
    weights = {k: float(v) for k, v in data.get("weights", {}).items()}

    unknown = set(bounds) - set(FREE_PARAMETERS)
    if unknown:
        raise ValueError(f"{name}: parametros libres no reconocidos: {sorted(unknown)}")

    return DisciplineSpec(name=data.get("name", name), fixed=fixed, bounds=bounds, weights=weights)
