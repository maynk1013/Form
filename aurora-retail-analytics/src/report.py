"""Write the executive memo as Markdown and as a single offline HTML file."""

from __future__ import annotations

import html
from pathlib import Path


def _esc(value: object) -> str:
    return html.escape(str(value))


def write_findings(
    path: Path,
    title: str,
    as_of: str,
    kpis: list[tuple[str, str, str]],
    bullets: list[str],
    actions: list[str],
    chart_notes: list[tuple[str, str]],
    tables: list[tuple[str, list[str], list[list[str]]]],
    footnotes: list[str],
) -> None:
    lines = [
        f"# {title}",
        "",
        f"Closed through {as_of}. Figures are computed from the SQLite warehouse. The dataset is synthetic.",
        "",
        "## Scorecard",
        "",
        "| Metric | Value | Definition |",
        "| --- | --- | --- |",
    ]
    for label, value, note in kpis:
        lines.append(f"| {label} | {value} | {note} |")
    lines.extend(["", "## What the numbers say", ""])
    for bullet in bullets:
        lines.append(f"- {bullet}")
    lines.extend(["", "## Actions", ""])
    for index, action in enumerate(actions, start=1):
        lines.append(f"{index}. {action}")
    lines.extend(["", "## Charts", ""])
    for filename, note in chart_notes:
        lines.append(f"- `{filename}` — {note}")
    for table_title, headers, rows in tables:
        lines.extend(["", f"## {table_title}", "", "| " + " | ".join(headers) + " |", "| " + " | ".join(["---"] * len(headers)) + " |"])
        for row in rows:
            lines.append("| " + " | ".join(row) + " |")
    lines.extend(["", "## Notes", ""])
    for note in footnotes:
        lines.append(f"- {note}")
    lines.append("")
    path.write_text("\n".join(lines))


def write_html(
    path: Path,
    title: str,
    kicker: str,
    subtitle: str,
    kpis: list[tuple[str, str, str]],
    bullets: list[str],
    actions: list[str],
    charts: list[tuple[str, str, str]],
    tables: list[tuple[str, list[str], list[list[str]]]],
    footnotes: list[str],
) -> None:
    kpi_html = []
    for label, value, note in kpis:
        kpi_html.append(
            "<article class='kpi'>"
            f"<p class='label'>{_esc(label)}</p>"
            f"<p class='value'>{_esc(value)}</p>"
            f"<p class='note'>{_esc(note)}</p>"
            "</article>"
        )
    bullet_html = "".join(f"<li>{_esc(item)}</li>" for item in bullets)
    action_html = "".join(f"<li>{_esc(item)}</li>" for item in actions)
    chart_html = []
    for filename, heading, caption in charts:
        chart_html.append(
            "<figure>"
            f"<figcaption><strong>{_esc(heading)}</strong> {_esc(caption)}</figcaption>"
            f"<img src='{_esc(filename)}' alt='{_esc(heading)}'>"
            "</figure>"
        )
    table_html = []
    for table_title, headers, rows in tables:
        head = "".join(f"<th>{_esc(header)}</th>" for header in headers)
        body = []
        for row in rows:
            body.append("<tr>" + "".join(f"<td>{_esc(cell)}</td>" for cell in row) + "</tr>")
        table_html.append(
            f"<h2>{_esc(table_title)}</h2>"
            "<table>"
            f"<thead><tr>{head}</tr></thead>"
            f"<tbody>{''.join(body)}</tbody>"
            "</table>"
        )
    notes = "".join(f"<li>{_esc(note)}</li>" for note in footnotes)
    document = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{_esc(title)}</title>
  <style>
    :root {{
      --ink: #1b3a4b;
      --muted: #5c6b73;
      --line: #e4ddd4;
      --paper: #f7f5f2;
      --card: #ffffff;
      --teal: #1f7a8c;
    }}
    * {{ box-sizing: border-box; }}
    body {{
      margin: 0;
      background: var(--paper);
      color: var(--ink);
      font-family: Georgia, "Iowan Old Style", Palatino, "Palatino Linotype", serif;
    }}
    .wrap {{ max-width: 980px; margin: 0 auto; padding: 48px 24px 80px; }}
    .kicker {{
      font-family: "Avenir Next", "Segoe UI", sans-serif;
      letter-spacing: 0.14em;
      text-transform: uppercase;
      font-size: 12px;
      color: var(--teal);
      margin: 0 0 8px;
    }}
    h1 {{ font-weight: 500; letter-spacing: -0.03em; font-size: 40px; margin: 0 0 8px; }}
    .subtitle {{ color: var(--muted); font-size: 18px; margin: 0 0 28px; }}
    .kpis {{ display: grid; grid-template-columns: repeat(3, 1fr); gap: 12px; margin-bottom: 28px; }}
    .kpi {{ background: var(--card); border-top: 3px solid var(--teal); padding: 14px 16px 12px; }}
    .label, .note {{
      font-family: "Avenir Next", "Segoe UI", sans-serif;
      color: var(--muted);
      margin: 0;
    }}
    .label {{ font-size: 12px; letter-spacing: 0.04em; text-transform: uppercase; }}
    .value {{
      font-family: "Avenir Next", "Segoe UI", sans-serif;
      font-size: 28px;
      margin: 6px 0 4px;
      letter-spacing: -0.03em;
    }}
    .note {{ font-size: 13px; }}
    h2 {{ font-weight: 500; font-size: 26px; margin: 36px 0 12px; }}
    li {{ margin: 8px 0; line-height: 1.45; }}
    figure {{ margin: 28px 0; background: var(--card); padding: 16px 16px 8px; }}
    figcaption {{ font-family: "Avenir Next", "Segoe UI", sans-serif; font-size: 14px; margin-bottom: 8px; line-height: 1.4; }}
    img {{ width: 100%; height: auto; display: block; }}
    table {{ width: 100%; border-collapse: collapse; background: var(--card); font-family: "Avenir Next", "Segoe UI", sans-serif; font-size: 14px; }}
    th, td {{ text-align: left; padding: 8px 10px; border-bottom: 1px solid var(--line); }}
    th {{ font-size: 12px; letter-spacing: 0.04em; text-transform: uppercase; color: var(--muted); }}
    footer {{ margin-top: 36px; color: var(--muted); font-family: "Avenir Next", "Segoe UI", sans-serif; font-size: 13px; }}
    @media (max-width: 800px) {{
      .kpis {{ grid-template-columns: 1fr; }}
      h1 {{ font-size: 32px; }}
    }}
    @media print {{
      body {{ background: white; }}
      .kpi, figure, table {{ break-inside: avoid; }}
    }}
  </style>
</head>
<body>
  <main class="wrap">
    <p class="kicker">{_esc(kicker)}</p>
    <h1>{_esc(title)}</h1>
    <p class="subtitle">{_esc(subtitle)}</p>
    <section class="kpis">{''.join(kpi_html)}</section>
    <h2>What the numbers say</h2>
    <ul>{bullet_html}</ul>
    <h2>Actions</h2>
    <ol>{action_html}</ol>
    {''.join(chart_html)}
    {''.join(table_html)}
    <footer>
      <ul>{notes}</ul>
    </footer>
  </main>
</body>
</html>
"""
    path.write_text(document)
