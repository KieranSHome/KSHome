# Kiwiii.Stream

The public site has these destinations:

- **Home:** `index.html` (the single-page homepage).
- **Blog:** [kiwiii.stream/blog](https://kiwiii.stream/blog/), published from the separate `KieranSHome/Blog` repository through Cloudflare Pages.
- **Jellyfin:** [jellyfin.kiwiii.stream](https://jellyfin.kiwiii.stream), the external media service.
- **Projects:** `/Projects/`, the project portfolio page.
- **Broke:** `/broke/`, the debt dashboard.

The homepage contains sections such as Services and About. Blog and Jellyfin are separate services; Projects and Broke use dedicated paths.

## Blog source

The consolidated blog source is `blog-project/` in this repository. Its `build.py` generates the site under `/blog/` during the GitHub Pages workflow. The former `KieranSHome/Blog` repository is retained as a non-destructive archive until migration verification is complete. Do not delete the old Blog repository until the consolidated site has been verified. Keep the homepage's latest-post feed integration aligned with the canonical blog when publishing new posts.

## Production safety

Do not store DNS, domain, Cloudflare, or Jellyfin configuration in this repository. Changes to those systems should be made separately and deliberately.
