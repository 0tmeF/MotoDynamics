"""Modelo parametrico de la geometria de una motocicleta.

Notacion siguiendo, en lo posible, a Cossalter, "Motorcycle Dynamics" (2a ed.).
Todas las unidades en SI: metros, radianes, kilogramos, newton.

El objeto `MotorcycleGeometry` guarda los parametros independientes que define
el diseñador/setup. Las magnitudes derivadas (avance, reparto de pesos, ...) se
calculan como propiedades para que siempre sean consistentes con los parametros.

TODO(teoria): completar formulas de altura del centro de masas del conjunto
moto+piloto y de la geometria del tren trasero (basculante) a partir del libro.
"""

from __future__ import annotations

import math
from dataclasses import dataclass, replace


@dataclass(frozen=True, slots=True)
class MotorcycleGeometry:
    """Parametros independientes de la geometria.

    Attributes
    ----------
    wheelbase:
        Distancia entre ejes `p` [m].
    rake:
        Angulo de lanzamiento (caster) `epsilon` medido respecto a la vertical
        [rad]. Un valor tipico de GP ronda 0.40 rad (~23 deg); una MX, mayor.
    triple_offset:
        Avance de tijas / offset `d` [m]: distancia perpendicular entre el eje
        de direccion y el eje de la rueda delantera.
    front_radius:
        Radio bajo carga de la rueda delantera `R_f` [m].
    rear_radius:
        Radio bajo carga de la rueda trasera `R_r` [m].
    cg_height:
        Altura del centro de masas del conjunto moto + piloto `h` [m].
    cg_x_from_front:
        Posicion longitudinal del centro de masas medida desde el eje delantero
        como fraccion de la distancia entre ejes (0 = sobre el eje delantero,
        1 = sobre el trasero).
    mass:
        Masa total del conjunto moto + piloto `m` [kg].
    swingarm_length:
        Longitud del basculante `l_s` [m].
    swingarm_angle:
        Angulo del basculante respecto a la horizontal en reposo [rad],
        positivo cuando el eje trasero queda por debajo del pivote.
    """

    wheelbase: float
    rake: float
    triple_offset: float
    front_radius: float
    rear_radius: float
    cg_height: float
    cg_x_from_front: float
    mass: float
    swingarm_length: float
    swingarm_angle: float

    G = 9.81  # aceleracion de la gravedad [m/s^2]

    # ------------------------------------------------------------------
    # Magnitudes derivadas de la geometria de direccion
    # ------------------------------------------------------------------
    @property
    def normal_trail(self) -> float:
        """Avance normal `a_n = R_f * sin(epsilon) - d` [m]."""
        return self.front_radius * math.sin(self.rake) - self.triple_offset

    @property
    def trail(self) -> float:
        """Avance a nivel del suelo `a = (R_f * sin(epsilon) - d) / cos(epsilon)` [m]."""
        return self.normal_trail / math.cos(self.rake)

    @property
    def rake_deg(self) -> float:
        return math.degrees(self.rake)

    # ------------------------------------------------------------------
    # Reparto de cargas estatico (moto vertical, en reposo)
    # ------------------------------------------------------------------
    @property
    def front_load_fraction(self) -> float:
        """Fraccion del peso total sobre el eje delantero en estatico."""
        return 1.0 - self.cg_x_from_front

    @property
    def rear_load_fraction(self) -> float:
        return self.cg_x_from_front

    @property
    def static_front_load(self) -> float:
        """Carga vertical sobre el eje delantero `N_f` [N]."""
        return self.front_load_fraction * self.mass * self.G

    @property
    def static_rear_load(self) -> float:
        return self.rear_load_fraction * self.mass * self.G

    # ------------------------------------------------------------------
    # Utilidades
    # ------------------------------------------------------------------
    def with_(self, **changes: float) -> MotorcycleGeometry:
        """Devuelve una copia con los parametros indicados modificados."""
        return replace(self, **changes)

    def summary(self) -> dict[str, float]:
        """Diccionario plano con parametros y derivados, util para logging/plots."""
        return {
            "wheelbase": self.wheelbase,
            "rake_deg": self.rake_deg,
            "triple_offset": self.triple_offset,
            "trail": self.trail,
            "normal_trail": self.normal_trail,
            "cg_height": self.cg_height,
            "front_load_fraction": self.front_load_fraction,
            "mass": self.mass,
            "swingarm_length": self.swingarm_length,
        }
