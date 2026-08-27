# MotoDynamics

Modelo de optimizacion de la geometria de motocicletas de competicion. A partir
de un conjunto de parametros de chasis y neumaticos, busca la geometria que
mejor se ajusta a los objetivos de una disciplina concreta: circuito (estilo
MotoGP, abreviado `gp`) o motocross (`mx`).

## Estado actual

Version 0.1.0 - esqueleto funcional de extremo a extremo.

Funciona hoy:

- Modelo parametrico de geometria (`MotorcycleGeometry`) con calculo de avance
  (trail) y reparto de carga estatico.
- Metricas de comportamiento cuasi-estatico: limites de aceleracion (caballito)
  y frenada (stoppie) con formulas fisicas; indices de agilidad y estabilidad
  **heuristicos y provisionales**.
- Definicion de disciplinas por YAML (`configs/gp.yaml`, `configs/mx.yaml`):
  parametros fijos, parametros libres con limites y pesos de los objetivos.
- Optimizador de suma ponderada con `scipy.optimize.differential_evolution`.
- CLI: `motodynamics gp`, `motodynamics mx`.
- Tests (`pytest`) y linter (`ruff`) pasando.

En progreso / pendiente:

- Sustituir los indices heuristicos de agilidad y estabilidad por modelos con
  respaldo teorico (estabilidad lineal de weave/wobble/capsize, indices de
  maniobrabilidad en curva). Ver [docs/theory.md](docs/theory.md).
- Cinematica del tren trasero (anti-squat, efecto cadena) y modelo de neumatico.
- Momentos de inercia reales del conjunto (ahora se aproxima por `m * h^2`).
- Paso a optimizacion multiobjetivo con frente de Pareto cuando los objetivos
  en conflicto esten bien definidos.

Con el modelo actual, al ser los objetivos casi lineales en los parametros, el
optimizador tiende a llevar las variables a los limites del rango. Los
resultados solo tienen valor cualitativo hasta que se incorpore la fisica de
`docs/theory.md`.

## Arquitectura

```
src/motodynamics/
  geometry/frame.py        MotorcycleGeometry: parametros y magnitudes derivadas
  dynamics/steady.py       metricas de comportamiento (evaluate_handling)
  disciplines/spec.py      DisciplineSpec y carga de configs/<nombre>.yaml
  optimization/problem.py  optimize_geometry: suma ponderada + differential_evolution
  io/config.py             carga de YAML
  cli.py                   punto de entrada de linea de comandos
configs/                   definicion de cada disciplina (gp, mx)
tests/                     pruebas de geometria y de optimizacion
docs/theory.md             ecuaciones implementadas y pendientes (base: Cossalter)
notebooks/                 exploracion interactiva
```

Flujo: `load_discipline` lee el YAML -> `DisciplineSpec` -> `optimize_geometry`
explora los parametros libres, construye una `MotorcycleGeometry` en cada
evaluacion, la pasa por `evaluate_handling` y puntua con los pesos de la
disciplina.

## Requisitos

- Python >= 3.11
- numpy, scipy, pyyaml (runtime); pytest, ruff (desarrollo)

## Instalacion

```bash
python -m venv .venv
# Windows PowerShell:  .venv\Scripts\Activate.ps1
# bash:                source .venv/bin/activate
pip install -e ".[dev]"
```

## Uso

```bash
motodynamics gp                 # optimiza la geometria para circuito
motodynamics mx --seed 3        # motocross, semilla del optimizador
motodynamics gp --json          # salida en JSON
```

Para definir una disciplina nueva, copia `configs/gp.yaml`, ajusta parametros
fijos, limites y pesos, y ejecuta `motodynamics <nombre>`.

## Tests

```bash
pytest -q
ruff check .
```

## Decisiones de diseno

- **Layout `src/`** y paquete instalable: los tests corren contra el paquete
  instalado, no contra el arbol de fuentes.
- **`MotorcycleGeometry` inmutable** (`frozen dataclass`): las magnitudes
  derivadas son propiedades, nunca quedan desincronizadas de los parametros.
- **Disciplina como dato (YAML), no como codigo**: añadir una categoria no
  requiere tocar Python.
- **Suma ponderada como primer objetivo**: simple y suficiente para el
  esqueleto; se migrara a multiobjetivo cuando aporte.
- El PDF del libro de referencia **no se versiona** (copyright); solo se
  registran en `docs/theory.md` las ecuaciones propias que se implementan.

## Limitaciones conocidas

Ver "Estado actual". El nucleo fisico todavia es un placeholder: las
conclusiones de setup no deben tomarse como validas hasta completar
`docs/theory.md`.
