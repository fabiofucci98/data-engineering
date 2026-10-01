"""Unit tests for the deterministic NameBuilder (pools, seeds, explosion)."""
import random
from pathlib import Path

import pytest

from generate import NameBuilder


def make_builder(tmp_path: Path, words: list[str], seed: int = 7) -> NameBuilder:
    (tmp_path / "x.txt").write_text("\n".join(words) + "\n", encoding="utf-8")
    return NameBuilder(tmp_path, random.Random(seed))


def test_same_seed_same_draws(tmp_path: Path) -> None:
    a = make_builder(tmp_path, ["a", "b", "c", "d", "e"], seed=7)
    b = make_builder(tmp_path, ["a", "b", "c", "d", "e"], seed=7)
    assert a.unique(["x", "x"], 5) == b.unique(["x", "x"], 5)


def test_different_seed_different_draws(tmp_path: Path) -> None:
    a = make_builder(tmp_path, ["a", "b", "c", "d", "e"], seed=7)
    b = make_builder(tmp_path, ["a", "b", "c", "d", "e"], seed=8)
    assert a.unique(["x", "x"], 5) != b.unique(["x", "x"], 5)


def test_unique_draws_without_replacement(tmp_path: Path) -> None:
    b = make_builder(tmp_path, ["a", "b", "c", "d", "e"], seed=1)
    out = b.unique(["x", "x"], 5)
    assert len(set(out)) == 5  # all distinct compounds


def test_unique_refuses_beyond_capacity(tmp_path: Path) -> None:
    b = make_builder(tmp_path, ["a", "b"], seed=1)
    with pytest.raises(ValueError):
        b.unique(["x", "x"], 5)  # 2x2 = 4 possible, asked for 5


def test_unique_single_shuffles_pool(tmp_path: Path) -> None:
    b = make_builder(tmp_path, ["a", "b", "c", "d"], seed=3)
    out = b.unique_single("x", 2)
    assert len(out) == 2 and set(out) <= {"a", "b", "c", "d"}


def test_unique_pairs_use_distinct_words(tmp_path: Path) -> None:
    b = make_builder(tmp_path, ["a", "b", "c", "d"], seed=5)
    for name in b.unique_pairs("x", 6):
        left, right = name.split(" & ")
        assert left != right


def test_unique_pairs_product_capacity(tmp_path: Path) -> None:
    # n=4 words -> n*(n-1) = 12 pairs; the 13th draw must raise.
    b = make_builder(tmp_path, ["a", "b", "c", "d"], seed=5)
    assert len(b.unique_pairs("x", 12)) == 12
    with pytest.raises(ValueError):
        b.unique_pairs("x", 13)


def test_missing_pool_raises(tmp_path: Path) -> None:
    b = NameBuilder(tmp_path, random.Random(1))
    with pytest.raises(ValueError):
        b.pool("does-not-exist")


def test_empty_pool_raises(tmp_path: Path) -> None:
    (tmp_path / "x.txt").write_text("\n", encoding="utf-8")
    b = NameBuilder(tmp_path, random.Random(1))
    with pytest.raises(ValueError):
        b.pool("x")