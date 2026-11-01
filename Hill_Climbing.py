"""
RPG Loadout Optimizer - Steepest-Ascent Hill Climbing (multi-skenario)
Score = ATK_total x (1 + CR_total x CD_total)
1 item per slot: Flower, Plume, Sands, Goblet, Circlet
"""
import random
import time
import tracemalloc
import statistics

N_TRIALS = 30
SEED = 42
SLOTS = ["Flower", "Plume", "Sands", "Goblet", "Circlet"]

# (ID, Slot, ATK, CritRate %, CritDMG %)
BASE_10 = [
    ("F1", "Flower", 10, 5, 10), ("F2", "Flower", 20, 2, 5),
    ("P1", "Plume", 15, 3, 10),  ("P2", "Plume", 25, 5, 5),
    ("S1", "Sands", 20, 5, 10),  ("S2", "Sands", 30, 2, 5),
    ("G1", "Goblet", 15, 4, 15), ("G2", "Goblet", 25, 6, 5),
    ("C1", "Circlet", 10, 5, 20), ("C2", "Circlet", 20, 10, 5),
]
EXTRA_3RD = [
    ("F3", "Flower", 5, 8, 15),  ("P3", "Plume", 10, 7, 20),
    ("S3", "Sands", 10, 8, 15),  ("G3", "Goblet", 10, 9, 20),
    ("C3", "Circlet", 15, 3, 25),
]
EXTRA_4TH = [
    ("F4", "Flower", 25, 7, 20),  ("P4", "Plume", 30, 8, 15),
    ("S4", "Sands", 35, 6, 20),   ("G4", "Goblet", 30, 10, 25),
    ("C4", "Circlet", 25, 12, 20),
]

SCENARIOS = [
    ("Skenario 1 - 15 Equipment", BASE_10 + EXTRA_3RD),
    ("Skenario 2 - 10 Equipment", BASE_10),
    ("Skenario 3 - 20 Equipment", BASE_10 + EXTRA_3RD + EXTRA_4TH),
]


class Counter:
    evals = 0


def totals(loadout):
    atk = sum(e[2] for e in loadout)
    cr = sum(e[3] for e in loadout)
    cd = sum(e[4] for e in loadout)
    return atk, cr, cd


def fitness(loadout):
    Counter.evals += 1
    atk, cr, cd = totals(loadout)
    return atk * (1 + (cr / 100) * (cd / 100))


def hill_climbing(by_slot):
    """Steepest-ascent: pilih tetangga terbaik, berhenti jika tidak ada yang lebih baik."""
    current = [random.choice(by_slot[s]) for s in SLOTS]
    current_score = fitness(current)
    iterations = 0
    while True:
        best_n, best_s = None, current_score
        for idx, s in enumerate(SLOTS):
            for cand in by_slot[s]:
                if cand is current[idx]:
                    continue
                n = current.copy()
                n[idx] = cand
                sc = fitness(n)
                if sc > best_s:
                    best_n, best_s = n, sc
        if best_n is None:      # local optimum
            break
        current, current_score = best_n, best_s
        iterations += 1
    return current, current_score, iterations


def fmt(x):
    return f"{round(x, 4):g}"


def run_scenario(name, equipment):
    by_slot = {s: [e for e in equipment if e[1] == s] for s in SLOTS}
    scores, iters, evals, mems = [], [], [], []
    best_sol, best_score = None, -1

    t_start = time.perf_counter()
    for _ in range(N_TRIALS):
        Counter.evals = 0
        tracemalloc.start()
        sol, sc, it = hill_climbing(by_slot)
        _, peak = tracemalloc.get_traced_memory()
        tracemalloc.stop()
        scores.append(sc); iters.append(it); evals.append(Counter.evals); mems.append(peak)
        if sc > best_score:
            best_sol, best_score = sol, sc
    elapsed = time.perf_counter() - t_start

    atk, cr, cd = totals(best_sol)
    print("=" * 55)
    print(f"SKENARIO: {name}")
    print("=" * 55)
    print("\nKombinasi Equipment Terbaik:")
    for e in best_sol:
        print(f"{e[1]:<8} | {e[0]:<3} | ATK: {e[2]:>2} | CR: {e[3]:>2}% | CD: {e[4]:>2}%")
    print(f"\nTotal ATK       : {atk}")
    print(f"Total Crit Rate : {cr}%")
    print(f"Total Crit DMG  : {cd}%")
    print(f"Best Score      : {fmt(max(scores))}")
    print(f"Average Score   : {fmt(statistics.mean(scores))}")
    print(f"Worst Score     : {fmt(min(scores))}")
    print(f"Execution Time  : {elapsed:.6f} seconds")
    print(f"Average Iterasi : {statistics.mean(iters):.2f}")
    print(f"Average Evaluasi: {statistics.mean(evals):.1f}")
    print(f"Peak Memory     : {statistics.mean(mems)/1024:.2f} KiB")
    print(f"Std Dev Score   : {statistics.pstdev(scores):.4f}")
    print()
    return dict(name=name, best=max(scores), avg=statistics.mean(scores),
                worst=min(scores), time=elapsed, iters=statistics.mean(iters),
                evals=statistics.mean(evals), std=statistics.pstdev(scores))


def main():
    random.seed(SEED)
    results = [run_scenario(n, eq) for n, eq in SCENARIOS]
    print("=" * 65)
    print("PERBANDINGAN HASIL PENGUJIAN")
    print("=" * 65)
    print(f"{'Skenario':<30}{'Best Score':>12}{'Average Score':>15}{'Waktu (s)':>10}")
    for r in results:
        print(f"{r['name']:<30}{r['best']:>12.4f}{r['avg']:>15.4f}{r['time']:>10.6f}")
    print()
    print(f"{'Skenario':<30}{'Worst':>10}{'Iterasi':>9}{'Evaluasi':>10}{'StdDev':>9}")
    for r in results:
        print(f"{r['name']:<30}{r['worst']:>10.4f}{r['iters']:>9.2f}{r['evals']:>10.1f}{r['std']:>9.4f}")


if __name__ == "__main__":
    main()