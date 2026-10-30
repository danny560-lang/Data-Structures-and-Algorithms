"""
Module 3-1 Activity: Heap Sort over the activity data sets

Reads each pipe-delimited data set (key|data-a|data-b|validation) into a list
of Record objects, sorts the list in place with a hand-written heap sort, and
verifies the result. After sorting, records can be looked up by key with a
binary search.

Assumptions (documented in the report):
  * The file is pipe-delimited with a header row: key|data-a|data-b|validation.
  * Records are sorted ascending by the numeric key (compared as an int,
    not as text).
  * Keys are not unique, so ties are broken by data-a, then data-b
    (case-sensitive, Unicode code-point order). This makes the output
    deterministic even though heap sort is not a stable sort.
  * The validation code is the SHA-256 hash of "key|data-a|data-b". Records
    whose hash does not match are reported but still sorted.
  * Blank words (e.g. "Guiana|") are legal values and are kept.

Usage:
  python heap_sort_app.py                      sort every data set in ./data
  python heap_sort_app.py FILE [FILE ...]      sort specific files
  python heap_sort_app.py --search 712811946   also look up keys after sorting
  python heap_sort_app.py --out sorted         also write sorted copies
"""

import argparse
import hashlib
import os
import sys
import time
from bisect import bisect_left
from typing import List, NamedTuple

DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")
HEADER = "key|data-a|data-b|validation"


class Record(NamedTuple):
    """One row of the data set.

    A NamedTuple is an immutable tuple with named fields. Because tuples
    compare field by field, `a < b` orders records by key first, then data_a,
    then data_b, which is exactly the sort order we want.
    """
    key: int
    data_a: str
    data_b: str
    validation: str

    def is_valid(self) -> bool:
        text = f"{self.key}|{self.data_a}|{self.data_b}"
        return hashlib.sha256(text.encode("utf-8")).hexdigest() == self.validation


# ---------------------------------------------------------------------------
# Reading the data set into the data structure (a Python list of Records)
# ---------------------------------------------------------------------------
def load_records(path: str) -> List[Record]:
    records: List[Record] = []
    with open(path, encoding="utf-8") as f:
        header = f.readline().strip()
        if header != HEADER:
            raise ValueError(f"{path}: unexpected header {header!r}")
        for line_no, line in enumerate(f, start=2):
            line = line.rstrip("\r\n")
            if not line:
                continue
            parts = line.split("|")
            if len(parts) != 4 or not parts[0].isdigit():
                print(f"  skipping malformed line {line_no}: {line[:60]!r}")
                continue
            records.append(Record(int(parts[0]), parts[1], parts[2], parts[3]))
    return records


# ---------------------------------------------------------------------------
# Heap sort (in place, ascending)
# ---------------------------------------------------------------------------
class SortStats:
    def __init__(self) -> None:
        self.comparisons = 0
        self.moves = 0


def _sift_down(a: list, start: int, end: int, stats: SortStats) -> None:
    """Restore the max-heap property for the subtree rooted at `start`.

    Only indexes < end belong to the heap. Instead of swapping at every
    level, the root item is held aside ("the hole" technique) and larger
    children are moved up until the item's correct position is found.
    """
    item = a[start]
    pos = start
    child = 2 * pos + 1                       # left child
    while child < end:
        right = child + 1
        if right < end:
            stats.comparisons += 1
            if a[child] < a[right]:           # pick the larger child
                child = right
        stats.comparisons += 1
        if not item < a[child]:               # item >= larger child: done
            break
        a[pos] = a[child]                     # move child up into the hole
        stats.moves += 1
        pos = child
        child = 2 * pos + 1
    a[pos] = item
    stats.moves += 1


