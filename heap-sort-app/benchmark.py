"""
Benchmarks for the report: how heap sort scales with input size and how it
reacts to differently structured input. Uses the same heap_sort() and
load_records() as the application.

Usage: python benchmark.py
"""

import math
import os
import random
import time
import tracemalloc

from heap_sort_app import DATA_DIR, Record, heap_sort, is_sorted, load_records


def timed_sort(records):
    data = list(records)
    t0 = time.perf_counter()
    stats = heap_sort(data)
    elapsed = time.perf_counter() - t0
    assert is_sorted(data)
    return elapsed, stats


def builtin_time(records):
    data = list(records)
    t0 = time.perf_counter()
    data.sort()
    return time.perf_counter() - t0


def main():
    files = sorted(os.path.join(DATA_DIR, f) for f in os.listdir(DATA_DIR) if f.endswith(".csv"))
    sets = [load_records(f) for f in files]
    big = [r for s in sets[1:] for r in s]          # data sets 2-5: 400,000 records
    random.seed(1)
    random.shuffle(big)

    # 1. Scaling with input size ---------------------------------------
    print("=== 1. Scaling with input size (random order) ===")
    print(f"{'n':>9} {'heap sort s':>12} {'comparisons':>13} {'comp/(n log2 n)':>16} {'list.sort() s':>14}")
    for n in (1_000, 12_500, 25_000, 50_000, 100_000, 200_000, 400_000):
        sample = big[:n]
        t, st = timed_sort(sample)
        print(f"{n:>9,} {t:>12.3f} {st.comparisons:>13,} "
              f"{st.comparisons / (n * math.log2(n)):>16.3f} {builtin_time(sample):>14.4f}")

    # 2. Effect of input structure --------------------------------------
    base = sets[1]                                  # data set 2, 100,000 records
    few_keys = [Record(r.key % 10, r.data_a, r.data_b, r.validation) for r in base]
    one_value = [base[0]] * len(base)
    cases = [
        ("random (as given)", base),
        ("already ascending", sorted(base)),
        ("descending", sorted(base, reverse=True)),
        ("only 10 distinct keys", few_keys),
        ("all records identical", one_value),
    ]
    print("\n=== 2. Effect of input structure (n = 100,000) ===")
    print(f"{'input':<24} {'heap sort s':>12} {'comparisons':>13} {'moves':>11} {'list.sort() s':>14}")
    for label, data in cases:
        t, st = timed_sort(data)
        print(f"{label:<24} {t:>12.3f} {st.comparisons:>13,} {st.moves:>11,} {builtin_time(data):>14.4f}")

    # 3. Memory -----------------------------------------------------------
    print("\n=== 3. Memory (data set 2) ===")
    tracemalloc.start()
    records = load_records(files[1])
    loaded, _ = tracemalloc.get_traced_memory()
    tracemalloc.reset_peak()
    heap_sort(records)
    _, sort_peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    print(f"  list of {len(records):,} Records: {loaded / 1e6:.1f} MB "
          f"(~{loaded / len(records):.0f} bytes per record)")
    print(f"  extra memory used while heap sorting: {(sort_peak - loaded) / 1e3:.1f} KB")


if __name__ == "__main__":
    main()
