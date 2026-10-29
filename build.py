#!/usr/bin/env python3
"""Rebuild the static guide from its preserved Sakubi source. Requires lxml."""
from pathlib import Path
from copy import deepcopy
from html import escape
import json, re
from urllib.parse import unquote
from lxml import html, etree
ROOT = Path(__file__).resolve().parent
source = html.parse(str(ROOT/'source/sakubi-original.html'))
body = source.getroot().find('body')
def text(node): return ' '.join(node.text_content().split())
def markup(node): return html.tostring(node, encoding='unicode', with_tail=True)
def slug(s): return re.sub(r'[^a-z0-9]+','-',s.lower()).strip('-')
sections = source.xpath('//section')
pages = [{'title': 'Introduction', 'file': 'index.html', 'section': None, 'nodes': [deepcopy(x) for x in list(body)[:5]], 'parent': None}]
section_pages = {}
used = {'index'}
for sec in sections:
    # The first license is duplicated verbatim at the end of the original.
    if sec is sections[0]: continue
    heads = sec.xpath('./h2 | ./h3 | ./h4 | ./h5')
    heading = heads[0] if heads else None
    title = text(heading) if heading is not None else 'Closing Words'
    key = heading.get('id') if heading is not None else None
    key = key or sec.get('id') or slug(title)
    base = key
    count = 2
    while key in used: key = f'{base}-{count}'; count += 1
    used.add(key)
    nodes = [deepcopy(x) for x in sec if isinstance(x.tag,str) and x.tag != 'section']
    page = {'title':title, 'file':key+'.html', 'section':sec, 'nodes':nodes, 'parent':None}
    if heading is None:
        nodes.insert(0,html.fromstring('<h1>Closing Words</h1>'))
    elif nodes:
        nodes[0].tag = 'h1'
        nodes[0].attrib.pop('style',None)
        if sec.get('id'): nodes[0].set('id',sec.get('id'))
    pages.append(page); section_pages[sec] = page
for p in pages:
    if p['section'] is not None:
        ancestor = p['section'].getparent()
        while ancestor is not None:
            if ancestor in section_pages:
                p['parent'] = section_pages[ancestor]['file']; break
            ancestor = ancestor.getparent()
anchors={}
for p in pages:
    for node in p['nodes']:
        for el in node.iter():
            if el.get('id'): anchors[el.get('id')]=p['file']
    if p['section'] is not None and p['section'].get('id'):
        anchors[p['section'].get('id')]=p['file']
