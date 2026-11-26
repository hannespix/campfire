#!/usr/bin/env python3
"""Regenerate the stage layout for the original Campfire PixiNotes talk."""

from base64 import b64encode
from html import escape
from math import ceil
from pathlib import Path
import json
import re

ROOT = Path(__file__).resolve().parents[1]
WIDTH = 1424
GAP = 128
TOP = 1096
RETURN = 2296

CHAPTERS = (
    ("I", ("The gathering",), "Welcome · One word", "#ffe06a",
     ("The gathering", "One word")),
    ("II", ("Old fires",), "AI history · Myth or Fact?", "#f6b875",
     ("Old fires", "Myth or Fact?", "Rumours")),
    ("III", ("Words by", "the fire"), "Tokens · Context · Glossary", "#c7df79",
     ("Words by the fire", "Token Oracle", "Context Circle", "Words · 30 terms")),
    ("IV", ("Kindling",), "One small build · Prompt Forge", "#ffc756",
     ("Kindling", "Prompt Forge")),
    ("V", ("Many fires",), "GitHub · Git Time Machine", "#c7df79",
     ("Many fires", "Git Time Machine")),
    ("VI", ("A fire for", "VAVE"), "vave.log · Discuss the ideas", "#c7b6fa",
     ("A fire for VAVE", "vave.log: ideas, not decisions")),
    ("VII", ("Smoke",), "Risks · Fireplace Check", "#f8a488",
     ("Smoke", "Fireplace Check")),
    ("VIII", ("Embers",), "Ideas · Booth Builder · Questions", "#ffd37a",
     ("Ideas for spaces", "Booth Builder", "Try on Monday (within VAVE's AI rules, with dummy data)",
      "Your questions", "Embers")),
)

# x, y, width and height within the station. The final chapter has a longer tool row.
SINGLE_TOOL = ((356, 504, 712, 504),)
TOOLS = (
    SINGLE_TOOL,
    ((44, 504, 648, 508), (732, 504, 648, 508)),
    ((44, 504, 416, 508), (504, 504, 416, 508), (964, 504, 416, 508)),
    ((276, 504, 872, 508),),
    ((276, 504, 872, 508),),
    ((44, 504, 1336, 508),),
    ((276, 504, 872, 508),),
)

BORDERS = ("#ac9855", "#ad906b", "#879b6b", "#ae9056",
           "#889968", "#9a8bb5", "#ac8576", "#a9915b")


def uri(svg: str) -> str:
    return "data:image/svg+xml;base64," + b64encode(svg.encode()).decode("ascii")


def cover(index: int, font: str) -> str:
    roman, lines, subtitle, accent, _ = CHAPTERS[index]
    label = " ".join(lines)
    original = (ROOT / "art" / f"chapter-{index + 1}.svg").read_text()
    # Keep the original pixel scene and its reduced-motion CSS. The wide card
    # supplies its own title, so crop out the text at the top of the square art.
    scene = re.sub(
        r"<svg\b[^>]*>",
        '<svg x="638" y="122" width="592" height="448" viewBox="4 40 152 115" '
        'shape-rendering="crispEdges" overflow="hidden">',
        original, count=1,
    )
    title_size = 108 if index == 0 else 121
    y = 373 if len(lines) == 1 else 315
    title = "".join(
        f'<text x="64" y="{y + n * 101}">{escape(line)}</text>'
        for n, line in enumerate(lines)
    )
    progress = "".join(
        f'<rect x="{64 + n * 39}" y="628" width="29" height="9" '
        f'fill="{accent if n == index else "#658045" if n < index else "#30432b"}"/>'
        for n in range(len(CHAPTERS))
    )
    return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1280 720" width="1280" height="720" role="img">
