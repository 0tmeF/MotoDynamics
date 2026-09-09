# MotoDynamics — instrucciones para la IA

Complementa el `~/.claude/CLAUDE.md` global (comunicación, verificación,
commits, seguridad, control de versiones). Ante conflicto, este archivo manda
en lo específico del proyecto.

Encuadre de origen en `Cero/intake/motodynamics2.md`: la idea "MotoDynamics2"
se resolvió como evolución de este repo, no como proyecto nuevo. Cero se
retiró; este proyecto es autónomo.

## Propósito

Modelo de análisis y optimización de la geometría y la dinámica de
motocicletas de competición. A partir de parámetros de chasis, neumáticos y
piloto, evalúa el comportamiento (estabilidad, agilidad, límites de tracción y
frenada) y busca la geometría que mejor sirve a los objetivos de una
disciplina: circuito (`gp`) o motocross (`mx`).

- **Un solo desarrollador.** Carlos lo construye y lo prueba. Entre una
  solución correcta y lenta y otra casi tan correcta que le ahorra revisión,
  gana la segunda.
- **El núcleo de valor es la física con respaldo teórico** (`docs/theory.md`,
  base: Cossalter, *Motorcycle Dynamics*). El optimizador, la CLI y los YAML
  de disciplina son andamiaje: existen para ejercitar y explotar esa física.
  Un índice heurístico sin derivación es deuda, no producto.

## Alcance

- **Sí:**
  - Geometría paramétrica de la moto y magnitudes derivadas (avance, reparto
    de carga, cinemática del tren trasero).
  - Métricas de comportamiento cuasi-estático y de estabilidad lineal
    (capsize, weave, wobble).
  - Definición de disciplinas como dato (`configs/<nombre>.yaml`) y
    optimización de los parámetros libres.
  - Análisis de telemetría propia cuando entre en el alcance (ingesta y
    contraste de datos reales contra el modelo).
- **No:**
  - Simulación transitoria multicuerpo de alta fidelidad ni motor de
    descriptores. Si se pide, es otro proyecto: vuelta a Cero.
  - Generación de código de producto para terceros.
  - Versionar el PDF del libro de referencia u otro material con copyright:
    solo se registran en `docs/theory.md` las ecuaciones propias implementadas.

## Cómo una regla se gana su sitio

Toda regla dice qué fallo concreto evita y qué cuesta. Una regla que nunca ha
evitado un fallo real se borra. Si una regla y el Propósito discrepan, manda
el Propósito, y la regla se corrige aquí en el mismo commit.

## Convenciones

- **Python >= 3.11**, layout `src/`, paquete instalable (`pip install -e .`).
  Los tests corren contra el paquete instalado.
- **Unidades SI en todo el núcleo**: metros, radianes, kilogramos, newton,
  segundos. Los grados solo aparecen en I/O (YAML, CLI, plots) y se convierten
  en el borde.
- **`MotorcycleGeometry` es inmutable** (`frozen dataclass`): las magnitudes
  derivadas son propiedades, nunca se desincronizan. Para variar un parámetro,
  `g.with_(...)`.
- **Disciplina como dato, no como código**: añadir una categoría es un YAML
  nuevo, no tocar Python.
- **Toda fórmula del núcleo enlaza a su sección de `docs/theory.md`.** Si la
  ecuación no está documentada, documentarla es parte del cambio.
- Nomenclatura de símbolos siguiendo a Cossalter cuando exista (`p`, `epsilon`,
  `a_n`, `N_f`...).
- Idioma del repo: español en documentación y comentarios; nombres de código
  en inglés (`wheelbase`, `evaluate_handling`).

## Verificación

Runner del proyecto:

```bash
pytest -q
ruff check .
```

- Cubre hoy: fórmula del avance, reparto de carga, copia inmutable, y el
  extremo a extremo del optimizador (que converge y respeta límites).
- Falta: tests de los índices de estabilidad lineal (pendientes de
  implementar) y de la cinemática del basculante.
- Regla global: todo cambio de lógica trae su verificación automática en este
  runner antes de considerarse terminado. Para física nueva, el test fija el
  resultado esperado con un caso analítico o un valor de referencia citado, no
  con inspección visual.

## Flujo de trabajo

- Cambios pequeños y revisables.
- Física nueva: primero la sección en `docs/theory.md` (ecuación y decisiones
  de modelado), luego el código que la implementa, luego el test que la fija.
- Tras tocar lógica: correr el runner y reportar la salida real.
- Commit de checkpoint al cerrar cada paso, con push automático en la rama
  actual (regla global). Sigue pidiendo OK para `push --force`, historia
  reescrita o un remoto nuevo.
- Rama antes para un cambio amplio.
