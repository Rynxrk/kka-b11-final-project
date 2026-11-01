this file code is made by ai
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
    """Score = ATK_total x (1 + CR_total x CD_total)"""
    Counter.evals += 1
    atk, cr, cd = totals(loadout)
    return atk * (1 + (cr / 100) * (cd / 100))


def random_solution(by_slot):
    return [random.choice(by_slot[s]) for s in SLOTS]


# ====== PARAMETER GA ======
POP_SIZE = 20
GENERATIONS = 50
CROSSOVER_RATE = 0.9
MUTATION_RATE = 0.1     # peluang mutasi per gen
TOURNAMENT_K = 3
ELITISM = 1             # jumlah individu terbaik yang langsung diteruskan


def tournament(pop, scores):
    contenders = random.sample(range(len(pop)), TOURNAMENT_K)
    winner = max(contenders, key=lambda i: scores[i])
    return pop[winner]


def crossover(p1, p2):
    """Uniform crossover: tiap slot diambil dari salah satu orang tua."""
    if random.random() > CROSSOVER_RATE:
        return p1.copy(), p2.copy()
    c1, c2 = [], []
    for g1, g2 in zip(p1, p2):
        if random.random() < 0.5:
            c1.append(g1); c2.append(g2)
        else:
            c1.append(g2); c2.append(g1)
    return c1, c2


def mutate(ind, by_slot):
    for idx, s in enumerate(SLOTS):
        if random.random() < MUTATION_RATE:
            ind[idx] = random.choice(by_slot[s])
    return ind


def genetic_algorithm(by_slot):
    pop = [random_solution(by_slot) for _ in range(POP_SIZE)]
    scores = [fitness(ind) for ind in pop]
    best_i = max(range(POP_SIZE), key=lambda i: scores[i])
    best, best_score = pop[best_i].copy(), scores[best_i]

    for _ in range(GENERATIONS):
        ranked = sorted(range(POP_SIZE), key=lambda i: scores[i], reverse=True)
        new_pop = [pop[i].copy() for i in ranked[:ELITISM]]
        while len(new_pop) < POP_SIZE:
            p1, p2 = tournament(pop, scores), tournament(pop, scores)
            c1, c2 = crossover(p1, p2)
            new_pop.append(mutate(c1, by_slot))
            if len(new_pop) < POP_SIZE:
                new_pop.append(mutate(c2, by_slot))
        pop = new_pop
        scores = [fitness(ind) for ind in pop]
        gi = max(range(POP_SIZE), key=lambda i: scores[i])
        if scores[gi] > best_score:
            best, best_score = pop[gi].copy(), scores[gi]
    return best, best_score, GENERATIONS



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
        sol, sc, it = genetic_algorithm(by_slot)
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
