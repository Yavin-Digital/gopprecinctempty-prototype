# Commissioner Precinct 4 directory

Public preview of an aggregate precinct directory. It lists 67 voting precincts in Denton County Commissioner Precinct 4.

Chair text was read from `site/charts/turnout-p1.jpg` and `site/charts/turnout-p2.jpg`. The chart footnote dates those labels to the Denton County GOP roster retrieved November 7, 2026. That is not an independent check that the label is the current roster.

Registered voters and ballots cast come from `site/data/pct4-turnout.csv`, an unofficial November 3, 2026 general-election snapshot saved November 4, 2026, 1:24:17 AM CST, version 385491.

Source landing page: https://results.enr.clarityelections.com/TX/Denton/127398/

Source export: https://results.enr.clarityelections.com/TX/Denton/127398/385491/reports/detailxml.zip

The site asks search engines not to index it. That is not a claim that the page is private.

```bash
python3 build/render.py
python3 -m unittest tests/test_directory.py
```
