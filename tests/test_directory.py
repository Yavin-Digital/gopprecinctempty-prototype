import json
import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "build"))

from precinct_directory import STATUS_CHAIR, STATUS_UNKNOWN, STATUS_VACANT, counts, rows  # noqa: E402


class DirectoryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        subprocess.run([sys.executable, "build/render.py"], cwd=ROOT, check=True)
        cls.page = (ROOT / "index.html").read_text(encoding="utf-8")
        cls.items = rows()
        cls.tally = counts(cls.items)

    def test_counts_match_the_chart_transcription_and_turnout_file(self):
        self.assertEqual(self.tally["precincts"], 67)
        self.assertEqual(self.tally[STATUS_CHAIR], 49)
        self.assertEqual(self.tally[STATUS_VACANT], 18)
        self.assertEqual(self.tally[STATUS_UNKNOWN], 0)
        by_precinct = {item["precinct"]: item for item in self.items}
        self.assertEqual(by_precinct["4043"]["label"], "Brandy Pope")
        self.assertEqual(by_precinct["4043"]["registered"], "2593")
        self.assertEqual(by_precinct["4043"]["ballots_cast"], "1391")
        self.assertEqual(by_precinct["4043"]["source"], "turnout-p1.jpg")
        self.assertEqual(by_precinct["4165"]["status"], STATUS_VACANT)
        self.assertEqual(by_precinct["4196"]["label"], "Mike Montes")
        self.assertEqual(by_precinct["4196"]["source"], "turnout-p2.jpg")
        self.assertEqual(len((ROOT / "data" / "pct4-turnout.csv").read_text().splitlines()), 68)

    def test_page_keeps_the_facts_and_leaves_out_the_campaign_chrome(self):
        text = self.page
        self.assertEqual(text.lower().count("<h1"), 1)
        self.assertIn('content="noindex, nofollow"', text)
        self.assertIn("No verified expressions of interest available", text)
        self.assertIn("not a claim that the page is private", text)
        self.assertIn("November 7, 2026", text)
        self.assertIn("1:24:17 AM CST", text)
        self.assertIn("385491", text)
        self.assertIn("189,707", text)
        self.assertIn("109,642", text)
        self.assertIn('href="/charts/turnout-p1.jpg"', text)
        self.assertIn('href="/charts/turnout-p2.jpg"', text)
        self.assertIn('href="/data/pct4-turnout.csv"', text)
        self.assertNotIn("review-banner", text)
        self.assertNotIn("current vacancy", text.lower())
        self.assertNotIn("recruit", text.lower())
        self.assertNotIn("password", text.lower())
        self.assertNotIn("pct4-long.csv", text)
        blocks = []
        for part in text.split('<script type="application/ld+json">')[1:]:
            blocks.append(json.loads(part.split("</script>", 1)[0]))
        self.assertEqual(next(b for b in blocks if b["@type"] == "ItemList")["numberOfItems"], 67)
        self.assertEqual((ROOT / "CNAME").read_text().strip(), "gopprecinctempty.clientreview.co")
        self.assertIn("Disallow: /", (ROOT / "robots.txt").read_text())
        self.assertTrue((ROOT / "charts" / "turnout-p1.jpg").is_file())
        self.assertTrue((ROOT / "charts" / "turnout-p2.jpg").is_file())
        self.assertFalse((ROOT / "data" / "pct4-long.csv").exists())


if __name__ == "__main__":
    unittest.main()
