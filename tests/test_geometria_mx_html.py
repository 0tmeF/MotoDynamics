"""Verificacion del explorador `docs/geometria-mx.html`.

El HTML es una herramienta interactiva: sus formulas replican `docs/theory.md`
seccion 1-2 y `dynamics/steady.py` (ya cubiertas por `test_geometry.py`). Lo
que este test protege es que los datos de entrada del explorador no se
desincronicen de la fuente de verdad del proyecto:

- los parametros marcados como fijos usan exactamente los valores de
  `configs/mx.yaml` (`fixed`);
- los rangos de los deslizadores caen dentro de los limites de `mx.yaml`
  (`bounds`), con la conversion de rad a grados donde aplica;
- el valor por defecto de cada parametro libre esta dentro de su rango.

No ejecuta el JavaScript (no hay runtime JS en el runner); la correccion de
las formulas se verifica en `test_geometry.py` sobre el modelo Python que el
HTML replica.
"""

from __future__ import annotations

import math
import re
from pathlib import Path

import yaml

RAIZ = Path(__file__).resolve().parent.parent
HTML = RAIZ / "docs" / "geometria-mx.html"
MX_YAML = RAIZ / "configs" / "mx.yaml"

# Parametros del HTML que son angulos: se declaran en grados, mx.yaml en rad.
ANGULOS = {"rake", "swingarm_angle"}
# Correspondencia clave del HTML -> clave en mx.yaml.
EN_BOUNDS = {
    "wheelbase", "rake", "triple_offset", "cg_height", "cg_x_from_front",
    "swingarm_length", "swingarm_angle",
}
EN_FIXED = {"front_radius", "rear_radius", "mass"}


def _parse_params(texto: str) -> dict[str, dict[str, float]]:
    """Extrae la tabla PARAMS del <script> del HTML.

    Cada fila: ["clave", "etq", min, max, paso, defecto, "unidad", "grupo", fijo]
    """
    bloque = re.search(r"var PARAMS = \[(.*?)\];", texto, re.DOTALL)
    assert bloque, "no se encontro la tabla PARAMS en el HTML"
    filas = re.findall(r"\[\s*(\"[^\"]+\".*?)\]", bloque.group(1), re.DOTALL)
    out: dict[str, dict[str, float]] = {}
    for fila in filas:
        partes = [p.strip() for p in _split_top_level(fila)]
        clave = partes[0].strip('"')
        out[clave] = {
            "min": float(partes[2]),
            "max": float(partes[3]),
            "defecto": float(partes[5]),
            "fijo": partes[8].strip() == "true",
        }
    return out


def _split_top_level(fila: str) -> list[str]:
    """Divide por comas ignorando las que van dentro de comillas."""
    out, buf, en_comillas = [], [], False
    for ch in fila:
        if ch == '"':
            en_comillas = not en_comillas
            buf.append(ch)
        elif ch == "," and not en_comillas:
            out.append("".join(buf))
            buf = []
        else:
            buf.append(ch)
    out.append("".join(buf))
    return out


def _rad(clave: str, valor_grados: float) -> float:
    return math.radians(valor_grados) if clave in ANGULOS else valor_grados


def test_html_existe_y_tiene_un_solo_title():
    texto = HTML.read_text(encoding="utf-8")
    assert texto.count("<title>") == 1
    assert 'id="svg"' in texto
    assert 'claude.use' not in texto, "el explorador no declara capabilities"


def test_fijos_coinciden_con_mx_yaml():
    cfg = yaml.safe_load(MX_YAML.read_text(encoding="utf-8"))
    params = _parse_params(HTML.read_text(encoding="utf-8"))
    for clave in EN_FIXED:
        assert params[clave]["fijo"] is True, f"{clave} deberia estar fijo"
        esperado = float(cfg["fixed"][clave])
        assert params[clave]["defecto"] == esperado
        assert params[clave]["min"] == esperado == params[clave]["max"]


def test_rangos_dentro_de_los_limites_de_mx_yaml():
    cfg = yaml.safe_load(MX_YAML.read_text(encoding="utf-8"))
    params = _parse_params(HTML.read_text(encoding="utf-8"))
    for clave in EN_BOUNDS:
        lim = cfg["bounds"][clave]
        p = params[clave]
        assert _rad(clave, p["min"]) >= lim["min"] - 1e-9, f"{clave} min fuera de bounds"
        assert _rad(clave, p["max"]) <= lim["max"] + 1e-9, f"{clave} max fuera de bounds"
        assert p["min"] <= p["defecto"] <= p["max"], f"{clave} defecto fuera de rango"


def test_defectos_libres_son_coherentes_con_una_geometria_valida():
    """Los valores por defecto del explorador construyen una MotorcycleGeometry
    con avance positivo (geometria fisicamente sensata)."""
    from motodynamics.geometry.frame import MotorcycleGeometry

    params = _parse_params(HTML.read_text(encoding="utf-8"))
    g = MotorcycleGeometry(
        wheelbase=params["wheelbase"]["defecto"],
        rake=math.radians(params["rake"]["defecto"]),
        triple_offset=params["triple_offset"]["defecto"],
        front_radius=params["front_radius"]["defecto"],
        rear_radius=params["rear_radius"]["defecto"],
        cg_height=params["cg_height"]["defecto"],
        cg_x_from_front=params["cg_x_from_front"]["defecto"],
        mass=params["mass"]["defecto"],
        swingarm_length=params["swingarm_length"]["defecto"],
        swingarm_angle=math.radians(params["swingarm_angle"]["defecto"]),
    )
    assert g.trail > 0
    assert 0 < g.front_load_fraction < 1
