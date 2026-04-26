from __future__ import annotations

import html
import textwrap
from dataclasses import dataclass, field
from pathlib import Path
from typing import Iterable, List, Optional


@dataclass
class Receipt:
    title: str
    columns: int = 42
    image_path: Optional[Path] = None
    lines: List[str] = field(default_factory=list)

    def center(self, text: str = "") -> None:
        self.lines.append(text.center(self.columns) if text else "")

    def text(self, text: str = "") -> None:
        if not text:
            self.lines.append("")
            return
        for line in textwrap.wrap(text, width=self.columns, replace_whitespace=False):
            self.lines.append(line)

    def label(self, label: str, value: str) -> None:
        prefix = f"{label}: "
        width = max(10, self.columns - len(prefix))
        wrapped = textwrap.wrap(value, width=width, replace_whitespace=False) or [""]
        self.lines.append(f"{prefix}{wrapped[0]}")
        for extra in wrapped[1:]:
            self.lines.append(" " * len(prefix) + extra)

    def divider(self, char: str = "-") -> None:
        self.lines.append(char * self.columns)

    def blank_rule(self, label: str, rows: int = 2) -> None:
        self.text(label)
        for _ in range(rows):
            self.lines.append("_" * self.columns)

    def bullet_list(self, items: Iterable[str]) -> None:
        for item in items:
            wrapped = textwrap.wrap(item, width=self.columns - 2, replace_whitespace=False)
            if not wrapped:
                continue
            self.lines.append(f"- {wrapped[0]}")
            for extra in wrapped[1:]:
                self.lines.append(f"  {extra}")

    def to_text(self) -> str:
        return "\n".join(self.lines).rstrip() + "\n"

    def to_html(self) -> str:
        body_lines = "\n".join(html.escape(line) for line in self.lines)
        image_html = ""
        if self.image_path and self.image_path.exists():
            image_html = f'<img class="receipt-image" src="{html.escape(self.image_path.resolve().as_uri())}" alt="Receipt image">'

        return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>{html.escape(self.title)}</title>
  <style>
    :root {{
      color-scheme: light;
      --paper: #fffef7;
      --ink: #191919;
      --edge: #d9d2bf;
    }}
    body {{
      margin: 0;
      min-height: 100vh;
      display: grid;
      place-items: start center;
      background: #ece9df;
      color: var(--ink);
      font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, "Liberation Mono", monospace;
    }}
    main {{
      width: min(384px, calc(100vw - 32px));
      margin: 32px 16px;
      background: var(--paper);
      border: 1px solid var(--edge);
      box-shadow: 0 18px 40px rgba(25, 25, 25, 0.16);
      padding: 24px 18px 32px;
    }}
    .receipt-image {{
      display: block;
      max-width: 100%;
      margin: 0 auto 18px;
      image-rendering: auto;
    }}
    pre {{
      margin: 0;
      white-space: pre-wrap;
      font-size: 14px;
      line-height: 1.32;
    }}
  </style>
</head>
<body>
  <main>
    {image_html}
    <pre>{body_lines}</pre>
  </main>
</body>
</html>
"""
