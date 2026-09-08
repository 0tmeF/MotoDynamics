# Investigación: modelo lineal de estabilidad de Sharp (1971)

Objetivo: trasladar a MotoDynamics un modelo de estabilidad lineal en marcha
recta (modos capsize, weave, wobble) con respaldo teórico y con datos de
referencia contra los que verificar el solver.

## Fuente primaria

R. S. Sharp, "The Stability and Control of Motorcycles", *Journal of
Mechanical Engineering Science*, Vol. 13, No. 5, 1971, pp. 316-329.

- Copia consultada (texto completo, apéndices y tablas):
  `http://commons.princeton.edu/wp-content/uploads/sites/80/2018/08/stability-of-motorcycles.pdf`
- Registro editorial: `https://journals.sagepub.com/doi/10.1243/JMES_JOUR_1971_013_051_02`

Es el trabajo que nombró los modos *weave* y *capsize* y estableció que hace
falta un modelo de **orden 8** con relajación de neumático para representar
bien el comportamiento en control libre (hands-off). Cossalter, *Motorcycle
Dynamics* (referencia ya citada en `docs/theory.md`) parte de esta línea.

## Estructura del modelo

- **Dos cuerpos rígidos** unidos por el eje de dirección: cuadro trasero
  (estructura + motor + depósito + basculante + rueda trasera + piloto rígido)
  y cuadro delantero (rueda delantera + horquilla + manillar). Amortiguador de
  dirección lineal de coeficiente `K` entre ambos.
- **Grados de libertad**: desplazamiento lateral `y`, guiñada `psi`, balanceo
  `phi`, giro de dirección `delta`. Velocidad de avance constante; sin cabeceo;
  ruedas como discos rígidos en contacto puntual, sin deslizamiento
  longitudinal (elimina las rotaciones de rueda de las ecuaciones).
- **Neumático**: fuerza lateral lineal en deriva y en caída (camber), con
  retardo de primer orden (longitud de relajación `sigma`):
  `(sigma/u) Ẏ + Y = C1·alpha + C2·gamma`.
  `y` se elimina, quedando 3 ecuaciones de 2º orden en `psi, phi, delta` más 2
  de 1º orden por la relajación de los dos neumáticos → **8 estados**.
- Se resuelve como problema de autovalores de `-(B)^-1 (A)` con
  `x = X·e^(mu·t)`. Parte real de `mu` = amortiguamiento (1/s), parte
  imaginaria = frecuencia circular (rad/s).

Las ecuaciones linealizadas completas (segundo orden, términos de orden
superior eliminados) están en el Apéndice 1 del paper, pp. 327-328, y la
variante sin deslizamiento en el Apéndice 2. Los coeficientes acoplan masas,
inercias de ambos cuadros, efectos giroscópicos de las ruedas (`i_fy`, `i_ry`)
y del volante de inercia del motor, el avance `t` y el ángulo de lanzamiento
`epsilon`.

## Parámetros de la "máquina estándar" (Apéndice 3)

Unidades imperiales del paper (slug, ft, lb, rad). Conversión a SI para
implementar: 1 slug = 14.5939 kg, 1 slug·ft² = 1.35582 kg·m², 1 ft = 0.3048 m,
1 lb = 4.44822 N.

| Símbolo | Valor | Significado |
|---|---|---|
| `M_f` | 2.1 slug | masa del cuadro delantero |
| `M_r` | 14.9 slug | masa del cuadro trasero (con piloto) |
| `Z_f` | −226 lb | carga vertical rueda delantera |
| `I_rx` | 23 slug·ft² | inercia de balanceo del cuadro trasero |
| `I_rz` | 15.54 slug·ft² | inercia de guiñada del cuadro trasero |
| `C_rxz` | 1.28 slug·ft² | producto de inercia del cuadro trasero |
| `I_fx` | 0.91 slug·ft² | inercia del cuadro delantero (eje paralelo al de dirección) |
| `I_fz` | 0.326 slug·ft² | inercia del cuadro delantero (eje de dirección) |
| `i_fy` | 0.53 slug·ft² | momento polar de la rueda delantera |
| `i_ry + λi` | 0.775 slug·ft² | polar de rueda trasera + volante motor reflejado |
| `a` | 3.112 ft | distancia de A a G_f a lo largo del eje de dirección |
| `b` | 1.574 ft | de A (bajo G_r) al eje trasero |
| `e` | 0.08 ft | offset de G_f respecto al eje de dirección |
| `f` | 0.093 ft | posición de G_f a lo largo de X4 |
| `h` | 2.02 ft | altura de G_r sobre el suelo |
| `R_f`, `R_r` | 1 ft | radios de rueda bajo carga |
| `t` | 0.38 ft | avance mecánico (trail) |
| `epsilon` | 0.4715 rad (27°) | ángulo de lanzamiento (steering head) |
| `C_f1` | 2512 lb/rad | rigidez de deriva delantera |
| `C_f2` | 211 lb/rad | rigidez de caída (camber) delantera |
| `C_r1` | 3559 lb/rad | rigidez de deriva trasera |
| `C_r2` | 298 lb/rad | rigidez de caída trasera |
| `K` | 5 lb·ft/(rad/s) | coeficiente del amortiguador de dirección |
| `sigma` | 0.8 ft | longitud de relajación (igual en ambos neumáticos) |

