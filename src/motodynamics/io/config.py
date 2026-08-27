"""Carga de ficheros de configuracion YAML."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml


def load_yaml(path: str | Path) -> dict[str, Any]:
    """Lee un YAML y devuelve un diccionario. Lanza si el nivel raiz no es un mapa."""
    path = Path(path)
    with path.open("r", encoding="utf-8") as fh:
        data = yaml.safe_load(fh)
    if not isinstance(data, dict):
        raise TypeError(f"{path}: se esperaba un mapa en la raiz, se obtuvo {type(data).__name__}")
    return data
