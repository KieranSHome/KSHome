# Kiwiii.Blog

Kiwiii.Blog is the static blog for [kiwiii.stream/blog](https://kiwiii.stream/blog), designed as a companion to [Kiwiii.Stream](https://kiwiii.stream).

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

The blog source lives in `blog-project/`. The GitHub Pages workflow runs `python3 blog-project/build.py` and publishes the generated site at `/blog/` alongside the main site. The feed is served at `/blog/feed.json` on the same origin, so no cross-origin request is required.

This migration changes repository files and GitHub Pages build steps only. It does not change DNS, Cloudflare routing, or Jellyfin settings.
