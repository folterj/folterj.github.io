"""Build the homepage into _site/ from site.yml, the GitHub API and ORCID."""
import hashlib
import io
import json
import os
import shutil
import urllib.request
from datetime import date
from html import escape
from pathlib import Path

import yaml
from PIL import Image

ROOT = Path(__file__).parent
SITE = ROOT / '_site'
VENUE_TYPES = {'preprint': 'Preprint', 'conference-paper': 'Conference paper', 'book-chapter': 'Book chapter'}
THUMBNAIL_SIZE = 720


def fetch_json(url, headers):
    request = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(request, timeout=30) as response:
        return json.load(response)


def github(path):
    headers = {'Accept': 'application/vnd.github+json'}
    token = os.environ.get('GITHUB_TOKEN')
    if token:
        headers['Authorization'] = f'Bearer {token}'
    return fetch_json(f'https://api.github.com/{path}', headers)


def fetch_publications(orcid):
    works = fetch_json(f'https://pub.orcid.org/v3.0/{orcid}/works', {'Accept': 'application/json'})
    publications = []
    for group in works['group']:
        summary = group['work-summary'][0]
        external_ids = (summary.get('external-ids') or {}).get('external-id', [])
        dois = [ext['external-id-value'].lower() for ext in external_ids if ext['external-id-type'] == 'doi']
        publication_date = summary.get('publication-date') or {}
        publications.append({
            'title': summary['title']['title']['value'],
            'year': (publication_date.get('year') or {}).get('value', ''),
            'venue': (summary.get('journal-title') or {}).get('value') or VENUE_TYPES.get(summary['type'], ''),
            'doi': dois[0] if dois else None,
        })
    return sorted(publications, key=lambda publication: publication['year'], reverse=True)


def make_thumbnail(name, source):
    """Shrink a repo image (a URL, or a path in this repo) into _site/thumbs/."""
    if source.startswith('http'):
        with urllib.request.urlopen(source, timeout=60) as response:
            data = response.read()
    else:
        data = (ROOT / source).read_bytes()
    target = SITE / 'thumbs' / name.replace('/', '_')
    target.parent.mkdir(parents=True, exist_ok=True)
    if source.lower().endswith('.svg'):
        # Vector images scale by themselves, so they are used as they are
        target = target.with_suffix('.svg')
        target.write_bytes(data)
        return target.relative_to(SITE).as_posix()
    image = Image.open(io.BytesIO(data))
    image = image.convert('RGBA' if 'A' in image.getbands() or image.mode == 'P' else 'RGB')
    image.thumbnail((THUMBNAIL_SIZE, THUMBNAIL_SIZE))
    target = target.with_suffix('.webp')
    image.save(target, 'WEBP', quality=85)
    return target.relative_to(SITE).as_posix()


def render_links(links):
    return ''.join(f'<a class="pill" href="{escape(link["url"])}">{escape(link["label"])}</a>' for link in links)


def render_orgs(orgs):
    items = ''.join(
        f'<a class="org" href="https://github.com/{escape(org["login"])}">'
        f'<img src="{escape(org["avatar_url"])}&s=80" alt="" loading="lazy"><span>{escape(org["name"] or org["login"])}</span></a>'
        for org in orgs)
    return f'<section><h2>Organisations</h2><div class="orgs">{items}</div></section>'


def render_repo(repo, description, image):
    docs = f'<a href="{escape(repo["homepage"])}">Docs</a>' if repo.get('homepage') else ''
    language = f'<span>{escape(repo["language"])}</span>' if repo.get('language') else ''
    if image:
        thumbnail = f'<img src="{escape(image["thumbnail"])}" alt="" loading="lazy">'
        thumbnail_class = f'thumb {image.get("fit", "cover")}'
    else:
        # Repos without an image show their owner's logo, so every card keeps the same shape
        thumbnail = f'<img src="{escape(repo["owner"]["avatar_url"])}&s=120" alt="" loading="lazy">'
        thumbnail_class = 'thumb placeholder'
    return (
        f'<article class="card">'
        f'<a class="{thumbnail_class}" href="{escape(repo["html_url"])}" tabindex="-1">{thumbnail}</a>'
        f'<div class="owner"><img src="{escape(repo["owner"]["avatar_url"])}&s=40" alt="" loading="lazy">{escape(repo["owner"]["login"])}</div>'
        f'<h3><a href="{escape(repo["html_url"])}">{escape(repo["name"])}</a></h3>'
        f'<p>{escape(description)}</p>'
        f'<div class="meta">{language}<span>★ {repo["stargazers_count"]}</span>{docs}</div>'
        f'</article>')


def render_featured(featured, repos, descriptions, images):
    sections = []
    for section in featured:
        cards = ''.join(
            render_repo(repos[name], repos[name]['description'] or descriptions.get(name, ''), images.get(name))
            for name in section['repos'])
        sections.append(f'<section><h2>{escape(section["section"])}</h2><div class="grid">{cards}</div></section>')
    return ''.join(sections)


def render_publications(publications, paper_repos):
    items = []
    for publication in publications:
        title = escape(publication['title'])
        if publication['doi']:
            title = f'<a href="https://doi.org/{escape(publication["doi"])}">{title}</a>'
        repo_links = ''.join(
            f'<a class="chip" href="https://github.com/{escape(name)}">{escape(name.split("/")[1])}</a>'
            for name in paper_repos.get(publication['doi'], []))
        items.append(
            f'<li><span class="year">{escape(publication["year"])}</span>'
            f'<div><div class="title">{title}</div><div class="venue">{escape(publication["venue"])}</div>'
            f'{f"<div>{repo_links}</div>" if repo_links else ""}</div></li>')
    return f'<section><h2>Publications</h2><ol class="pubs">{"".join(items)}</ol></section>'


def build():
    config = yaml.safe_load((ROOT / 'site.yml').read_text(encoding='utf-8'))
    paper_repos = {doi.lower(): names for doi, names in config['paper_repos'].items()}
    repo_names = {name for section in config['featured'] for name in section['repos']}
    repos = {name: github(f'repos/{name}') for name in repo_names}
    orgs = [github(f'orgs/{org["login"]}') for org in github(f'users/{config["github_user"]}/orgs')]
    publications = fetch_publications(config['orcid'])

    shutil.rmtree(SITE, ignore_errors=True)
    images = config.get('images', {})
    for name, image in images.items():
        image['thumbnail'] = make_thumbnail(name, image['src'])

    template = (ROOT / 'template.html').read_text(encoding='utf-8')
    page = (template
            .replace('{{name}}', escape(config['name']))
            .replace('{{title}}', escape(config['title']))
            .replace('{{photo}}', escape(config['photo']))
            .replace('{{bio}}', escape(config['bio'].strip()))
            .replace('{{links}}', render_links(config['links']))
            .replace('{{orgs}}', render_orgs(orgs))
            .replace('{{featured}}', render_featured(config['featured'], repos, config.get('descriptions', {}), images))
            .replace('{{publications}}', render_publications(publications, paper_repos))
            .replace('{{updated}}', date.today().isoformat())
            # Browsers cache style.css, so a changed stylesheet needs a new URL to be fetched
            .replace('{{style_version}}', hashlib.sha1((ROOT / 'style.css').read_bytes()).hexdigest()[:8]))

    shutil.copytree(ROOT / 'static', SITE / 'static')
    for name in ('CNAME', 'style.css'):
        if (ROOT / name).exists():
            shutil.copy(ROOT / name, SITE / name)
    (SITE / 'index.html').write_text(page, encoding='utf-8')


if __name__ == '__main__':
    build()
