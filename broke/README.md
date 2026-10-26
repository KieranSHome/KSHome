# Broke — Kiwiii.Stream

A privacy-conscious, static dashboard for sharing an honest aggregate view of a debt-reduction journey. Intended site: **https://broke.kiwiii.stream**.

## Current state

This repository starts with a static HTML/CSS/JavaScript dashboard. It uses the shared Kiwiii.Stream stylesheet at `https://kiwiii.stream/brand.css`; `style.css` contains only Broke-specific layout and dashboard styling.

The public data file is a deliberately empty template. No real financial figures or progress have been invented. Keep values unpublished until a reviewed, approved aggregate export is ready.

## Files

- `index.html` — dashboard page and site navigation.
- `style.css` — dashboard-specific styling; shared branding belongs in `brand.css` in the KSHome repository.
- `app.js` — fetches and renders the public summary.
- `data/public.json` — public-safe data contract/template only.
- `scripts/README.md` — requirements for a future reviewed export workflow.

## Privacy rules — mandatory

Never commit or publish:
- the private Excel workbook or any backup/copy of it;
- creditor names, account/reference numbers, payment references, or creditor-specific balances;
- bank statements, transaction-level data, addresses, identity documents, or other identifying details;
- credentials, API keys, tokens, or environment files.

Only publish aggregate figures after explicit review. Check totals, dates, units, and reporting periods before publishing. Keep missing values as `null`; do not guess or fill in unknowns. Do not publish a projected debt-free date or promise a particular outcome. The site is informational, not financial advice.

## Local preview

Run a local static server from this directory (fetching JSON may not work from a direct `file://` URL). With Python installed:

```powershell
py -m http.server 8080
```

Then open `http://localhost:8080`.

## Cloudflare Pages

Consolidated deployment configuration:
- The public dashboard files are maintained under `broke/` in `KieranSHome/KSHome`.
- Framework preset: **None**.
- Build command: leave blank.
- Build output directory: `/` (repository root of KSHome GitHub Pages).
- Add the custom domain only after checking the published data and privacy review.

The repository currently contains only static site assets and an unpublished data template. The dashboard is deployed with the main KSHome GitHub Pages site. DNS and Jellyfin settings remain separate.

## Shared brand contract

Load `https://kiwiii.stream/brand.css` before `style.css`. Keep shared typography, global resets, buttons, and site-wide tokens in the master stylesheet; keep this repository's `style.css` limited to Broke-specific components.
