"""
Module Four Activity: Recursion, Functional Programming, and Exception Handling
Data set: catalog.json (Deep Space Survey 2025 astronomical catalog)

Part One - Recursion with Exception Handling
    1. recursive_sum()          -> exception handling for invalid inputs in a recursive function
    2. get_nested_value()       -> exception handling while recursively processing nested data
    3. find_leaves() /
       print_innermost_leaves() -> recursive navigation that outputs the innermost leaf data

Part Two - Functional Constructs
    4. Anonymous (lambda) functions used to sort, transform, and filter the data
    5. Higher-order functions map(), filter(), and reduce() used to process the data
    6. apply_to_collection()    -> a function that accepts another function as an argument
"""

import json
from functools import reduce

DATA_FILE = "catalog.json"


# ---------------------------------------------------------------------------
# Loading the data set
# ---------------------------------------------------------------------------
def load_catalog(file_path):
    """Load the JSON catalog, handling a missing file or malformed JSON."""
    try:
        with open(file_path, "r", encoding="utf-8") as file:
            return json.load(file)["astronomical_catalog"]
    except FileNotFoundError:
        print(f"Error: The file '{file_path}' was not found.")
    except json.JSONDecodeError as error:
        print(f"Error: '{file_path}' is not valid JSON ({error}).")
    except KeyError:
        print("Error: The file does not contain an 'astronomical_catalog' key.")
    return None


# ===========================================================================
# PART ONE: RECURSION WITH EXCEPTION HANDLING
# ===========================================================================

# ---------------------------------------------------------------------------
# 1. Exception handling in a recursive function to manage invalid inputs
# ---------------------------------------------------------------------------
def recursive_sum(values):
    """
    Recursively add up a list of numbers.

    Raises:
        TypeError:  if the input is not a list or tuple.
        ValueError: if any element is not a number (bools are rejected too).
    """
    if not isinstance(values, (list, tuple)):
        raise TypeError(f"Expected a list or tuple, got {type(values).__name__}.")

    # Base case: an empty list adds up to zero.
    if len(values) == 0:
        return 0

    first = values[0]
    if isinstance(first, bool) or not isinstance(first, (int, float)):
        raise ValueError(f"Invalid value {first!r}: all elements must be numbers.")

    # Recursive case: first element plus the sum of the rest.
    return first + recursive_sum(values[1:])


def safe_recursive_sum(values, label):
    """Call recursive_sum and handle any invalid input gracefully."""
    try:
        total = recursive_sum(values)
        print(f"  {label}: {total:,.2f}")
        return total
    except (TypeError, ValueError) as error:
        print(f"  {label}: could not compute -> {error}")
        return None
    except RecursionError:
        print(f"  {label}: the list is too long to sum recursively.")
        return None


# ---------------------------------------------------------------------------
# 2. Exception handling in a recursive function that processes nested data
# ---------------------------------------------------------------------------
def get_nested_value(data, path):
    """
    Recursively follow a path of keys (for dictionaries) and indexes (for
    lists) through the nested catalog and return the value at the end.

    Example path: ["galaxies", 0, "star_systems", 0, "name"]

    Raises:
        KeyError:   if a dictionary key does not exist.
        IndexError: if a list index is out of range.
        TypeError:  if the path tries to step into a value that is not a
                    dictionary or list, or uses the wrong kind of key.
    """
    # Base case: nothing left in the path, so this is the value we want.
    if not path:
        return data

    step, remaining = path[0], path[1:]

    try:
        if isinstance(data, dict):
            next_level = data[step]
        elif isinstance(data, list):
            if not isinstance(step, int):
                raise TypeError(f"List index must be an integer, got {step!r}.")
            next_level = data[step]
        else:
            raise TypeError(
                f"Cannot look up {step!r} inside a {type(data).__name__} value."
            )
    except KeyError:
        raise KeyError(f"Key {step!r} was not found.") from None
    except IndexError:
        raise IndexError(
            f"Index {step} is out of range (list has {len(data)} items)."
        ) from None

    # Recursive case: keep walking down the remaining path.
    return get_nested_value(next_level, remaining)


def safe_get(data, path):
    """Call get_nested_value and report any problems instead of crashing."""
    readable_path = " -> ".join(str(step) for step in path)
    try:
        value = get_nested_value(data, path)
        print(f"  {readable_path}\n      = {value}")
        return value
    except (KeyError, IndexError, TypeError) as error:
        message = error.args[0] if error.args else error
        print(f"  {readable_path}\n      ! Error: {message}")
        return None


# ---------------------------------------------------------------------------
# 3. Recursive function that navigates the nested structure and outputs the
#    innermost leaf data
# ---------------------------------------------------------------------------
def find_leaves(data, path="catalog", depth=0):
    """
    Recursively walk every dictionary and list in the data and return a list
    of (path, depth, value) tuples for each leaf (a value that is not a
    dictionary or list). Empty containers and None are treated as leaves.
    """
    leaves = []

    if isinstance(data, dict) and data:
        for key, value in data.items():
            leaves.extend(find_leaves(value, f"{path}.{key}", depth + 1))
    elif isinstance(data, list) and data:
        for index, item in enumerate(data):
            leaves.extend(find_leaves(item, f"{path}[{index}]", depth + 1))
    else:
        # Base case: a leaf value.
        leaves.append((path, depth, data))

    return leaves


