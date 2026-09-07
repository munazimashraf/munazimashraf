"""
Generate an animated terminal-style GitHub profile info card.

Output:
    info-card.svg

Run:
    python3 scripts/make_info_card.py
"""

import os
from xml.sax.saxutils import escape

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "..", "info-card.svg")

WIDTH = 820
HEIGHT = 700
lines = [
    ("prompt", "munazimashraf@github:~$ whoami"),
    ("name", "Munazim Ashraf Bhat"),
    ("sep", "────────────────────────────────────────────"),
    ("label", "ROLE       "),
    ("value", "Penetration Tester"),
    ("label", "FOCUS      "),
    ("value", "Web Application Security"),
    ("label", "           "),
    ("value", "Application Security"),
    ("label", "           "),
    ("value", "Manual Security Testing"),
    ("label", "           "),
    ("value", "Vulnerability Assessment"),
    ("label", "           "),
    ("value", "Bug Bounty"),
    ("sep", "────────────────────────────────────────────"),
    ("label", "TOOLS      "),
    ("value", "Burp Suite • Kali Linux • Nmap"),
    ("label", "KNOWLEDGE  "),
    ("value", "OWASP Top 10 • XSS • SQL Injection"),
    ("label", "           "),
    ("value", "Bash • Network Security • Ethical Hacking"),
    ("sep", "────────────────────────────────────────────"),
    ("label", "CURRENT    "),
    ("value", "M.Sc. Information Technology"),
    ("label", "           "),
    ("value", "IUST • 2026—2028"),
    ("sep", "────────────────────────────────────────────"),
    ("label", "STATUS     "),
    ("value", "Hunting bugs. Building security knowledge."),
    ("label", "           "),
    ("value", "Breaking apps safely."),
]

# Layout
LEFT = 34
TOP = 48
LINE_H = 20
FONT_SIZE = 15

svg = []

svg.append(f'''<svg xmlns="http://www.w3.org/2000/svg"
    width="{WIDTH}"
    height="{HEIGHT}"
    viewBox="0 0 {WIDTH} {HEIGHT}">

  <rect width="100%" height="100%" rx="12"
        fill="#0d1117"
        stroke="#30363d"
        stroke-width="2"/>

  <rect x="0" y="0" width="{WIDTH}" height="34"
        rx="12"
        fill="#161b22"/>

  <circle cx="18" cy="17" r="5" fill="#ff5f56"/>
  <circle cx="36" cy="17" r="5" fill="#ffbd2e"/>
  <circle cx="54" cy="17" r="5" fill="#27c93f"/>

  <text x="76" y="22"
        font-family="monospace"
        font-size="12"
        fill="#8b949e">munazimashraf@github</text>
''')

y = TOP

for i, (kind, text) in enumerate(lines):
    safe = escape(text)

    delay = 0.08 * i

    if kind == "prompt":
        fill = "#58a6ff"
        weight = "bold"
    elif kind == "name":
        fill = "#ffffff"
        weight = "bold"
    elif kind == "sep":
        fill = "#30363d"
        weight = "normal"
    elif kind == "label":
        fill = "#7ee787"
        weight = "bold"
    else:
        fill = "#c9d1d9"
        weight = "normal"

    svg.append(f'''
  <text x="{LEFT}" y="{y}"
        font-family="monospace"
        font-size="{FONT_SIZE}"
        font-weight="{weight}"
        fill="{fill}"
        opacity="0">
    {safe}
    <animate attributeName="opacity"
             from="0" to="1"
             begin="{delay:.2f}s"
             dur="0.25s"
             fill="freeze"/>
  </text>
''')

    y += LINE_H

# Animated cursor at the bottom
cursor_y = HEIGHT - 30

svg.append(f'''
  <rect x="{LEFT + 190}" y="{cursor_y - 15}"
        width="9" height="17"
        fill="#7ee787">
    <animate attributeName="opacity"
             values="1;0;1"
             dur="0.9s"
             repeatCount="indefinite"/>
  </rect>
''')

svg.append("</svg>")

with open(OUT, "w", encoding="utf-8") as f:
    f.write("\n".join(svg))

print("wrote", os.path.abspath(OUT))
