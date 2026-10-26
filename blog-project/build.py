#!/usr/bin/env python3
"""Build Kiwiii.Blog static pages and a JSON feed using only Python's stdlib."""
from datetime import date
from html import escape
import json
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parent
POSTS = ROOT / "posts"
SITE = "https://blog.kiwiii.stream"
HOME = "https://kiwiii.stream"

CSS = """
:root{color-scheme:dark;--bg:#101b1b;--panel:#172626;--panel2:#1d332d;--ink:#edf5df;--muted:#a9b9aa;--leaf:#9bd36a;--lime:#e6c85a;--teal:#77d9c0;--line:#345048;--pink:#e8a58d;--width:1080px;--reading:760px}
*{box-sizing:border-box}
html{scroll-behavior:smooth;scroll-padding-top:24px}
body{margin:0;background:radial-gradient(ellipse at 82% 0%,#263f36 0,transparent 34rem),radial-gradient(ellipse at 0% 35%,#1b3430 0,transparent 36rem),var(--bg);color:var(--ink);font:16px/1.75 "DM Sans",system-ui,-apple-system,"Segoe UI",sans-serif;-webkit-font-smoothing:antialiased}
body:before{content:"";position:fixed;inset:0;z-index:-1;pointer-events:none;opacity:.11;background-image:radial-gradient(#d8e8bd 1px,transparent 1px);background-size:28px 28px;mask-image:linear-gradient(#000,transparent 75%)}
a{color:var(--lime);text-underline-offset:.22em}a:hover{color:var(--teal)}a:focus-visible{outline:3px solid var(--lime);outline-offset:4px}
.wrap{width:min(var(--width),calc(100% - 40px));margin-inline:auto}
header{border-bottom:1px solid var(--line);background:#101b1be8}
.topbar{min-height:82px;display:flex;align-items:center;justify-content:space-between;gap:24px}
.brand{display:inline-flex;align-items:center;gap:11px;color:var(--ink);text-decoration:none;font-weight:900;letter-spacing:-.04em;font-size:1.2rem}.brand-logo{display:block;width:250px;max-width:min(52vw,250px);height:auto}
.brand:hover{color:var(--ink)}
.brand-icon{display:grid;place-items:center;width:42px;height:42px;border:1px solid #78905d;border-radius:13px 13px 13px 4px;background:linear-gradient(145deg,#2b493d,#172a27);color:var(--lime);font-size:1.2rem;box-shadow:0 0 25px #9bd36a14}
.brand-name span{color:var(--leaf)}
.nav{display:flex;align-items:center;gap:24px;font-size:.86rem;font-weight:700}.nav a{text-decoration:none;color:var(--muted)}.nav a:hover{color:var(--lime)}
main{min-height:65vh;padding:clamp(42px,7vw,84px) 0}
.hero{padding:clamp(26px,5vw,52px);border:1px solid #48654e;border-radius:20px 20px 20px 4px;background:linear-gradient(125deg,#203d35f0,#142522f5);margin-bottom:48px}
.kicker,.meta,.date{color:var(--leaf);font-size:.75rem;font-weight:800;letter-spacing:.13em;text-transform:uppercase}
h1,h2,h3{font-family:"Nunito","DM Sans",system-ui,sans-serif;line-height:1.15;letter-spacing:-.04em;text-wrap:balance}
h1{font-size:clamp(2.8rem,7vw,5.5rem);margin:12px 0 18px;max-width:14ch}
h1 em{color:var(--lime);font-style:normal}
.intro{max-width:65ch;color:var(--muted);font-size:1.06rem}
.hero-bottom{display:flex;flex-wrap:wrap;gap:9px;margin-top:25px}.tag{border:1px solid #48654e;border-radius:999px;padding:5px 10px;color:#d8e8bd;font-size:.75rem}
.section-title{display:flex;align-items:end;justify-content:space-between;gap:20px;margin:0 0 18px}.section-title h2{font-size:clamp(1.6rem,4vw,2.3rem);margin:0}.section-title p{max-width:45ch;color:var(--muted);margin:0}
.post-list{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:16px}
.post-card{min-width:0;padding:25px;border:1px solid var(--line);border-radius:15px 15px 15px 4px;background:linear-gradient(145deg,#1b2d2a,#152321);transition:transform .18s,border-color .18s}
.post-card:hover{transform:translateY(-3px);border-color:#66866a}
.post-card h2{font-size:clamp(1.35rem,3vw,1.8rem);margin:9px 0}.post-card h2 a{color:var(--ink);text-decoration:none}.post-card h2 a:hover{color:var(--lime)}
.post-card p{color:var(--muted);margin:0 0 14px}.read-link{font-weight:800;text-decoration:none;font-size:.88rem}
.empty{padding:28px;border:1px dashed var(--line);border-radius:14px;color:var(--muted)}
.article-shell{width:min(var(--reading),calc(100% - 40px));margin-inline:auto}
.back-link{display:inline-block;margin-bottom:38px;text-decoration:none;font-weight:800;font-size:.9rem}
.article-head{padding:clamp(24px,5vw,46px);border:1px solid var(--line);border-radius:18px 18px 18px 4px;background:linear-gradient(145deg,#1b302b,#142321)}
.article-head h1{font-size:clamp(2.3rem,6vw,4.4rem);max-width:unset;margin:12px 0 18px}
.article-head .excerpt{color:var(--muted);font-size:1.08rem;margin-bottom:0}
article.prose{padding:clamp(8px,2vw,20px) 0;color:var(--muted);font-size:1.06rem;line-height:1.9;overflow-wrap:anywhere}
.prose h2,.prose h3,.prose h4{color:var(--ink);margin-top:2em}
.prose h2{font-size:1.8rem}.prose h3{font-size:1.35rem}
.prose p,.prose li{color:var(--muted)}.prose li{margin:.35em 0}.prose strong{color:var(--ink)}
.prose blockquote{margin:1.6em 0;padding:5px 0 5px 20px;border-left:3px solid var(--lime);color:#d8e8bd}
.prose code{padding:2px 5px;border-radius:4px;background:#0c1515;color:#d8e8bd;font-size:.9em}
.prose pre{padding:18px;overflow:auto;border:1px solid var(--line);border-radius:10px;background:#0c1515;color:var(--ink)}
.prose pre code{padding:0}.prose hr{border:0;border-top:1px solid var(--line);margin:2.5em 0}
footer{border-top:1px solid var(--line);padding:26px 0 34px;color:var(--muted);font-size:.85rem}
.footer-inner{display:flex;flex-wrap:wrap;align-items:center;justify-content:space-between;gap:14px}.footer-links{display:flex;gap:18px}.footer-links a{text-decoration:none}
@media(max-width:680px){.topbar{align-items:flex-start;flex-direction:column;padding:15px 0;gap:12px}.nav{width:100%;flex-wrap:wrap;gap:10px 18px}.post-list{grid-template-columns:1fr}.section-title{align-items:flex-start;flex-direction:column}.hero{padding:24px}.footer-inner{align-items:flex-start;flex-direction:column}}
@media(prefers-reduced-motion:reduce){*,*:before,*:after{scroll-behavior:auto!important;transition:none!important}.post-card:hover{transform:none}}
"""

