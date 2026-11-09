"""Factual precinct directory from the November 7, 2026 chart labels.

Labels were read from the existing turnout graphics and checked against the
Governor and United States Senator graphics for the second sheet. They are
not a verified current roster. This module does not rank precincts or infer
interest in the office.
"""

from __future__ import annotations

import csv
import html
from pathlib import Path

DATA = Path(__file__).resolve().parents[1] / "data"
STATUS_VACANT = "labeled vacant in Nov 7 roster"
STATUS_CHAIR = "chair listed in Nov 7 roster"
STATUS_UNKNOWN = "unverified/unknown"
INTEREST = "No verified expressions of interest available"

# precinct, printed label, source graphic. Vacant is the chart's own words.
# Sheet 1 was read from turnout-p1.jpg. Sheet 2 was read from turnout-p2.jpg
# and the same labels were read again on governor-p2.jpg.
_SHEET1 = "turnout-p1.jpg"
_SHEET2 = "turnout-p2.jpg"

RAW = [
    ("4043", "Brandy Pope", _SHEET1),
    ("4161", "Jeri Buckner", _SHEET1),
    ("4162", "Brittany Pierce", _SHEET1),
    ("4163", "David Scott", _SHEET1),
    ("4164", "Westin Gentry", _SHEET1),
    ("4165", "Vacant (per GOP roster)", _SHEET1),
    ("4166", "Vacant (per GOP roster)", _SHEET1),
    ("4167", "Nan Stocker", _SHEET1),
    ("4168", "Vacant (per GOP roster)", _SHEET1),
    ("4169", "Jesse Davis", _SHEET1),
    ("4170", "Vacant (per GOP roster)", _SHEET1),
    ("4171", "Vacant (per GOP roster)", _SHEET1),
    ("4173", "Vacant (per GOP roster)", _SHEET1),
    ("4174", "Vacant (per GOP roster)", _SHEET1),
    ("4175", "Twila Henderson", _SHEET1),
    ("4176", "Jennifer Harris", _SHEET1),
    ("4177", "Tonya Morris", _SHEET1),
    ("4178", "Vacant (per GOP roster)", _SHEET1),
    ("4179", "Carol Ryan", _SHEET1),
    ("4180", "Heather Moss", _SHEET1),
    ("4181", "Deloy Nelson", _SHEET1),
    ("4182", "Terry Evans", _SHEET1),
    ("4183", "Brad Book", _SHEET1),
    ("4184", "Brent Bowen", _SHEET1),
    ("4185", "David Parker", _SHEET1),
    ("4186", "Don Hicks", _SHEET1),
    ("4187", "Vacant (per GOP roster)", _SHEET1),
    ("4188", "Vacant (per GOP roster)", _SHEET1),
    ("4189", "Marsha Grunder", _SHEET1),
    ("4190", "Sonja Knight", _SHEET1),
    ("4191", "Kellie Mason", _SHEET1),
    ("4192", "Jayne Howell", _SHEET1),
    ("4193", "Kim Taylor", _SHEET1),
    ("4194", "Vacant (per GOP roster)", _SHEET1),
    ("4195", "Rena Hardeman", _SHEET2),
    ("4196", "Mike Montes", _SHEET2),
    ("4197", "Preston Sloan", _SHEET2),
    ("4198", "Dave Augustus", _SHEET2),
    ("4199", "Peyton Inge", _SHEET2),
    ("4200", "Lance Mutzman", _SHEET2),
    ("4201", "Tom Carroll", _SHEET2),
    ("4202", "Erica Wheeler", _SHEET2),
    ("4203", "Vacant (per GOP roster)", _SHEET2),
    ("4204", "Guy Anderson", _SHEET2),
    ("4205", "Missy Grau", _SHEET2),
    ("4206", "Mike Gwartney", _SHEET2),
    ("4207", "Gloria McDonald", _SHEET2),
    ("4208", "Todd Bayuk", _SHEET2),
    ("4209", "Donald Glacy", _SHEET2),
    ("4210", "Rick Lifto", _SHEET2),
    ("4211", "Sean Nelson", _SHEET2),
    ("4212", "Barkat Ali", _SHEET2),
    ("4213", "Lisette Miller", _SHEET2),
    ("4214", "Vacant (per GOP roster)", _SHEET2),
    ("4215", "Renni Patterson", _SHEET2),
    ("4216", "Vacant (per GOP roster)", _SHEET2),
    ("4217", "David Rettig", _SHEET2),
    ("4218", "Alexandra Holmes", _SHEET2),
    ("4219", "James Clark", _SHEET2),
    ("4220", "Tomas Mendoza", _SHEET2),
    ("4221", "Vacant (per GOP roster)", _SHEET2),
    ("4222", "Monty Webb", _SHEET2),
    ("4223", "Vacant (per GOP roster)", _SHEET2),
    ("4226", "Scott Smith", _SHEET2),
    ("4231", "Jon Almeida", _SHEET2),
    ("4232", "Vacant (per GOP roster)", _SHEET2),
    ("4233", "Vacant (per GOP roster)", _SHEET2),
]


def _status(label: str) -> str:
    if label == "Vacant (per GOP roster)":
        return STATUS_VACANT
    if label:
        return STATUS_CHAIR
    return STATUS_UNKNOWN


