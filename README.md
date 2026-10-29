# Kiwiii.Stream

The public website is maintained in `KieranSHome/KSHome` and deployed to Cloudflare Pages from the generated `dist/` directory.

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

- The custom domain website deploys through Cloudflare Pages from this repository. Its build command is `python3 blog-project/build.py`, and its output directory is `dist`. Cloudflare Pages is the production deployment.
- Jellyfin and Caddy remain separate services; this repository must not change their server configuration.
- DNS and domain routing changes are separate from repository changes.
- Do not add secrets, private financial records, or generated private exports.

## Kiwiii Blocks

Play at `/Projects/blocks/`; the Projects page includes a shared top-ten leaderboard.
The build explicitly copies the four game assets to `dist/Projects/blocks/`.
Cloudflare Pages compiles `functions/api/blocks.js` from the repository root.

Run `node tests/blocks.cjs` and `python3 blog-project/build.py` to check the game and site.

### Shared leaderboard storage

The `BLOCKS_DB` D1 binding is configured on the existing `kshome` Pages project:
production uses `kiwiii-blocks`; previews use `kiwiii-blocks-preview` so test scores stay separate.
Both databases use the schema in `database/blocks.sql`. For a new installation, create the
database, run that schema, add the D1 binding in Pages Settings → Bindings for each environment,
and redeploy. No secret or raw IP address is written to this repository or the database.

Players explicitly opt in to publish a 1–16 character nickname and score at game over.
The API bounds request bodies, validates names/scores, requires same-origin JSON, limits new
sessions to 30/hour per daily IP hash, and atomically consumes each session once. Temporary
sessions/hashes are pruned after 24 hours when the next session starts; only the top 100 scores
are retained. The UI shows the top ten and offers refresh. Stored names are rendered as text.

This is a casual browser scoreboard: timing and score plausibility checks deter simple abuse,
but a modified client can fabricate results. Competitive integrity would require server-side
deterministic replay verification. Public nicknames should not contain personal information.
To remove an inappropriate score, delete its row from `blocks_scores` in the D1 console.
