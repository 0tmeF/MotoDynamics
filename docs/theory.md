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

## 3. Estabilidad lineal en marcha recta (modelo de Sharp 1971)

Referencia: R. S. Sharp, "The Stability and Control of Motorcycles", *J. Mech.
Eng. Sci.* 13(5), 1971, 316-329. Investigacion y datos en
`docs/research/sharp-1971-estabilidad-lineal.md`. No se reproduce el paper;
aqui se registra el modelo que se implementa y las decisiones.

### 3.1 Cuerpos y grados de libertad

Dos cuerpos rigidos unidos por el eje de direccion:

- **Cuadro trasero** (`r`): estructura, motor, deposito, basculante, rueda
  trasera y piloto rigidamente unido. Masa `M_r`, inercias `I_rx` (balanceo),
  `I_rz` (guiñada), producto `C_rxz`.
- **Cuadro delantero** (`f`): rueda delantera, horquilla, manillar. Masa
  `M_f`, inercias `I_fx`, `I_fz` respecto a ejes por su centro de masas, uno
  de ellos paralelo al eje de direccion (principal por hipotesis).

Amortiguador de direccion lineal de coeficiente `K` entre ambos cuadros.

Grados de libertad: lateral `y`, guiñada `psi`, balanceo `phi`, direccion
`delta`. Hipotesis: velocidad de avance `u` constante, sin cabeceo, ruedas
como discos rigidos en contacto puntual sin deslizamiento longitudinal (esto
elimina las rotaciones de rueda), perturbaciones pequeñas (ecuaciones
lineales), aerodinamica despreciable frente a fuerzas de neumatico.

### 3.2 Neumatico

Fuerza lateral lineal en angulo de deriva `alpha` y de caida `gamma`, con
retardo de primer orden por la longitud de relajacion `sigma`:

    (sigma / u) * dY/dt + Y = C1 * alpha + C2 * gamma

para cada eje (`C_f1, C_f2` delante; `C_r1, C_r2` detras). Los angulos de
deriva se obtienen de la cinematica del contacto (Sharp, ec. 15-17); la caida
trasera es simplemente `phi`, la delantera incluye el termino `sin(epsilon)`
del giro de direccion.

### 3.3 Ecuaciones y solucion

Eliminando `y` quedan 3 ecuaciones de 2º orden en `psi, phi, delta` y 2 de 1º
orden por la relajacion de los dos neumaticos: **sistema de orden 8**. Los
coeficientes (Sharp, Apendice 1, pp. 327-328) acoplan masas, las inercias de
ambos cuadros, los efectos giroscopicos de las dos ruedas y del volante de
inercia del motor (`i_fy`, `i_ry + lambda*i`), el avance `t` y el angulo de
lanzamiento `epsilon`.

En forma de espacio de estados `x = [v, r, Phi, Delta, phi, delta, Y_f, Y_r]`
se escribe `B*mu*x + A*x = 0`; los modos son los autovalores de `-B^-1 A`,
funcion de `u`. Parte real = amortiguamiento (1/s), parte imaginaria =
frecuencia circular (rad/s).

### 3.4 Modos

- **Capsize**: no oscilatorio. La maquina cae de lado como un barco
  escorando. Bien amortiguado a baja velocidad; leve divergencia a media y
  alta (la controla el piloto con peso y par de direccion).
- **Weave**: oscilatorio, 0.2-3.5 Hz, involucra balanceo + guiñada +
  direccion del conjunto. Inestable a muy baja velocidad, bien amortiguado a
  media, moderado a alta.
- **Wobble**: oscilatorio, ~9 Hz casi independiente de la velocidad;
  oscilacion rapida de la direccion sola. Amortiguamiento muy sensible a `K` y
  a `sigma`.

### 3.5 Verificacion

El solver se contrasta contra los autovalores publicados de la "maquina
estandar" de Sharp (Tablas 1-3, modelo 1), transcritos en el documento de
investigacion, a varias velocidades y con tolerancia. Ademas, comprobaciones
cualitativas: weave inestable a baja `u`, wobble de frecuencia casi constante,
capsize levemente divergente en un rango intermedio. Los juegos de parametros
GP y MX (de literatura) se fijan por regresion, sin verdad externa.

### 3.6 Unidades

Sharp usa unidades imperiales (slug, ft, lb). La implementacion trabaja en SI;
la conversion de sus parametros esta en el documento de investigacion. `u` en
m/s internamente; la CLI y los plots pueden mostrar km/h.

## 4. Pendiente (por trasladar del libro)

- [ ] Indice de maniobrabilidad y par de vuelco en curva estacionaria.
- [ ] Cinematica del tren trasero: anti-squat, variacion de la distancia entre
      ejes con el recorrido, efecto de la cadena.
- [ ] Momentos de inercia del conjunto para los indices cuasi-estaticos
      (sustituir el proxy `m * h^2`); el modelo de estabilidad ya usa inercias
      explicitas.

## 5. Sobre los indices heuristicos actuales

`agility` y `stability` en `dynamics/steady.py` son formulas ad-hoc para tener
una funcion objetivo que corra de extremo a extremo. `stability` se sustituira
por el modelo lineal de la seccion 3 (margen de amortiguamiento de weave y
wobble, y velocidad de divergencia de capsize). Mientras tanto, los resultados
de la optimizacion solo tienen valor cualitativo.
