#!/usr/bin/env python3
"""The Franchises tile may only appear in the home screen's My Media row.

Jellyfin keeps visited pages in the DOM and also renders card rows for search
results, person pages and library views. With a localized home screen the
English "My Media" heading is absent, so the structural fallback must stay
confined to the visible home page. Browser mock only; live Jellyfin still
required.
"""
from pathlib import Path
from playwright.sync_api import sync_playwright

repo = Path(__file__).resolve().parents[1]
js = (repo / 'src/Jellyfin.Plugin.FranchiseExplorer/Web/franchise-my-media.js').read_text(encoding='utf-8')
TILE = '#franchise-explorer-my-media-tile'

STYLE = '''<style>
body{background:#101114;color:white}.hide{display:none}.itemsContainer{display:flex;gap:12px}
.card{width:180px}.poster{height:110px;background:#126078}
</style>'''

HOME = '''<div id="indexPage" class="page homePage libraryPage{hidden}">
<div class="tabContent pageTabContent is-active" id="homeTab" data-index="0"><div class="sections">
<div class="verticalSection section0" id="libraries"><h2 class="sectionTitle">Meine Medien</h2>
<div class="itemsContainer"><div class="card" data-collectiontype="books"><div class="poster"></div><span>Bücher</span></div>
<div class="card" data-collectiontype="boxsets"><div class="poster"></div><span>Sammlungen</span></div>
<div class="card" data-collectiontype="movies"><div class="poster"></div><span>Filme</span></div></div></div>
<div class="verticalSection section1" id="watching"><h2 class="sectionTitle">Weiterschauen</h2>
<div class="itemsContainer"><div class="card">Serie A</div><div class="card">Serie B</div></div></div>
</div></div></div>'''

SEARCH = '''<div id="searchPage" class="page libraryPage{hidden}">
<div class="verticalSection" id="search-movies"><h2 class="sectionTitle">Filme</h2>
<div class="itemsContainer"><div class="card" data-type="Movie"><div class="poster"></div><span>Film A</span></div>
<div class="card" data-type="Movie"><div class="poster"></div><span>Film B</span></div></div></div></div>'''

PERSON = '''<div id="itemDetailPage" class="page itemDetailPage{hidden}">
<section class="verticalSection" id="person-movies"><h2 class="sectionTitle">Filme</h2>
<div class="itemsContainer"><div class="card" data-type="Movie" data-collectiontype="movies"><div class="poster"></div><span>Film C</span></div>
<div class="card" data-type="Movie"><div class="poster"></div><span>Film D</span></div></div></section></div>'''


def page_html(*parts):
    return '<!doctype html><html lang="de"><head><meta charset="utf-8">' + STYLE + '</head><body>' + ''.join(parts) + '</body></html>'


def open_page(browser, html, hash_):
    page = browser.new_page()
    page.route('http://fe.test/**', lambda route: route.fulfill(status=200, content_type='text/html', body=html))
    page.goto('http://fe.test/web/' + hash_)
    page.add_script_tag(content=js)
    page.wait_for_timeout(400)
    return page


with sync_playwright() as p:
    browser = p.chromium.launch(headless=True, executable_path='/usr/bin/chromium' if Path('/usr/bin/chromium').exists() else None, args=['--no-sandbox'])

    # Localized home screen: tile goes into Meine Medien, never into other rows.
    page = open_page(browser, page_html(HOME.format(hidden='')), '#/home')
    page.locator(TILE).wait_for(timeout=5000)
    assert page.locator(TILE).count() == 1
    assert page.locator('#libraries ' + TILE).count() == 1
    assert page.locator('#watching ' + TILE).count() == 0
    page.close()

    # Search results without any home page in the DOM (e.g. direct load).
    page = open_page(browser, page_html(SEARCH.format(hidden='')), '#/search.html?query=star')
    assert page.locator(TILE).count() == 0, 'Tile must not appear in search results'
    page.close()

    # Person page shown while the cached home page is hidden.
    page = open_page(browser, page_html(HOME.format(hidden=' hide'), PERSON.format(hidden='')), '#/details?id=person1')
    assert page.locator('#person-movies ' + TILE).count() == 0, 'Tile must not appear on a person page'
    assert page.locator(TILE).count() == 0
    page.close()

    # Navigating from home to search keeps the tile in the (now hidden) home row
    # only, and a stray tile outside home is removed.
    page = open_page(browser, page_html(HOME.format(hidden=''), SEARCH.format(hidden=' hide')), '#/home')
    page.locator('#libraries ' + TILE).wait_for(timeout=5000)
    page.evaluate('''() => {
      document.getElementById('indexPage').classList.add('hide');
      document.getElementById('searchPage').classList.remove('hide');
      const stray = document.getElementById('franchise-explorer-my-media-tile');
      document.querySelector('#search-movies .itemsContainer').appendChild(stray);
      location.hash = '#/search.html?query=star';
    }''')
    page.wait_for_timeout(400)
    assert page.locator('#search-movies ' + TILE).count() == 0, 'Stray tile in search results must be removed'
    page.evaluate('''() => {
      document.getElementById('searchPage').classList.add('hide');
      document.getElementById('indexPage').classList.remove('hide');
      location.hash = '#/home';
    }''')
    page.locator('#libraries ' + TILE).wait_for(timeout=5000)
    assert page.locator(TILE).count() == 1
    page.close()

    browser.close()

print('Franchises tile is limited to the home My Media row (browser mock; live Jellyfin still required).')
