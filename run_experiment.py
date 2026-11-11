"""Doubling experiment: python run_experiment.py (writes results/*.csv and results/*.png)"""
from p3_env import *
from starter import *

SIZES = [62500, 125000, 250000, 500000, 1000000]
DFS_QUERIES, INDEX_QUERIES, RECOMPUTE_UPDATES, ANCESTOR_UPDATES = 10, 1000, 5, 1000
if QUICK:
    SIZES, DFS_QUERIES, RECOMPUTE_UPDATES, ANCESTOR_UPDATES = [4000, 8000], 5, 3, 100


def per_op(fn, items, repeat=3):
    """Average seconds per item over `repeat` runs of fn on every item."""
    total = 0.0
    for _ in range(repeat):
        t0 = time.perf_counter()
        for x in items:
            fn(x)
        total += (time.perf_counter() - t0) / len(items)
    return total / repeat


def experiment():
    rows, prev = [], {}
    print(f"{'files':>9} | {'DFS search':>14} | {'index search':>14} | {'recompute all':>14} | {'ancestors only':>14}   (per operation)")
    for n in SIZES:
        files = generate_files(n, seed=n)
        root = build_tree(files)
        index = build_index(root)
        compute_sizes(root)
        queries = random_queries(files, INDEX_QUERIES, seed=n)
        res = {"DFS search": per_op(lambda q: find_dfs(root, q), queries[:DFS_QUERIES], repeat=1),
               "index search": per_op(lambda q: find_indexed(index, q), queries)}
        ops = random_updates(files, 2 * (RECOMPUTE_UPDATES + ANCESTOR_UPDATES), seed=n)

        def do(op):
            if op[0] == "add":
                add_file(root, index, op[1], op[2])
            else:
                delete_file(root, index, op[1])

        def do_and_recompute(op):
            do(op)
            compute_sizes(root)

        a, b = 2 * RECOMPUTE_UPDATES, 2 * RECOMPUTE_UPDATES + 2 * ANCESTOR_UPDATES
        res["recompute all"] = per_op(do_and_recompute, ops[:a], repeat=1)
        res["ancestors only"] = per_op(do, ops[a:b], repeat=1)
        cells = []
        for name, t in res.items():
            ratio = f"x{t / prev[name]:.1f}" if name in prev else ""
            prev[name] = t
            rows.append({"n": n, "method": name, "seconds": t})
            cells.append(f"{t * 1e6:>9.1f} us {ratio:>5}" if t < 0.01 else f"{t * 1e3:>9.1f} ms {ratio:>5}")
        print(f"{n:>9} | " + " | ".join(cells), flush=True)
    return rows


try:
    rows = experiment()
    save_csv(rows, "results/experiment.csv")
    plot_doubling(rows, "Project 3: time per operation", "results/experiment.png")
except NotImplementedError:
    print("⏳ Finish Tasks 1-3 first.")
