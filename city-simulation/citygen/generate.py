"""City geography generator - fills the city database up to target sizes.

Deterministic (seeded), dictionary-driven naming (no AI at runtime), idempotent
fill loop: counts current rows, generates only the missing rows, stops when every
table is at or above its target.

Inputs: --population, --buildings-per-block, --seed (+ optional --target-buildings).

Examples:
    python citygen/generate.py --dry-run --seed 42
    python citygen/generate.py --population 1000 --buildings-per-block 8 --seed 42
"""
from __future__ import annotations

import argparse
import math
import os
import random
import time
from dataclasses import dataclass
from pathlib import Path

import psycopg
from dotenv import load_dotenv

PACKAGE_DIR = Path(__file__).resolve().parent
POOLS_DIR = Path(os.getenv("CITY_POOLS_DIR", PACKAGE_DIR.parent / "pools"))

DEFAULT_POPULATION = 1_000
DEFAULT_BUILDINGS_PER_BLOCK = 8
DEFAULT_SEED = 42
BATCH_SIZE = 5_000

# --- Planning assumptions (single block: readable and retunable) ---
ASSUMPTIONS = {
    "household_size": 3,           # people per house
    "kids_per_household": 1.0,     # children per household
    "school_capacity": 150,        # children per school
    "residents_per_shop": 250,     # people served by one shop
    "workplace_capacity": 100,     # workers per workplace
    "participation_rate": 0.80,    # share of non-children in the workforce
    "residents_per_hospital": 5_000,
    "residents_per_park": 2_000,
    "residents_per_restaurant": 250,
    "residents_per_civic": 2_000,
    "min_grid_side": 3,
    "density_buffer": 1.10,        # grid slack so zoning always fits
}

BUILDING_TYPES = (
    "house", "school", "shop", "workplace",
    "hospital", "park", "restaurant", "civic",
)

BUILDING_CAPACITY = {
    "house": ASSUMPTIONS["household_size"],
    "school": ASSUMPTIONS["school_capacity"],
    "shop": 25,
    "workplace": ASSUMPTIONS["workplace_capacity"],
    "hospital": 20,
    "park": 0,
    "restaurant": 30,
    "civic": 500,
}

# How much each building type prefers each district type (higher = preferred).
# Every district type must appear in every map (park = 0 everywhere except parks).
DISTRICT_PREFERENCE = {
    "house":      {"residential": 3, "downtown": 1, "industrial": 0, "park": 0},
    "school":     {"residential": 3, "downtown": 1, "industrial": 0, "park": 0},
    "shop":       {"downtown": 3, "residential": 2, "industrial": 0, "park": 0},
    "workplace":  {"industrial": 3, "downtown": 2, "residential": 0, "park": 0},
    "hospital":   {"downtown": 3, "residential": 2, "industrial": 0, "park": 0},
    "park":       {"park": 3, "residential": 1, "downtown": 0, "industrial": 0},
    "restaurant": {"downtown": 3, "residential": 2, "industrial": 0, "park": 0},
    "civic":      {"downtown": 3, "residential": 1, "industrial": 0, "park": 0},
}

BLOCK_SIZE_M = 100
AVENUE_SPEED = 50
RESIDENTIAL_SPEED = 30
AVENUE_LANES = 4
RESIDENTIAL_LANES = 2
AVENUE_CAPACITY = 1_800
RESIDENTIAL_CAPACITY = 800

DISTRICT_PLAN = [  # (type, how many)
    ("downtown", 1),
    ("residential", 2),
    ("industrial", 1),
    ("park", 1),
]


@dataclass
class CityPlan:
    population: int
    buildings_per_block: int
    seed: int
    grid_side: int
    buildings_per_type: dict[str, int]
    target_districts: int
    target_intersections: int
    target_road_segments: int

    @property
    def blocks(self) -> int:
        return self.grid_side * self.grid_side

    @property
    def total_buildings(self) -> int:
        return sum(self.buildings_per_type.values())


