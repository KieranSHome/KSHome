# Kiwiii.Stream

The public website is maintained and deployed from this repository, `KieranSHome/KSHome`.

## Site map

- **Home:** `/` — the main landing page.
- **Blog:** `/blog/` — generated from Markdown in `blog-project/posts/`.
- **Projects:** `/Projects/` — the project portfolio.
- **Broke:** `/broke/` — the privacy-conscious public debt dashboard.
- **Jellyfin:** `https://jellyfin.kiwiii.stream/` — the existing external media service.

## Blog workflow

Add or edit Markdown files in `blog-project/posts/`. Set `published: true` to include a post in the public build; keep drafts at `published: false`. The Cloudflare Pages build runs `python3 blog-project/build.py`, which generates the blog under `/blog/`, including article pages and `/blog/feed.json`.

The canonical blog address is `https://kiwiii.stream/blog/`. The former `KieranSHome/Blog` repository remains as a non-destructive archive; the active blog source is `KieranSHome/KSHome/blog-project/`.

## Broke privacy rules

Only reviewed aggregate figures may be published. Never copy the private workbook, raw transactions, creditor or account details, identity documents, or credentials into this repository. The current `broke/data/public.json` is an unpublished template with null values.

## Production boundaries

- The custom domain website deploys through Cloudflare Pages from this repository. Its build command is `python3 blog-project/build.py`, and its output directory is `.`. Cloudflare Pages is the production deployment.
- Jellyfin and Caddy remain separate services; this repository must not change their server configuration.
- DNS and domain routing changes are separate from repository changes.
- Do not add secrets, private financial records, or generated private exports.
