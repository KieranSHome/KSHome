"""Exercise publication decisions and generated output in a disposable site copy."""
import importlib.util
from pathlib import Path
import shutil
import tempfile
import unittest

ROOT = Path(__file__).resolve().parent.parent
spec = importlib.util.spec_from_file_location("blog_builder", ROOT / "blog-project/build.py")
builder = importlib.util.module_from_spec(spec)
spec.loader.exec_module(builder)


class PublicationTests(unittest.TestCase):
    def test_only_explicit_true_is_publishable(self):
        with tempfile.TemporaryDirectory() as directory:
            post = Path(directory) / "note.md"
            for value in ("false", "no", "0", "", "draft", "yes", "1", "TRUE", "tru", "null"):
                with self.subTest(value=value):
                    post.write_text(f"---\ntitle: Note\npublished: {value}\n---\nDraft body", encoding="utf-8")
                    self.assertIsNone(builder.read_post(post))
            post.write_text("---\ntitle: Note\n---\nNo publish flag", encoding="utf-8")
            self.assertIsNone(builder.read_post(post))
            post.write_text("---\npublished: true\n---\nNo title", encoding="utf-8")
            self.assertIsNone(builder.read_post(post))
            for value in ("true", "'true'", '"true"'):
                post.write_text(f"---\ntitle: Note\npublished: {value}\n---\nPublic body", encoding="utf-8")
                self.assertTrue(builder.read_post(post)["published"])

    def test_rebuild_excludes_drafts_from_pages_feed_and_listing(self):
        with tempfile.TemporaryDirectory() as directory:
            site = Path(directory) / "site"
            shutil.copytree(ROOT, site, ignore=shutil.ignore_patterns(".git", "dist", "__pycache__"))
            original = builder.ROOT, builder.POSTS, builder.DIST, builder.OUT
            try:
                builder.ROOT = site / "blog-project"
                builder.POSTS = builder.ROOT / "posts"
                builder.DIST = site / "dist"
                builder.OUT = builder.DIST / "blog"
                post = builder.POSTS / "publication-regression.md"
                post.write_text("---\ntitle: Publication regression\npublished: true\n---\nPublic body", encoding="utf-8")
                builder.main()
                article = builder.OUT / "posts/publication-regression.html"
                self.assertTrue(article.exists())
                for value in ("false", "draft", ""):
                    with self.subTest(value=value):
                        post.write_text(f"---\ntitle: Publication regression\npublished: {value}\n---\nHidden body", encoding="utf-8")
                        builder.main()
                        self.assertFalse(article.exists(), "old article must be removed")
                        for name in ("feed.json", "index.html"):
                            self.assertNotIn("Publication regression", (builder.OUT / name).read_text(encoding="utf-8"))
            finally:
                builder.ROOT, builder.POSTS, builder.DIST, builder.OUT = original


if __name__ == "__main__":
    unittest.main()
