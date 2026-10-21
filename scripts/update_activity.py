from datetime import date, datetime, timedelta
from html.parser import HTMLParser
from pathlib import Path
import urllib.request
import xml.sax.saxutils as xml

USERNAME = "Scapin961"
ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "assets" / "activity.svg"
URL = f"https://github.com/users/{USERNAME}/contributions"

class ContributionCells(HTMLParser):
    def __init__(self):
        super().__init__()
        self.cells = []

    def handle_starttag(self, tag, attrs):
        if tag != "td":
            return
        attrs = dict(attrs)
        classes = attrs.get("class", "").split()
        raw_date = attrs.get("data-date")
        level = attrs.get("data-level")
        if raw_date and level is not None and "ContributionCalendar-day" in classes:
            try:
                self.cells.append((date.fromisoformat(raw_date), max(0, min(4, int(level)))))
            except (ValueError, TypeError):
                pass

def main():
    request = urllib.request.Request(URL, headers={"User-Agent": "Scapin961-profile-readme/1.0"})
    with urllib.request.urlopen(request, timeout=30) as response:
        page = response.read().decode("utf-8", errors="replace")

    parser = ContributionCells()
    parser.feed(page)
    if not parser.cells:
        raise RuntimeError("GitHub returned no contribution cells; keeping the existing chart.")

    cells = sorted({day: level for day, level in parser.cells}.items())
    first_day = cells[0][0]
    start = first_day - timedelta(days=(first_day.weekday() + 1) % 7)
    weeks = ((cells[-1][0] - start).days // 7) + 1
    colors = ["#161b22", "#0e4429", "#006d32", "#26a641", "#39d353"]
    left, top, step, size = 42, 42, 15, 11
    width = left + weeks * step + 18
    height = 166

    marks = []
    levels = dict(cells)
    for week in range(weeks):
        for weekday in range(7):
            day = start + timedelta(days=week * 7 + weekday)
            if day not in levels:
                continue
            level = levels[day]
            x, y = left + week * step, top + weekday * step
            label = xml.escape(f"{level} contribution level on {day.isoformat()}")
            marks.append(f'<rect x="{x}" y="{y}" width="{size}" height="{size}" rx="3" fill="{colors[level]}"><title>{label}</title></rect>')

    month_labels = []
    last_month = None
    for week in range(weeks):
        day = start + timedelta(days=week * 7)
        if day.month != last_month:
            month_labels.append(f'<text x="{left + week * step}" y="25">{day.strftime("%b")}</text>')
            last_month = day.month

    weekday_labels = [
        '<text x="8" y="68">Mon</text>', '<text x="8" y="98">Wed</text>', '<text x="8" y="128">Fri</text>'
    ]
    legend_x = max(left, width - 160)
    legend = ''.join(f'<rect x="{legend_x + i * 15}" y="{height - 20}" width="11" height="11" rx="3" fill="{color}"/>' for i, color in enumerate(colors))

    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" role="img" aria-labelledby="title desc">
<title id="title">Atividade de Scapin no GitHub</title>
<desc id="desc">Calendário de contribuições dos últimos doze meses, atualizado automaticamente.</desc>
<style>text {{ font-family: ui-monospace, SFMono-Regular, Consolas, monospace; fill: #a6ffb4; font-size: 11px; }} .caption {{ fill: #39d353; font-size: 13px; font-weight: 600; }}</style>
<text class="caption" x="8" y="16">Contribuições públicas no último ano</text>
{''.join(month_labels)}
{''.join(weekday_labels)}
{''.join(marks)}
<text x="{legend_x - 60}" y="{height - 10}">Menos</text>{legend}<text x="{legend_x + 85}" y="{height - 10}">Mais</text>
</svg>'''
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(svg, encoding="utf-8")
    print(f"Updated {OUTPUT} with {len(cells)} daily contribution cells.")

if __name__ == "__main__":
    main()
