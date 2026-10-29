#!/usr/bin/env python3
"""Verify the Pages release artifact and leaderboard schema; never deploys."""
from pathlib import Path
import sqlite3

root = Path(__file__).resolve().parent.parent
for name in ("index.html", "style.css", "game.js", "leaderboard.js"):
    source = root / "Projects" / "blocks" / name
    output = root / "dist" / "Projects" / "blocks" / name
    assert output.is_file() and output.read_bytes() == source.read_bytes(), f"Missing or stale game asset: {name}"
projects = (root / "dist" / "Projects" / "index.html").read_text()
assert 'href="/Projects/blocks/"' in projects, "Missing game card"
assert 'id="leaderboard"' in projects, "Missing Projects leaderboard"
assert '/Projects/blocks/leaderboard.js' in projects, "Missing leaderboard client"
assert (root / "functions" / "api" / "blocks.js").is_file(), "Missing Pages Function"
with sqlite3.connect(":memory:") as db:
    db.executescript((root / "database" / "blocks.sql").read_text())
    # Schema can be applied again without destroying data.
    db.executescript((root / "database" / "blocks.sql").read_text())
    tables = {row[0] for row in db.execute("SELECT name FROM sqlite_master WHERE type='table'")}
    assert {"blocks_scores", "blocks_sessions"} <= tables
    for score, lines in ((0, 0), (-1, 0), (10000001, 0), (100, -1), (100, 10001)):
        try:
            db.execute("INSERT INTO blocks_scores VALUES ('invalid', 'check', ?, ?, 0)", (score, lines))
        except sqlite3.IntegrityError:
            pass
        else:
            raise AssertionError("Score bounds are not enforced")
print("Pages game assets, Projects integration, and D1 schema verified. No deployment performed.")