assets={"sakubi yesterday's grammar guide.png":'sakubi-logo.png','unihan test.png':'unihan-test.png','sakubi the day it was made.png':'sakubi-original-logo.png'}
for p in pages:
    for node in p['nodes']:
        for el in node.iter():
            if not isinstance(el.tag,str): continue
            el.attrib.pop('onclick',None)
            if el.tag=='a':
                href=el.get('href','')
                if 'Press here to zoom in' in text(el):
                    percent = re.search(r'(100|150|250)%',text(el))
                    if percent: el.set('data-reader-size',str(int(percent.group(1))*16//100))
                if href.startswith('#') and href[1:] in anchors:
                    el.set('href', anchors[href[1:]]+href)
            if el.tag=='img':
                name=unquote(el.get('src',''))
                if name in assets: el.set('src','assets/'+assets[name])
                el.set('alt', 'Sakubi — Yesterday’s Grammar Guide' if 'grammar guide' in name else ('Japanese and Chinese glyph comparison' if 'unihan' in name else 'Original Sakubi logo'))
            if el.tag=='iframe': el.set('loading','lazy');el.set('title','The Biggest Mistake People Make in Language Learning')
    if p['file']=='index.html':
        # Match the reference introduction: logo first, followed by the guide name.
        p['nodes']=[html.fromstring('<h1 class="sr-only">昨日 Sakubi: Yesterday\'s Grammar Guide</h1>'),
                    html.fromstring('<img class="hero-logo" src="assets/sakubi-logo.png" alt="昨日 Sakubi — Yesterday’s Grammar Guide">'),
                    html.fromstring('<p>Welcome to <strong>Sakubi!</strong></p>'),
                    html.fromstring('<p>Yesterday’s Grammar Guide.</p>')]+[x for x in p['nodes'][1:] if not x.xpath('.//img')]
        p['nodes'].append(html.fromstring('<p><a href="what-you-need.html">Before you begin</a>, read what you need and <a href="how-to-use-this-guide-and-learn-japanese.html">how to use this guide</a>. Then start with <a href="intro.html">the introduction to Japanese grammar</a>.</p>'))
    p['content']='\n'.join(markup(n) for n in p['nodes'])
by_file={p['file']:p for p in pages}

def link(p,current):
    return f'<a href="{p["file"]}"'+(' class="active" aria-current="page"' if p['file']==current else '')+'>'+escape(p['title'])+'</a>'
def nav_items(items,current):
    out=[]
    for p in items:
        children=[x for x in pages if x['parent']==p['file']]
        if p['title'].startswith('SECTION '):
            out.append('<li class="part-title">'+link(p,current)+'</li>')
            out.append(nav_items(children,current))
        elif children:
            active = current==p['file'] or any(x['file']==current or any(y['file']==current for y in pages if y['parent']==x['file']) for x in children)
            out.append(f'<li class="group"><div class="group-title">{link(p,current)}<button class="expand" aria-label="Expand {escape(p["title"],quote=True)}" aria-expanded="{str(active).lower()}" aria-controls="group-{p["file"][:-5]}">❱</button></div><ul id="group-{p["file"][:-5]}"'+('' if active else ' hidden')+'>'+nav_items(children,current)+'</ul></li>')
        else:
            out.append('<li'+(' class="intermission"' if 'Intermission' in p['title'] else '')+'>'+link(p,current)+'</li>')
    return '\n'.join(out)
icons={
'menu':'<path d="M4 6h16M4 12h16M4 18h16"/>',
'paint':'<path d="m14 5 5 5M11 14l9-9-2-2-9 9M9 13c-7-1-1 8-7 7 6 3 11-1 7-7Z"/>',
'search':'<circle cx="10" cy="10" r="6"/><path d="m15 15 5 5"/>',
'print':'<path d="M7 8V3h10v5M7 17H3V9h18v8h-4M7 14h10v7H7Z"/>',
'left':'<path d="m15 5-7 7 7 7"/>',
'right':'<path d="m9 5 7 7-7 7"/>'}
def icon(n): return '<svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">'+icons[n]+'</svg>'
search=[]
for i,p in enumerate(pages):
    crumbs=[]; parent=p['parent']
    while parent:
        pp=by_file[parent];crumbs.insert(0,link(pp,''));parent=pp['parent']
    crumb='<nav class="breadcrumbs" aria-label="Breadcrumb">'+'<span> / </span>'.join(crumbs)+'</nav>' if crumbs else ''
    previous=pages[i-1] if i else None
    following=pages[i+1] if i+1<len(pages) else None
    def turn(target,direction):
        return f'<a class="page-turn {direction}" href="{target["file"]}" aria-label="{"Previous" if direction=="prev" else "Next"} chapter" title="{escape(target["title"],quote=True)}">{icon("left" if direction=="prev" else "right")}</a>' if target else ''
    pager='<nav class="page-navigation" aria-label="Page navigation">'+turn(previous,'prev')+turn(following,'next')+'</nav>'
    content=f'''<!doctype html>
<html lang="en" data-theme="navy"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><title>{escape(p['title'])} - Sakubi</title><meta name="description" content="Sakubi: Yesterday's Grammar Guide. A free Japanese grammar primer."><link rel="icon" href="assets/favicon.svg" type="image/svg+xml"><link rel="stylesheet" href="assets/style.css"><script>try{{let t=localStorage.getItem('sakubi-theme');if(['navy','light','rust','coal','ayu'].includes(t))document.documentElement.dataset.theme=t; if(localStorage.getItem('sakubi-sidebar')==='hidden')document.documentElement.classList.add('sidebar-hidden')}}catch(e){{}}</script><script src="assets/search-index.js" defer></script><script src="assets/app.js" defer></script></head>
<body data-page="{p['file']}"><a class="skip-link" href="#content">Skip to content</a>
<aside id="sidebar" aria-label="Table of contents"><nav class="sidebar-scrollbox"><ul class="chapter">{nav_items([x for x in pages if x['parent'] is None],p['file'])}</ul></nav></aside>
<button id="scrim" aria-label="Close table of contents" tabindex="-1"></button>
<div id="page-wrapper"><header class="menu-bar"><div class="tools"><button id="sidebar-toggle" aria-label="Toggle table of contents" aria-controls="sidebar" aria-expanded="true" title="Table of contents">{icon('menu')}</button><div class="theme-control"><button id="theme-toggle" aria-label="Change theme" aria-expanded="false" aria-controls="theme-menu" title="Change theme">{icon('paint')}</button><div id="theme-menu" hidden><button data-theme="light">Light</button><button data-theme="rust">Rust</button><button data-theme="coal">Coal</button><button data-theme="navy">Navy</button><button data-theme="ayu">Ayu</button></div></div><button id="search-toggle" aria-label="Search the guide" aria-expanded="false" aria-controls="search-panel" title="Search (S)">{icon('search')}</button></div><a class="menu-title" href="index.html">Sakubi</a><button id="print-button" aria-label="Print this chapter" title="Print this chapter">{icon('print')}</button></header>
<div class="content"><section id="search-panel" hidden aria-label="Search"><label class="sr-only" for="search-input">Search the guide</label><input id="search-input" type="search" placeholder="Search this book…" autocomplete="off"><p id="search-status" role="status"></p><ol id="search-results"></ol></section><main id="content" tabindex="-1">{crumb}{p['content']}</main>{pager}<footer><a href="license.html">License</a> · <a href="https://sakubi.neocities.org/">Original Sakubi</a> · <a href="https://yoku.bi/Introduction.html">Layout reference: Yokubi</a></footer></div></div></body></html>'''
    (ROOT/p['file']).write_text(content,encoding='utf-8')
    search.append({'title':p['title'],'url':p['file'],'text':' '.join(html.fromstring('<div>'+p['content']+'</div>').text_content().split())})
(ROOT/'Introduction.html').write_text((ROOT/'index.html').read_text(),encoding='utf-8')
(ROOT/'assets/search-index.js').write_text('window.SAKUBI_SEARCH = '+json.dumps(search,ensure_ascii=False)+';',encoding='utf-8')
(ROOT/'source/pages.json').write_text(json.dumps([{'title':p['title'],'file':p['file'],'parent':p['parent']} for p in pages],ensure_ascii=False,indent=2),encoding='utf-8')
print(f'Built {len(pages)} chapters ({sum(p["title"].startswith("Lesson ") for p in pages)} main lessons) plus Introduction.html alias.')