def print_innermost_leaves(data):
    """Print the leaf values that sit at the deepest level of nesting."""
    try:
        leaves = find_leaves(data)
    except RecursionError:
        print("  The data is nested too deeply to process.")
        return []

    if not leaves:
        print("  No leaf data found.")
        return []

    max_depth = max(depth for _, depth, _ in leaves)
    innermost = [leaf for leaf in leaves if leaf[1] == max_depth]

    print(f"  Total leaf values found: {len(leaves)}")
    print(f"  Deepest nesting level: {max_depth}")
    print(f"  Innermost leaf values ({len(innermost)}):")
    for path, _, value in innermost:
        print(f"    {path} = {value}")
    return innermost


# ===========================================================================
# PART TWO: FUNCTIONAL CONSTRUCTS
# ===========================================================================

# ---------------------------------------------------------------------------
# 6. A function that accepts another function as an argument
#    (defined first because it is used in the Part Two demo below)
# ---------------------------------------------------------------------------
def apply_to_collection(collection, func):
    """
    Apply any function passed in (named or lambda) to every item in a
    collection and return the results as a list. Items that cause an error
    are skipped and reported.
    """
    if not callable(func):
        raise TypeError("The second argument must be a function.")

    results = []
    for item in collection:
        try:
            results.append(func(item))
        except (KeyError, TypeError, ValueError) as error:
            print(f"  Skipped an item: {error!r}")
    return results


def describe_planet(planet):
    """A named function that can be passed to apply_to_collection."""
    zone = "in" if planet["habitable_zone"] else "outside"
    return f"{planet['name']} ({planet['mass_earth_masses']} Earth masses, {zone} the habitable zone)"


# ===========================================================================
# DEMONSTRATION
# ===========================================================================
def main():
    catalog = load_catalog(DATA_FILE)
    if catalog is None:
        return

    print("=" * 70)
    print(f"{catalog['catalog_name']} ({catalog['catalog_id']})")
    print("=" * 70)

    # ---------------------------------------------------------------- Part 1
    print("\nPART ONE: RECURSION WITH EXCEPTION HANDLING")

    print("\n1. Recursive sum with invalid-input handling")
    galaxy_masses = [galaxy["mass_solar_masses"] for galaxy in catalog["galaxies"]]
    safe_recursive_sum(galaxy_masses, "Total galaxy mass (solar masses)")
    safe_recursive_sum([1.374, 1.308, "heavy", 0.388], "List with a text value")
    safe_recursive_sum("TRAPPIST-1", "A string instead of a list")
    safe_recursive_sum(None, "None instead of a list")

    print("\n2. Recursive lookup in nested data with error handling")
    safe_get(catalog, ["galaxies", 0, "star_systems", 0, "planets", 1, "moons", 1, "name"])
    safe_get(catalog, ["black_holes", 0, "accretion_disk", "temperature_k"])
    safe_get(catalog, ["galaxies", 9, "name"])                      # bad index
    safe_get(catalog, ["nebulae", 0, "magnitude"])                  # missing key
    safe_get(catalog, ["pulsars", 0, "name", "first_letter"])       # step into a string
    safe_get(catalog, ["star_clusters", "first"])                   # wrong index type

    print("\n3. Innermost leaf data in the nested catalog")
    print_innermost_leaves(catalog)

    # ---------------------------------------------------------------- Part 2
    print("\nPART TWO: FUNCTIONAL CONSTRUCTS")

    print("\n4. Anonymous (lambda) functions")
    galaxies_by_distance = sorted(catalog["galaxies"], key=lambda g: g["distance_ly"])
    print("  Galaxies sorted from nearest to farthest:")
    for galaxy in galaxies_by_distance:
        print(f"    {galaxy['name']:<20} {galaxy['distance_ly']:>12,} ly")

    ly_to_million_ly = lambda ly: round(ly / 1_000_000, 2)
    print("  Galaxy distances in millions of light-years:",
          [ly_to_million_ly(g["distance_ly"]) for g in galaxies_by_distance])

    hottest_cluster_star = max(
        (star for cluster in catalog["star_clusters"] for star in cluster["notable_stars"]),
        key=lambda s: s["temperature_k"],
    )
    print(f"  Hottest notable cluster star: {hottest_cluster_star['name']} "
          f"({hottest_cluster_star['temperature_k']:,} K)")

    print("\n5. Higher-order functions: map(), filter(), reduce()")
    all_exoplanets = [p for system in catalog["exoplanet_systems"] for p in system["planets"]]

    habitable = list(filter(lambda p: p["habitable_zone"], all_exoplanets))
    print("  filter() - habitable-zone planets:", [p["name"] for p in habitable])

    pulsar_rpm = list(map(lambda p: (p["name"], round(p["frequency_hz"] * 60, 1)),
                          catalog["pulsars"]))
    print("  map()    - pulsar rotations per minute:", pulsar_rpm)

    all_planets = [
        planet
        for galaxy in catalog["galaxies"]
        for system in galaxy["star_systems"]
        for planet in system["planets"]
    ]
    total_moons = reduce(lambda total, planet: total + len(planet["moons"]), all_planets, 0)
    print(f"  reduce() - total moons orbiting galaxy planets: {total_moons}")

    print("\n6. Function that accepts another function as an argument")
    print("  Passing a named function (describe_planet):")
    for line in apply_to_collection(all_exoplanets, describe_planet):
        print(f"    {line}")

    print("  Passing a lambda (nebula name and type):")
    print("   ", apply_to_collection(catalog["nebulae"],
                                     lambda n: f"{n['name']} [{n['type']}]"))

    print("  Passing a lambda that hits a missing key (handled):")
    print("   ", apply_to_collection(catalog["black_holes"],
                                     lambda bh: bh["spin_rate"]))

    try:
        apply_to_collection(catalog["pulsars"], "not a function")
    except TypeError as error:
        print(f"  Passing a non-function is rejected: {error}")


if __name__ == "__main__":
    main()
