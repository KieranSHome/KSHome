# Kiwiii.Stream

The public site has these destinations:

- **Home:** `index.html` (the single-page homepage).
- **Blog:** [blog.kiwiii.stream](https://blog.kiwiii.stream/), generated from Markdown posts in `blog-project/posts/`.
- **Jellyfin:** [jellyfin.kiwiii.stream](https://jellyfin.kiwiii.stream), the external media service.
- **Projects:** `/Projects/`, the project portfolio page.
- **Broke:** `/broke/`, the debt dashboard.

The homepage contains sections such as Services and About. Blog and Jellyfin are separate services; Projects and Broke use dedicated paths.

## Blog source

Edit Markdown posts in `blog-project/posts/` and use `blog-project/build.py` to build the blog output. The homepage reads the blog's `feed.json` to display the latest post.

## Production safety

Do not store DNS, domain, Cloudflare, or Jellyfin configuration in this repository. Changes to those systems should be made separately and deliberately.
