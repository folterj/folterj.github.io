# folterj.github.io

Personal homepage: featured GitHub projects, organisations and publications.

- Edit `site.yml` to change the bio, links, featured repos and which repos are shown with a publication.
- Repo details (description, stars, docs link) come from the GitHub API and publications from ORCID, refreshed daily by the workflow.
- Card images are listed under `images` in `site.yml`; the build shrinks them into thumbnails. Images not hosted in a repo go in `images/`.
- Preview locally: `pip install pyyaml pillow`, `python build.py`, then open `_site/index.html`.