def plan_city(population: int, buildings_per_block: int) -> CityPlan:
    """Turn the two inputs into every target count (grid derived too)."""
    a = ASSUMPTIONS
    houses = population // a["household_size"]  # floor, matches the human's 333
    children = int(houses * a["kids_per_household"])
    workers = int((population - children) * a["participation_rate"])

    buildings_per_type = {
        "house": houses,
        "school": math.ceil(children / a["school_capacity"]),
        "shop": math.ceil(population / a["residents_per_shop"]),
        "workplace": math.ceil(workers / a["workplace_capacity"]),
        "hospital": max(1, math.ceil(population / a["residents_per_hospital"])),
        "park": max(1, math.ceil(population / a["residents_per_park"])),
        "restaurant": math.ceil(population / a["residents_per_restaurant"]),
        "civic": max(1, math.ceil(population / a["residents_per_civic"])),
    }
    total = sum(buildings_per_type.values())
    blocks_needed = math.ceil(total / buildings_per_block * a["density_buffer"])
    side = max(a["min_grid_side"], math.ceil(math.sqrt(blocks_needed)))
    return CityPlan(
        population=population,
        buildings_per_block=buildings_per_block,
        seed=DEFAULT_SEED,
        grid_side=side,
        buildings_per_type=buildings_per_type,
        target_districts=sum(count for _, count in DISTRICT_PLAN),
        target_intersections=(side + 1) ** 2,
        target_road_segments=2 * side * (side + 1),
    )


def rescale_counts(counts: dict[str, int], target_total: int) -> dict[str, int]:
    """Scale building counts to a target total, keeping proportions (escape hatch)."""
    current = sum(counts.values())
    if target_total <= 0 or target_total == current:
        return dict(counts)
    scaled = {
        btype: max(1, round(count * target_total / current))
        for btype, count in counts.items()
    }
    diff = target_total - sum(scaled.values())
    scaled[max(scaled, key=scaled.get)] += diff
    return scaled


def database_url() -> str:
    """Build the city Postgres connection string (CITY_POSTGRES_* overrides POSTGRES_*)."""
    user = os.getenv("CITY_POSTGRES_USER", os.getenv("POSTGRES_USER", "postgres"))
    password = os.getenv("CITY_POSTGRES_PASSWORD", os.getenv("POSTGRES_PASSWORD", "postgres"))
    host = os.getenv("CITY_POSTGRES_HOST", os.getenv("POSTGRES_HOST", "localhost"))
    port = os.getenv("CITY_POSTGRES_PORT", os.getenv("POSTGRES_PORT", "5432"))
    dbname = os.getenv("CITY_POSTGRES_DB", os.getenv("POSTGRES_DB", "city"))
    return f"postgresql://{user}:{password}@{host}:{port}/{dbname}"


