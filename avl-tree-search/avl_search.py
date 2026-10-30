"""
avl_search.py
Module Four Assignment - Part 2: Search Algorithm

Loads a data set into the AVL tree from avl_tree.py and searches it with a
binary search. For each word searched, the program reports:
    - whether the word was found
    - how many times the word appears in the data set
    - how many AVL tree nodes were accessed to find it, and which ones
    - a linear scan of the raw data used to double-check the result

Usage:
    python avl_search.py                          (prompts for a file and a word)
    python avl_search.py <data_file> <word> [<word> ...]
"""

import math
import sys
import time

from avl_tree import AVLTree


def load_words(file_path):
    """
    Read a data set where every record looks like "sequence|word".
    The header line is skipped and the sequence number is discarded, so only
    the word in the data field is returned.
    """
    words = []
    with open(file_path, "r", encoding="utf-8") as file:
        next(file, None)  # skip the "sequence|data" header
        for line_number, line in enumerate(file, start=2):
            line = line.strip()
            if not line:
                continue
            parts = line.split("|", 1)
            if len(parts) != 2 or not parts[1]:
                print(f"  Skipping malformed record on line {line_number}: {line!r}")
                continue
            words.append(parts[1])  # keep the word, discard the sequence number
    return words


def build_tree(words):
    """Insert every word into a new AVL tree and return the tree."""
    tree = AVLTree()
    for word in words:
        tree.insert(word)
    return tree


def linear_count(words, target):
    """
    Independent check: scan the raw list one word at a time.
    Returns (occurrences, comparisons needed to reach the first match).
    """
    occurrences = 0
    first_match_at = None
    for index, word in enumerate(words):
        if word == target:
            occurrences += 1
            if first_match_at is None:
                first_match_at = index + 1
    comparisons = first_match_at if first_match_at is not None else len(words)
    return occurrences, comparisons


def print_tree_summary(tree, words, load_seconds):
    n = tree.size
    print(f"  Records loaded:          {len(words):,}")
    print(f"  Distinct words (nodes):  {n:,}")
    print(f"  Duplicate records:       {len(words) - n:,}")
    print(f"  Rotations performed:     {tree.rotations:,}")
    print(f"  Tree height:             {tree.height()}")
    print(f"  log2(n):                 {math.log2(n):.2f}")
    print(f"  AVL height limit:        {1.44 * math.log2(n + 2) - 0.328:.2f}  (1.44 log2(n+2) - 0.328)")
    print(f"  Valid AVL tree:          {tree.validate()}")
    print(f"  Load time:               {load_seconds:.3f} seconds")

    sorted_words = tree.inorder()
    print(f"  In-order (first 5):      {sorted_words[:5]}")
    print(f"  In-order is sorted:      {all(sorted_words[i] < sorted_words[i + 1] for i in range(len(sorted_words) - 1))}")
    print(f"  Pre-order (first 5):     {tree.preorder()[:5]}")
    print(f"  Post-order (last 3):     {tree.postorder()[-3:]}")
    print("  Level-order (top 3 levels):")
    for depth, level in enumerate(tree.level_order(max_levels=3)):
        print(f"    Level {depth}: {level}")


def report_search(tree, words, target):
    print(f"\n  Searching for '{target}'")
    start = time.perf_counter()
    node, path = tree.search(target)
    elapsed_us = (time.perf_counter() - start) * 1_000_000

    occurrences, linear_comparisons = linear_count(words, target)

    if node is not None:
        print(f"    Result:                FOUND")
        print(f"    Times in data set:     {node.count}"
              f"  ({'appears more than once' if node.count > 1 else 'appears only once'})")
    else:
        print(f"    Result:                NOT FOUND")
    print(f"    AVL nodes accessed:    {len(path)}  (tree height {tree.height()})")
    print(f"    Search path:           {' -> '.join(path)}")
    print(f"    Search time:           {elapsed_us:.1f} microseconds")
    print(f"    Linear scan check:     {occurrences} occurrence(s), "
          f"{linear_comparisons:,} comparisons to reach it")
    tree_count = node.count if node is not None else 0
    print(f"    Results agree:         {tree_count == occurrences}")


def run(file_path, targets):
    print("=" * 72)
    print(f"Data set: {file_path}")
    print("=" * 72)

    try:
        start = time.perf_counter()
        words = load_words(file_path)
        tree = build_tree(words)
        load_seconds = time.perf_counter() - start
    except FileNotFoundError:
        print(f"  Error: '{file_path}' was not found.")
        return
    except UnicodeDecodeError:
        print(f"  Error: '{file_path}' is not a readable text file.")
        return

    if tree.size == 0:
        print("  The data set contained no words.")
        return

    print_tree_summary(tree, words, load_seconds)
    for target in targets:
        report_search(tree, words, target)
    print()


def main():
    if len(sys.argv) >= 3:
        run(sys.argv[1], sys.argv[2:])
        return

    file_path = sys.argv[1] if len(sys.argv) == 2 else input("Data set file: ").strip()
    word = input("Word to search for: ").strip()
    run(file_path, [word])


if __name__ == "__main__":
    main()
