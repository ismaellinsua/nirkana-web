"""The website's legal texts (ops/legal.py): published only when complete and escaped, and never with a gap on the live site."""

import json
import shutil
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "ops"))
import legal  # noqa: E402

TERMS_VERSION = legal.TERMS_VERSION
EXAMPLE = json.loads((ROOT / "legal" / "datos.example.json").read_text())


def complete(**changes):
    data = json.loads(json.dumps(EXAMPLE))
    data["subencargados"][-1].update(nombre="Correo Ejemplo SL", ubicacion="Unión Europea (España)")
    data.update(titular="Ana Prueba <b>", nif="12345678Z", domicilio="Calle Mayor 1, 28001 Madrid",
                fecha="7 de octubre de 2026", **changes)
    return data


def test_nothing_is_published_while_a_gap_remains():
    with pytest.raises(legal.LegalError) as missing:
        legal.render(EXAMPLE)
    for field in ("nif", "domicilio", "fecha", "titular", "subencargados"):
        assert field in str(missing.value)
    with pytest.raises(legal.LegalError, match="subencargados"):
        legal.render(complete(subencargados=[]))


def test_published_pages_are_complete_escaped_and_linked(tmp_path):
    docs = tmp_path / "docs"
    shutil.copytree(ROOT / "docs", docs)
    data = tmp_path / "datos.json"
    data.write_text(json.dumps(complete()))
    written = legal.publish(data, docs, pages=legal.PAGES)
    assert {p.name for p in written} >= {"aviso-legal.html", "condiciones.html", "encargado.html", "index.html"}
    for page in ("aviso-legal", "condiciones", "encargado"):
        text = (docs / f"{page}.html").read_text()
        assert "{{" not in text and "PENDIENTE" not in text
        assert "12345678Z" in text and "Ana Prueba &lt;b&gt;" in text and "<b>" not in text
        assert (f"Versión {TERMS_VERSION}" in text) == (page != "aviso-legal")  # what businesses accept is versioned
    assert "<td>Correo Ejemplo SL</td>" in (docs / "encargado.html").read_text()
    for page in [docs / "index.html", docs / "tpv-tiendas" / "index.html"]:
        footer = page.read_text()
        assert footer.count("aviso-legal.html") == 1 and footer.count("condiciones.html\">Condiciones") == 1
    assert legal.link_footers(docs, legal.PAGES) == []  # running it again changes nothing


def test_by_default_only_the_aviso_legal_is_published_and_it_needs_only_its_own_data(tmp_path):
    with pytest.raises(legal.LegalError) as missing:
        legal.render(EXAMPLE, pages=legal.DEFAULT_PAGES)
    message = str(missing.value)
    for field in ("titular", "nif", "domicilio", "fecha"):
        assert field in message
    assert "subencargados" not in message and "proveedor de email" not in message  # not used by the aviso legal

    docs = tmp_path / "docs"
    shutil.copytree(ROOT / "docs", docs)
    data = tmp_path / "datos.json"
    # no sub-processors listed and a conditions-only value still undecided: the aviso legal uses neither
    data.write_text(json.dumps(complete(subencargados=[], meses_tras_baja="PENDIENTE (decidir con la gestoría)")))
    written = legal.publish(data, docs)
    assert not (docs / "condiciones.html").exists() and not (docs / "encargado.html").exists()
    aviso = (docs / "aviso-legal.html").read_text()
    assert "12345678Z" in aviso and "Calle Mayor 1, 28001 Madrid" in aviso and "Ana Prueba &lt;b&gt;" in aviso
    assert "{{" not in aviso and "PENDIENTE" not in aviso
    # the customers' conditions are the app's: the link goes there, never to a page this website does not have
    assert 'href="https://app.nirkana.es/legal/condiciones.html"' in aviso and 'href="/condiciones.html"' not in aviso
    for page in (docs / "index.html", docs / "tpv-tiendas" / "index.html", docs / "404.html"):
        footer = page.read_text()
        assert footer.count("aviso-legal.html") == 1 and "condiciones.html\">Condiciones" not in footer, page
    assert {p.name for p in written} >= {"aviso-legal.html", "index.html", "privacidad.html"}
    assert legal.publish(data, docs) == [docs / "aviso-legal.html"]  # again: only the page itself is rewritten

    # the privacy notice names the same person, with the NIF and address, and the date of the change
    privacy = (docs / "privacidad.html").read_text()
    assert "Ana Prueba &lt;b&gt; , titular".replace(" ,", ",") in privacy or "Ana Prueba &lt;b&gt;, titular" in privacy
    assert "NIF 12345678Z; domicilio: Calle Mayor 1, 28001 Madrid" in privacy
    assert "Última actualización: 7 de octubre de 2026." in privacy and "Ismael Linsua" not in privacy
    assert "<b>" not in privacy

    # publishing everything later adds the conditions' links without duplicating the legal notice's
    data.write_text(json.dumps(complete()))
    legal.publish(data, docs, pages=legal.PAGES)
    footer = (docs / "index.html").read_text()
    assert footer.count("aviso-legal.html") == 1 and footer.count("condiciones.html\">Condiciones") == 1


def test_the_owners_identity_cannot_be_left_blank(tmp_path):
    docs = tmp_path / "docs"
    shutil.copytree(ROOT / "docs", docs)
    data = tmp_path / "datos.json"
    data.write_text(json.dumps(complete(email="  ")))
    with pytest.raises(legal.LegalError, match="email"):
        legal.publish(data, docs)
    assert not (docs / "aviso-legal.html").exists()


def test_the_live_website_never_shows_a_gap():
    for page in (ROOT / "docs").rglob("*.html"):
        text = page.read_text()
        assert "{{" not in text and "PENDIENTE" not in text, page


def test_every_gap_in_the_texts_has_a_value_in_the_example():
    gaps = set()
    for page in (ROOT / "legal").glob("*.html"):
        gaps |= set(legal.GAP.findall(page.read_text()))
    computed = {"contenido", "titulo", "pagina", "version_texto", "tabla_subencargados"}
    assert gaps - computed <= set(EXAMPLE), gaps - computed - set(EXAMPLE)
