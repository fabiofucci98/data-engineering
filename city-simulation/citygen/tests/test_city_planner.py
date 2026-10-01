"""Unit tests for the city planning formulas and grid derivation (offline)."""
from generate import CityPlan, plan_city, rescale_counts


def test_plan_1000_matches_design() -> None:
    p = plan_city(1_000, 8)
    assert p.buildings_per_type == {
        "house": 333,
        "school": 3,
        "shop": 4,
        "workplace": 6,
        "hospital": 1,
        "park": 1,
        "restaurant": 4,
        "civic": 1,
    }
    assert p.total_buildings == 353
    assert p.grid_side == 7             # 49 blocks, 64 intersections, 112 segments
    assert p.target_districts == 5
    assert p.target_intersections == 64
    assert p.target_road_segments == 112


def test_plan_10000_matches_observed() -> None:
    p = plan_city(10_000, 8)
    assert p.buildings_per_type["house"] == 3_333
    assert p.buildings_per_type["restaurant"] == 40
    assert p.total_buildings == 3_502
    assert p.grid_side == 22
    assert p.target_intersections == 529
    assert p.target_road_segments == 1_012


def test_min_grid_side_for_tiny_population() -> None:
    p = plan_city(50, 8)
    assert p.grid_side >= 3  # min_grid_side floor


def test_plan_is_a_cityplan() -> None:
    assert isinstance(plan_city(1_000, 8), CityPlan)


def test_rescale_counts_preserves_total() -> None:
    counts = plan_city(1_000, 8).buildings_per_type
    scaled = rescale_counts(counts, 4_000)
    assert sum(scaled.values()) == 4_000
    assert sum(scaled.values()) != sum(counts.values())


def test_rescale_same_total_is_noop() -> None:
    counts = plan_city(1_000, 8).buildings_per_type
    assert rescale_counts(counts, sum(counts.values())) == counts