def heap_sort(a: list) -> SortStats:
    """Sort list `a` in place in ascending order. Returns operation counts."""
    stats = SortStats()
    n = len(a)
    # Phase 1: build a max-heap bottom-up (Floyd's method), O(n).
    for start in range(n // 2 - 1, -1, -1):
        _sift_down(a, start, n, stats)
    # Phase 2: repeatedly move the max (a[0]) to the end of the unsorted
    # region and re-heapify the shrunken heap, O(n log n).
    for end in range(n - 1, 0, -1):
        a[0], a[end] = a[end], a[0]
        stats.moves += 2
        _sift_down(a, 0, end, stats)
    return stats


def is_sorted(a: list) -> bool:
    return all(a[i] <= a[i + 1] for i in range(len(a) - 1))


# ---------------------------------------------------------------------------
# Binary search on the sorted list (supporting feature)
# ---------------------------------------------------------------------------
def find_by_key(sorted_records: List[Record], key: int) -> List[Record]:
    """Return every record with this key, in O(log n) + number of matches.

    bisect_left/bisect_right are the standard library's binary search. A
    1-tuple (key,) sorts before any full record with that key, and
    (key + 1,) sorts before any record with the next key, so the slice
    between them is exactly the records whose key matches.
    """
    lo = bisect_left(sorted_records, (key,))
    hi = bisect_left(sorted_records, (key + 1,), lo)
    return sorted_records[lo:hi]


# ---------------------------------------------------------------------------
# Driver
# ---------------------------------------------------------------------------
def process(path: str, search_keys: List[int], out_dir: str) -> None:
    name = os.path.basename(path)
    print(f"\n=== {name} ===")

    t0 = time.perf_counter()
    records = load_records(path)
    load_s = time.perf_counter() - t0

    invalid = [r for r in records if not r.is_valid()]
    dup_keys = len(records) - len({r.key for r in records})
    blanks = sum(1 for r in records if not r.data_a or not r.data_b)
    print(f"  loaded {len(records):,} records in {load_s:.3f}s  "
          f"(invalid hashes: {len(invalid)}, duplicate keys: {dup_keys}, "
          f"blank words: {blanks})")

    t0 = time.perf_counter()
    stats = heap_sort(records)
    sort_s = time.perf_counter() - t0
    print(f"  heap sort: {sort_s:.3f}s, {stats.comparisons:,} comparisons, "
          f"{stats.moves:,} moves")
    print(f"  verified sorted: {is_sorted(records)}")

    print("  first 3:")
    for r in records[:3]:
        print(f"    {r.key}  {r.data_a:<18} {r.data_b:<18} {r.validation[:12]}...")
    print("  last 3:")
    for r in records[-3:]:
        print(f"    {r.key}  {r.data_a:<18} {r.data_b:<18} {r.validation[:12]}...")

    for key in search_keys:
        hits = find_by_key(records, key)
        if hits:
            shown = ", ".join(f"{h.data_a}/{h.data_b}" for h in hits)
            print(f"  search {key}: {len(hits)} match(es) -> {shown}")
        else:
            print(f"  search {key}: not found")

    if out_dir:
        os.makedirs(out_dir, exist_ok=True)
        out_path = os.path.join(out_dir, name.replace(".csv", " (sorted).csv"))
        with open(out_path, "w", encoding="utf-8", newline="\n") as f:
            f.write(HEADER + "\n")
            for r in records:
                f.write(f"{r.key}|{r.data_a}|{r.data_b}|{r.validation}\n")
        print(f"  wrote {out_path}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Heap sort the activity data sets.")
    parser.add_argument("files", nargs="*", help="data set files (default: every .csv in ./data)")
    parser.add_argument("--search", type=int, nargs="*", default=[], metavar="KEY",
                        help="keys to look up with binary search after sorting")
    parser.add_argument("--out", default="", metavar="DIR",
                        help="write a sorted copy of each data set into DIR")
    args = parser.parse_args()

    files = args.files or sorted(
        os.path.join(DATA_DIR, f) for f in os.listdir(DATA_DIR) if f.endswith(".csv"))
    if not files:
        sys.exit("No data sets found.")
    for path in files:
        process(path, args.search, args.out)


if __name__ == "__main__":
    main()
