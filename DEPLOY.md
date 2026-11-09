# Deploy this preview

This directory is ready to publish as the root of https://github.com/Yavin-Digital/gopprecinctempty-prototype

The agent that built it could not push: GitHub returned 403 for `cursor[bot]` on that repository. Nothing was deployed.

From this folder, with an account that can write to the repository:

```bash
git remote add origin https://github.com/Yavin-Digital/gopprecinctempty-prototype.git
git push -u origin main
```

Then set GitHub Pages to deploy from the `main` branch, folder `/` (root). `CNAME` is already `gopprecinctempty.clientreview.co`. Do not change DNS. Do not change the campaign repository `mikemontesforprecinctchair-prototype`.

After Pages finishes, check `https://gopprecinctempty.clientreview.co/` for HTTP 200. A 404 before that check means the site is not up.