class NameBuilder:
    """Deterministic name drawing from one-word-per-line pool files."""

    def __init__(self, pools_dir: Path, rng: random.Random) -> None:
        self.pools_dir = pools_dir
        self.rng = rng
        self._cache: dict[str, list[str]] = {}

    def pool(self, name: str) -> list[str]:
        if name not in self._cache:
            path = self.pools_dir / f"{name}.txt"
            try:
                content = path.read_text(encoding="utf-8")
            except OSError as exc:
                raise ValueError(f"Cannot read pool file: {path} ({exc})") from exc
            words = [
                line.strip()
                for line in content.splitlines()
                if line.strip()
            ]
            if not words:
                raise ValueError(f"Empty pool file: {path}")
            self._cache[name] = words
        return self._cache[name]

    def unique(self, pools: list[str], count: int, joiner: str = " ") -> list[str]:
        """Draw `count` unique compounds, one word from each pool, no replacement."""
        sizes = [len(self.pool(p)) for p in pools]
        space = math.prod(sizes)
        if count > space:
            raise ValueError(f"Need {count} names; pools {pools} only make {space}.")
        order = list(range(space))
        self.rng.shuffle(order)
        names = []
        for k in order[:count]:
            rest = k
            indexes = []
            for size in sizes:
                indexes.append(rest % size)
                rest //= size
            names.append(joiner.join(self.pool(p)[i] for p, i in zip(pools, indexes)))
        return names

    def unique_single(self, pool: str, count: int) -> list[str]:
        words = list(self.pool(pool))
        self.rng.shuffle(words)
        return words[:count]

    def unique_pairs(self, pool: str, count: int, joiner: str = " & ") -> list[str]:
        """'A & B' compounds, drawn WITHOUT replacement from the combination space.

        Capacity is n x (n-1) distinct ordered pairs (not n/2) — the pool explodes
        combinatorially, matching the product rule of `unique`. n words support
        n*(n-1) pairs: 20 words -> 380 restaurant names (population ~47k at 1/250).
        """
        pool_words = self.pool(pool)
        n = len(pool_words)
        space = n * (n - 1)
        if count > space:
            raise ValueError(
                f"Need {count} {joiner.strip()} - compounds from pool '{pool}' "
                f"(capacity {space}: {n} words -> {n}x{n-1} combinations). "
                f"Grow the pool: add words to pools/{pool}.txt."
            )
        order = list(range(space))
        self.rng.shuffle(order)
        names = []
        for k in order[:count]:
            a = k % n
            b = (k // n) % (n - 1)
            if b >= a:  # bijection onto ordered pairs with distinct words
                b += 1
            names.append(f"{pool_words[a]}{joiner}{pool_words[b]}")
        return names


def building_names(name_builder: NameBuilder, building_type: str, count: int) -> list[str]:
    """Names per building type, following the naming recipe table (pools/README.md)."""
    recipes = {
        "house": lambda: [""] * count,  # single-family homes: no name, address only
        "school": lambda: name_builder.unique(["school_name", "school_level"], count),
        "shop": lambda: name_builder.unique(["shop_adjective", "shop_noun"], count),
        "workplace": lambda: name_builder.unique(["workplace_noun", "workplace_suffix"], count),
        "hospital": lambda: name_builder.unique(["hospital_name", "hospital_suffix"], count),
        "park": lambda: [f"{n} Park" for n in name_builder.unique_single("park_name", count)],
        "restaurant": lambda: name_builder.unique_pairs("restaurant_noun", count),
        "civic": lambda: name_builder.unique(["civic_name", "civic_type"], count),
    }
    return recipes[building_type]()


def district_rows(name_builder: NameBuilder) -> list[dict]:
    names = name_builder.unique(
        ["district_character", "district_place"],
        sum(count for _, count in DISTRICT_PLAN),
    )
    rows, n = [], 0
    for district_type, count in DISTRICT_PLAN:
        for _ in range(count):
            rows.append({"name": names[n], "district_type": district_type})
            n += 1
    return rows


def intersection_rows(side: int) -> list[dict]:
    return [
        {"ix": ix, "iy": iy, "coord_x": ix * BLOCK_SIZE_M, "coord_y": iy * BLOCK_SIZE_M}
        for iy in range(side + 1)
        for ix in range(side + 1)
    ]


def segment_row(from_ix: int, from_iy: int, to_ix: int, to_iy: int, avenue: bool, name: str) -> dict:
    return {
        "from_ix": from_ix,
        "from_iy": from_iy,
        "to_ix": to_ix,
        "to_iy": to_iy,
        "name": name,
        "road_class": "avenue" if avenue else "residential",
        "speed_limit": AVENUE_SPEED if avenue else RESIDENTIAL_SPEED,
        "lanes": AVENUE_LANES if avenue else RESIDENTIAL_LANES,
        "capacity_per_hour": AVENUE_CAPACITY if avenue else RESIDENTIAL_CAPACITY,
        "length_m": BLOCK_SIZE_M,
    }


def road_segment_rows(plan: CityPlan, name_builder: NameBuilder) -> tuple[list[dict], dict]:
    """All road segments + front-street name for every block (south edge)."""
    side = plan.grid_side
    names = name_builder.unique(
        ["road_first", "road_middle", "road_type"], plan.target_road_segments
    )
    rows: list[dict] = []
    front: dict[tuple[int, int], str] = {}
    idx = 0
    # Vertical streets: (ix, iy) -> (ix, iy+1); every 2nd street is an avenue.
    for ix in range(side + 1):
        avenue = ix % 2 == 0
        for iy in range(side):
            rows.append(segment_row(ix, iy, ix, iy + 1, avenue, names[idx]))
            idx += 1
    # Horizontal streets: (ix, iy) -> (ix+1, iy) -> the south edge of block (ix, iy).
    for iy in range(side + 1):
        avenue = iy % 2 == 0
        for ix in range(side):
            rows.append(segment_row(ix, iy, ix + 1, iy, avenue, names[idx]))
            front[(ix, iy)] = names[idx]
            idx += 1
    return rows, front


def assign_block_districts(
    side: int, park_count: int, rng: random.Random
) -> dict[tuple[int, int], str]:
    """Every block (bx, by) gets a district type; parks carved from residential areas."""
    block_types: dict[tuple[int, int], str] = {}
    center = side // 2
    for by in range(side):
        for bx in range(side):
            if max(abs(bx - center), abs(by - center)) <= 1:
                block_types[(bx, by)] = "downtown"
            elif by == side - 1:
                block_types[(bx, by)] = "industrial"
            else:
                block_types[(bx, by)] = "residential"
    residential = sorted(b for b, t in block_types.items() if t == "residential")
    rng.shuffle(residential)
    for block in residential[:park_count]:
        block_types[block] = "park"
    return block_types


def block_district_names(
    plan: CityPlan, districts: list[dict], block_types: dict
) -> dict[tuple[int, int], str]:
    """Map each block to a concrete district *name* (residential split east/west)."""
    by_type: dict[str, list[str]] = {}
    for row in districts:
        by_type.setdefault(row["district_type"], []).append(row["name"])
    center = plan.grid_side // 2
    result: dict[tuple[int, int], str] = {}
    for (bx, by), dtype in block_types.items():
        names = by_type[dtype]
        if dtype == "residential" and len(names) > 1:
            chosen = names[0] if bx < center else names[1]
        else:
            chosen = names[0]
        result[(bx, by)] = chosen
    return result


def preferred_block_order(
    blocks: list, block_types: dict, building_type: str, rng: random.Random
) -> list:
    """Blocks for a building type: highest preference first, seeded tie-break."""
    pref = DISTRICT_PREFERENCE[building_type]
    order = sorted(blocks, key=lambda b: -pref[block_types[b]])
    rng.shuffle(order)
    order.sort(key=lambda b: -pref[block_types[b]])  # stable: keeps seeded tie order
    return order


def building_rows(
    plan: CityPlan,
    block_types: dict,
    block_district: dict,
    front_street: dict,
    district_id_by_name: dict[str, int],
    name_builder: NameBuilder,
) -> list[dict]:
    """All building rows, placed block by block, slots 0..buildings_per_block."""
    blocks = list(block_types)
    used_slots: dict[tuple[int, int], int] = {}
    rows: list[dict] = []
    for building_type in BUILDING_TYPES:
        need = plan.buildings_per_type[building_type]
        names = building_names(name_builder, building_type, need)
        placed = 0
        for block in preferred_block_order(blocks, block_types, building_type, name_builder.rng):
            bx, by = block
            slot = used_slots.get(block, 0)
            while slot < plan.buildings_per_block and placed < need:
                rows.append({
                    "building_type": building_type,
                    "name": names[placed],
                    "capacity": BUILDING_CAPACITY[building_type],
                    "block_ix": bx,
                    "block_iy": by,
                    "slot": slot,
                    "address": f"{slot * 4 + 1} {front_street[block]}",
                    "district_id": district_id_by_name[block_district[block]],
                })
                used_slots[block] = slot + 1
                slot += 1
                placed += 1
            if placed == need:
                break
        if placed < need:
            raise RuntimeError(f"Not enough block slots for {need} x '{building_type}'.")
    return rows


DISTRICTS_SQL = """
    INSERT INTO districts (name, district_type) VALUES (%(name)s, %(district_type)s)
    ON CONFLICT (name) DO NOTHING
"""

INTERSECTIONS_SQL = """
    INSERT INTO intersections (ix, iy, coord_x, coord_y)
    VALUES (%(ix)s, %(iy)s, %(coord_x)s, %(coord_y)s)
    ON CONFLICT (ix, iy) DO NOTHING
"""

ROAD_SEGMENTS_SQL = """
    INSERT INTO road_segments
        (from_ix, from_iy, to_ix, to_iy, name, road_class, speed_limit, lanes,
         capacity_per_hour, length_m)
    VALUES (%(from_ix)s, %(from_iy)s, %(to_ix)s, %(to_iy)s, %(name)s,
            %(road_class)s, %(speed_limit)s, %(lanes)s, %(capacity_per_hour)s,
            %(length_m)s)
    ON CONFLICT (from_ix, from_iy, to_ix, to_iy) DO NOTHING
"""

BUILDINGS_SQL = """
    INSERT INTO buildings
        (building_type, name, capacity, block_ix, block_iy, slot, address, district_id)
    VALUES (%(building_type)s, %(name)s, %(capacity)s, %(block_ix)s, %(block_iy)s,
            %(slot)s, %(address)s, %(district_id)s)
    ON CONFLICT (block_ix, block_iy, slot) DO NOTHING
"""

GENERATION_SQL = """
    INSERT INTO city_generation (id, population, buildings_per_block, seed, total_buildings, grid_side)
    VALUES (1, %(population)s, %(buildings_per_block)s, %(seed)s, %(total_buildings)s, %(grid_side)s)
    ON CONFLICT (id) DO UPDATE SET
        population = EXCLUDED.population,
        buildings_per_block = EXCLUDED.buildings_per_block,
        seed = EXCLUDED.seed,
        total_buildings = EXCLUDED.total_buildings,
        grid_side = EXCLUDED.grid_side,
        generated_at = now()
"""


def table_count(conn: psycopg.Connection, table: str) -> int:
    with conn.cursor() as cur:
        cur.execute(f"SELECT count(*) FROM {table}")
        return cur.fetchone()[0]


def fill_table(
    conn: psycopg.Connection, table: str, sql: str, rows: list[dict], expected: int
) -> int:
    """Insert rows idempotently in batches (ON CONFLICT DO NOTHING); returns inserted."""
    before = table_count(conn, table)
    if before >= expected:
        return 0
    with conn.cursor() as cur:
        for start in range(0, len(rows), BATCH_SIZE):
            if table_count(conn, table) >= expected:
                break
            cur.executemany(sql, rows[start : start + BATCH_SIZE])
            conn.commit()
    return table_count(conn, table) - before


def print_table_result(conn: psycopg.Connection, name: str, inserted: int, expected: int) -> None:
    print(f"  {name:<14}: need {expected:>5}, have {table_count(conn, name):>5}, inserted {inserted}")


def print_plan(plan: CityPlan, name_builder: NameBuilder) -> None:
    print("City plan (dry run - nothing is written)")
    print(
        f"  inputs           : --population {plan.population} "
        f"--buildings-per-block {plan.buildings_per_block} --seed {plan.seed}"
    )
    print(f"  grid             : {plan.grid_side} x {plan.grid_side} = {plan.blocks} blocks")
    print(f"  intersections    : {plan.target_intersections}")
    print(
        f"  road segments    : {plan.target_road_segments}  (name sources: "
        f"{len(name_builder.pool('road_first'))} x {len(name_builder.pool('road_middle'))} x "
        f"{len(name_builder.pool('road_type'))} = "
        f"{len(name_builder.pool('road_first')) * len(name_builder.pool('road_middle')) * len(name_builder.pool('road_type'))})"
    )
    print(f"  districts        : {plan.target_districts}")
    print("  buildings:")
    for building_type in BUILDING_TYPES:
        print(f"    {building_type:<12}: {plan.buildings_per_type[building_type]}")
    print(f"  total buildings  : {plan.total_buildings}")
    print("  sample names (as the run will write them):")
    # Mirror the exact RNG draw order of a real run so the preview is truthful:
    # districts -> road names -> block districts -> per type (names + block order).
    district_rows(name_builder)
    road_names = name_builder.unique(
        ["road_first", "road_middle", "road_type"], plan.target_road_segments
    )
    block_types = assign_block_districts(
        plan.grid_side, plan.buildings_per_type["park"], name_builder.rng
    )
    print(f"    {'road':<12}: {', '.join(road_names[:3])}, ...")
    for building_type in BUILDING_TYPES:
        need = plan.buildings_per_type[building_type]
        names = building_names(name_builder, building_type, need)
        preferred_block_order(
            list(block_types), block_types, building_type, name_builder.rng
        )
        label = "homes use addresses only" if building_type == "house" else ", ".join(names[:3])
        print(f"    {building_type:<12}: {label}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate the simulated grid city into Postgres.")
    parser.add_argument(
        "--population", type=int, default=DEFAULT_POPULATION,
        help=f"People the city must house (default: {DEFAULT_POPULATION}).",
    )
    parser.add_argument(
        "--buildings-per-block", type=int, default=DEFAULT_BUILDINGS_PER_BLOCK,
        dest="buildings_per_block",
        help=(
            f"Buildings allowed per block (default: {DEFAULT_BUILDINGS_PER_BLOCK}); "
            "grid size derives from it."
        ),
    )
    parser.add_argument(
        "--seed", type=int, default=DEFAULT_SEED,
        help=f"Random seed - same seed = same city (default: {DEFAULT_SEED}).",
    )
    parser.add_argument(
        "--target-buildings", type=int, default=None,
        help="Optional override: rescale building counts to this total (experiments).",
    )
    parser.add_argument(
        "--dry-run", action="store_true",
        help="Print the plan and sample names, write nothing.",
    )
    parser.add_argument(
        "--pools-dir", type=Path, default=POOLS_DIR,
        help=f"Name pools folder (default: {POOLS_DIR}).",
    )
    return parser.parse_args()


def ensure_seed_consistency(conn: psycopg.Connection, plan: CityPlan) -> None:
    """A city DB holds exactly ONE canonical city: (seed, population, buildings-per-block).

    Matching params = idempotent resume (no-op). Anything different would merge a
    second, seed-shaped city into the same tables — natural keys overlap, names clash,
    and count expectations break. Refuse with instructions instead.
    """
    with conn.cursor() as cur:
        cur.execute(
            "SELECT population, buildings_per_block, seed "
            "FROM city_generation WHERE id = 1"
        )
        row = cur.fetchone()
    if row is None:
        return  # fresh database — first generation wins
    pop, bpb, seed = int(row[0]), int(row[1]), int(row[2])
    if (seed, pop, bpb) == (plan.seed, plan.population, plan.buildings_per_block):
        return  # identical city — safe resumable no-op
    raise SystemExit(
        f"ERROR: citydb already holds a different city: "
        f"population {pop}, buildings-per-block {bpb}, seed {seed}.\n"
        f"Requested: population {plan.population}, buildings-per-block "
        f"{plan.buildings_per_block}, seed {plan.seed}.\n"
        "A database stores exactly one canonical city. To generate a different one:\n"
        "  docker compose -f city-simulation/docker-compose.yml down -v\n"
        "then re-run generate.py with the parameters you want."
    )


def main() -> None:
    load_dotenv(PACKAGE_DIR.parent / ".env")
    args = parse_args()

    plan = plan_city(args.population, args.buildings_per_block)
    plan.seed = args.seed
    if args.target_buildings:
        plan.buildings_per_type = rescale_counts(plan.buildings_per_type, args.target_buildings)

    rng = random.Random(args.seed)
    name_builder = NameBuilder(args.pools_dir, rng)

    if args.dry_run:
        print_plan(plan, name_builder)
        return

    print("Generating city ...")
    t0 = time.time()
    try:
        with psycopg.connect(database_url()) as conn:
            # 0. the DB holds one canonical city: (seed, population, buildings-per-block)
            ensure_seed_consistency(conn, plan)

            # 2. districts (need names + ids before buildings)
            districts = district_rows(name_builder)
            inserted = fill_table(conn, "districts", DISTRICTS_SQL, districts, plan.target_districts)
            with conn.cursor() as cur:
                cur.execute("SELECT name, district_id FROM districts")
                district_id_by_name = dict(cur.fetchall())
            print_table_result(conn, "districts", inserted, plan.target_districts)

            # 3. intersections
            intersections = intersection_rows(plan.grid_side)
            inserted = fill_table(conn, "intersections", INTERSECTIONS_SQL, intersections, plan.target_intersections)
            print_table_result(conn, "intersections", inserted, plan.target_intersections)

            # 4. road segments (also builds the front-street map for addresses)
            segments, front = road_segment_rows(plan, name_builder)
            inserted = fill_table(conn, "road_segments", ROAD_SEGMENTS_SQL, segments, plan.target_road_segments)
            print_table_result(conn, "road_segments", inserted, plan.target_road_segments)

            # 5. buildings (placement + names)
            block_types = assign_block_districts(
                plan.grid_side, plan.buildings_per_type["park"], rng
            )
            block_district = block_district_names(plan, districts, block_types)
            buildings = building_rows(
                plan, block_types, block_district, front, district_id_by_name, name_builder
            )
            inserted = fill_table(conn, "buildings", BUILDINGS_SQL, buildings, plan.total_buildings)
            print_table_result(conn, "buildings", inserted, plan.total_buildings)

            # last: generation metadata — written ONLY after a successful run, so a
            # crashed run can never poison the seed guard above (city_generation
            # always describes a COMPLETED city).
            with conn.cursor() as cur:
                cur.execute(
                    GENERATION_SQL,
                    {
                        "population": plan.population,
                        "buildings_per_block": plan.buildings_per_block,
                        "seed": plan.seed,
                        "total_buildings": plan.total_buildings,
                        "grid_side": plan.grid_side,
                    },
                )
            conn.commit()
    except psycopg.OperationalError as exc:
        print(f"ERROR: cannot connect to Postgres ({exc}). Is the city-db service up?")
        raise SystemExit(1)

    print(f"Done in {time.time() - t0:.1f}s.")


if __name__ == "__main__":
    main()