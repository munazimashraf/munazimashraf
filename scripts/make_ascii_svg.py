import os
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))

INP = os.path.join(HERE, "..", "data", "source-prepped.png")
OUT = os.path.join(HERE, "..", "avi-ascii.svg")

RAMP = " .`:-=+*cs#%@"

COLS = 100
ROWS = 53

FONT_SIZE = 10
CHAR_W = 6
LINE_H = 10

img = Image.open(INP).convert("L")

# Resize while compensating for the tall shape of monospace characters.
img = img.resize((COLS, ROWS))

pixels = img.load()

lines = []

for y in range(ROWS):
    chars = []

    for x in range(COLS):
        value = pixels[x, y]

        # White = sparse, black = dense.
        idx = int((255 - value) / 255 * (len(RAMP) - 1))
        idx = max(0, min(len(RAMP) - 1, idx))

        chars.append(RAMP[idx])

    lines.append("".join(chars))


WIDTH = COLS * CHAR_W
HEIGHT = ROWS * LINE_H

svg = []

svg.append(f'''<svg xmlns="http://www.w3.org/2000/svg"
    width="{WIDTH}"
    height="{HEIGHT}"
    viewBox="0 0 {WIDTH} {HEIGHT}">

<rect width="100%" height="100%" fill="white"/>

<style>
.ascii {{
    font-family: "Courier New", monospace;
    font-size: {FONT_SIZE}px;
    font-weight: 600;
    fill: #111;
    white-space: pre;
}}

.reveal {{
    animation-name: reveal;
    animation-duration: 0.8s;
    animation-timing-function: linear;
    animation-fill-mode: forwards;
}}

@keyframes reveal {{
    from {{
        clip-path: inset(0 100% 0 0);
    }}
    to {{
        clip-path: inset(0 0 0 0);
    }}
}}
</style>
''')

# Fallback: the complete ASCII art exists in the SVG.
# Each row is then revealed with CSS animation.
for y, line in enumerate(lines):
    safe_line = line.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")

    delay = y * 0.055

    svg.append(
        f'''<text
    x="0"
    y="{(y + 1) * LINE_H}"
    class="ascii reveal"
    style="animation-delay: {delay:.3f}s">{safe_line}</text>
'''
    )

svg.append("</svg>")

with open(OUT, "w", encoding="utf-8") as f:
    f.write("".join(svg))

print("wrote", OUT)
print(f"grid: {COLS} x {ROWS}")
