"""Throwaway check of the PUBLISHED site (not the repository) in a real Chrome: are the live files the ones in docs/, and does the
new design behave on the live page? Prints one line per check; exit code 1 if any fails."""

import hashlib
import sys
from pathlib import Path

from playwright.sync_api import sync_playwright

SITE = "https://nirkana.es"
DOCS = Path("docs")
bad = []


def check(ok, text):
    print(("  ok     " if ok else "  FALLA  ") + text, flush=True)
    if not ok:
        bad.append(text)


# (url path, file in docs/)
SAME = [("/", "index.html"), ("/assets/site.css", "assets/site.css"), ("/assets/site.js", "assets/site.js"),
        ("/tpv-restaurantes/", "tpv-restaurantes/index.html"), ("/tpv-tiendas/", "tpv-tiendas/index.html"),
        ("/programa-facturacion-autonomos/", "programa-facturacion-autonomos/index.html"),
        ("/tpv-tienda-online/", "tpv-tienda-online/index.html"),
        ("/assets/img/panel.webp", "assets/img/panel.webp"), ("/assets/img/movil.webp", "assets/img/movil.webp"),
        ("/assets/img/shots/mesas-c.webp", "assets/img/shots/mesas-c.webp"), ("/assets/img/shots/vender-c.webp", "assets/img/shots/vender-c.webp"),
        ("/assets/img/shots/agenda-c.webp", "assets/img/shots/agenda-c.webp"), ("/assets/img/shots/productos-c.webp", "assets/img/shots/productos-c.webp"),
        ("/demo/index.html", "demo/index.html")]


def fake_counter(route):  # nothing may reach the visit counter from a test
    route.fulfill(status=200, content_type="image/gif", body=b"GIF89a")


def open_page(browser, path, width, height):
    errors = []
    ctx = browser.new_context(viewport={"width": width, "height": height}, locale="es-ES", reduced_motion="reduce")
    ctx.route("https://*.goatcounter.com/**", fake_counter)
    page = ctx.new_page()
    page.on("console", lambda m: errors.append(m.text) if m.type == "error" else None)
    page.on("pageerror", lambda e: errors.append(str(e)))
    page.goto(SITE + path, wait_until="load")
    page.wait_for_timeout(1500)
    return ctx, page, errors


def scroll_to(page, selector, extra=0):
    page.evaluate("([s, e]) => window.scrollTo(0, document.querySelector(s).getBoundingClientRect().top + window.scrollY + e)", [selector, extra])
    page.wait_for_timeout(500)


with sync_playwright() as pw:
    browser = pw.chromium.launch(channel="chrome")
    print("== 1. Lo publicado es lo del repositorio (SHA-256) ==", flush=True)
    api = browser.new_context().request
    for url, name in SAME:
        resp = api.get(SITE + url)
        local = hashlib.sha256((DOCS / name).read_bytes()).hexdigest()
        live = hashlib.sha256(resp.body()).hexdigest() if resp.ok else "-"
        check(resp.ok and live == local, f"{url} → HTTP {resp.status}, {'igual' if live == local else 'DISTINTO'} que docs/{name}")

    print("== 2. Escritorio 1440 px: portada y cabecera ==", flush=True)
    ctx, page, errors = open_page(browser, "/", 1440, 900)
    top = page.locator(".top")
    check("on-dark" in (top.get_attribute("class") or ""), "arriba del todo la cabecera es oscura (sobre la portada)")
    scroll_to(page, "#sectores", 300)
    check("on-dark" not in (top.get_attribute("class") or ""), "sobre la banda clara de sectores la cabecera es clara")
    scroll_to(page, "#funciones", 380)
    check("on-dark" in (top.get_attribute("class") or ""), "sobre la historia de funciones (oscura) la cabecera es oscura")
    scroll_to(page, "#movil", 200)
    check("on-dark" in (top.get_attribute("class") or ""), "sobre la banda del móvil (oscura) la cabecera es oscura")
    scroll_to(page, "#precio", 0)
    check("on-dark" not in (top.get_attribute("class") or ""), "sobre el precio la cabecera es clara")
    check(page.evaluate("getComputedStyle(document.querySelector('.hero-sectors')).display") == "grid", "los sectores de la portada van en cuadrícula 2×2")
    check(page.evaluate("getComputedStyle(document.querySelector('.swipe-hint')).display") == "none", "el aviso «Desliza» no sale en escritorio")
    ratio = page.evaluate("(() => { const c = document.querySelector('.c2'); return c.offsetTop / c.offsetParent.clientHeight; })()")
    check(abs(ratio - 0.68) < 0.03, f"la etiqueta «Solomillo…» está en su sitio nuevo ({ratio:.2f} del alto)")
    check(page.evaluate("getComputedStyle(document.querySelector('.price-card'), '::before').height") == "5px", "la tarjeta de precio lleva su franja de color")
    check(not errors, f"sin errores de consola en la portada ({errors[:2]})")
    ctx.close()

    print("== 3. Móvil 390 px: galería en carrusel ==", flush=True)
    ctx, page, errors = open_page(browser, "/", 390, 844)
    check(page.evaluate("getComputedStyle(document.querySelector('.bento')).display") == "flex", "la galería es una fila (carrusel)")
    check(page.evaluate("getComputedStyle(document.querySelector('.bento')).overflowX") == "auto", "la fila se desliza con el dedo")
    check(page.evaluate("getComputedStyle(document.querySelector('.swipe-hint')).display") == "flex", "sale el aviso «Desliza para ver más»")
    height = page.evaluate("document.documentElement.scrollHeight")
    check(height < 21500, f"la portada del móvil mide {height} px (antes 23148)")
    check(page.evaluate("document.documentElement.scrollWidth <= window.innerWidth"), "no hay desplazamiento horizontal de la página")
    check(not errors, f"sin errores de consola en el móvil ({errors[:2]})")
    ctx.close()

    print("== 4. Páginas de sector: captura en la portada ==", flush=True)
    for path in ("/tpv-restaurantes/", "/tpv-tiendas/", "/programa-facturacion-autonomos/", "/tpv-tienda-online/"):
        for width, height in ((1440, 900), (390, 844)):
            ctx, page, errors = open_page(browser, path, width, height)
            img = page.locator(".sub-hero-shot img")
            loaded = img.count() == 1 and img.evaluate("i => i.complete && i.naturalWidth === 1200")
            columns = len(page.evaluate("getComputedStyle(document.querySelector('.sub-hero-grid')).gridTemplateColumns").split())
            check(loaded and columns == (2 if width > 900 else 1) and not errors and
                  page.evaluate("document.documentElement.scrollWidth <= window.innerWidth"),
                  f"{path} a {width} px: captura cargada, {columns} columna(s), sin errores ni desbordes {errors[:1]}")
            ctx.close()
    browser.close()

print(f"\n{len(bad)} fallo(s)")
sys.exit(1 if bad else 0)
