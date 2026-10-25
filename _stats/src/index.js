/* Visitor statistics for chrisjpereira.com, served at stats.chrisjpereira.com
   - POST /hit  : page views, time on page and clicks sent by /a.js on the website (no cookies; visitors are counted
                  with a daily hash of IP + browser, so nobody is tracked from one day to the next)
   - GET  /     : the statistics page (Chris only: one-time sign-in link by email, 30-day session)
   Tables are created on first use. */

const OWNER = 'chris@impact5r.com';
const COOKIE = 'cjp_stats';
const TZ = 8; // days and hours are counted in Singapore time (UTC+8)
const BOT = /bot|crawl|spider|slurp|headless|lighthouse|preview|facebookexternalhit|curl|python|wget|axios|httpclient|phantom|puppeteer|playwright|scrapy/i;

const SCHEMA = [
  `CREATE TABLE IF NOT EXISTS hits (id TEXT PRIMARY KEY, ts INTEGER NOT NULL, day TEXT NOT NULL, hour INTEGER NOT NULL, vid TEXT NOT NULL,
    path TEXT NOT NULL, hash TEXT NOT NULL DEFAULT '', lang TEXT NOT NULL DEFAULT '', ref TEXT NOT NULL DEFAULT '', ref_host TEXT NOT NULL DEFAULT '',
    source TEXT NOT NULL DEFAULT '', channel TEXT NOT NULL DEFAULT '', utm_campaign TEXT NOT NULL DEFAULT '', country TEXT NOT NULL DEFAULT '',
    city TEXT NOT NULL DEFAULT '', device TEXT NOT NULL DEFAULT '', browser TEXT NOT NULL DEFAULT '', os TEXT NOT NULL DEFAULT '',
    screen INTEGER NOT NULL DEFAULT 0, dur INTEGER NOT NULL DEFAULT 0)`,
  'CREATE INDEX IF NOT EXISTS hits_day ON hits(day)',
  'CREATE INDEX IF NOT EXISTS hits_ts ON hits(ts)',
  `CREATE TABLE IF NOT EXISTS events (rowid INTEGER PRIMARY KEY AUTOINCREMENT, ts INTEGER NOT NULL, day TEXT NOT NULL, vid TEXT NOT NULL,
    pv TEXT NOT NULL DEFAULT '', type TEXT NOT NULL, url TEXT NOT NULL DEFAULT '', label TEXT NOT NULL DEFAULT '')`,
  'CREATE INDEX IF NOT EXISTS events_day ON events(day)',
  'CREATE TABLE IF NOT EXISTS logins (id TEXT PRIMARY KEY, expires INTEGER NOT NULL, used INTEGER NOT NULL DEFAULT 0)',
  'CREATE TABLE IF NOT EXISTS sessions (id TEXT PRIMARY KEY, expires INTEGER NOT NULL)',
  'CREATE TABLE IF NOT EXISTS limits (k TEXT PRIMARY KEY, n INTEGER NOT NULL, until INTEGER NOT NULL)',
  // Google Search Console: one row per day (kept for good, so history grows past Google's 16-month limit) + the latest breakdowns
  'CREATE TABLE IF NOT EXISTS gsc_day (day TEXT PRIMARY KEY, clicks INTEGER NOT NULL, imp INTEGER NOT NULL, pos REAL NOT NULL)',
  'CREATE TABLE IF NOT EXISTS gsc_feed (k TEXT PRIMARY KEY, at INTEGER NOT NULL, json TEXT NOT NULL)',
];
let ready = false;
async function init(env) { if (ready) return; await env.DB.batch(SCHEMA.map((s) => env.DB.prepare(s))); ready = true; }

