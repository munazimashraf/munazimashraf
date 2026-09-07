"""
Render an animated GitHub-style contribution heatmap.

Input:
    data/contributions.json

Output:
    contrib-heatmap.svg

No JavaScript. Animation is entirely inside the SVG.
"""

import json
import os
from datetime import date, timedelta


HERE = os.path.dirname(os.path.abspath(__file__))

INPUT = os.path.join(
    HERE, "..", "data", "contributions.json"
)

OUTPUT = os.path.join(
    HERE, "..", "contrib-heatmap.svg"
)


# ------------------------------------------------------------
# Appearance
# ------------------------------------------------------------

WIDTH = 860
HEIGHT = 250

BG = "#0d1117"
BORDER = "#30363d"
TEXT = "#8b949e"
TEXT_BRIGHT = "#c9d1d9"

LEVEL_COLORS = {
    0: "#161b22",
    1: "#0e4429",
    2: "#006d32",
    3: "#26a641",
    4: "#39d353",
}

CELL = 12
GAP = 3

GRID_X = 70
GRID_Y = 75

ANIMATION_DURATION = 0.45
ANIMATION_STAGGER = 0.018


# ------------------------------------------------------------
# Load contribution data
# ------------------------------------------------------------

with open(INPUT, "r", encoding="utf-8") as f:
    data = json.load(f)


USERNAME = data["username"]
TOTAL = data.get(
    "total",
    sum(x["count"] for x in data["contributions"])
)

items = data["contributions"]


# ------------------------------------------------------------
# Convert to dictionary
# ------------------------------------------------------------

contributions = {}

for item in items:
    contributions[item["date"]] = {
        "count": item["count"],
        "level": item["level"],
    }


# ------------------------------------------------------------
# Build a 53-week calendar
#
# GitHub's contribution calendar is Sunday -> Saturday.
# We take the latest 53 weeks represented by the fetched data.
# ------------------------------------------------------------

dates = sorted(
    date.fromisoformat(x["date"])
    for x in items
)

last_date = dates[-1]

# Find the Sunday containing the last date.
last_sunday = last_date - timedelta(
    days=(last_date.weekday() + 1) % 7
)

# 53 columns = 371 days.
first_sunday = last_sunday - timedelta(
    weeks=52
)


# ------------------------------------------------------------
# SVG helpers
# ------------------------------------------------------------

def esc(value):
    return (
        str(value)
        .replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
    )


svg = []

svg.append(
    f'''<svg xmlns="http://www.w3.org/2000/svg"
    width="{WIDTH}"
    height="{HEIGHT}"
    viewBox="0 0 {WIDTH} {HEIGHT}">

    <rect
        x="0"
        y="0"
        width="{WIDTH}"
        height="{HEIGHT}"
        rx="10"
        fill="{BG}"
        stroke="{BORDER}"
        stroke-width="1"
    />

    <style>
        .terminal {{
            font-family:
                "SFMono-Regular",
                "Menlo",
                "Monaco",
                "Consolas",
                monospace;
        }}

        .cell {{
            transform-box: fill-box;
            transform-origin: center;
            animation: reveal 0.45s ease-out forwards;
            opacity: 0;
        }}

        @keyframes reveal {{
            0% {{
                opacity: 0;
                transform: scale(0.2);
            }}

            70% {{
                opacity: 1;
                transform: scale(1.08);
            }}

            100% {{
                opacity: 1;
                transform: scale(1);
            }}
        }}

        .cursor {{
            animation: blink 1s steps(2, start) infinite;
        }}

        @keyframes blink {{
            50% {{
                opacity: 0;
            }}
        }}
    </style>
'''
)


# ------------------------------------------------------------
# Terminal header
# ------------------------------------------------------------

svg.append(
    f'''
    <text
        x="24"
        y="30"
        class="terminal"
        font-size="14"
        fill="{TEXT}"
    >{esc(USERNAME)}@github:~$ contributions --year</text>

    <text
        x="24"
        y="51"
        class="terminal"
        font-size="16"
        font-weight="bold"
        fill="{TEXT_BRIGHT}"
    >{last_date.year}</text>

    <text
        x="72"
        y="51"
        class="terminal cursor"
        font-size="16"
        fill="{LEVEL_COLORS[4]}"
    >█</text>

    <text
        x="WIDTH_PLACEHOLDER"
        y="51"
        class="terminal"
        font-size="13"
        fill="{TEXT}"
    ></text>
'''
)