def read_post(path):
    raw = path.read_text(encoding="utf-8")
    meta, body = {}, raw
    if raw.startswith("---\n"):
        parts = raw.split("---", 2)
        if len(parts) == 3:
            body = parts[2].strip()
            for line in parts[1].splitlines():
                if ":" not in line:
                    continue
                key, value = line.split(":", 1)
                key, value = key.strip(), value.strip().strip('"').strip("'")
                if key == "published":
                    meta[key] = value.lower() not in {"false", "no", "0"}
                else:
                    meta[key] = value
    if not meta.get("title") or meta.get("published") is False:
        return None
    slug = path.stem
    excerpt = meta.get("excerpt") or re.sub(r"\s+", " ", body)[:180]
    categories = [item.strip() for item in meta.get("category", "Notes").split(",") if item.strip()]
    return {"title":meta["title"],"date":meta.get("date",date.today().isoformat()),
            "excerpt":excerpt,"url":f"{SITE}/posts/{slug}.html","published":True,
            "slug":slug,"body":body,"categories":categories}

def inline_markdown(text):
    text = escape(text, quote=False)
    codes = []
    def hold_code(match):
        codes.append("<code>"+match.group(1)+"</code>")
        return f"\x00CODE{len(codes)-1}\x00"
    text = re.sub(r"`([^`]+)`", hold_code, text)
    def link(match):
        label, url = match.group(1), match.group(2).strip()
        if url.startswith("//") or (re.match(r"^[a-zA-Z][a-zA-Z0-9+.-]*:",url) and not url.lower().startswith(("https:","http:","mailto:"))):
            return label
        return f'<a href="{escape(url,quote=True)}">{label}</a>'
    text = re.sub(r"\[([^\]]+)\]\(([^)]+)\)",link,text)
    text = re.sub(r"\*\*(.+?)\*\*",r"<strong>\1</strong>",text)
    text = re.sub(r"(?<!\*)\*([^*\n]+)\*(?!\*)",r"<em>\1</em>",text)
    for i, fragment in enumerate(codes):
        text = text.replace(f"\x00CODE{i}\x00",fragment)
    return text

