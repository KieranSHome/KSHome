# Kiwiii.Stream Blog

The blog is published at [kiwiii.stream/blog](https://kiwiii.stream/blog/) as part of the main Kiwiii.Stream site.

## Design

Botanical eco-tech meets a friendly sci-fi command console. The shared design system is `/brand.css`; the Blog uses the approved asset `assets/Kiwiii Blog Kiwi Emblem Logo.png`.

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

Use `published: false` for drafts. The generator includes only posts explicitly marked `published: true`. The repository is public, so this hides drafts from the website but not from GitHub; keep sensitive or private drafts outside this repository.

## Media in posts

- **Images:** use Markdown image syntax, such as `![Kiwi in the garden](/assets/kiwi.jpg)`. Add the image to the repository's root `assets/` folder, then use its `/assets/filename.jpg` path. Remote HTTPS image URLs also work.
- **YouTube:** put a marker on its own line: `{{youtube: https://youtu.be/VIDEO_ID}}`. Standard YouTube watch, short, Shorts, and embed URLs are accepted; invalid URLs render as a link.
- **Social posts:** put a marker on its own line: `{{social: https://social.example/post/123 | Read the original post}}`. This creates a consistent link card to the original post. It does not copy the post text or run the platform's embed scripts.

Keep image alt text descriptive. A commit to the repository triggers the Cloudflare Pages build and publishes the generated article.

## Build and deploy

From the repository root:

```powershell
python blog-project/build.py
```

The script reads Markdown from `blog-project/posts/`, copies only the public site pages and assets into `dist/`, and generates the blog under `dist/blog/`. Cloudflare Pages runs `python3 blog-project/build.py` and publishes `dist/`. Unpublished posts are excluded from the generated site, and old generated article pages are cleared on each build. The feed is available at `/blog/feed.json`.

The separate `KieranSHome/Blog` repository is an archive. Make future blog changes in `KieranSHome/KSHome/blog-project/`.

