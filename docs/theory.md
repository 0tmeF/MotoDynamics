# Base teorica

Notas propias derivadas de la teoria de dinamica de la motocicleta
(referencia principal: V. Cossalter, *Motorcycle Dynamics*, 2a ed.). No se
reproduce texto ni figuras del libro; solo se registran las ecuaciones que se
implementan y las decisiones de modelado.

## 1. Geometria de direccion

Notacion:

- `p` distancia entre ejes.
- `epsilon` angulo de lanzamiento (caster) respecto a la vertical.
- `d` avance de tijas (offset), perpendicular al eje de direccion.
- `R_f` radio bajo carga de la rueda delantera.

Avance (trail):

    a_n = R_f * sin(epsilon) - d          (avance normal, perpendicular al eje)
    a   = a_n / cos(epsilon)              (avance medido a nivel del suelo)

Implementado en `geometry/frame.py`. Mas avance => mas estabilidad direccional
y mas esfuerzo en el manillar; menos avance => mas agilidad y tendencia al
oscilado (wobble).

## 2. Reparto de carga y transferencia longitudinal

En estatico, con el centro de masas a distancia `b` del eje trasero:

    N_f = m g (p - b) / p
    N_r = m g b / p

Bajo aceleracion longitudinal `a_x` (frenada negativa):

    Delta_N = m a_x h / p

Limites (rueda que se despega, N -> 0):

    a_x,caballito = (N_f,est / (m g)) * g * p / h     (el eje delantero se levanta)
    a_x,stoppie   = (N_r,est / (m g)) * g * p / h     (el eje trasero se levanta)

Implementado en `dynamics/steady.py` como `accel_limit` y `brake_limit`.

## 3. Pendiente (por trasladar del libro)

- [ ] Indice de maniobrabilidad y par de vuelco en curva estacionaria.
- [ ] Modelo lineal de estabilidad: modos de *capsize*, *weave* y *wobble*;
      dependencia con velocidad, avance y rigidez de direccion.
- [ ] Cinematica del tren trasero: anti-squat, variacion de la distancia entre
      ejes con el recorrido, efecto de la cadena.
- [ ] Modelo de neumatico (rigidez de deriva y de camber, relajacion).
- [ ] Momentos de inercia del conjunto (sustituir el proxy `m * h^2`).

## 4. Sobre los indices heuristicos actuales

`agility` y `stability` en `dynamics/steady.py` son formulas ad-hoc para tener
una funcion objetivo que corra de extremo a extremo. Se sustituiran por los
modelos de la seccion 3. Mientras tanto, los resultados de la optimizacion solo
tienen valor cualitativo.