<title>{roman} · {escape(label)}</title>
<desc>{escape(subtitle)}</desc>
<style>{font} .stage-type {{ font-family: "Jersey 10", "Courier New", monospace; }}
.stage-label {{ font-family: system-ui, sans-serif; }}</style>
<rect width="1280" height="720" fill="#0a130a"/>
<path d="M16 16H1264V704H16Z" fill="none" stroke="#30432b" stroke-width="4"/>
<path d="M16 86V16H86 M1194 704H1264V634" fill="none" stroke="{accent}" stroke-width="4"/>
<path d="M64 110H546" stroke="#30432b" stroke-width="3"/>
<rect x="630" y="114" width="608" height="464" fill="#071007" stroke="#30432b" stroke-width="4"/>
{scene}
<path d="M64 176H99V183H64Z M64 604H546" fill="{accent}" stroke="#30432b" stroke-width="2"/>
<text class="stage-label" x="64" y="87" fill="#a9bd92" font-size="24" letter-spacing="5">PLAYING WITH FIRE</text>
<text class="stage-type" x="64" y="228" fill="{accent}" font-size="54">{roman} / VIII</text>
<g class="stage-type" fill="#edf3cf" font-size="{title_size}">{title}</g>
<text class="stage-label" x="64" y="511" fill="#d2dfa9" font-size="31">{escape(subtitle)}</text>
{progress}
</svg>"""


def put(node: dict, x: int, y: int, width: int, height: int) -> None:
    node.update(position={"x": x, "y": y}, width=width, height=height, autoFit=False)


def outline(key: str, x: int, y: int, height: int, color: str) -> dict:
    inset = 30
    corners = [(x + inset, y), (x + WIDTH - inset, y),
               (x + WIDTH, y + inset), (x + WIDTH, y + height - inset),
               (x + WIDTH - inset, y + height), (x + inset, y + height),
               (x, y + height - inset), (x, y + inset), (x + inset, y)]
    # Nearby samples keep PixiNotes' freehand smoothing close to each corner.
    points = []
    for (ax, ay), (bx, by) in zip(corners, corners[1:]):
        steps = ceil(max(abs(bx - ax), abs(by - ay)) / 40)
        points.extend([round(ax + (bx - ax) * step / steps),
                       round(ay + (by - ay) * step / steps)] for step in range(steps))
    points.append([x + inset + 20, y])
    return {"id": key, "tool": "pen", "color": color, "width": 14, "points": points}


def edge(source: str, target: str, between: bool) -> dict:
    return {
        "id": f"stage-{source}-{target}",
        "source": source,
        "target": target,
        "type": "labeled",
        "data": {
            "label": "", "kind": "dashed" if between else "arrow", "head": True,
            "width": 9 if between else 5, "color": "#ae7833" if between else "#6d805d",
        },
    }


def build() -> dict:
    data = json.loads((ROOT / "campfire.pixiboard.json").read_text())
    board = data["board"]
    nodes = board["nodes"]
    by_name = {n["data"].get("title") or n["data"].get("name"): n
               for n in nodes if n["type"] != "fluessig"}
    original_title, = (n for n in nodes if n["type"] == "fluessig")
    title = {
        "id": "stage-title", "type": "image",
        "data": {
            "src": uri((ROOT / "art" / "title-fire.svg").read_text()),
            "name": "title-fire.svg", "titel": "Playing with Fire",
        },
    }
    put(title, 3136, 0, 1728, 972)
    put(original_title, 1060, 240, 1860, 460)
    ordered = [title, original_title]
    joins = {original_title["id"]}
    drawings = []
    font, = re.findall(r'@font-face\s*\{[^}]+\}', (ROOT / "index.html").read_text())

    for i, (_, _, _, _, titles) in enumerate(CHAPTERS):
        col = i if i < 4 else 7 - i
        x, y = col * (WIDTH + GAP), TOP if i < 4 else RETURN
        is_last = i == len(CHAPTERS) - 1
        drawings.append(outline(f"station-{i+1}", x, y, 1544 if is_last else 1056, BORDERS[i]))
        panel = by_name[f"chapter-{i+1}.svg"]
        panel["data"]["src"] = uri(cover(i, font))
        put(panel, x + 44, y + 44, 640, 360)
        joins.add(panel["id"])
        ordered.append(panel)

        if is_last:
            slots = ((732, 44, 648, 404), (44, 504, 840, 520), (924, 504, 456, 460),
                     (44, 1072, 560, 400), (652, 1072, 728, 428))
        else:
            slots = ((732, 44, 648, 404), *TOOLS[i])
        for name, (left, top, width, height) in zip(titles, slots, strict=True):
            node = by_name[name]
            put(node, x + left, y + top, width, height)
            ordered.append(node)

    if {n["id"] for n in nodes} != {n["id"] for n in ordered[1:]}:
        raise ValueError("The stage layout must include every original Campfire card.")

    board.update(
        id="campfire-stage-board",
        name="Campfire · Playing with Fire · Stage",
        bg="gruen",
        nodes=ordered,
        edges=[edge(a["id"], b["id"], b["id"] in joins) for a, b in zip(ordered, ordered[1:])],
        drawings=drawings,
    )
    return data


if __name__ == "__main__":
    output = ROOT / "boards" / "campfire-stage.pixiboard.json"
    output.write_text(json.dumps(build(), ensure_ascii=False, separators=(",", ":")) + "\n", encoding="utf-8")