const enc = new TextEncoder();
async function sha(s) { const b = await crypto.subtle.digest('SHA-256', enc.encode(s)); return [...new Uint8Array(b)].map((x) => x.toString(16).padStart(2, '0')).join(''); }
const tok = () => { const a = new Uint8Array(24); crypto.getRandomValues(a); return btoa(String.fromCharCode(...a)).replace(/\+/g, '-').replace(/\//g, '_').replace(/=+$/, ''); };
const esc = (s) => String(s ?? '').replace(/[&<>"']/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]));
const local = (ms) => new Date(ms + TZ * 36e5);
const dayOf = (ms) => local(ms).toISOString().slice(0, 10);
const html = (body, status = 200, extra = {}) => new Response(body, { status, headers: { 'content-type': 'text/html; charset=utf-8', 'cache-control': 'no-store', 'x-frame-options': 'DENY', 'referrer-policy': 'no-referrer', ...extra } });
const cors = { 'access-control-allow-origin': '*' };

/* ---------- visitor details ---------- */
function device(ua) {
  if (/iPad|Tablet|PlayBook|Silk|(Android(?!.*Mobile))/i.test(ua)) return 'Tablet';
  if (/Mobi|iPhone|iPod|Android|HarmonyOS/i.test(ua)) return 'Mobile';
  return 'Desktop';
}
function browser(ua) {
  if (/MicroMessenger/i.test(ua)) return 'WeChat';
  if (/LinkedInApp/i.test(ua)) return 'LinkedIn app';
  if (/Edg\//.test(ua)) return 'Edge';
  if (/OPR\/|Opera/.test(ua)) return 'Opera';
  if (/SamsungBrowser/.test(ua)) return 'Samsung Internet';
  if (/Firefox\/|FxiOS/.test(ua)) return 'Firefox';
  if (/QQBrowser|UCBrowser|Quark|baiduboxapp/i.test(ua)) return 'Chinese mobile browser';
  if (/Chrome\/|CriOS/.test(ua)) return 'Chrome';
  if (/Safari\//.test(ua)) return 'Safari';
  return 'Other';
}
function os(ua) {
  if (/HarmonyOS|OpenHarmony/i.test(ua)) return 'HarmonyOS';
  if (/iPhone|iPad|iPod/.test(ua)) return 'iOS';
  if (/Android/.test(ua)) return 'Android';
  if (/Windows/.test(ua)) return 'Windows';
  if (/Mac OS X|Macintosh/.test(ua)) return 'macOS';
  if (/CrOS/.test(ua)) return 'ChromeOS';
  if (/Linux/.test(ua)) return 'Linux';
  return 'Other';
}
const SOURCES = [
  ['AI assistant', /(^|\.)(chatgpt\.com|chat\.openai\.com|openai\.com|perplexity\.ai|claude\.ai|gemini\.google\.com|bard\.google\.com|copilot\.microsoft\.com|deepseek\.com|kimi\.(ai|com|moonshot\.cn)|doubao\.com|you\.com|phind\.com|poe\.com|yuanbao\.tencent\.com|tongyi\.aliyun\.com|qianwen\.com|grok\.com|meta\.ai|mistral\.ai)$/],
  ['Search', /(^|\.)(google\.[a-z.]+|bing\.com|baidu\.com|duckduckgo\.com|yandex\.[a-z]+|sogou\.com|so\.com|search\.yahoo\.com|yahoo\.com|ecosia\.org|naver\.com|brave\.com|startpage\.com|qwant\.com|sm\.cn)$/],
  ['Social', /(^|\.)(linkedin\.com|lnkd\.in|x\.com|t\.co|twitter\.com|facebook\.com|fb\.com|m\.facebook\.com|l\.facebook\.com|instagram\.com|weibo\.com|weibo\.cn|weixin\.qq\.com|mp\.weixin\.qq\.com|zhihu\.com|xiaohongshu\.com|xhslink\.com|youtube\.com|youtu\.be|reddit\.com|threads\.net|bsky\.app|douyin\.com|bilibili\.com|substack\.com|medium\.com|telegram\.org|t\.me|whatsapp\.com)$/],
  ['Email', /(^|\.)(mail\.google\.com|outlook\.live\.com|outlook\.office\.com|outlook\.office365\.com|mail\.yahoo\.com|mail\.qq\.com|exmail\.qq\.com|larksuite\.com|feishu\.cn)$/],
];
function classify(host, utm) {
  if (utm) { const u = utm.toLowerCase(); for (const [k, re] of SOURCES) if (re.test(u) || re.test(u + '.com')) return k; if (/newsletter|email|mail/.test(u)) return 'Email'; return 'Campaign'; }
  if (!host) return 'Direct';
  for (const [k, re] of SOURCES) if (re.test(host)) return k;
  return 'Other websites';
}
const pretty = (host) => host.replace(/^www\./, '').replace(/^m\./, '').replace(/^l\.facebook\.com$/, 'facebook.com').replace(/^lnkd\.in$/, 'linkedin.com').replace(/^t\.co$/, 'x.com (t.co)');

/* ---------- collecting ---------- */
async function overLimit(env, k, max, secs) {
  const t = Math.floor(Date.now() / 1000);
  const r = await env.DB.prepare('SELECT n, until FROM limits WHERE k = ?1').bind(k).first();
  if (!r || r.until < t) { await env.DB.prepare('INSERT OR REPLACE INTO limits (k, n, until) VALUES (?1, 1, ?2)').bind(k, t + secs).run(); return false; }
  if (r.n >= max) return true;
  await env.DB.prepare('UPDATE limits SET n = n + 1 WHERE k = ?1').bind(k).run();
  return false;
}

async function hit(env, req) {
  const ua = req.headers.get('user-agent') || '';
  const ok = new Response(null, { status: 204, headers: cors });
  if (!ua || BOT.test(ua)) return ok;
  const origin = req.headers.get('origin') || '';
  if (origin && !/^https:\/\/(www\.)?chrisjpereira\.com$/.test(origin)) return ok;
  let b; try { b = JSON.parse(await req.text()); } catch { return ok; }
  const id = String(b.id || '').slice(0, 40); if (!/^[a-z0-9]{8,40}$/.test(id)) return ok;
  const ip = req.headers.get('cf-connecting-ip') || '';
  const now = Date.now(), day = dayOf(now);
  if (await overLimit(env, 'ip:' + (await sha(ip)).slice(0, 16), 600, 3600)) return ok; // a single address flooding the counter
  const vid = (await sha(`${day}|${ip}|${ua}|${env.SALT || 'cjp'}`)).slice(0, 20);
  const cf = req.cf || {};
  if (b.t === 'pv') {
    const path = String(b.p || '/').slice(0, 200).replace(/\/index\.html$/, '/');
    let ref = String(b.r || '').slice(0, 500), rh = '';
    try { const u = new URL(ref); rh = u.hostname.toLowerCase(); if (/(^|\.)chrisjpereira\.com$/.test(rh)) { rh = ''; ref = ''; } } catch { ref = ''; }
    const utm = String(b.us || '').slice(0, 60);
    const channel = classify(rh, utm);
    const source = utm ? utm.toLowerCase() : rh ? pretty(rh) : 'Direct';
    await env.DB.prepare(`INSERT OR IGNORE INTO hits (id, ts, day, hour, vid, path, hash, lang, ref, ref_host, source, channel, utm_campaign, country, city, device, browser, os, screen)
      VALUES (?1,?2,?3,?4,?5,?6,?7,?8,?9,?10,?11,?12,?13,?14,?15,?16,?17,?18,?19)`)
      .bind(id, now, day, local(now).getUTCHours(), vid, path, String(b.h || '').slice(0, 40), String(b.l || '').slice(0, 10), ref, rh, source, channel,
        String(b.uc || '').slice(0, 80), String(cf.country || ''), String(cf.city || ''), device(ua), browser(ua), os(ua), Math.max(0, Math.min(10000, +b.w || 0))).run();
  } else if (b.t === 'end') {
    const d = Math.max(0, Math.min(+b.d || 0, 30 * 6e4)); // cap a forgotten open tab at 30 minutes
    if (d) await env.DB.prepare('UPDATE hits SET dur = dur + ?1 WHERE id = ?2').bind(Math.round(d / 1000), id).run();
  } else if (['out', 'sum', 'copy', 'dl', 'mail'].includes(b.t)) {
    await env.DB.prepare('INSERT INTO events (ts, day, vid, pv, type, url, label) VALUES (?1,?2,?3,?4,?5,?6,?7)')
      .bind(now, day, vid, id, b.t, String(b.u || '').slice(0, 500), String(b.x || '').slice(0, 200)).run();
  }
  return ok;
}

/* ---------- sign-in (Chris only) ---------- */
const cookieOf = (req) => { const m = new RegExp(`(?:^|;\\s*)${COOKIE}=([A-Za-z0-9_-]+)`).exec(req.headers.get('cookie') || ''); return m ? m[1] : ''; };
async function signedIn(env, req) {
  const raw = cookieOf(req); if (!raw) return false;
  const r = await env.DB.prepare('SELECT expires FROM sessions WHERE id = ?1').bind(await sha(raw)).first();
  return !!r && r.expires > Date.now();
}
const page = (title, body, head = '') => `<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="robots" content="noindex,nofollow">
<title>${esc(title)}</title><link rel="icon" href="https://chrisjpereira.com/favicon-48.png">
<link rel="preconnect" href="https://fonts.googleapis.com"><link href="https://fonts.googleapis.com/css2?family=Playfair+Display:wght@500;600&family=Inter:wght@400;500;600&display=swap" rel="stylesheet">
<style>${CSS}</style>${head}</head><body>${body}</body></html>`;

function loginPage(msg = '') {
  return page('Sign in · Site stats', `<main class="login"><p class="brand"><b>彭家荣</b> Chris Pereira</p><h1>Site stats</h1>
<p class="muted">Enter your email and we'll send you a one-time sign-in link.</p>
<form method="post" action="/login"><input type="email" name="email" required placeholder="you@example.com" autocomplete="email"><button>Send link</button></form>
${msg ? `<p class="note">${msg}</p>` : ''}</main>`);
}

async function sendLink(env, req) {
  const f = await req.formData(); const email = String(f.get('email') || '').trim().toLowerCase();
  const ip = req.headers.get('cf-connecting-ip') || '';
  const done = loginPage('If that address can open the stats page, a sign-in link is on its way. It works once and expires in 15 minutes.');
  if (await overLimit(env, 'login:' + ip, 5, 3600) || await overLimit(env, 'login-all', 20, 3600)) return html(loginPage('Too many requests. Please try again later.'), 429);
  if (email !== (env.OWNER_EMAIL || OWNER)) return html(done);
  const t = tok();
  await env.DB.prepare('INSERT INTO logins (id, expires) VALUES (?1, ?2)').bind(await sha(t), Date.now() + 15 * 6e4).run();
  const link = `${new URL(req.url).origin}/auth?t=${t}`;
  try {
    await env.EMAIL.send({
      to: email, from: { email: env.MAIL_FROM || 'website@forms.impact5r.com', name: 'chrisjpereira.com stats' },
      subject: 'Sign in to your site stats',
      text: `Hi Chris, this is a system-generated message from your chrisjpereira.com stats page.\n\nClick to sign in (valid for 15 minutes, one use only):\n\n${link}\n\nIf you didn't ask for this, ignore this email.`,
      html: `<div style="font:15px/1.6 Arial,sans-serif;color:#161616;max-width:520px"><p>Hi Chris, this is a system-generated message from your <b>chrisjpereira.com</b> stats page.</p>
<p>Use the button below to sign in. The link works once and expires in 15 minutes.</p>
<p style="margin:24px 0"><a href="${esc(link)}" style="background:#B3262B;color:#fff;text-decoration:none;padding:12px 22px;font-weight:bold;display:inline-block">Open site stats</a></p>
<p style="font-size:12px;color:#8C8C8C">If you didn't ask for this, you can ignore this email.</p></div>`,
    });
  } catch (e) { console.log('mail failed', e && (e.code || e.message)); return html(loginPage('The email could not be sent. Please try again later.'), 502); }
  return html(done);
}

async function redeem(env, req) {
  const t = new URL(req.url).searchParams.get('t') || '';
  const id = await sha(t);
  const r = await env.DB.prepare('SELECT expires, used FROM logins WHERE id = ?1').bind(id).first();
  if (!r || r.used || r.expires < Date.now()) return html(loginPage('That link has expired or was already used. Please request a new one.'), 403);
  const s = tok();
  await env.DB.batch([
    env.DB.prepare('UPDATE logins SET used = 1 WHERE id = ?1').bind(id),
    env.DB.prepare('INSERT INTO sessions (id, expires) VALUES (?1, ?2)').bind(await sha(s), Date.now() + 30 * 864e5),
    env.DB.prepare('DELETE FROM logins WHERE expires < ?1').bind(Date.now()),
    env.DB.prepare('DELETE FROM sessions WHERE expires < ?1').bind(Date.now()),
  ]);
  return new Response(null, { status: 302, headers: { location: '/', 'set-cookie': `${COOKIE}=${s}; Path=/; Max-Age=${30 * 86400}; HttpOnly; Secure; SameSite=Lax` } });
}

/* ---------- Google Search Console (via Chris's Apps Script web app, URL in secret GSC_URL) ---------- */
async function gscRefresh(env) {
  if (!env.GSC_URL) return;
  const r = await fetch(env.GSC_URL, { redirect: 'follow', signal: AbortSignal.timeout(25000) });
  const j = await r.json();
  if (!j || !Array.isArray(j.date)) throw new Error('GSC feed: unexpected response');
  const st = j.date.map((x) => env.DB.prepare('INSERT INTO gsc_day (day, clicks, imp, pos) VALUES (?1, ?2, ?3, ?4) ON CONFLICT(day) DO UPDATE SET clicks = ?2, imp = ?3, pos = ?4')
    .bind(x.keys[0], x.clicks, x.impressions, x.position));
  st.push(env.DB.prepare("INSERT INTO gsc_feed (k, at, json) VALUES ('feed', ?1, ?2) ON CONFLICT(k) DO UPDATE SET at = ?1, json = ?2")
    .bind(Date.now(), JSON.stringify({ from: j.from, to: j.to, query: j.query, page: j.page, country: j.country, device: j.device })));
  for (let i = 0; i < st.length; i += 50) await env.DB.batch(st.slice(i, i + 50));
}
async function gscGet(env, ctx) {
  const row = await env.DB.prepare("SELECT at, json FROM gsc_feed WHERE k = 'feed'").first();
  if (env.GSC_URL && (!row || Date.now() - row.at > 6 * 36e5)) {
    const job = gscRefresh(env).catch((e) => console.log('gsc', e && e.message));
    if (!row) { await job; return gscGet(env, null); }
    if (ctx) ctx.waitUntil(job);
  }
  return row ? { at: row.at, ...JSON.parse(row.json) } : null;
}
const ISO3 = { SGP: 'SG', CHN: 'CN', HKG: 'HK', USA: 'US', GBR: 'GB', CAN: 'CA', AUS: 'AU', IND: 'IN', MYS: 'MY', TWN: 'TW', JPN: 'JP', KOR: 'KR', DEU: 'DE', FRA: 'FR', NLD: 'NL', IDN: 'ID', THA: 'TH', VNM: 'VN', PHL: 'PH', ARE: 'AE', SAU: 'SA', CHE: 'CH', ITA: 'IT', ESP: 'ES', BRA: 'BR', MEX: 'MX', NZL: 'NZ', IRL: 'IE', SWE: 'SE', RUS: 'RU', ZAF: 'ZA', NGA: 'NG', KEN: 'KE', EGY: 'EG', TUR: 'TR', PAK: 'PK', BGD: 'BD', MAC: 'MO', BEL: 'BE', POL: 'PL', ISR: 'IL', QAT: 'QA', NOR: 'NO', DNK: 'DK', FIN: 'FI', AUT: 'AT', PRT: 'PT', GRC: 'GR', ARG: 'AR', CHL: 'CL', COL: 'CO', PER: 'PE', KAZ: 'KZ', UZB: 'UZ', LKA: 'LK', KHM: 'KH', MMR: 'MM', LAO: 'LA', NPL: 'NP' };

async function gscSection(env, ctx, from, today, prevFrom, prevTo, isAll) {
  if (!env.GSC_URL) return '';
  let f; try { f = await gscGet(env, ctx); } catch (e) { console.log('gsc', e && e.message); }
  const [cur, prv, daily] = await env.DB.batch([
    env.DB.prepare('SELECT SUM(clicks) c, SUM(imp) i, SUM(pos * imp) / NULLIF(SUM(imp), 0) p, MIN(day) f FROM gsc_day WHERE day >= ?1 AND day <= ?2').bind(isAll ? '0000' : from, today),
    env.DB.prepare('SELECT SUM(clicks) c, SUM(imp) i FROM gsc_day WHERE day >= ?1 AND day <= ?2').bind(prevFrom, prevTo),
    env.DB.prepare('SELECT day, clicks, imp FROM gsc_day WHERE day >= ?1 AND day <= ?2 ORDER BY day').bind(isAll ? '0000' : from, today),
  ]);
  const C = cur.results[0] || {}, P = prv.results[0] || {};
  const delta = (a, b) => (isAll || !b ? '' : `<span class="delta ${a >= b ? 'up' : 'down'}">${a >= b ? '▲' : '▼'} ${Math.abs(Math.round(((a - b) / b) * 100))}%</span>`);
  const rows = daily.results, byDay = Object.fromEntries(rows.map((r) => [r.day, r]));
  const start = isAll ? (rows[0]?.day || today) : from;
  const days = []; for (let t = Date.parse(start + 'T00:00:00Z'); t <= Date.parse(today + 'T00:00:00Z'); t += 864e5) days.push(new Date(t).toISOString().slice(0, 10));
  const max = Math.max(1, ...days.map((d) => byDay[d]?.imp || 0)), Wd = 900, H = 150, bw = Wd / Math.max(1, days.length);
  const bars = days.map((d, i) => { const r = byDay[d] || { clicks: 0, imp: 0 }; const h = (r.imp / max) * (H - 15); const hc = (r.clicks / max) * (H - 15);
    return `<rect class="imp" x="${(i * bw + bw * 0.15).toFixed(1)}" y="${(H - h).toFixed(1)}" width="${(bw * 0.7).toFixed(1)}" height="${h.toFixed(1)}"><title>${d}: ${r.imp} times shown, ${r.clicks} clicks</title></rect>${r.clicks ? `<rect x="${(i * bw + bw * 0.15).toFixed(1)}" y="${(H - Math.max(2, hc)).toFixed(1)}" width="${(bw * 0.7).toFixed(1)}" height="${Math.max(2, hc).toFixed(1)}"><title>${d}: ${r.clicks} clicks</title></rect>` : ''}`; }).join('');
  const ticks = days.length > 1 ? [0, Math.floor((days.length - 1) / 2), days.length - 1].map((i) => `<text x="${(i * bw + bw / 2).toFixed(1)}" y="${H + 16}" text-anchor="${i === 0 ? 'start' : i === days.length - 1 ? 'end' : 'middle'}">${days[i].slice(rk_year(days) ? 0 : 5)}</text>`).join('') : '';
  const chart = `<svg viewBox="0 0 ${Wd} ${H + 22}" class="chart gsc" role="img" aria-label="Google Search per day">${bars}${ticks}</svg>`;
  const ctr = C.i ? ((C.c / C.i) * 100).toFixed(1) + '%' : '–';
  const pct = (x) => (x * 100).toFixed(1) + '%';
  const tbl = (title, head, list, map, note) => table(title, head, (list || []).map(map), { numCols: [1, 2, 3], note });
  const rowsOf = (k) => (f && f[k]) || [];
  const short = (u) => { try { const x = new URL(u); return pageName(x.pathname) + (x.hash ? ' ' + x.hash : ''); } catch { return u; } };
  const per = f ? `${f.from} to ${f.to}` : '';
  return `<h2 class="sect">Google Search</h2>
<p class="note sect-note">From Google Search Console: how often the site showed up in Google results and how often people clicked. Includes the months before the stats page existed. Google's figures arrive 2–3 days late and use US Pacific dates.${f ? ` Last updated ${T(local(f.at).toISOString().slice(0, 16).replace('T', ' '), f.at)}.` : ''}</p>
<div class="kpis k4">
  <div><b>${n(C.c)}</b><span>Clicks from Google ${delta(C.c || 0, P.c || 0)}</span></div>
  <div><b>${n(C.i)}</b><span>Times shown in Google ${delta(C.i || 0, P.i || 0)}</span></div>
  <div><b>${ctr}</b><span>Click rate</span></div>
  <div><b>${C.p ? C.p.toFixed(1) : '–'}</b><span>Average position in results</span></div>
</div>
<section class="card wide"><h2>Google Search per day</h2><p class="note">Light bars: times shown in Google. Dark bars: clicks.${C.f && !isAll && C.f > from ? ` Google data starts ${C.f}.` : ''}</p>${chart}</section>
<div class="grid">
${tbl('Search terms', ['Search term', 'Clicks', 'Position', 'Shown'], rowsOf('query'), (r) => [esc(r.keys[0]), r.clicks, `<span data-v="${r.position}">${r.position.toFixed(1)}</span>`, r.impressions], `What people typed into Google before seeing the site, ${per}. Google hides rare searches for privacy.`)}
${tbl('Pages in Google', ['Page', 'Clicks', 'Position', 'Shown'], rowsOf('page'), (r) => [`<a href="${esc(r.keys[0])}" target="_blank" rel="noopener">${esc(short(r.keys[0]))}</a>`, r.clicks, `<span data-v="${r.position}">${r.position.toFixed(1)}</span>`, r.impressions], per)}
${tbl('Searchers by country', ['Country', 'Clicks', 'Click rate', 'Shown'], rowsOf('country'), (r) => [country(ISO3[String(r.keys[0]).toUpperCase()] || String(r.keys[0]).toUpperCase()), r.clicks, `<span data-v="${r.ctr}">${pct(r.ctr)}</span>`, r.impressions], per)}
${tbl('Searchers by device', ['Device', 'Clicks', 'Click rate', 'Shown'], rowsOf('device'), (r) => [esc(r.keys[0][0] + r.keys[0].slice(1).toLowerCase()), r.clicks, `<span data-v="${r.ctr}">${pct(r.ctr)}</span>`, r.impressions], per)}
</div>`;
}
const rk_year = (days) => days.length > 400;
const T = (s, d) => `<time datetime="${new Date(d).toISOString()}">${s}</time>`;

/* ---------- the statistics page ---------- */
const RANGES = [['today', 'Today', 0], ['7d', '7 days', 6], ['30d', '30 days', 29], ['90d', '90 days', 89], ['all', 'All time', 3650]];
const FLAG = (cc) => (/^[A-Z]{2}$/.test(cc) ? String.fromCodePoint(...[...cc].map((c) => 127397 + c.charCodeAt(0))) : '');
let regionNames; try { regionNames = new Intl.DisplayNames(['en'], { type: 'region' }); } catch { regionNames = null; }
const country = (cc) => (cc ? `${FLAG(cc)} ${esc((regionNames && regionNames.of(cc)) || cc)}` : 'Unknown');
const PAGES = { '/': 'Home (English)', '/zh/': 'Home (中文)', '/quotes/': 'Quotes' };
const pageName = (p) => PAGES[p] || p;
const fmtDur = (s) => { s = Math.round(s || 0); if (s < 60) return `${s}s`; const m = Math.floor(s / 60); return m < 60 ? `${m}m ${String(s % 60).padStart(2, '0')}s` : `${Math.floor(m / 60)}h ${m % 60}m`; };
const n = (x) => Number(x || 0).toLocaleString('en-US');

function table(title, head, rows, opts = {}) {
  const total = opts.total || rows.reduce((a, r) => a + Number(r[r.length - 1] || 0), 0) || 1;
  const body = rows.length ? rows.map((r) => {
    const v = Number(r[r.length - 1] || 0);
    return `<tr>${r.map((c, i) => i === r.length - 1 ? `<td class="num" data-v="${v}"><span class="bar" style="width:${Math.max(2, Math.round((v / total) * 100))}%"></span>${n(v)}</td>`
      : `<td${typeof c === 'number' ? ` class="num" data-v="${c}"` : opts.numCols?.includes(i) ? ' class="num"' : ''}>${c}</td>`).join('')}</tr>`;
  }).join('') : `<tr><td colspan="${head.length}" class="muted">No data yet</td></tr>`;
  return `<section class="card${opts.wide ? ' wide' : ''}"><h2>${title}</h2>${opts.note ? `<p class="note">${opts.note}</p>` : ''}<div class="tw"><table class="sort"><thead><tr>${head.map((h, i) => `<th${i === head.length - 1 || opts.numCols?.includes(i) ? ' class="num"' : ''}>${h}</th>`).join('')}</tr></thead><tbody>${body}</tbody></table></div></section>`;
}

async function stats(env, req, ctx) {
  const url = new URL(req.url);
  const rk = RANGES.find((r) => r[0] === url.searchParams.get('r')) || RANGES[2];
  const now = Date.now(), today = dayOf(now), from = dayOf(now - rk[2] * 864e5);
  const prevFrom = dayOf(now - (2 * rk[2] + 1) * 864e5), prevTo = dayOf(now - (rk[2] + 1) * 864e5);
  const D = env.DB, W = 'day >= ?1 AND day <= ?2';
  const q = (sql, ...a) => D.prepare(sql).bind(from, today, ...a);
  const [kpi, prev, daily, pages, channels, sources, countries, cities, devices, browsers, oss, langs, hours, outs, sums, other, recent, live, first, screens, campaigns] = await D.batch([
    q(`SELECT COUNT(*) pv, COUNT(DISTINCT vid) v, AVG(CASE WHEN dur > 0 THEN dur END) avgd, COUNT(DISTINCT country) c FROM hits WHERE ${W}`),
    D.prepare(`SELECT COUNT(*) pv, COUNT(DISTINCT vid) v FROM hits WHERE ${W}`).bind(prevFrom, prevTo),
    q(`SELECT day, COUNT(DISTINCT vid) v, COUNT(*) pv FROM hits WHERE ${W} GROUP BY day ORDER BY day`),
    q(`SELECT path, COUNT(DISTINCT vid) v, AVG(CASE WHEN dur > 0 THEN dur END) d, COUNT(*) pv FROM hits WHERE ${W} GROUP BY path ORDER BY pv DESC LIMIT 25`),
    q(`SELECT channel, COUNT(DISTINCT vid) v FROM hits WHERE ${W} GROUP BY channel ORDER BY v DESC`),
    q(`SELECT source, channel, COUNT(DISTINCT vid) v FROM hits WHERE ${W} AND source != 'Direct' GROUP BY source ORDER BY v DESC LIMIT 25`),
    q(`SELECT country, COUNT(DISTINCT vid) v FROM hits WHERE ${W} GROUP BY country ORDER BY v DESC LIMIT 30`),
    q(`SELECT city, country, COUNT(DISTINCT vid) v FROM hits WHERE ${W} AND city != '' GROUP BY city, country ORDER BY v DESC LIMIT 30`),
    q(`SELECT device, COUNT(DISTINCT vid) v FROM hits WHERE ${W} GROUP BY device ORDER BY v DESC`),
    q(`SELECT browser, COUNT(DISTINCT vid) v FROM hits WHERE ${W} GROUP BY browser ORDER BY v DESC`),
    q(`SELECT os, COUNT(DISTINCT vid) v FROM hits WHERE ${W} GROUP BY os ORDER BY v DESC`),
    q(`SELECT CASE WHEN path LIKE '/zh%' THEN '中文 site' ELSE 'English site' END s, COUNT(DISTINCT vid) v FROM hits WHERE ${W} GROUP BY s ORDER BY v DESC`),
    q(`SELECT hour, COUNT(*) pv FROM hits WHERE ${W} GROUP BY hour`),
    q(`SELECT label, url, COUNT(*) c FROM events WHERE ${W} AND type = 'out' GROUP BY url ORDER BY c DESC LIMIT 30`),
    q(`SELECT label, COUNT(*) c FROM events WHERE ${W} AND type = 'sum' GROUP BY label ORDER BY c DESC LIMIT 20`),
    q(`SELECT type, label, COUNT(*) c FROM events WHERE ${W} AND type IN ('copy','dl','mail') GROUP BY type, label ORDER BY c DESC LIMIT 20`),
    D.prepare('SELECT ts, path, source, channel, country, city, device, browser, dur FROM hits ORDER BY ts DESC LIMIT 40'),
    D.prepare('SELECT COUNT(DISTINCT vid) v FROM hits WHERE ts > ?1').bind(now - 5 * 6e4),
    D.prepare('SELECT MIN(day) d FROM hits'),
    q(`SELECT CASE WHEN screen < 600 THEN 'Phone (under 600px)' WHEN screen < 1024 THEN 'Tablet / small laptop' WHEN screen < 1600 THEN 'Laptop' ELSE 'Large screen' END s, COUNT(DISTINCT vid) v FROM hits WHERE ${W} AND screen > 0 GROUP BY s ORDER BY v DESC`),
    q(`SELECT utm_campaign, source, COUNT(DISTINCT vid) v FROM hits WHERE ${W} AND utm_campaign != '' GROUP BY utm_campaign, source ORDER BY v DESC LIMIT 20`),
  ]);
  const K = kpi.results[0] || {}, P = prev.results[0] || {};
  const visitsPerDay = daily.results;
  const outTotal = outs.results.reduce((a, r) => a + r.c, 0);
  const delta = (a, b) => (rk[0] === 'all' || !b ? '' : `<span class="delta ${a >= b ? 'up' : 'down'}">${a >= b ? '▲' : '▼'} ${Math.abs(Math.round(((a - b) / b) * 100))}%</span>`);

  // daily chart (inline SVG): bars = visitors, line = page views
  const days = []; for (let t = Date.parse(from + 'T00:00:00Z'); t <= Date.parse(today + 'T00:00:00Z'); t += 864e5) days.push(new Date(t).toISOString().slice(0, 10));
  const byDay = Object.fromEntries(visitsPerDay.map((r) => [r.day, r]));
  const shown = rk[0] === 'all' ? days.filter((d) => d >= (first.results[0]?.d || today)) : days;
  const max = Math.max(1, ...shown.map((d) => byDay[d]?.pv || 0));
  const Wd = 900, H = 180, bw = Wd / Math.max(1, shown.length);
  const bars = shown.map((d, i) => { const r = byDay[d] || { v: 0, pv: 0 }; const h = (r.v / max) * (H - 20); return `<rect x="${(i * bw + bw * 0.15).toFixed(1)}" y="${(H - h).toFixed(1)}" width="${(bw * 0.7).toFixed(1)}" height="${h.toFixed(1)}" rx="2"><title>${d}: ${r.v} visitors, ${r.pv} page views</title></rect>`; }).join('');
  const line = shown.map((d, i) => `${(i * bw + bw / 2).toFixed(1)},${(H - ((byDay[d]?.pv || 0) / max) * (H - 20)).toFixed(1)}`).join(' ');
  const ticks = shown.length > 1 ? [0, Math.floor((shown.length - 1) / 2), shown.length - 1].map((i) => `<text x="${(i * bw + bw / 2).toFixed(1)}" y="${H + 16}" text-anchor="${i === 0 ? 'start' : i === shown.length - 1 ? 'end' : 'middle'}">${shown[i].slice(5)}</text>`).join('') : '';
  const chart = `<svg viewBox="0 0 ${Wd} ${H + 22}" class="chart" role="img" aria-label="Visitors per day">${bars}<polyline points="${line}" fill="none"/>${ticks}</svg>`;

  // hour of day (Singapore time)
  const hr = Object.fromEntries(hours.results.map((r) => [r.hour, r.pv])); const hmax = Math.max(1, ...Object.values(hr));
  const hourBars = Array.from({ length: 24 }, (_, h) => `<div title="${String(h).padStart(2, '0')}:00, ${hr[h] || 0} page views"><span style="height:${Math.round(((hr[h] || 0) / hmax) * 100)}%"></span><i>${h % 6 === 0 ? h : ''}</i></div>`).join('');

  const tabs = RANGES.map((r) => `<a href="?r=${r[0]}"${r === rk ? ' class="on"' : ''}>${r[1]}</a>`).join('');
  const ai = channels.results.find((r) => r.channel === 'AI assistant');
  const search = await gscSection(env, ctx, from, today, prevFrom, prevTo, rk[0] === 'all');
  const body = `<header class="top"><div class="wrap"><p class="brand"><b>彭家荣</b> Chris Pereira <span>Site stats</span></p><nav>${tabs}</nav></div></header>
<main class="wrap">
<div class="live"><span class="dot"></span>${n(live.results[0]?.v)} on the site right now <span class="muted">· times in Singapore time · <a href="https://chrisjpereira.com/" target="_blank" rel="noopener">chrisjpereira.com ↗</a></span></div>
<div class="kpis">
  <div><b>${n(K.v)}</b><span>Visitors ${delta(K.v || 0, P.v || 0)}</span></div>
  <div><b>${n(K.pv)}</b><span>Page views ${delta(K.pv || 0, P.pv || 0)}</span></div>
  <div><b>${fmtDur(K.avgd)}</b><span>Average time on page</span></div>
  <div><b>${K.v ? (K.pv / K.v).toFixed(1) : '0'}</b><span>Pages per visitor</span></div>
  <div><b>${n(outTotal)}</b><span>Clicks to articles, videos and links</span></div>
  <div><b>${n(K.c)}</b><span>Countries</span></div>
</div>
${ai ? `<p class="flag">🤖 <b>${n(ai.v)}</b> visitor${ai.v === 1 ? '' : 's'} came from AI assistants (ChatGPT, Perplexity, Claude, DeepSeek and others) in this period.</p>` : ''}
<section class="card wide"><h2>Visitors per day</h2><p class="note">Bars: visitors. Line: page views. ${rk[0] === 'all' ? '' : `Compared with the previous ${rk[1].toLowerCase()} in the ▲▼ figures above.`}</p>${chart}</section>
<div class="grid">
${table('Where visitors come from', ['Channel', 'Visitors'], channels.results.map((r) => [esc(r.channel), r.v]))}
${table('Referring sites and campaigns', ['Source', 'Channel', 'Visitors'], sources.results.map((r) => [esc(r.source), esc(r.channel), r.v]))}
${table('Pages', ['Page', 'Visitors', 'Avg. time', 'Views'], pages.results.map((r) => [esc(pageName(r.path)), r.v, `<span data-v="${Math.round(r.d || 0)}">${fmtDur(r.d)}</span>`, r.pv]), { numCols: [1, 2] })}
${table('Countries', ['Country', 'Visitors'], countries.results.map((r) => [country(r.country), r.v]))}
${table('Cities', ['City', 'Visitors'], cities.results.map((r) => [`${FLAG(r.country)} ${esc(r.city)}`, r.v]))}
${table('English or Chinese site', ['Site', 'Visitors'], langs.results.map((r) => [esc(r.s), r.v]))}
${table('Devices', ['Device', 'Visitors'], devices.results.map((r) => [esc(r.device), r.v]))}
${table('Screen sizes', ['Screen', 'Visitors'], screens.results.map((r) => [esc(r.s), r.v]))}
${table('Browsers and apps', ['Browser', 'Visitors'], browsers.results.map((r) => [esc(r.browser), r.v]), { note: 'WeChat and LinkedIn app mean the site was opened inside those apps.' })}
${table('Operating systems', ['System', 'Visitors'], oss.results.map((r) => [esc(r.os), r.v]))}
<section class="card"><h2>Time of day</h2><p class="note">Page views by hour, Singapore time (UTC+8).</p><div class="hours">${hourBars}</div></section>
${campaigns.results.length ? table('Tagged campaigns (utm)', ['Campaign', 'Source', 'Visitors'], campaigns.results.map((r) => [esc(r.utm_campaign), esc(r.source), r.v])) : ''}
${table('Most clicked articles, videos and links', ['Item', 'Goes to', 'Clicks'], outs.results.map((r) => { let h = ''; try { h = new URL(r.url).hostname.replace(/^www\./, ''); } catch {} return [esc(r.label || r.url), `<a href="${esc(r.url)}" target="_blank" rel="noopener">${esc(h)} ↗</a>`, r.c]; }), { wide: true, note: 'Which of your coverage, writing and profile links visitors actually open.' })}
${table('Summaries opened', ['Entry', 'Opens'], sums.results.map((r) => [esc(r.label), r.c]), { wide: true, note: 'Times a visitor clicked "Short summary" on a commentary or writing entry.' })}
${other.results.length ? table('Bios copied, downloads and emails', ['Action', 'Item', 'Count'], other.results.map((r) => [({ copy: 'Copied bio', dl: 'Downloaded', mail: 'Clicked email' })[r.type], esc(r.label), r.c])) : ''}
</div>
${search}
<section class="card wide"><h2>Latest visits</h2><div class="tw"><table class="sort"><thead><tr><th>When</th><th>Page</th><th>From</th><th>Where</th><th>Device</th><th class="num">Time on page</th></tr></thead><tbody>
${recent.results.map((r) => { const d = local(r.ts); return `<tr><td data-v="${r.ts}">${T(d.toISOString().slice(5, 16).replace('T', ' '), r.ts)}</td><td>${esc(pageName(r.path))}</td><td>${esc(r.source === 'Direct' ? 'Direct' : r.source)}</td><td>${FLAG(r.country)} ${esc([r.city, r.country].filter(Boolean).join(', '))}</td><td>${esc(r.device)} · ${esc(r.browser)}</td><td class="num" data-v="${r.dur}">${r.dur ? fmtDur(r.dur) : '–'}</td></tr>`; }).join('') || '<tr><td colspan="6" class="muted">No visits yet</td></tr>'}
</tbody></table></div></section>
<footer class="muted">No cookies are used on the website. Each visitor is counted with a daily anonymous code (IP and browser, hashed with a secret), so people are never followed from one day to the next.
Visits from bots are left out. To stop counting your own visits on a device, open <a href="https://chrisjpereira.com/?notrack=1" target="_blank" rel="noopener">chrisjpereira.com/?notrack=1</a> once on it (<a href="https://chrisjpereira.com/?notrack=0" target="_blank" rel="noopener">undo</a>). · <a href="/logout">Sign out</a></footer>
</main><script>${SORT_JS}</script>`;
  return html(page(`Site stats · ${rk[1]}`, body));
}

const SORT_JS = `document.querySelectorAll('table.sort').forEach(function(t){t.querySelectorAll('th').forEach(function(th,i){th.addEventListener('click',function(){var tb=t.tBodies[0],rows=[].slice.call(tb.rows);if(rows.length<2)return;var dir=th.dataset.dir==='desc'?'asc':'desc';t.querySelectorAll('th').forEach(function(h){delete h.dataset.dir});th.dataset.dir=dir;var val=function(r){var c=r.cells[i];if(!c)return '';var e=c.querySelector('[data-v]');var v=c.dataset.v||(e&&e.dataset.v);return v!==undefined&&v!==null&&v!==''?+v:c.innerText.toLowerCase()};rows.sort(function(a,b){var x=val(a),y=val(b);var r=(typeof x==='number'&&typeof y==='number')?x-y:String(x).localeCompare(String(y));return dir==='asc'?r:-r});rows.forEach(function(r){tb.appendChild(r)})})})});`;

const CSS = `:root{--ink:#161616;--muted:#6b6b6b;--rule:#e6e1d8;--bg:#f7f4ee;--card:#fff;--red:#B3262B}
*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--ink);font:15px/1.5 Inter,system-ui,sans-serif}
a{color:var(--red)}.wrap{max-width:1200px;margin:0 auto;padding:0 20px}.muted{color:var(--muted)}
.top{background:#fff;border-bottom:1px solid var(--rule);position:sticky;top:0;z-index:5}.top .wrap{display:flex;align-items:center;justify-content:space-between;gap:12px;flex-wrap:wrap;min-height:60px}
.brand{margin:0;font-family:"Playfair Display",Georgia,serif;font-size:19px}.brand b{background:var(--red);color:#fff;font:600 14px Inter,sans-serif;padding:3px 7px;border-radius:4px;margin-right:6px;vertical-align:2px}.brand span{color:var(--muted);font:500 13px Inter;letter-spacing:.08em;text-transform:uppercase;margin-left:8px}
nav{display:flex;gap:4px;flex-wrap:wrap}nav a{padding:6px 12px;border-radius:999px;color:var(--ink);text-decoration:none;font-size:14px}nav a.on{background:var(--ink);color:#fff}
.live{margin:22px 0 8px;font-size:14px}.dot{display:inline-block;width:9px;height:9px;border-radius:50%;background:#2e9e5b;margin-right:8px;box-shadow:0 0 0 4px rgba(46,158,91,.18)}
.kpis{display:grid;grid-template-columns:repeat(6,1fr);gap:1px;background:var(--rule);border:1px solid var(--rule);border-radius:10px;overflow:hidden;margin:12px 0 18px}
.kpis div{background:#fff;padding:18px}.kpis b{display:block;font:600 30px/1.1 "Playfair Display",Georgia,serif}.kpis span{display:block;margin-top:6px;font-size:13px;color:var(--muted)}
.delta{font-size:12px;margin-left:4px}.delta.up{color:#2e7d4f}.delta.down{color:var(--red)}
.flag{background:#fff;border-left:3px solid var(--red);padding:10px 14px;border-radius:6px;margin:0 0 18px}
.grid{display:grid;grid-template-columns:1fr 1fr;gap:18px}.card{background:var(--card);border:1px solid var(--rule);border-radius:10px;padding:18px 18px 8px;margin:0 0 18px;min-width:0}.grid .card{margin:0}.card.wide{grid-column:1/-1}
.card h2{margin:0 0 4px;font:600 19px "Playfair Display",Georgia,serif}.note{margin:0 0 10px;font-size:13px;color:var(--muted)}
.tw{max-height:420px;overflow:auto}table{width:100%;border-collapse:collapse;font-size:14px}
th{position:sticky;top:0;background:#fff;text-align:left;font-weight:600;font-size:12px;letter-spacing:.05em;text-transform:uppercase;color:var(--muted);padding:8px 6px;border-bottom:1px solid var(--rule);cursor:pointer;user-select:none;white-space:nowrap}
th[data-dir=asc]::after{content:" ▲"}th[data-dir=desc]::after{content:" ▼"}
td{padding:7px 6px;border-bottom:1px solid #f0ece4;vertical-align:top;overflow-wrap:anywhere}.num{text-align:right;white-space:nowrap;position:relative}
td.num .bar{position:absolute;right:0;top:4px;bottom:4px;background:rgba(179,38,43,.09);border-radius:3px;z-index:0}td.num{z-index:1}
.chart{width:100%;height:auto;display:block;margin:6px 0 10px}.chart rect{fill:rgba(179,38,43,.75)}.chart polyline{stroke:#161616;stroke-width:1.6}.chart text{font-size:11px;fill:#6b6b6b}
.hours{display:grid;grid-template-columns:repeat(24,1fr);gap:3px;height:150px;align-items:end;padding-bottom:22px}.hours div{height:100%;display:flex;flex-direction:column;justify-content:flex-end;position:relative}
.hours span{display:block;background:rgba(179,38,43,.75);border-radius:2px 2px 0 0;min-height:2px}.hours i{position:absolute;bottom:-20px;left:0;font-size:11px;color:var(--muted);font-style:normal}
footer{font-size:13px;margin:10px 0 40px}
.sect{font:600 26px "Playfair Display",Georgia,serif;margin:34px 0 2px;padding-top:18px;border-top:1px solid var(--rule)}.sect-note{max-width:820px}
.grid+.card,.grid+.sect{margin-top:18px}.kpis.k4{grid-template-columns:repeat(4,1fr)}.chart.gsc rect{fill:#161616}.chart.gsc rect.imp{fill:rgba(179,38,43,.22)}
.login{max-width:420px;margin:12vh auto;padding:0 20px}.login h1{font:600 34px "Playfair Display",Georgia,serif;margin:10px 0}.login form{display:flex;gap:8px;margin-top:18px}
.login input{flex:1;padding:11px 12px;border:1px solid var(--rule);border-radius:6px;font:inherit}.login button{background:var(--red);color:#fff;border:0;border-radius:6px;padding:11px 16px;font:600 15px Inter;cursor:pointer}
@media(max-width:900px){.kpis,.grid+.card,.grid+.sect{margin-top:18px}.kpis.k4{grid-template-columns:repeat(2,1fr)}.grid{grid-template-columns:1fr}.kpis b{font-size:26px}}`;

export default {
  async fetch(req, env, ctx) {
    const url = new URL(req.url);
    try {
      await init(env);
      if (url.pathname === '/hit') {
        if (req.method === 'OPTIONS') return new Response(null, { status: 204, headers: { ...cors, 'access-control-allow-methods': 'POST', 'access-control-allow-headers': 'content-type' } });
        if (req.method === 'POST') return await hit(env, req);
        return new Response('ok', { headers: cors });
      }
      if (url.pathname === '/robots.txt') return new Response('User-agent: *\nDisallow: /\n');
      if (url.pathname === '/login' && req.method === 'POST') return await sendLink(env, req);
      if (url.pathname === '/auth') return await redeem(env, req);
      if (url.pathname === '/logout') {
        const raw = cookieOf(req); if (raw) await env.DB.prepare('DELETE FROM sessions WHERE id = ?1').bind(await sha(raw)).run();
        return new Response(null, { status: 302, headers: { location: '/', 'set-cookie': `${COOKIE}=; Path=/; Max-Age=0; HttpOnly; Secure; SameSite=Lax` } });
      }
      if (url.pathname === '/') return (await signedIn(env, req)) ? await stats(env, req, ctx) : html(loginPage());
      return new Response('Not found', { status: 404 });
    } catch (e) {
      console.log('error', e && e.stack);
      return url.pathname === '/hit' ? new Response(null, { status: 204, headers: cors }) : html(page('Error', '<main class="login"><h1>Something went wrong</h1><p class="muted">Please reload the page.</p></main>'), 500);
    }
  },
  // keep the database tidy: raw visits are kept for two years
  async scheduled(_e, env) {
    await init(env);
    const cut = dayOf(Date.now() - 730 * 864e5);
    await env.DB.batch([env.DB.prepare('DELETE FROM hits WHERE day < ?1').bind(cut), env.DB.prepare('DELETE FROM events WHERE day < ?1').bind(cut),
      env.DB.prepare('DELETE FROM limits WHERE until < ?1').bind(Math.floor(Date.now() / 1000))]);
    try { await gscRefresh(env); } catch (e) { console.log('gsc', e && e.message); }
  },
};
