(() => {
  'use strict';
  const $ = (s) => document.querySelector(s);
  const root = document.documentElement;
  const store = { get(k) { try { return localStorage.getItem(k); } catch { return null; } }, set(k,v) { try { localStorage.setItem(k,v); } catch {} } };
  const savedSize = Number(store.get('sakubi-reader-size'));
  if ([16,24,40].includes(savedSize)) root.style.setProperty('--reader-size', savedSize + 'px');
  document.querySelectorAll('[data-reader-size]').forEach(link => link.addEventListener('click', e => { e.preventDefault(); const size = Number(link.dataset.readerSize); root.style.setProperty('--reader-size',size + 'px'); store.set('sakubi-reader-size',String(size)); }));
  const mobile = () => window.matchMedia('(max-width:1079px)').matches;
  const sidebarButton = $('#sidebar-toggle');
  function updateSidebar() { sidebarButton.setAttribute('aria-expanded', String(mobile() ? root.classList.contains('mobile-open') : !root.classList.contains('sidebar-hidden'))); if (mobile() && !root.classList.contains('mobile-open')) $('#sidebar').setAttribute('inert',''); else $('#sidebar').removeAttribute('inert'); }
  sidebarButton.addEventListener('click', () => { if (mobile()) root.classList.toggle('mobile-open'); else { root.classList.toggle('sidebar-hidden'); store.set('sakubi-sidebar',root.classList.contains('sidebar-hidden') ? 'hidden' : 'visible'); } updateSidebar(); });
  $('#scrim').addEventListener('click', () => { root.classList.remove('mobile-open'); updateSidebar(); sidebarButton.focus(); });
  window.addEventListener('resize', updateSidebar); updateSidebar();
  document.querySelectorAll('.expand').forEach(button => {
    const group = document.getElementById(button.getAttribute('aria-controls'));
    const key = 'sakubi-group-' + group.id;
    const saved = store.get(key);
    if (saved && !group.querySelector('.active')) { group.hidden = saved !== 'open'; button.setAttribute('aria-expanded',String(!group.hidden)); }
    button.addEventListener('click', () => { group.hidden = !group.hidden; button.setAttribute('aria-expanded',String(!group.hidden)); store.set(key,group.hidden ? 'closed' : 'open'); });
  });
  const scrollbox = $('.sidebar-scrollbox');
  try { const scroll = sessionStorage.getItem('sakubi-sidebar-scroll'); if (scroll !== null) scrollbox.scrollTop = Number(scroll); else document.querySelector('#sidebar .active')?.scrollIntoView({block:'nearest'}); } catch {}
  scrollbox.addEventListener('click', () => { try { sessionStorage.setItem('sakubi-sidebar-scroll', String(scrollbox.scrollTop)); } catch {} });
  const themeMenu = $('#theme-menu'), themeButton = $('#theme-toggle');
  themeButton.addEventListener('click', () => { themeMenu.hidden = !themeMenu.hidden; themeButton.setAttribute('aria-expanded',String(!themeMenu.hidden)); if (!themeMenu.hidden) themeMenu.querySelector('button').focus(); });
  themeMenu.querySelectorAll('button').forEach(button => button.addEventListener('click', () => { root.dataset.theme = button.dataset.theme; store.set('sakubi-theme',button.dataset.theme); themeMenu.hidden = true; themeButton.setAttribute('aria-expanded','false'); themeButton.focus(); }));
  document.addEventListener('click', e => { if (!e.target.closest('.theme-control')) { themeMenu.hidden = true; themeButton.setAttribute('aria-expanded','false'); } });
  $('#print-button').addEventListener('click', () => window.print());
  const searchPanel = $('#search-panel'), searchInput = $('#search-input'), searchButton = $('#search-toggle'), results = $('#search-results'), status = $('#search-status');
  function setSearch(open) { searchPanel.hidden = !open; searchButton.setAttribute('aria-expanded',String(open)); if (open) { searchInput.focus(); searchPanel.scrollIntoView({block:'start'}); } }
  searchButton.addEventListener('click', () => setSearch(searchPanel.hidden));
  function runSearch() {
    const query = searchInput.value.trim().toLocaleLowerCase();
    results.replaceChildren();
    if (!query) { status.textContent = 'Search all lessons, examples, and intermissions.'; return; }
    const terms = query.split(/\s+/).filter(Boolean);
    const matches = (window.SAKUBI_SEARCH || []).map(page => {
      const title = page.title.toLocaleLowerCase(), all = (title + ' ' + page.text).toLocaleLowerCase();
      return {page, score: terms.every(term => all.includes(term)) ? terms.reduce((s,term) => s + (title.includes(term) ? 10 : 1),0) : 0};
    }).filter(x => x.score).sort((a,b) => b.score-a.score);
    status.textContent = matches.length ? `${matches.length} matching chapters` : `No chapters found for “${searchInput.value.trim()}”.`;
    for (const {page} of matches.slice(0,40)) {
      const li = document.createElement('li'), a = document.createElement('a'), snippet = document.createElement('p');
      a.href = page.url; a.textContent = page.title;
      const at = page.text.toLocaleLowerCase().indexOf(terms[0]); const start = Math.max(0,at-65);
      snippet.textContent = (start ? '…' : '') + page.text.slice(start,start+230) + '…'; li.append(a,snippet); results.append(li);
    }
  }
  searchInput.addEventListener('input',runSearch); runSearch();
  document.addEventListener('keydown', e => {
    const typing = /INPUT|TEXTAREA|SELECT/.test(e.target.tagName) || e.target.isContentEditable;
    if (e.key === 'Escape') { setSearch(false); themeMenu.hidden = true; themeButton.setAttribute('aria-expanded','false'); root.classList.remove('mobile-open'); updateSidebar(); sidebarButton.focus(); }
    if (!typing && !e.ctrlKey && !e.metaKey && !e.altKey) {
      if (e.key.toLowerCase() === 's' || e.key === '/') { e.preventDefault(); setSearch(true); }
      if (e.key === 'ArrowRight') $('.page-turn.next')?.click();
      if (e.key === 'ArrowLeft') $('.page-turn.prev')?.click();
    }
  });
  // Preserve original single-page fragment links shared by readers.
  if (/^(index|Introduction)\.html$/.test(location.pathname.split('/').pop() || 'index.html') && location.hash) {
    const hash = location.hash;
    const target = (window.SAKUBI_SEARCH || []).find(page => page.url === hash.slice(1)+'.html');
    if (target) location.replace(target.url + hash);
  }
})();
