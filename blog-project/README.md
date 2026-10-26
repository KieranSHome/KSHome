# Kiwiii.Stream blog project

This directory is the source for the independently deployed blog at `https://blog.kiwiii.stream`. It uses Markdown files with YAML-style front matter and a small Python standard-library build script.

## Write a post

Create a `.md` file in `posts/` with this front matter:

```yaml
---
title: "A post title"
date: "2026-10-26"
excerpt: "A short summary for the homepage and blog listing."
published: true
---
```

Write the article in Markdown beneath the front matter. Set `published: false` for drafts. Run `python3 build.py` from this directory to regenerate `feed.json` and `index.html`.

## Homepage integration

The main website reads `https://blog.kiwiii.stream/feed.json` and displays the newest published post. The feed must be served with HTTPS and allow cross-origin requests from `https://kiwiii.stream` (and optionally `https://www.kiwiii.stream`). If the feed cannot be reached, the homepage retains its fallback blog card.

## Deployment note

This is source scaffolding only. The blog subdomain must be connected to a separate static deployment whose project root is this directory. No DNS, domain, Cloudflare or Jellyfin settings are changed by this pull request. Configure the subdomain and deployment separately after reviewing and testing the preview.
