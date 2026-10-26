#!/usr/bin/env python3
"""Build a simple static blog listing and JSON feed from Markdown posts.

Uses only the Python standard library. Markdown article files are retained as
source; the generated feed is consumed by the Kiwiii.Stream homepage.
"""
from datetime import date
from html import escape
import json
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parent
POSTS = ROOT / "posts"
SITE = "https://blog.kiwiii.stream"


def read_post(path):
    raw = path.read_text(encoding="utf-8")
    meta = {}
    body = raw
    if raw.startswith("---\n"):
        parts = raw.split("---", 2)
        if len(parts) == 3:
            body = parts[2].strip()
            for line in parts[1].splitlines():
                if ":" not in line:
                    continue
                key, value = line.split(":", 1)
                value = value.strip().strip('"').strip("'")
                if key.strip() == "published":
                    meta[key.strip()] = value.lower() not in {"false", "no", "0"}
                else:
                    meta[key.strip()] = value
    if not meta.get("title") or meta.get("published") is False:
        return None
    slug = path.stem
    excerpt = meta.get("excerpt") or re.sub(r"\s+", " ", body)[:180]
    return {
        "title": meta["title"],
        "date": meta.get("date", date.today().isoformat()),
        "excerpt": excerpt,
        "url": f"{SITE}/posts/{slug}.html",
        "published": True,
        "slug": slug,
        "body": body,
    }


def render_article(post):
    paragraphs = [p.strip() for p in post["body"].split("\n\n") if p.strip()]
    rendered = []
    for paragraph in paragraphs:
        if paragraph.startswith("## "):
            rendered.append("<h2>" + escape(paragraph[3:]) + "</h2>")
        else:
            rendered.append("<p>" + escape(paragraph).replace("\n", "<br>") + "</p>")
    page = """<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<meta name="description" content="{excerpt}"><meta name="theme-color" content="#101b1b">
<title>{title} — Kiwiii notes</title><style>
:root{{color-scheme:dark;--bg:#101b1b;--panel:#172626;--ink:#edf5df;--muted:#a9b9aa;--lime:#e6c85a;--line:#345048}}
*{{box-sizing:border-box}}body{{margin:0;background:var(--bg);color:var(--ink);font:17px/1.8 system-ui,sans-serif}}
main{{width:min(760px,calc(100% - 36px));margin:0 auto;padding:50px 0 90px}}a{{color:var(--lime)}}.brand{{font-weight:800;text-decoration:none}}.meta{{margin-top:55px;color:var(--lime);font-size:12px;letter-spacing:1px;text-transform:uppercase}}h1{{font-size:clamp(36px,7vw,60px);line-height:1.08;letter-spacing:-1.5px}}p{{color:var(--muted)}}article{{margin-top:30px}}footer{{margin-top:55px;padding-top:20px;border-top:1px solid var(--line);font-size:13px}}
</style></head><body><main><a class="brand" href="{site}/">Kiwiii.Stream ↗</a><p class="meta">{date}</p><h1>{title}</h1><p>{excerpt}</p><article>{body}</article><footer><a href="{site}/">← Back to Kiwiii.Stream</a></footer></main></body></html>"""
    out = ROOT / "posts" / (post["slug"] + ".html")
    out.write_text(page.format(
        title=escape(post["title"]), date=escape(post["date"]),
        excerpt=escape(post["excerpt"]), body="\n".join(rendered), site=SITE,
    ), encoding="utf-8")


def main():
    POSTS.mkdir(exist_ok=True)
    posts = [p for path in POSTS.glob("*.md") if (p := read_post(path))]
    posts.sort(key=lambda p: p["date"], reverse=True)
    for post in posts:
        render_article(post)
    public_posts = [{k: p[k] for k in ("title", "date", "excerpt", "url", "published")} for p in posts]
    (ROOT / "feed.json").write_text(json.dumps({
        "title": "Kiwiii notes", "home": SITE + "/", "posts": public_posts
    }, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    cards = "".join(
        '<article><p class="date">{date}</p><h2><a href="{url}">{title}</a></h2><p>{excerpt}</p></article>'.format(
            date=escape(p["date"]), url=escape("/posts/" + p["slug"] + ".html"),
            title=escape(p["title"]), excerpt=escape(p["excerpt"])
        ) for p in posts
    ) or "<p>New writing will appear here soon.</p>"
    listing = """<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="theme-color" content="#101b1b"><title>Kiwiii notes</title><style>
:root{{color-scheme:dark;--bg:#101b1b;--panel:#172626;--ink:#edf5df;--muted:#a9b9aa;--lime:#e6c85a;--line:#345048}}*{{box-sizing:border-box}}body{{margin:0;background:radial-gradient(ellipse at 80% 0,#263f36,transparent 35rem),var(--bg);color:var(--ink);font:16px/1.7 system-ui,sans-serif}}main{{width:min(850px,calc(100% - 36px));margin:0 auto;padding:50px 0 90px}}a{{color:var(--lime)}}.brand{{font-weight:800;text-decoration:none}}h1{{font-size:clamp(42px,8vw,72px);line-height:1.05;letter-spacing:-2px}}.intro{{max-width:600px;color:var(--muted)}}article{{padding:25px 0;border-top:1px solid var(--line)}}.date{{font-size:12px;color:var(--lime);text-transform:uppercase;letter-spacing:1px}}h2{{margin-bottom:5px}}article p{{color:var(--muted)}}footer{{margin-top:50px;padding-top:20px;border-top:1px solid var(--line);font-size:13px}}
</style></head><body><main><a class="brand" href="{site}/">Kiwiii.Stream ↗</a><h1>Notes from the stream.</h1><p class="intro">Thoughts, experiments, useful discoveries and ideas in progress — collected as they come.</p>{cards}<footer><a href="{site}/">← Back to Kiwiii.Stream</a></footer></main></body></html>"""
    (ROOT / "index.html").write_text(listing.format(site=SITE, cards=cards), encoding="utf-8")


if __name__ == "__main__":
    main()