# Replace placeholder with right-aligned total.
svg[-1] = svg[-1].replace(
    "x=\"WIDTH_PLACEHOLDER\"",
    f'x="{WIDTH - 24}" text-anchor="end"'
)

svg.append(
    f'''
    <text
        x="{WIDTH - 24}"
        y="30"
        class="terminal"
        font-size="13"
        fill="{TEXT}"
        text-anchor="end"
    >{TOTAL} contributions in the last year</text>
'''
)


# ------------------------------------------------------------
# Day labels
# ------------------------------------------------------------

for row, label in [
    (1, "Mon"),
    (3, "Wed"),
    (5, "Fri"),
]:
    y = GRID_Y + row * (CELL + GAP) + 10

    svg.append(
        f'''
        <text
            x="24"
            y="{y}"
            class="terminal"
            font-size="10"
            fill="{TEXT}"
        >{label}</text>
        '''
    )


# ------------------------------------------------------------
# Month labels
# ------------------------------------------------------------

previous_month = None

for col in range(53):

    sunday = first_sunday + timedelta(weeks=col)

    # Don't label months outside our actual calendar range.
    if sunday.month != previous_month:

        month_name = sunday.strftime("%b")

        x = GRID_X + col * (CELL + GAP)

        svg.append(
            f'''
            <text
                x="{x}"
                y="{GRID_Y - 10}"
                class="terminal"
                font-size="10"
                fill="{TEXT}"
            >{month_name}</text>
            '''
        )

        previous_month = sunday.month


# ------------------------------------------------------------
# Draw contribution cells
# ------------------------------------------------------------

animation_index = 0

for col in range(53):

    sunday = first_sunday + timedelta(weeks=col)

    for row in range(7):

        current = sunday + timedelta(days=row)

        key = current.isoformat()

        info = contributions.get(
            key,
            {
                "count": 0,
                "level": 0,
            }
        )

        level = max(
            0,
            min(4, int(info["level"]))
        )

        count = info["count"]

        x = GRID_X + col * (CELL + GAP)
        y = GRID_Y + row * (CELL + GAP)

        delay = animation_index * ANIMATION_STAGGER

        color = LEVEL_COLORS[level]

        # Tooltip.
        if count == 0:
            tooltip = f"No contributions on {current}"
        elif count == 1:
            tooltip = f"1 contribution on {current}"
        else:
            tooltip = f"{count} contributions on {current}"

        svg.append(
            f'''
            <g
                class="cell"
                style="animation-delay:{delay:.3f}s"
            >
                <rect
                    x="{x}"
                    y="{y}"
                    width="{CELL}"
                    height="{CELL}"
                    rx="2"
                    fill="{color}"
                >
                    <title>{esc(tooltip)}</title>
                </rect>
            </g>
            '''
        )

        animation_index += 1


# ------------------------------------------------------------
# Legend
# ------------------------------------------------------------

legend_y = GRID_Y + 7 * (CELL + GAP) + 26

svg.append(
    f'''
    <text
        x="{GRID_X}"
        y="{legend_y}"
        class="terminal"
        font-size="10"
        fill="{TEXT}"
    >Less</text>
    '''
)

for i in range(5):

    x = GRID_X + 38 + i * (CELL + GAP)

    svg.append(
        f'''
        <rect
            x="{x}"
            y="{legend_y - 10}"
            width="{CELL}"
            height="{CELL}"
            rx="2"
            fill="{LEVEL_COLORS[i]}"
        />
        '''
    )

svg.append(
    f'''
    <text
        x="{GRID_X + 38 + 5 * (CELL + GAP) + 6}"
        y="{legend_y}"
        class="terminal"
        font-size="10"
        fill="{TEXT}"
    >More</text>
    '''
)


# ------------------------------------------------------------
# Footer
# ------------------------------------------------------------

svg.append(
    f'''
    <text
        x="{WIDTH - 24}"
        y="{HEIGHT - 16}"
        class="terminal"
        font-size="10"
        fill="{TEXT}"
        text-anchor="end"
    >github.com/{esc(USERNAME)}</text>
'''
)


svg.append("</svg>")


# ------------------------------------------------------------
# Write SVG
# ------------------------------------------------------------

with open(OUTPUT, "w", encoding="utf-8") as f:
    f.write("".join(svg))


print(f"wrote {OUTPUT}")
print(f"total contributions: {TOTAL}")
print("grid: 53 weeks x 7 days")