def render_markdown(source):
    lines=source.splitlines(); out=[]; paragraph=[]; list_kind=None; code_lines=[]; in_code=False
    def flush_paragraph():
        if paragraph:
            out.append("<p>"+"<br>\n".join(inline_markdown(line) for line in paragraph)+"</p>")
            paragraph.clear()
    def close_list():
        nonlocal list_kind
        if list_kind:
            out.append(f"</{list_kind}>"); list_kind=None
    for line in lines:
        if line.strip().startswith("```"):
            flush_paragraph(); close_list()
            if in_code:
                out.append("<pre><code>"+escape("\n".join(code_lines))+"</code></pre>")
                code_lines.clear(); in_code=False
            else: in_code=True
            continue
        if in_code: code_lines.append(line); continue
        if not line.strip(): flush_paragraph(); close_list(); continue
        heading=re.match(r"^(#{1,4})\s+(.+)$",line)
        if heading:
            flush_paragraph(); close_list(); level=len(heading.group(1))
            out.append(f"<h{level}>"+inline_markdown(heading.group(2))+f"</h{level}>"); continue
        if re.match(r"^\s*(---+|\*\*\*+|___+)\s*$",line):
            flush_paragraph(); close_list(); out.append("<hr>"); continue
        quote=re.match(r"^\s*>\s?(.*)$",line)
        if quote:
            flush_paragraph(); close_list(); out.append("<blockquote><p>"+inline_markdown(quote.group(1))+"</p></blockquote>"); continue
        item=re.match(r"^\s*([-*+]\s+|\d+[.)]\s+)(.+)$",line)
        if item:
            flush_paragraph(); wanted="ol" if item.group(1).strip()[0].isdigit() else "ul"
            if list_kind != wanted: close_list(); out.append(f"<{wanted}>"); list_kind=wanted
            out.append("<li>"+inline_markdown(item.group(2))+"</li>"); continue
        close_list(); paragraph.append(line.strip())
    if in_code: out.append("<pre><code>"+escape("\n".join(code_lines))+"</code></pre>")
    flush_paragraph(); close_list()
    return "\n".join(out)

def header():
    return f'<header><div class="wrap topbar"><a class="brand" href="{SITE}/" aria-label="Kiwiii Blog home"><img class="brand-logo" src="/assets/logos/kiwiii-blog.svg" alt="Kiwiii.Blog"></a><nav class="nav" aria-label="Main navigation"><a href="{SITE}/">Notebook</a><a href="{HOME}/">Kiwiii.Stream ↗</a></nav></div></header>'

