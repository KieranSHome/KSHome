# Kiwiii Blocks release

## Intended deployment

The existing Cloudflare Pages project `kshome` is the production website.
Merge PR #5 into `main` only after final user go-live approval. Its existing Git integration
runs `python3 blog-project/build.py` and publishes `dist`, compiling the root
`functions/` directory as Pages Functions. No new Worker, domain, route or DNS record is needed.

Production `BLOCKS_DB` is bound to `kiwiii-blocks`; preview `BLOCKS_DB` is bound to
`kiwiii-blocks-preview`. Both have `database/blocks.sql` applied. Preview scores never feed
the production leaderboard. Do not run score-submission test fixtures against production.

## Preview trigger correction

The separate Workers Builds trigger `8e0725ac-e4bb-47ff-b426-b7f3147ff785` applies only to
`codex/kiwiii-blocks`. It previously ran an empty build command followed by
`npx wrangler preview`, which failed because this is a Pages repository with no Workers
preview configuration. No custom domain is attached to that separate `kshome` Worker.

The trigger now performs validation only:
- Build command: `python3 blog-project/build.py && node tests/blocks.cjs`
- Final command: `python3 tests/check-release.py`
- Label: `Pages release validation (no Worker deploy)`

These commands validate real gameplay/API logic, the generated game assets and Projects
integration, and the D1 schema in an in-memory SQLite database. They do not deploy or disable
checks. Pages remains responsible for preview and production deployment. The trigger is
still restricted to the same branch and paths. To reverse the trigger configuration change,
restore its original name, empty build command and `npx wrangler preview` final command;
this would restore the old failing redundant preview behavior.

## Final go-live action

Merge PR #5 into `main` and watch the resulting **Cloudflare Pages** production deployment.
Confirm the deployed commit matches the merge result, then check:
- `https://kiwiii.stream/Projects/` has the game card and shared leaderboard.
- `https://kiwiii.stream/Projects/blocks/` starts, moves, drops, pauses and restarts.
- `GET /api/blocks` responds successfully and uses the production database.
- Play remains available during leaderboard failures.
- No synthetic score submissions are made to production.

Before merge the last known production commit is
`3e425b68b4db6dafd52656ee052283052f80b4d3`. If the release misbehaves, roll back
the Pages production deployment to the previous successful deployment; leave the additive
D1 schema and databases intact so no score data is lost. A source revert can follow if needed.
