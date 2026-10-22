"""Publica el sitio: copia a un repositorio público solo lo que se ve en nirkana.es, y nada más.

Este repositorio (el de trabajo) es privado: aquí están las notas, el código de apoyo, las pruebas y las plantillas. El repositorio
público (nirkana-sitio) es solo el escaparate: la carpeta docs/ con las páginas, los estilos, los scripts y las imágenes que cualquiera
puede abrir en nirkana.es, un README corto, una licencia de «todos los derechos reservados» que no nombra nada de lo privado (la
de este repositorio sí) y el flujo que mantiene despierta la prueba de 24 horas.

    python ops/publicar_sitio.py ../nirkana-sitio            # copia y deja los cambios sin confirmar, para revisarlos
    python ops/publicar_sitio.py ../nirkana-sitio --check    # no escribe nada: sale con error si la copia pública no coincide

Reglas que el script hace cumplir (y prueba tests/test_publicar_sitio.py):
  - Solo se copian archivos de tipos de la web (HTML, CSS, JS, imágenes, la plantilla de Excel, robots.txt y sitemap.xml). Una nota
    .md, un .py, un .json o un .env en docs/ detiene el proceso: no se publica «por si acaso».
  - La copia pública queda exactamente igual que lo permitido: todo lo que no esté en la lista (un archivo que se coló a mano, una
    carpeta vieja) se borra de ella. El historial de Git de la copia pública no se toca.
  - docs/CNAME es del repositorio público (lo escribe GitHub al poner el dominio en Settings → Pages): ni se copia ni se borra.
"""

from __future__ import annotations

import argparse
import filecmp
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DOCS = ROOT / "docs"
TEMPLATES = ROOT / "ops" / "publico"

EXTENSIONS = {".html", ".css", ".js", ".svg", ".png", ".jpg", ".jpeg", ".webp", ".ico", ".webmanifest", ".xlsx", ".xml", ".txt"}
NAMES = {".nojekyll"}
OWNED_BY_THE_PUBLIC_REPOSITORY = {"docs/CNAME"}   # GitHub writes it when the domain is set in Settings → Pages
EXCLUDED_FOLDERS = {"caja"}                       # the offline cash register of the previous product: not part of the site any more


class PublishError(Exception):
    pass


def files_under(folder: Path) -> list[Path]:
    return sorted(path for path in folder.rglob("*") if path.is_file())


def expected(docs: Path = DOCS, templates: Path = TEMPLATES) -> dict[str, Path]:
    """The whole public tree: relative path in the public repository → the file in this one it comes from."""
    tree: dict[str, Path] = {}
    forbidden = []
    for path in files_under(docs):
        relative = path.relative_to(docs).as_posix()
        if relative.split("/")[0] in EXCLUDED_FOLDERS or f"docs/{relative}" in OWNED_BY_THE_PUBLIC_REPOSITORY:
            continue
        if path.name not in NAMES and path.suffix.lower() not in EXTENSIONS:
            forbidden.append(f"docs/{relative}")
            continue
        tree[f"docs/{relative}"] = path
    if forbidden:
        raise PublishError("en docs/ hay archivos que no son de la web y no se publican (muévelos fuera de docs/): " + ", ".join(forbidden))
    tree["README.md"] = templates / "README.md"
    tree["LICENSE"] = templates / "LICENSE"
    tree[".github/workflows/despertar-prueba.yml"] = templates / "despertar-prueba.yml"
    for relative, source in tree.items():
        if not source.is_file():
            raise PublishError(f"falta {source} (para {relative})")
    return tree


def present(destination: Path) -> set[str]:
    """What the public checkout holds now (everything except Git's own folder)."""
    return {path.relative_to(destination).as_posix() for path in files_under(destination) if ".git" not in path.relative_to(destination).parts[:1]}


def differences(destination: Path, tree: dict[str, Path]) -> tuple[list[str], list[str], list[str]]:
    """(to add, to change, to remove) so that `destination` becomes exactly `tree`."""
    now = present(destination)
    add = sorted(relative for relative in tree if relative not in now)
    change = sorted(relative for relative in tree if relative in now and not filecmp.cmp(tree[relative], destination / relative, shallow=False))
    remove = sorted(relative for relative in now - set(tree) if relative not in OWNED_BY_THE_PUBLIC_REPOSITORY)
    return add, change, remove


def apply(destination: Path, tree: dict[str, Path]) -> tuple[list[str], list[str], list[str]]:
    add, change, remove = differences(destination, tree)
    for relative in remove:
        (destination / relative).unlink()
    for relative in add + change:
        target = destination / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(tree[relative], target)
    for folder in sorted((p for p in destination.rglob("*") if p.is_dir() and ".git" not in p.relative_to(destination).parts[:1]), reverse=True):
        if not any(folder.iterdir()):
            folder.rmdir()
    return add, change, remove


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("destino", type=Path, help="copia (clon) del repositorio público")
    parser.add_argument("--check", action="store_true", help="no escribe: falla si la copia pública no coincide")
    args = parser.parse_args(argv)
    destination = args.destino.resolve()
    if not (destination / ".git").exists():
        print(f"ERROR: {destination} no es una copia (clon) de un repositorio de Git", file=sys.stderr)
        return 1
    try:
        tree = expected()
    except PublishError as error:
        print(f"ERROR: {error}", file=sys.stderr)
        return 1
    if args.check:
        add, change, remove = differences(destination, tree)
        for label, names in (("falta", add), ("distinto", change), ("sobra", remove)):
            for name in names:
                print(f"{label}: {name}", file=sys.stderr)
        return 1 if add or change or remove else 0
    add, change, remove = apply(destination, tree)
    print(f"{destination.name}: {len(add)} archivos nuevos, {len(change)} cambiados y {len(remove)} borrados. Revisa con «git status» y confirma.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
