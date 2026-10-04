"""
Benchmark de los tres algoritmos con scrambles de 1 a 19 movimientos.

Uso:
    python benchmark.py
    python benchmark.py --trials 5 --max-time 30 --max-states 1500000
    python benchmark.py --min 1 --max 12 --algos astar bidirectional
    python benchmark.py --mem          # mide pico de RAM (más lento)

Genera `resultados.csv` (una fila por corrida) y imprime una tabla
resumen por profundidad y algoritmo, lista para el reporte.
"""

import argparse
import csv
import gc
import random
import tracemalloc

from rubik import RubikCube, Axis, Direction
from search_algorithms import SearchAlgorithms

NAMES = {"astar": "A*", "gbf": "GBF", "bidirectional": "Bidirectional"}


def make_scramble(cube_moves, rng):
    """Cubo mezclado con `cube_moves` movimientos aleatorios sin
    cancelaciones triviales (nunca el mismo eje dos veces seguidas)."""
    cube = RubikCube()
    last_axis = None
    axes = list(Axis)
    for _ in range(cube_moves):
        axis = rng.choice([a for a in axes if a != last_axis])
        direction = rng.choice(list(Direction))
        times = rng.choice([1, 2])
        cube.turn(axis, direction, times, False)
        last_axis = axis
    return cube


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--min", type=int, default=1)
    parser.add_argument("--max", type=int, default=19)
    parser.add_argument("--trials", type=int, default=5)
    parser.add_argument("--max-time", type=float, default=30.0)
    parser.add_argument("--max-states", type=int, default=1_500_000)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--astar-weight", type=float, default=1.0)
    parser.add_argument(
        "--algos", nargs="+",
        default=["astar", "gbf", "bidirectional"],
        choices=["astar", "gbf", "bidirectional"]
    )
    parser.add_argument("--csv", default="resultados.csv")
    parser.add_argument("--mem", action="store_true")
    args = parser.parse_args()

    solver = SearchAlgorithms(
        max_states=args.max_states,
        max_time=args.max_time,
        astar_weight=args.astar_weight
    )
    rng = random.Random(args.seed)
    rows = []

    for depth in range(args.min, args.max + 1):
        for trial in range(args.trials):
            cube = make_scramble(depth, rng)
            for algo in args.algos:
                gc.collect()
                if args.mem:
                    tracemalloc.start()

                result = getattr(solver, algo)(cube)

                peak_mb = 0.0
                if args.mem:
                    peak_mb = tracemalloc.get_traced_memory()[1] / 1e6
                    tracemalloc.stop()

                valid = (
                    solver.verify_solution(cube, result.moves)
                    if result.success else False
                )
                rows.append({
                    "scramble": depth,
                    "trial": trial,
                    "algorithm": result.algorithm,
                    "success": int(result.success and valid),
                    "solution_len": len(result.moves) if result.success else "",
                    "expanded": result.explored_nodes,
                    "stored_states": result.stored_states,
                    "time_s": round(result.execution_time, 4),
                    "peak_mb": round(peak_mb, 1),
                    "message": result.message,
                })
                print(
                    f"[{depth:2d} movs | intento {trial + 1}] "
                    f"{result.algorithm:<14} "
                    f"{'OK ' if rows[-1]['success'] else 'FAIL'} "
                    f"{result.execution_time:7.2f}s "
                    f"exp={result.explored_nodes:>9,} "
                    f"mem={result.stored_states:>9,}",
                    flush=True
                )

    with open(args.csv, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)

    # ---------------- resumen para el reporte ----------------
    print("\n=== RESUMEN (promedios por profundidad y algoritmo) ===")
    header = (
        f"{'movs':>4} {'algoritmo':<14} {'éxito':>7} {'t prom(s)':>10} "
        f"{'expandidos':>11} {'estados':>10} {'long.sol':>9}"
    )
    print(header)
    print("-" * len(header))
    for depth in range(args.min, args.max + 1):
        for algo in args.algos:
            sel = [
                r for r in rows
                if r["scramble"] == depth and r["algorithm"] == NAMES[algo]
            ]
            if not sel:
                continue
            ok = [r for r in sel if r["success"]]
            avg = lambda key, data: (
                sum(r[key] for r in data) / len(data) if data else 0
            )
            sol = avg("solution_len", ok) if ok else float("nan")
            print(
                f"{depth:>4} {sel[0]['algorithm']:<14} "
                f"{len(ok):>3}/{len(sel):<3} "
                f"{avg('time_s', sel):>10.2f} "
                f"{avg('expanded', sel):>11,.0f} "
                f"{avg('stored_states', sel):>10,.0f} "
                f"{sol:>9.1f}"
            )

    print(f"\nDetalle guardado en {args.csv}")


if __name__ == "__main__":
    main()