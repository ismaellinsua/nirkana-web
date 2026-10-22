"""The publication script (ops/publicar_sitio.py): the public repository gets what is seen on nirkana.es and nothing else."""

import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "ops"))

import publicar_sitio as publish  # noqa: E402


def write(path: Path, text: str = "x") -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    return path


@pytest.fixture
def world(tmp_path):
    """A small private repository (docs, templates, license) and an empty public checkout."""
    docs, templates = tmp_path / "docs", tmp_path / "ops" / "publico"
    write(docs / "index.html", "<html></html>")
    write(docs / "assets" / "site.css", "a{}")
    write(docs / ".nojekyll", "")
    write(docs / "CNAME", "nirkana.es")
    write(templates / "README.md", "# nirkana.es")
    write(templates / "despertar-prueba.yml", "name: x")
    write(tmp_path / "LICENSE", "todos los derechos reservados")
    public = tmp_path / "publico"
    (public / ".git").mkdir(parents=True)
    return docs, templates, tmp_path, public


def tree(world):
    docs, templates, root, _ = world
    return publish.expected(docs, templates, root)


def test_the_real_docs_only_hold_files_of_the_website():
    # If this fails: something that is not of the site (a note, a script, a data file) is in docs/. Move it out; it would be public.
    tree = publish.expected()
    assert "docs/index.html" in tree and "docs/CNAME" not in tree
    assert not [name for name in tree if name.endswith((".md", ".py", ".json", ".yml", ".sh", ".env")) and name not in ("README.md", ".github/workflows/despertar-prueba.yml")]


def test_a_note_or_a_script_in_docs_stops_the_publication(world):
    docs, _, _, _ = world
    write(docs / "NOTA-INTERNA.md")
    write(docs / "assets" / "ayuda.py")
    with pytest.raises(publish.PublishError) as error:
        tree(world)
    assert "NOTA-INTERNA.md" in str(error.value) and "ayuda.py" in str(error.value)


def test_the_folder_of_the_previous_product_is_not_published(world):
    docs, _, _, _ = world
    write(docs / "caja" / "index.html")
    assert not [name for name in tree(world) if name.startswith("docs/caja")]


def test_the_copy_is_the_site_plus_three_fixed_files_and_never_the_domain_file(world):
    _, _, _, public = world
    add, change, remove = publish.apply(public, tree(world))
    assert sorted(add) == [".github/workflows/despertar-prueba.yml", "LICENSE", "README.md", "docs/.nojekyll", "docs/assets/site.css", "docs/index.html"]
    assert change == [] and remove == []
    assert not (public / "docs" / "CNAME").exists()


def test_what_github_wrote_for_the_domain_is_kept_and_what_does_not_belong_is_removed(world):
    docs, _, _, public = world
    publish.apply(public, tree(world))
    write(public / "docs" / "CNAME", "nirkana.es")                    # written by GitHub when the domain is set
    write(public / "docs" / "caja" / "index.html")                    # an old file that must not stay
    write(public / "notas" / "WEB.md")                                # something that slipped in by hand
    write(docs / "index.html", "<html>nuevo</html>")
    add, change, remove = publish.apply(public, tree(world))
    assert change == ["docs/index.html"]
    assert remove == ["docs/caja/index.html", "notas/WEB.md"]
    assert (public / "docs" / "CNAME").read_text() == "nirkana.es"
    assert not (public / "notas").exists() and not (public / "docs" / "caja").exists()   # empty folders go too


def test_the_git_folder_of_the_public_copy_is_never_touched(world):
    _, _, _, public = world
    write(public / ".git" / "config", "[core]")
    publish.apply(public, tree(world))
    assert (public / ".git" / "config").read_text() == "[core]"


def test_check_mode_writes_nothing_and_says_whether_the_copy_matches(world, capsys, monkeypatch):
    docs, templates, root, public = world
    monkeypatch.setattr(publish, "DOCS", docs)
    monkeypatch.setattr(publish, "TEMPLATES", templates)
    monkeypatch.setattr(publish, "ROOT", root)
    original = publish.expected
    monkeypatch.setattr(publish, "expected", lambda: original(docs, templates, root))
    assert publish.main([str(public), "--check"]) == 1
    assert not (public / "docs").exists(), "--check no escribe"
    assert "falta: docs/index.html" in capsys.readouterr().err
    assert publish.main([str(public)]) == 0
    assert publish.main([str(public), "--check"]) == 0


def test_it_refuses_a_folder_that_is_not_a_git_checkout(tmp_path, capsys):
    assert publish.main([str(tmp_path)]) == 1
    assert "no es una copia" in capsys.readouterr().err


def test_the_public_readme_says_nothing_about_what_stays_private():
    text = (ROOT / "ops" / "publico" / "README.md").read_text(encoding="utf-8")
    for private in ("notas", "ops/", "tests", "legal", "Render", "Neon", "nirkana-app", "secret", "token"):
        assert private.lower() not in text.lower(), private
    assert "nirkana.es" in text and "LICENSE" in text


def test_the_public_keep_alive_workflow_keeps_its_rules_and_tells_no_story():
    text = (ROOT / "ops" / "publico" / "despertar-prueba.yml").read_text(encoding="utf-8")
    for story in ("Neon", "database", "base de datos", "750", "plan gratuito", "free plan", "Render's"):
        assert story not in text, story
    assert "vars.PRUEBA_DE_PAGO != 'si'" in text and "/api/" not in text and "permissions: {}" in text