def rows():
    labels = {item[0]: item for item in RAW}
    with (DATA / "pct4-turnout.csv").open(encoding="utf-8", newline="") as handle:
        turnout = list(csv.DictReader(handle))
    built = []
    for item in turnout:
        precinct = item["precinct"]
        known = labels.get(precinct)
        if known is None:
            built.append({
                "precinct": precinct,
                "label": "",
                "status": STATUS_UNKNOWN,
                "source": "",
                "registered": item["registered"],
                "ballots_cast": item["ballots_cast"],
            })
            continue
        _precinct, label, source = known
        built.append({
            "precinct": precinct,
            "label": label,
            "status": _status(label),
            "source": source,
            "registered": item["registered"],
            "ballots_cast": item["ballots_cast"],
        })
    return built


def counts(items=None):
    items = rows() if items is None else items
    return {
        "precincts": len(items),
        STATUS_VACANT: sum(1 for item in items if item["status"] == STATUS_VACANT),
        STATUS_CHAIR: sum(1 for item in items if item["status"] == STATUS_CHAIR),
        STATUS_UNKNOWN: sum(1 for item in items if item["status"] == STATUS_UNKNOWN),
    }


def directory_table(items) -> str:
    body = []
    for item in items:
        source = item["source"]
        source_html = (
            f'<a href="/data/precinct-4/{html.escape(source)}">{html.escape(source)}</a>'
            if source
            else "No legible label was read"
        )
        label = item["label"] if item["label"] else "No legible label was read"
        body.append(
            "<tr data-precinct=\"{p}\" data-status=\"{s}\">"
            "<th scope=\"row\">{p}</th>"
            "<td>{status}</td>"
            "<td>{label}</td>"
            "<td>{source}</td>"
            "<td>{registered}</td>"
            "<td>{ballots}</td>"
            "</tr>".format(
                p=html.escape(item["precinct"]),
                s=html.escape(item["status"]),
                status=html.escape(item["status"]),
                label=html.escape(label),
                source=source_html,
                registered=html.escape(item["registered"]),
                ballots=html.escape(item["ballots_cast"]),
            )
        )
    return (
        '<div class="results-scroll"><table class="directory-table" id="precinct-directory">'
        "<caption>67 voting precincts in Commissioner Precinct 4, in the order of pct4-turnout.csv. "
        "Chair text is the label printed on the November 7, 2026 chart named in the source column.</caption>"
        "<thead><tr>"
        "<th scope=\"col\">Precinct</th>"
        "<th scope=\"col\">Status of the Nov 7 chart label</th>"
        "<th scope=\"col\">Label printed on the chart</th>"
        "<th scope=\"col\">Source chart</th>"
        "<th scope=\"col\">Registered voters</th>"
        "<th scope=\"col\">Ballots cast</th>"
        "</tr></thead><tbody>"
        + "".join(body)
        + "</tbody></table></div>"
        '<p id="directory-filter-status" role="status"></p>'
    )


def item_list():
    items = rows()
    elements = []
    for index, item in enumerate(items, start=1):
        elements.append({
            "@type": "ListItem",
            "position": index,
            "name": item["precinct"],
            "description": item["status"],
        })
    return {
        "@context": "https://schema.org",
        "@type": "ItemList",
        "name": "Voting precincts in Denton County Commissioner Precinct 4",
        "numberOfItems": len(elements),
        "itemListElement": elements,
    }


def write_ledger(root: Path) -> None:
    items = rows()
    tally = counts(items)
    folder = root / "_brief" / "election"
    folder.mkdir(parents=True, exist_ok=True)
    lines = [
        "# Precinct directory evidence ledger",
        "",
        "Private. Not a current roster and not a recruitment list.",
        "",
        "Each label was read from the named chart in `site/data/precinct-4/`. Sheet 1 is `turnout-p1.jpg`. Sheet 2 is `turnout-p2.jpg`. The same sheet 2 labels were also read on `governor-p2.jpg` for precincts 4198 through 4233, and on `senate-p2.jpg` for precincts 4198 through 4212. The charts’ footnote dates the chair column to the Denton County GOP roster retrieved November 7, 2026. That date is not an independent verification that the label is the current roster.",
        "",
        "The turnout file supplies the precinct list and the registered and ballots-cast counts. It does not contain chair names. A precinct absent from the charts would be unverified/unknown. None of these 67 were absent.",
        "",
        f"- Precincts: {tally['precincts']}",
        f"- {STATUS_CHAIR}: {tally[STATUS_CHAIR]}",
        f"- {STATUS_VACANT}: {tally[STATUS_VACANT]}",
        f"- {STATUS_UNKNOWN}: {tally[STATUS_UNKNOWN]}",
        "",
        "No verified expressions of interest are in this repository. None were added.",
        "",
        "| Precinct | Status | Printed label | Source chart | Registered | Ballots cast |",
        "|---|---|---|---|---|---|",
    ]
    for item in items:
        lines.append(
            f"| {item['precinct']} | {item['status']} | {item['label'] or '—'} | {item['source'] or '—'} | {item['registered']} | {item['ballots_cast']} |"
        )
    lines.append("")
    (folder / "precinct-directory-ledger.md").write_text("\n".join(lines), encoding="utf-8")
