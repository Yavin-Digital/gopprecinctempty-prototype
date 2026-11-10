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

    def test_map_uses_the_official_precinct_polygons(self):
        geojson_path = ROOT / "data" / "pct4-precincts.geojson"
        note = (ROOT / "data" / "pct4-boundaries.md").read_text(encoding="utf-8")
        data = json.loads(geojson_path.read_text(encoding="utf-8"))
        self.assertLess(geojson_path.stat().st_size, 1_000_000)
        self.assertEqual(data["type"], "FeatureCollection")
        self.assertEqual(len(data["features"]), 67)
        ids = [feature["properties"]["precinct"] for feature in data["features"]]
        self.assertEqual(ids, sorted(item["precinct"] for item in self.items))
        self.assertEqual(set(ids), {item["precinct"] for item in self.items})
        for feature in data["features"]:
            self.assertIn(feature["geometry"]["type"], ("Polygon", "MultiPolygon"))
            self._assert_coordinates_in_denton(feature["geometry"]["coordinates"])
        self.assertIn("https://gis.dentoncounty.gov/arcgis/rest/services/PoliticalBoundaries_GC/MapServer/9", note)
        self.assertIn("2026-11-10", note)
        self.assertIn("None of the 67 precincts were missing", note)
        self.assertEqual(self.page.count('class="show-on-map"'), 67)
        self.assertIn('id="precinct-map"', self.page)
        self.assertIn("Tap to use the map", self.page)
        self.assertIn('src="/vendor/leaflet/leaflet.js"', self.page)
        self.assertIn("https://gis.dentoncounty.gov/arcgis/rest/services/PoliticalBoundaries_GC/MapServer/9", self.page)
        self.assertIn("chair listed in Nov 7 roster", self.page)
        self.assertIn("labeled vacant in Nov 7 roster", self.page)
        map_js = (ROOT / "js" / "map.js").read_text(encoding="utf-8")
        css = (ROOT / "css" / "site.css").read_text(encoding="utf-8")
        self.assertIn("/data/pct4-precincts.geojson", map_js)
        self.assertIn("https://tile.openstreetmap.de/{z}/{x}/{y}.png", map_js)
        self.assertNotIn("api_key", map_js.lower())
        self.assertNotIn("apikey", map_js.lower())
        self.assertIn("#0d0572", map_js)
        self.assertIn("#9a3412", map_js)
        self.assertIn("--chair-fill: #0d0572", css)
        self.assertIn("--vacant-fill: #9a3412", css)

    def _assert_coordinates_in_denton(self, coords):
        if isinstance(coords[0], (int, float)):
            self.assertGreaterEqual(coords[0], -98)
            self.assertLessEqual(coords[0], -96.5)
            self.assertGreaterEqual(coords[1], 32.5)
            self.assertLessEqual(coords[1], 34)
            return
        for part in coords:
            self._assert_coordinates_in_denton(part)


if __name__ == "__main__":
    unittest.main()