def footer():
    return f'<footer><div class="wrap footer-inner"><span>Small notes from a curious corner of the internet.</span><nav class="footer-links" aria-label="Footer navigation"><a href="{SITE}/">Blog home</a><a href="{HOME}/">Kiwiii.Stream ↗</a></nav></div></footer>'

def document(title, description, canonical, content):
    return f'''<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<meta name="description" content="{escape(description,quote=True)}"><meta name="theme-color" content="#101b1b">
<link rel="canonical" href="{escape(canonical,quote=True)}"><link rel="icon" type="image/svg+xml" href="/assets/logos/kiwiii-blog.svg"><meta property="og:type" content="article"><meta property="og:site_name" content="Kiwiii.Blog">
<meta property="og:title" content="{escape(title,quote=True)}"><meta property="og:description" content="{escape(description,quote=True)}">
<meta name="twitter:card" content="summary"><title>{escape(title)} — Kiwiii.Blog</title>
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700;800&family=Nunito:wght@600;700;800;900&display=swap" rel="stylesheet">
<style>{CSS}</style></head><body>{header()}<main class="wrap">{content}</main>{footer()}</body></html>'''

def render_article(post):
    body = render_markdown(post["body"])
    categories = "".join(f'<span class="tag">{escape(c)}</span>' for c in post["categories"])
    content = f'''<div class="article-shell"><a class="back-link" href="{SITE}/">← All notes</a>
<header class="article-head"><p class="date">{escape(post["date"])}</p><h1>{escape(post["title"])}</h1><p class="excerpt">{escape(post["excerpt"])}</p><div class="hero-bottom">{categories}</div></header>
<article class="prose">{body}</article><p><a class="back-link" href="{SITE}/">← Back to all notes</a></p></div>'''
    (POSTS / (post["slug"]+".html")).write_text(document(post["title"],post["excerpt"],post["url"],content),encoding="utf-8")

def main():
    POSTS.mkdir(exist_ok=True)
    posts=[p for path in POSTS.glob("*.md") if (p:=read_post(path))]
    posts.sort(key=lambda p:p["date"],reverse=True)
    for post in posts: render_article(post)
    public=[{k:p[k] for k in ("title","date","excerpt","url","published","categories")} for p in posts]
    (ROOT/"feed.json").write_text(json.dumps({"title":"Kiwiii.Blog","home":SITE+"/","posts":public},ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    cards="".join(f'<article class="post-card"><p class="date">{escape(p["date"])}</p><h2><a href="/posts/{escape(p["slug"])}.html">{escape(p["title"])}</a></h2><p>{escape(p["excerpt"])}</p><a class="read-link" href="/posts/{escape(p["slug"])}.html">Read note ↗</a></article>' for p in posts)
    if not cards: cards='<p class="empty">New writing will appear here soon.</p>'
    content=f'''<section class="hero"><p class="kicker">K I W I I I . B L O G &nbsp; / &nbsp; FIELD NOTES</p><h1>Notes from <em>the stream.</em></h1><p class="intro">Thoughts, experiments, useful discoveries and ideas in progress — a calm little archive of technology, nature, creative projects and the connections between them.</p><div class="hero-bottom"><span class="tag">Practical technology</span><span class="tag">Nature &amp; everyday life</span><span class="tag">Projects in progress</span></div></section>
<section aria-labelledby="latest-title"><div class="section-title"><h2 id="latest-title">Latest notes</h2><p>Longer thoughts, lessons learned and things worth writing down.</p></div><div class="post-list">{cards}</div></section>'''
    index=document("Kiwiii.Blog","Notes on technology, nature, personal projects and the ideas that connect them.",SITE+"/",content)
    (ROOT/"index.html").write_text(index,encoding="utf-8")

if __name__=="__main__":
    main()