Nota: el paper no tabula `j` (altura de G_f) ni `k` (posición longitudinal de
G_f) ni el reparto de la distancia entre ejes; se derivan de `a, e, f,
epsilon` y de la geometría de la Fig. 1. Esto hay que fijarlo con cuidado al
implementar y es la fuente más probable de discrepancia con el benchmark.

## Datos de referencia: autovalores de la máquina estándar

Modelo 1 de las Tablas 1-3 del paper (tratamiento completo del neumático).
Velocidad en ft/s (1 ft/s = 0.3048 m/s). Para cada modo oscilatorio: primer
número = amortiguamiento (parte real, 1/s), segundo = frecuencia circular
(parte imaginaria, rad/s).

**Capsize** (no oscilatorio, parte real en 1/s):

| u (ft/s) | 10 | 20 | 30 | 50 | 70 | 100 | 130 | 160 |
|---|---|---|---|---|---|---|---|---|
| Re | −3.56 | −2.83 | −0.13 | +0.08 | +0.08 | +0.07 | +0.05 | +0.04 |

Divergente (Re > 0) por encima de ~35 ft/s, máxima divergencia cerca de
60 ft/s; leve.

**Weave** (oscilatorio):

| u (ft/s) | 10 | 20 | 30 | 50 | 70 | 100 | 130 | 160 |
|---|---|---|---|---|---|---|---|---|
| Re | +2.01 | −0.18 | −3.36 | −6.59 | −3.97 | −1.82 | −1.13 | −0.96 |
| Im | 1.63 | 2.09 | 4.56 | 11.4 | 16.8 | 19.2 | 20.4 | 21.2 |

Inestable por debajo de ~20 ft/s; bien amortiguado a media velocidad;
moderado a alta. Frecuencia sube de ~0.2 Hz (5 ft/s) a ~3.4 Hz (160 ft/s).

**Wobble** (oscilatorio):

| u (ft/s) | 10 | 20 | 30 | 50 | 70 | 100 | 130 | 160 |
|---|---|---|---|---|---|---|---|---|
| Re | −5.20 | −5.91 | −6.42 | −6.52 | −5.70 | −3.94 | −2.24 | −0.82 |
| Im | 55.7 | 55.8 | 55.5 | 54.6 | 54.0 | 54.3 | 55.6 | 57.5 |

Frecuencia casi independiente de la velocidad, ~9 Hz (55 rad/s). Bien
amortiguado salvo a muy alta velocidad. Muy sensible a `K` y a `sigma`.

## Efectos de diseño (Tablas 1-3, casos 2-34)

El paper cuantifica el efecto de cambiar cada parámetro (avance, lanzamiento,
posición de centros de masa, inercias de rueda, `K`, `sigma`, pasajero,
distancia entre ejes). Útil como segunda batería de verificación cualitativa:
p. ej. subir `K` amortigua wobble y desamortigua weave; bajar `h` mejora weave
a alta y baja velocidad; acortar el avance agrava la inestabilidad de capsize.

## Cómo se usa en MotoDynamics

1. `docs/theory.md` §3: registrar el modelo (ecuaciones y decisiones).
2. Implementar el solver con estos parámetros como caso de prueba; el test
   fija los autovalores del benchmark con tolerancia (transcripción de tabla,
   no memoria).
3. Construir juegos de parámetros GP y MX a partir de literatura (Cossalter y
   trabajos posteriores con datos de moto deportiva y de campo) como objetos
   de análisis; sus autovalores se fijan por regresión, no contra verdad
   externa (los modelos reales de competición no publican autovalores).
