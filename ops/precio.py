"""The «desde N € al mes» price of the home page, in one place: read it, check it, change it.

    python ops/precio.py        # shows the price and checks that every place agrees
    python ops/precio.py 60     # sets it to 60 everywhere

The number appears in eight places of docs/index.html: six sentences (the line under the hero button, the price section,
the calculator, the «¿Cuánto cuesta?» answer and its copy in the FAQPage data) and the two prices of the Offer data that
search engines read. Changing them by hand and missing one would leave the page contradicting itself. The price you charge
by card is the one set in Stripe (Product → Price): change it there too, or the web and the checkout will disagree.
"""

import re
import sys
from pathlib import Path

HOME = Path(__file__).resolve().parent.parent / "docs" / "index.html"
SENTENCE = re.compile(r"(desde )(\d+)( € al mes)", re.IGNORECASE)
OFFER = re.compile(r'("price": ")(\d+)(")')
EXPECTED = {"frases": 6, "datos de buscadores": 2}


def found(html: str) -> dict[str, list[int]]:
    return {"frases": [int(m.group(2)) for m in SENTENCE.finditer(html)],
            "datos de buscadores": [int(m.group(2)) for m in OFFER.finditer(html)]}


def problems(html: str) -> list[str]:
    """What is wrong with the price in this page: a missing place, or two different numbers."""
    places = found(html)
    out = [f"Se esperaban {EXPECTED[kind]} cifras en {kind} y hay {len(numbers)}"
           for kind, numbers in places.items() if len(numbers) != EXPECTED[kind]]
    everything = {n for numbers in places.values() for n in numbers}
    if len(everything) > 1:
        out.append(f"La página dice precios distintos: {sorted(everything)}")
    return out


def current(html: str) -> int:
    return found(html)["frases"][0]


def change(html: str, price: int) -> str:
    if not 1 <= price <= 999:
        raise ValueError("El precio debe ser un número entero entre 1 y 999")
    html = SENTENCE.sub(lambda m: f"{m.group(1)}{price}{m.group(3)}", html)
    return OFFER.sub(lambda m: f"{m.group(1)}{price}{m.group(3)}", html)


def main(argv: list[str]) -> int:
    html = HOME.read_text(encoding="utf-8")
    if len(argv) > 1:
        try:
            html = change(html, int(argv[1]))
        except ValueError as error:
            print(f"ERROR: {error}")
            return 2
        HOME.write_text(html, encoding="utf-8")
    found_problems = problems(html)
    for problem in found_problems:
        print(f"ERROR: {problem}")
    if not found_problems:
        print(f"Precio de la web: desde {current(html)} € al mes (en las 8 cifras de docs/index.html).")
        if len(argv) > 1:
            print("Recuerda: el precio de cobro con tarjeta es el de Stripe (Product → Price); cámbialo allí también.")
    return 1 if found_problems else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
