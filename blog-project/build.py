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


def inline_markdown(text):
    """Render common inline Markdown without allowing unsafe link schemes."""
    text = escape(text, quote=False)
    code = []
    def hold_code(match):
        code.append("<code>" + match.group(1) + "</code>")
        return f"\x00CODE{len(code) - 1}\x00"
    text = re.sub(r"`([^`]+)`", hold_code, text)
    def link(match):
        label, url = match.group(1), match.group(2).strip()
        if url.startswith("//") or (re.match(r"^[a-zA-Z][a-zA-Z0-9+.-]*:", url) and not url.lower().startswith(("https:", "http:", "mailto:"))):
            return label
        return f'<a href="{escape(url, quote=True)}">{label}</a>'
    text = re.sub(r"\[([^\]]+)\]\(([^)]+)\)", link, text)
    text = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", text)
    text = re.sub(r"(?<!\*)\*([^*\n]+)\*(?!\*)", r"<em>\1</em>", text)
    for index, fragment in enumerate(code):
        text = text.replace(f"\x00CODE{index}\x00", fragment)
    return text


def render_markdown(source):
    """Render headings, paragraphs, unordered/ordered lists, quotes and code."""
    lines = source.splitlines()
    out, paragraph, list_kind, code_lines = [], [], None, []
    in_code = False

    def flush_paragraph():
        if paragraph:
            out.append("<p>" + "<br>\n".join(inline_markdown(line) for line in paragraph) + "</p>")
            paragraph.clear()

    def close_list():
        nonlocal list_kind
        if list_kind:
            out.append(f"</{list_kind}>")
            list_kind = None

    for line in lines:
        if line.strip().startswith("```"):
            flush_paragraph()
            close_list()
            if in_code:
                out.append("<pre><code>" + escape("\n".join(code_lines)) + "</code></pre>")
                code_lines.clear()
                in_code = False
            else:
                in_code = True
            continue
        if in_code:
            code_lines.append(line)
            continue
        if not line.strip():
            flush_paragraph()
            close_list()
            continue
        heading = re.match(r"^(#{1,4})\s+(.+)$", line)
        if heading:
            flush_paragraph()
            close_list()
            level = len(heading.group(1))
            out.append(f"<h{level}>" + inline_markdown(heading.group(2)) + f"</h{level}>")
            continue
        if re.match(r"^\s*(---+|\*\*\*+|___+)\s*$", line):
            flush_paragraph()
            close_list()
            out.append("<hr>")
            continue
        quote = re.match(r"^\s*>\s?(.*)$", line)
        if quote:
            flush_paragraph()
            close_list()
            out.append("<blockquote><p>" + inline_markdown(quote.group(1)) + "</p></blockquote>")
            continue
        item = re.match(r"^\s*([-*+]\s+|\d+[.)]\s+)(.+)$", line)
        if item:
            flush_paragraph()
            wanted = "ol" if item.group(1).strip()[0].isdigit() else "ul"
            if list_kind != wanted:
                close_list()
                out.append(f"<{wanted}>")
                list_kind = wanted
            out.append("<li>" + inline_markdown(item.group(2)) + "</li>")
            continue
        close_list()
        paragraph.append(line.strip())
    if in_code:
        out.append("<pre><code>" + escape("\n".join(code_lines)) + "</code></pre>")
    flush_paragraph()
    close_list()
    return "\n".join(out)


def render_article(post):
    rendered = render_markdown(post["body"])
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
