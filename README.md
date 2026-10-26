# Kiwiii.Stream

The public site has these destinations:

- **Home:** `index.html` (the single-page homepage).
- **Blog:** [blog.kiwiii.stream](https://blog.kiwiii.stream/), published from the separate `KieranSHome/Blog` repository through Cloudflare Pages.
- **Jellyfin:** [jellyfin.kiwiii.stream](https://jellyfin.kiwiii.stream), the external media service.
- **Projects:** `/Projects/`, the project portfolio page.
- **Broke:** `/broke/`, the debt dashboard.

The homepage contains sections such as Services and About. Blog and Jellyfin are separate services; Projects and Broke use dedicated paths.

## Blog source

The canonical blog source is the separate [`KieranSHome/Blog`](https://github.com/KieranSHome/Blog) repository. Its `build.py` generates the Cloudflare Pages site in `dist/`. The `blog-project/` directory in this repository is a legacy copy and should not be treated as the live deployment source. Keep the homepage's latest-post feed integration aligned with the canonical blog when publishing new posts.

## Production safety

Do not store DNS, domain, Cloudflare, or Jellyfin configuration in this repository. Changes to those systems should be made separately and deliberately.
