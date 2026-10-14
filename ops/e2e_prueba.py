"""What a visitor lives through when pressing «Probar gratis», in a real browser, against the published site.

    python ops/e2e_prueba.py [https://nirkana.es/]

Opens the site, presses the first visible «Probar gratis», and measures: when the waiting screen appears, when the visitor
lands on the trial, and when the trial's own page is usable. Meant to be run when the free trial is asleep (it sleeps after
15 minutes without visits); it only reads, never signs up. Exit code 1 when the trial never became usable in 4 minutes.
"""

import re
import sys
import time

from playwright.sync_api import TimeoutError as PlaywrightTimeout
from playwright.sync_api import sync_playwright

SITE = sys.argv[1] if len(sys.argv) > 1 else "https://nirkana.es/"
USABLE_WITHIN_S = 240


def main() -> int:
    with sync_playwright() as pw:
        browser = pw.chromium.launch(channel="chrome")
        page = browser.new_page(viewport={"width": 1280, "height": 800})
        page.goto(SITE, wait_until="load")
        link = page.locator("a[data-trial]:visible").first
        print(f"Botón: «{link.inner_text().strip()}» → {link.get_attribute('href')}")
        started = time.time()
        link.click()

        try:
            page.locator("dialog.trial-wait[open]").wait_for(timeout=3000)
            print(f"{time.time() - started:6.1f} s  sale la pantalla «Preparando tu prueba gratuita»")
        except PlaywrightTimeout:
            print(f"{time.time() - started:6.1f} s  no salió pantalla de espera (la prueba estaba despierta, o falló)")

        try:
            page.wait_for_url(re.compile(r"^https://[^/]*onrender\.com/"), timeout=120_000)
        except PlaywrightTimeout:
            print("  FALLA: no se llevó al visitante a la prueba en 2 minutos")
            return 1
        print(f"{time.time() - started:6.1f} s  el visitante llega a la prueba ({page.url})")

        # the trial's own page is usable once the app answers (the host's waiting page has no «NirKanA» in its title)
        deadline = started + USABLE_WITHIN_S
        while time.time() < deadline:
            try:
                title = page.title()
            except Exception:  # the page is reloading
                title = ""
            if "NirKanA" in title:
                print(f"{time.time() - started:6.1f} s  la prueba está usable («{title}»)")
                return 0
            time.sleep(2)
        print(f"  FALLA: la prueba no estuvo usable en {USABLE_WITHIN_S} s")
        return 1


if __name__ == "__main__":
    sys.exit(main())
