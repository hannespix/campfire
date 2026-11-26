#!/usr/bin/env python3
"""Build the standalone V2 deck and the PixiNotes demo board."""

from base64 import b64encode
import json
from pathlib import Path
import re


V2 = Path(__file__).resolve().parent
REPO = V2.parent
MIME = {".svg": "image/svg+xml", ".png": "image/png"}
MODULES = (
    ("booth-builder", "Booth Builder"),
    ("context-circle", "Context Circle"),
    ("prompt-forge", "Prompt Forge"),
    ("git-time-machine", "Git Time Machine"),
    ("fireplace-check", "Fireplace Check"),
    ("myth-or-fact", "Myth or Fact?"),
    ("token-oracle", "Token Oracle"),
    ("inventory", "Words by the Fire"),
)


def encode(data: bytes) -> str:
    return b64encode(data).decode("ascii")


def artwork(filename: str) -> str:
    source = V2 / "art" / filename
    if not source.is_file():
        source = REPO / "art" / filename
    return f"data:{MIME[source.suffix]};base64,{encode(source.read_bytes())}"


def build_talk() -> str:
    template = (REPO / "decks" / "gathering.html").read_text(encoding="utf-8")
    header, remainder = template.split('<div class="slides">', maxsplit=1)
    scripts = remainder[remainder.index('<script>/* vendor/reveal/reveal.js */') :]
    header = re.sub(
        r"<title>[^<]*</title>", "<title>Playing with Fire · Campfire V2</title>", header
    )
    theme = (V2 / "src" / "talk.css").read_text(encoding="utf-8")
    header = header.replace("</head>", f"<style>\n{theme}</style>\n</head>")
    slides = (V2 / "src" / "talk.slides.html").read_text(encoding="utf-8")
    slides = re.sub(
        r'data-art="([a-z0-9-]+\.(?:svg|png))"',
        lambda match: f'src="{artwork(match[1])}"',
        slides,
    )
    return f'{header}<div class="slides">\n{slides}</div>\n</div>\n{scripts}'


def card(key: str, kind: str, x: int, y: int, width: int, height: int, data: dict) -> dict:
    return {
        "id": key,
        "type": kind,
        "position": {"x": x, "y": y},
        "width": width,
        "height": height,
        "autoFit": False,
        "data": data,
    }


def paragraph(text: str) -> dict:
    return {"type": "paragraph", "content": text}


def bubbles(title: str, question: str, examples: tuple[str, ...] = ()) -> dict:
    return {
        "title": title,
        "frage": question,
        "ideen": {
            f"example-{i}": {"text": idea, "von": "campfire", "name": "Example", "t": i}
            for i, idea in enumerate(examples)
        },
        "stimmen": {},
        "gruppen": {},
        "abstimmung": {"phase": "aus", "punkte": 3, "t": 0},
    }


def build_board() -> dict:
    nodes = [
        card("title", "image", 0, 0, 520, 293, {
            "src": artwork("title-fire.svg"),
            "name": "title-fire.svg",
            "titel": "Campfire V2",
        }),
        card("route", "note", 0, 330, 520, 320, {
            "title": "Demos & conversation",
            "color": "yellow",
            "blocks": [
                paragraph("First, run Booth Builder with one change to the floor plan."),
                paragraph("Then add an idea in a local copy using the PixiNotes MCP connection."),
                paragraph("Collect the room's questions and agree on one possible next test."),
            ],
        }),
        card("mcp-example", "bubbles", 1780, 0, 580, 620, bubbles(
            "MCP example",
            "What should VAVE try next?",
            ("Test the right-hand entrance", "Try one capacity planning week"),
        )),
        card("questions", "bubbles", 2420, 0, 640, 620, bubbles(
            "Your questions",
            "Which recurring task at VAVE would be worth a small test?",
        )),
        card("next-test", "kanban", 3120, 0, 920, 620, {
            "title": "Next test",
            "cols": ["Ideas", "Questions for VAVE", "Next test", "Done"],
            "items": [
                {"id": "test-booth", "text": "Ask a colleague to compare two routes through a stand.", "col": 0},
                {"id": "test-capacity", "text": "Ask a project lead to find a double booking in an example week.", "col": 0},
                {"id": "assign-owner", "text": "Who will try it, and what result would count as useful?", "col": 1},
            ],
        }),
    ]
    files = {}
    for index, (slug, title) in enumerate(MODULES):
        filename = f"{slug}.html"
        source = (V2 / "modules" / filename).read_bytes()
        if index == 0:
            x, y, width, height = 580, 0, 1140, 740
        else:
            row, col = divmod(index - 1, 4)
            x, y, width, height = col * 690, 850 + row * 690, 620, 620
        nodes.append(card(slug, "htmlapp", x, y, width, height, {
            "name": title,
            "size": len(source),
        }))
        files[slug] = {"name": filename, "mime": "text/html", "b64": encode(source)}

    route = ("title", "route", "booth-builder", "mcp-example", "questions", "next-test")
    edges = [
        {"id": f"e-{a}-{b}", "source": a, "target": b, "type": "labeled",
         "data": {"label": "", "kind": "arrow"}}
        for a, b in zip(route, route[1:])
    ]
    return {
        "app": "pixinotes-board",
        "version": 2,
        "board": {
            "id": "campfire-v2-demos",
            "name": "Campfire V2 · Demos & conversation",
            "nodes": nodes,
            "edges": edges,
            "drawings": [],
            "bg": "dots",
        },
        "dateien": files,
    }


def main() -> None:
    talk = build_talk()
    board = json.dumps(build_board(), ensure_ascii=False, separators=(",", ":"))
    (V2 / "talk.html").write_text(talk, encoding="utf-8")
    (V2 / "campfire-v2.pixiboard.json").write_text(board + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
