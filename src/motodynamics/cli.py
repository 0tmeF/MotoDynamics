"""Interfaz de linea de comandos.

Uso:
    motodynamics gp
    motodynamics mx --seed 3
"""

from __future__ import annotations

import argparse
import json

from motodynamics.disciplines.spec import load_discipline
from motodynamics.optimization.problem import optimize_geometry


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="motodynamics", description=__doc__)
    parser.add_argument("discipline", help="nombre de la disciplina (configs/<nombre>.yaml)")
    parser.add_argument("--seed", type=int, default=0, help="semilla del optimizador")
    parser.add_argument("--json", action="store_true", help="salida en JSON")
    args = parser.parse_args(argv)

    spec = load_discipline(args.discipline)
    result = optimize_geometry(spec, seed=args.seed)

    payload = {
        "discipline": result.discipline,
        "success": result.success,
        "score": result.score,
        "n_eval": result.n_eval,
        "free_values": result.free_values,
        "metrics": result.metrics,
        "geometry": result.geometry.summary(),
    }

    if args.json:
        print(json.dumps(payload, indent=2, ensure_ascii=False))
    else:
        print(f"Disciplina: {payload['discipline']}  (score={payload['score']:.4f})")
        print("\nParametros optimizados:")
        for k, v in payload["free_values"].items():
            print(f"  {k:18s} {v:10.4f}")
        print("\nMetricas:")
        for k, v in payload["metrics"].items():
            print(f"  {k:18s} {v:10.4f}")
    return 0 if result.success else 1


if __name__ == "__main__":
    raise SystemExit(main())
