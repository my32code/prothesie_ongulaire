"""Local browser checks. Requires Python, Playwright and its Chromium browser."""
from pathlib import Path
from html.parser import HTMLParser
from urllib.parse import urlsplit, unquote
from playwright.sync_api import sync_playwright
import tempfile

ROOT = Path(__file__).resolve().parents[1]
PAGES = ['index.html', 'services.html', 'galery.html', 'about.html']

class Document(HTMLParser):
    def __init__(self, source):
        super().__init__()
        self.links = []
        self.ids = set()
        self.feed(source)

    def handle_starttag(self, tag, attributes):
        attrs = dict(attributes)
        if 'id' in attrs:
            assert attrs['id'] not in self.ids, f'Duplicate id: {attrs["id"]}'
            self.ids.add(attrs['id'])
        for key in ['src', 'href']:
            if key in attrs:
                self.links.append(attrs[key])

for filename in PAGES:
    source = (ROOT / filename).read_text(encoding='utf-8')
    doc = Document(source)
    assert source.count('<h1>') == 1, filename
    assert 'lang="fr"' in source and 'name="description"' in source
    assert 'user-scalable=no' not in source
    assert 'jquery' not in source and 'action="#"' not in source
    assert source.count('src="assets/js/site.js"') == 1
    for link in doc.links:
        parsed = urlsplit(link)
        if parsed.scheme or parsed.netloc:
            continue
        assert link != '#', filename
        target = ROOT / unquote(parsed.path) if parsed.path else ROOT / filename
        assert target.exists(), f'{filename}: missing {link}'
        if parsed.fragment:
            ids = Document(target.read_text(encoding='utf-8')).ids
            assert parsed.fragment in ids, f'{filename}: missing anchor {link}'

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page()
    # Network-independent check: the local stylesheet has a system-font fallback.
    page.route('https://**/*', lambda route: route.abort())
    errors = []
    page.on('pageerror', lambda error: errors.append(str(error)))
    for width in [360, 768, 1440]:
        page.set_viewport_size({'width': width, 'height': 950})
        for filename in PAGES:
            page.goto((ROOT / filename).as_uri())
            assert page.locator('nav [aria-current="page"]').count() == 1
            assert page.evaluate('document.documentElement.scrollWidth <= innerWidth'), f'Overflow: {filename} at {width}'
            assert page.locator('main h1').is_visible()
            assert page.locator('a[href^="https://wa.me/"]').count() >= 1
            for img in page.locator('img[src]').all():
                if img.is_visible():
                    img.scroll_into_view_if_needed()
                else:
                    img.evaluate('(img) => { img.loading = "eager"; }')
                img.evaluate('(img) => img.decode()')
                assert img.evaluate('(img) => img.naturalWidth > 0')
    page.goto((ROOT / 'galery.html').as_uri())
    first = page.locator('[data-gallery]').first
    for _ in range(2):
        first.focus()
        page.keyboard.press('Enter')
        assert page.locator('dialog[open]').count() == 1
        assert page.locator('dialog img').get_attribute('src') == first.evaluate('(a) => a.href')
        page.keyboard.press('Escape')
        assert page.locator('dialog[open]').count() == 0
        assert first.evaluate('(a) => a === document.activeElement')
        assert 'photo-open' not in page.locator('body').get_attribute('class')
    first.click()
    page.get_by_role('button', name='Fermer la photo').click()
    assert page.locator('dialog[open]').count() == 0
    page.goto((ROOT / 'index.html').as_uri())
    page.keyboard.press('Tab')
    assert page.get_by_text('Aller au contenu').evaluate('(a) => a === document.activeElement')
    page.evaluate('document.activeElement.blur()')
    page.locator('img').evaluate_all('(images) => Promise.all(images.map(img => { img.loading = "eager"; return img.decode(); }))')
    page.screenshot(path=str(Path(tempfile.gettempdir()) / 'bsy-desktop.png'), full_page=True)
    page.set_viewport_size({'width': 360, 'height': 800})
    page.screenshot(path=str(Path(tempfile.gettempdir()) / 'bsy-mobile.png'), full_page=True)
    assert not errors, errors
    offline = browser.new_context(java_script_enabled=False)
    fallback = offline.new_page()
    fallback.route('https://**/*', lambda route: route.abort())
    fallback.goto((ROOT / 'galery.html').as_uri())
    target = fallback.locator('[data-gallery]').first.get_attribute('href')
    fallback.locator('[data-gallery]').first.click()
    assert fallback.url.endswith(target)
    browser.close()

print('PASS: 4 pages, local links and anchors, 3 viewport sizes, images, keyboard, repeated dialog opening, JS-free gallery.')
print('Screenshots:', Path(tempfile.gettempdir()) / 'bsy-desktop.png', Path(tempfile.gettempdir()) / 'bsy-mobile.png')
