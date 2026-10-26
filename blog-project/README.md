# Kiwiii.Blog

Kiwiii.Blog is the static blog for [blog.kiwiii.stream](https://blog.kiwiii.stream), designed as a companion to [Kiwiii.Stream](https://kiwiii.stream).

## Visual direction

Botanical eco-tech meets a friendly sci-fi command console: deep teal surfaces, leaf green and warm lime accents, quiet dotted texture, rounded panels, accessible contrast, responsive layout, and restrained motion. The header and favicon use the approved artwork at `https://kiwiii.stream/assets/Kiwiii%20Blog%20Kiwi%20Emblem%20Logo.png`.

## Write a post

Create a Markdown file in `posts/` with front matter:

```yaml
---
title: "A post title"
date: "2026-10-26"
excerpt: "A short summary for the homepage and blog listing."
category: "Projects"
published: true
---
```

Use `published: false` for a draft. Categories are optional and can be comma-separated. The builder supports headings, paragraphs, links, bold and italic text, quotes, lists, horizontal rules, inline code and fenced code blocks.

Build from this directory:

```bash
python3 build.py
```

This regenerates `index.html`, individual `posts/*.html` pages and `feed.json`. Only Python's standard library is required.

## Deployment

The blog source lives in this repository's `blog-project/` directory. Configure the static host for `blog.kiwiii.stream` to use that directory as its project/root directory and run `python3 build.py` as its build command (or commit generated output). Ensure `feed.json` is served over HTTPS and allows cross-origin requests from `https://kiwiii.stream` so the main site can show the latest post.

This work changes repository files only. It does not change DNS, Cloudflare, domain routing, or Jellyfin settings.
