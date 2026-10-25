/* chrisjpereira.com visitor stats: no cookies, no personal data. Sends page views, time on page and link clicks to stats.chrisjpereira.com */
(function () {
  try {
    var E = 'https://stats.chrisjpereira.com/hit', q = location.search, ls = window.localStorage;
    if (/[?&]notrack=1/.test(q)) ls.setItem('cjp_nt', '1');
    if (/[?&]notrack=0/.test(q)) ls.removeItem('cjp_nt');
    if (ls.getItem('cjp_nt') || navigator.webdriver) return;
    var id = Math.random().toString(36).slice(2) + Date.now().toString(36), shown = Date.now();
    var send = function (o) { o.id = id; var b = JSON.stringify(o); if (navigator.sendBeacon) navigator.sendBeacon(E, b); else fetch(E, { method: 'POST', body: b, keepalive: true, mode: 'no-cors' }); };
    var p = new URLSearchParams(q);
    send({ t: 'pv', p: location.pathname, h: location.hash.slice(0, 40), r: document.referrer, l: document.documentElement.lang, w: screen.width, us: p.get('utm_source') || '', um: p.get('utm_medium') || '', uc: p.get('utm_campaign') || '' });
    var flush = function () { if (document.visibilityState === 'hidden') send({ t: 'end', d: Date.now() - shown }); else shown = Date.now(); };
    document.addEventListener('visibilitychange', flush);
    var label = function (a) { var li = a.closest('li'), el = li && (li.querySelector('.what') || li.querySelector('.en') || li.querySelector('b')); return ((el && el.innerText) || a.innerText || '').trim().slice(0, 160); };
    document.addEventListener('click', function (e) {
      var a = e.target.closest('a,button'); if (!a) return;
      if (a.classList.contains('sumbtn')) { if (a.getAttribute('aria-expanded') !== 'true') send({ t: 'sum', x: label(a) }); return; }
      if (a.hasAttribute('data-copy')) return send({ t: 'copy', x: a.getAttribute('data-copy') });
      var h = a.getAttribute('href') || '';
      if (a.hasAttribute('download')) return send({ t: 'dl', x: h });
      if (/^mailto:/.test(h)) return send({ t: 'mail', x: h.slice(7) });
      if (/^https?:/.test(h) && a.host !== location.host) send({ t: 'out', u: h, x: label(a) });
    }, true);
  } catch (e) {}
})();
