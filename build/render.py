"""Write the standalone precinct directory. Reads only the packaged labels and turnout file."""

from __future__ import annotations

import html
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "build"))

from precinct_directory import (  # noqa: E402
    INTEREST,
    STATUS_CHAIR,
    STATUS_UNKNOWN,
    STATUS_VACANT,
    counts,
    rows,
)

SITE = ROOT
HOST = "https://gopprecinctempty.clientreview.co"
SOURCE_PAGE = "https://results.enr.clarityelections.com/TX/Denton/127398/"
SOURCE_ZIP = "https://results.enr.clarityelections.com/TX/Denton/127398/385491/reports/detailxml.zip"
SNAPSHOT = "November 4, 2026, 1:24:17 AM CST"
ROSTER_DATE = "November 7, 2026"


def page() -> str:
    items = rows()
    tally = counts(items)
    registered = sum(int(item["registered"]) for item in items)
    ballots = sum(int(item["ballots_cast"]) for item in items)
    body_rows = []
    list_items = []
    for index, item in enumerate(items, start=1):
        source = item["source"]
        source_html = f'<a href="/charts/{html.escape(source)}">{html.escape(source)}</a>'
        body_rows.append(
            "<tr data-precinct=\"{p}\" data-status=\"{s}\">"
            "<th scope=\"row\">{p}</th><td>{status}</td><td>{label}</td><td>{source}</td><td>{reg}</td><td>{ballots}</td>"
            "</tr>".format(
                p=html.escape(item["precinct"]),
                s=html.escape(item["status"]),
                status=html.escape(item["status"]),
                label=html.escape(item["label"]),
                source=source_html,
                reg=html.escape(item["registered"]),
                ballots=html.escape(item["ballots_cast"]),
            )
        )
        list_items.append({
            "@type": "ListItem",
            "position": index,
            "name": item["precinct"],
            "description": item["status"],
        })
    title = "Denton County Commissioner Precinct 4 directory"
    description = (
        "Directory of 67 voting precincts in Denton County Commissioner Precinct 4. "
        "Chair labels are the November 7, 2026 roster text printed on the turnout charts, not a verified current roster. "
        "No verified expressions of interest are available."
    )
    webpage = {
        "@context": "https://schema.org",
        "@type": "WebPage",
        "url": HOST + "/",
        "name": title,
        "description": description,
        "inLanguage": "en",
        "dateModified": "2026-11-07",
    }
    item_list = {
        "@context": "https://schema.org",
        "@type": "ItemList",
        "name": "Voting precincts in Denton County Commissioner Precinct 4",
        "numberOfItems": len(items),
        "itemListElement": list_items,
    }
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <meta name="robots" content="noindex, nofollow">
  <title>{html.escape(title)}</title>
  <meta name="description" content="{html.escape(description)}">
  <link rel="canonical" href="{HOST}/">
  <link rel="stylesheet" href="/css/site.css">
  <script type="application/ld+json">{json.dumps(webpage, ensure_ascii=False)}</script>
  <script type="application/ld+json">{json.dumps(item_list, ensure_ascii=False)}</script>
</head>
<body>
  <a class="skip" href="#directory">Skip to the precinct table</a>
  <header class="site-header">
    <div class="wrap">
      <p class="kicker">Denton County, Texas</p>
      <p class="title">Commissioner Precinct 4 directory</p>
    </div>
  </header>
  <main id="directory" class="wrap">
    <h1>Precinct directory</h1>
    <p class="lede">The 67 voting precincts in County Commissioner Precinct 4, with the chair label printed on the {ROSTER_DATE} charts. This is not all of Denton County.</p>
    <h2>What the labels are</h2>
    <p>The chair text was read from <a href="/charts/turnout-p1.jpg">turnout-p1.jpg</a> and <a href="/charts/turnout-p2.jpg">turnout-p2.jpg</a>. The chart footnote says those labels are the Denton County GOP roster retrieved {ROSTER_DATE}. They were not independently rechecked as the roster on any later date. A printed label is not a claim about who holds the office today.</p>
    <p>Status words: “{STATUS_CHAIR}”, “{STATUS_VACANT}”, and “{STATUS_UNKNOWN}”. “{STATUS_VACANT}” means the chart prints “Vacant (per GOP roster)” as of that {ROSTER_DATE} label. It is not a later confirmation that the office is empty.</p>
    <p>Of these 67 precincts, {tally[STATUS_CHAIR]} have a name printed on the chart, {tally[STATUS_VACANT]} are labeled vacant on that chart, and {tally[STATUS_UNKNOWN]} had no legible label.</p>
    <h2>Expressions of interest</h2>
    <p>{INTEREST}</p>
    <p>This page does not identify, rank, or recommend anyone for the office. Registered voters and ballots cast are counts from the unofficial November 3, 2026 general election snapshot saved {SNAPSHOT}, version 385491. Adding the 67 registered-voter cells gives {registered:,}. Adding the 67 ballots-cast cells gives {ballots:,}. Those are sums of this file, not a countywide total, and they are not a score.</p>
    <h2>Source</h2>
    <p>Election counts: Denton County Elections, <a href="{SOURCE_ZIP}">detailxml.zip</a> for version 385491. Landing page: <a href="{SOURCE_PAGE}">Denton County results</a>. The turnout file on this site is <a href="/data/pct4-turnout.csv">pct4-turnout.csv</a>. N/A in the underlying choice export means not on the ballot, not zero. This page does not publish that choice file.</p>
    <p>The noindex tag asks search engines not to index this preview host. It is not a claim that the page is private.</p>
    <h2>Filter the table</h2>
    <form class="filters" action="#precinct-directory" method="get" onsubmit="return false">
      <div>
        <label for="directory-precinct">Precinct number</label>
        <input id="directory-precinct" name="precinct" type="search" inputmode="numeric" autocomplete="off">
      </div>
      <div>
        <label for="directory-status">Chart label status</label>
        <select id="directory-status" name="status">
          <option value="">All 67 precincts</option>
          <option value="{STATUS_CHAIR}">{STATUS_CHAIR}</option>
          <option value="{STATUS_VACANT}">{STATUS_VACANT}</option>
          <option value="{STATUS_UNKNOWN}">{STATUS_UNKNOWN}</option>
        </select>
      </div>
    </form>
    <h2>The 67 precincts</h2>
    <div class="scroll">
      <table id="precinct-directory">
        <caption>67 voting precincts in Commissioner Precinct 4, in the order of pct4-turnout.csv. Chair text is the label printed on the {ROSTER_DATE} chart named in the source column.</caption>
        <thead>
          <tr>
            <th scope="col">Precinct</th>
            <th scope="col">Status of the Nov 7 chart label</th>
            <th scope="col">Label printed on the chart</th>
            <th scope="col">Source chart</th>
            <th scope="col">Registered voters</th>
            <th scope="col">Ballots cast</th>
          </tr>
        </thead>
        <tbody>
          {''.join(body_rows)}
        </tbody>
      </table>
    </div>
    <p id="directory-filter-status" role="status"></p>
  </main>
  <script src="/js/directory.js"></script>
</body>
</html>
"""


def main() -> None:
    html_text = page()
    (SITE / "index.html").write_text(html_text, encoding="utf-8")
    print(f"rows in page: {html_text.count('<tr data-precinct=')}")


if __name__ == "__main__":
    main()
