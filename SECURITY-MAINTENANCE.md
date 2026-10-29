# Security maintenance — 29 October 2026

## Repository controls

- CodeQL covers Actions, JavaScript/TypeScript and Python on main pushes, pull requests and the existing weekly schedule.
- Blog publication accepts only lowercase `published: true`. Regression checks cover omitted, false, blank and invalid values, generated listings/feeds and removal of stale articles.
- The leaderboard enforces a shared D1-backed budget of 60 JSON POSTs per IP-derived key per UTC minute before reading the body. The existing 30 session starts/hour restriction remains.
- Public leaderboard reads are cached at the edge for ten seconds, with a canonical key per origin. Writes, tokens and errors are not cached. Score submission invalidates the local cached list; other locations may remain stale for ten seconds.
- Session and request-budget expiry cleanup uses indexed, bounded batches after an accepted session start. Reapply the additive `database/blocks.sql` schema in preview and production before deploying the API change.
- Financial dashboard files and data are outside this change.

## Separate Workers review

Cloudflare's active deployment/version metadata was inspected for `kshome` version
`226e0d81-4855-40d9-b9da-4b441445888d` and `blog` version
`78ffe38f-4757-4e85-94f9-04c777d01ac5`.

Both versions have no executable script handlers and no bindings. They serve static assets
directly (`serve_directly: true`, `raw_run_worker_first: false`), which explains why script
download endpoints returned empty content. This closes the missing executable-handler
question; it does not claim a full audit of the separately stored asset bundles.

The `blog` Worker has the custom hostname `blog.kiwiii.stream`; an ordinary request redirects
to the canonical `https://kiwiii.stream/blog/`. The `kshome` Worker has no custom domain,
and the zone's Worker route list is empty. The production website remains the Pages project.

## Transport rollout

All four public hostnames completed TLS 1.2 connections before rollout. The zone
minimum was raised to TLS 1.2. HSTS starts at one day with subdomain inheritance and preloading disabled,
so the apex policy does not force HTTPS on separately hosted subdomains. Keep the existing
origin SSL mode, DNS records and Jellyfin/Caddy configuration unchanged.

The zone HSTS header was confirmed on the blog Worker redirect. Pages did not inherit
that header in readback, so `_headers` and the API JSON response explicitly supply the
same one-day policy. Zone settings apply to traffic using that zone's proxy; the
DNS-only Jellyfin service remains controlled by Caddy.

The pre-change Jellyfin response was HTTP 502 from Caddy. Its TLS connection succeeded;
the upstream availability problem is separate from this work.

The existing leaked-credential rate-limit rule is retained. No additional paid services,
plan changes, DNS proxy changes or replacement of existing security rules are part of this work.

## Validation and rollback

Run `node tests/blocks.cjs`, `python3 tests/blog-publication.py`,
`python3 tests/blocks-storage.py`, `python3 blog-project/build.py` and
`python3 tests/check-release.py`. Live synthetic submissions belong only in a preview.

To roll back application behavior, restore the previous Pages deployment or revert the
repository change; leave the additive database objects in place. The prior zone minimum
was TLS 1.0 and HSTS was disabled. Turning HSTS off stops advertising it, but clients that
already received the policy may retain it for the advertised one day.
