# folterj.github.io

Personal homepage at https://joostdefolter.info: featured GitHub projects, publications and organisations.

## How it works
- `site.yml` holds everything chosen by hand: bio, links, featured repos, card images and which repos belong to which paper.
- `build.py` combines it with live data into `_site/`: repo descriptions, stars and docs links from the GitHub API, publications from ORCID, organisations from the GitHub profile.
- The workflow in `.github/workflows/pages.yml` builds and deploys on every push to `main` and daily at 05:00 UTC, so new stars, papers and descriptions appear without edits.

## Making changes
Edit `site.yml` and push; the site updates within about two minutes.

| To change | Edit |
|---|---|
| Bio, title, profile links | `bio`, `title`, `links` |
| Photo | replace `static/joost.jpg` |
| Featured repos, sections and their order | `featured` |
| A repo's description | its GitHub description, or `descriptions` if it has none |
| A repo's "Docs" link | the repo's website field on GitHub |
| A card image | `images`: a URL (e.g. `https://raw.githubusercontent.com/<owner>/<repo>/HEAD/<path>`) or a file in `images/` (SVGs are used as they are, other images are shrunk); add `fit: contain` for logos and diagrams so they aren't cropped |
| Repos shown with a paper | `paper_repos`, keyed by DOI in lower case |
| Publications | add or fix them in ORCID (0000-0001-9704-2925); the next build picks them up |
| Layout and colours | `template.html`, `style.css` |

Preview locally: `pip install pyyaml pillow`, `python build.py`, then open `_site/index.html`.
Run it again by hand: Actions → Build and deploy → Run workflow.

## Domain, DNS and email
- `joostdefolter.info` is registered at Cloudflare (renews automatically; expires June 2028 at the time of writing). Keep a valid card on the Cloudflare account.
- DNS is at Cloudflare: four A records for `@` to `185.199.108.153`, `.109.153`, `.110.153`, `.111.153` and a CNAME `www` to `folterj.github.io`, all **DNS only** (grey cloud) so GitHub can renew its HTTPS certificate.
- The custom domain is set in this repo's Settings → Pages (the `CNAME` file only records it), with Enforce HTTPS on.
- Email: Cloudflare Email Routing forwards every address at the domain (catch-all) to folterj@gmail.com. Its MX and SPF records are managed by Cloudflare; don't delete them.

## Things to watch
- GitHub disables the daily schedule after 60 days without commits to this repo and sends an email; re-enable it under Actions, or push any change.
- After a DNS change, a router or browser can show the old site for a few hours; check from another network before changing anything.
- The previous Joomla site (pages, images, downloads) is backed up at `E:\Personal\PersonalPage\joostdefolter.info-backup`.

## To do
- Replace the drawn illustrations (`images/*.svg`) with real screenshots or figures once those repos have them.
- Fix the all-caps title of the 2018 NICE paper in ORCID.
- Confirm the IEEE 11073 papers' repo links (IEEE11073Analyser, IEEEAgentManager) in `paper_repos`.
- Optionally attach the old site's downloads (installers, manuals) to GitHub Releases on their repos.
