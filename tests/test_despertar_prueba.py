"""The workflow that keeps the free trial awake: it must never reach the database and must stay inside the free hours."""

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
WORKFLOW = (ROOT / ".github/workflows/despertar-prueba.yml").read_text(encoding="utf-8")
SITE = (ROOT / "docs/assets/site.js").read_text(encoding="utf-8")

# Render gives 750 free instance hours a month to the whole workspace; leave room for visitors at night.
MAX_AWAKE_HOURS_A_DAY = 17


def ping_url():
    code = "\n".join(line for line in WORKFLOW.splitlines() if not line.lstrip().startswith("#"))
    urls = re.findall(r"https://[^\s'\";]+", code)
    assert len(urls) == 1, urls
    return urls[0]


def test_it_asks_the_same_address_the_website_sends_visitors_to():
    trial = re.search(r'const TRIAL_URL = "([^"]*)";', SITE).group(1)
    assert trial and ping_url().startswith(trial + "/")


def test_it_asks_for_a_static_image_never_for_anything_that_reaches_the_database():
    path = "/" + ping_url().split("/", 3)[3]
    assert path.startswith("/icons/") and path.endswith(".svg"), path
    assert "/api/" not in path


def test_it_runs_every_5_minutes_or_more_and_only_during_the_day():
    schedules = re.findall(r'cron:\s*"([^"]+)"', WORKFLOW)
    assert len(schedules) == 1, schedules
    minute, hour, day, month, weekday = schedules[0].split()
    assert (day, month, weekday) == ("*", "*", "*")
    step = int(re.fullmatch(r"\d+-\d+/(\d+)", minute).group(1))
    assert step >= 5, "GitHub does not run schedules more often than every 5 minutes"
    first, last = map(int, re.fullmatch(r"(\d+)-(\d+)", hour).groups())
    assert 0 <= first <= last <= 23
    assert last - first + 1 <= MAX_AWAKE_HOURS_A_DAY, "it would eat Render's free hours"


def test_it_can_be_switched_off_and_never_fails_the_run():
    assert "vars.PRUEBA_DE_PAGO != 'si'" in WORKFLOW
    assert "::warning::" in WORKFLOW
    assert re.search(r"^permissions: \{\}$", WORKFLOW, re.M), "it needs no access to the repository"
