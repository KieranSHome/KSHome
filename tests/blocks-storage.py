"""Run the API's actual rate and cleanup SQL against an isolated SQLite database."""
from pathlib import Path
import re
import sqlite3
import unittest

ROOT = Path(__file__).resolve().parent.parent
SOURCE = (ROOT / "functions/api/blocks.js").read_text(encoding="utf-8")


def query(name):
    match = re.search(r"const " + name + r" = `([^`]+)`;", SOURCE)
    if not match:
        raise AssertionError(f"Missing API SQL: {name}")
    return match.group(1)


class StorageTests(unittest.TestCase):
    def setUp(self):
        self.db = sqlite3.connect(":memory:")
        schema = (ROOT / "database/blocks.sql").read_text(encoding="utf-8")
        self.db.executescript(schema)
        self.db.executescript(schema)  # additive and safe to reapply

    def tearDown(self):
        self.db.close()

    def test_write_budget_blocks_and_resets_without_affecting_other_keys(self):
        sql = query("WRITE_RATE_SQL")
        for count in range(1, 61):
            self.assertEqual(self.db.execute(sql, ("first", 100)).fetchone(), (count,))
        for _ in range(5):
            self.assertIsNone(self.db.execute(sql, ("first", 100)).fetchone())
        self.assertEqual(self.db.execute("SELECT requests FROM blocks_request_limits WHERE rate_key='first'").fetchone(), (60,))
        self.assertEqual(self.db.execute(sql, ("second", 100)).fetchone(), (1,))
        self.assertEqual(self.db.execute(sql, ("first", 101)).fetchone(), (1,))

    def test_cleanup_is_bounded_and_preserves_live_records(self):
        self.db.executemany("INSERT INTO blocks_sessions VALUES (?,100,'old',0)", [(str(i),) for i in range(250)])
        self.db.execute("INSERT INTO blocks_sessions VALUES ('live',200,'live',0)")
        self.db.executemany("INSERT INTO blocks_request_limits VALUES (?,100,1)", [(str(i),) for i in range(250)])
        self.db.execute("INSERT INTO blocks_request_limits VALUES ('live',200,1)")
        for sql, table in ((query("SESSION_CLEANUP_SQL"), "blocks_sessions"), (query("RATE_CLEANUP_SQL"), "blocks_request_limits")):
            with self.subTest(table=table):
                self.db.execute(sql, (200,))
                self.assertEqual(self.db.execute(f"SELECT COUNT(*) FROM {table}").fetchone(), (151,))
                plan = " ".join(str(row) for row in self.db.execute("EXPLAIN QUERY PLAN " + sql, (200,)))
                self.assertIn("USING INDEX", plan, "expiry cleanup must use an index")
                self.assertNotIn("USE TEMP B-TREE", plan, "expiry order must not sort the entire table")


if __name__ == "__main__":
    unittest.main()
