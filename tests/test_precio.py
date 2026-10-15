"""ops/precio.py: the price of the home page is one number in eight places; changing it must change all of them."""

import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "ops"))

import precio  # noqa: E402

HTML = (ROOT / "docs" / "index.html").read_text(encoding="utf-8")


def test_the_published_page_has_the_price_in_all_places_and_they_agree():
    assert precio.problems(HTML) == []
    assert len(precio.found(HTML)["frases"]) == 6 and len(precio.found(HTML)["datos de buscadores"]) == 2


def test_changing_the_price_changes_every_place_and_nothing_else():
    other = precio.current(HTML) + 7
    changed = precio.change(HTML, other)
    assert precio.problems(changed) == [] and precio.current(changed) == other
    assert f"desde {other} € al mes" in changed.lower() and f'"price": "{other}"' in changed
    # only those eight numbers differ
    assert precio.change(changed, precio.current(HTML)) == HTML


def test_a_missing_place_or_a_different_number_is_reported():
    assert precio.problems(HTML.replace("Desde", "A partir de", 1))   # one sentence gone
    split = HTML.replace('"price": "', '"price": "9', 1)               # one offer says another number
    assert any("distintos" in p for p in precio.problems(split))


def test_the_command_refuses_nonsense(tmp_path, monkeypatch):
    page = tmp_path / "index.html"
    page.write_text(HTML, encoding="utf-8")
    monkeypatch.setattr(precio, "HOME", page)
    assert precio.main(["precio.py", "abc"]) == 2
    assert precio.main(["precio.py", "0"]) == 2
    other = precio.current(HTML) + 7
    assert precio.main(["precio.py", str(other)]) == 0 and precio.current(page.read_text(encoding="utf-8")) == other
    assert precio.main(["precio.py"]) == 0                              # reading changes nothing


def test_prices_outside_the_range_are_refused():
    with pytest.raises(ValueError):
        precio.change(HTML, 1000)
