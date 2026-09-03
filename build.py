#!/usr/bin/env python3
"""
Static-Site-Generator für Run & See Lucerne.

Erzeugt aus src/content.json + src/config.json + src/base.css + src/themes/<theme>.css:

    index.html          Englisch  (Canonical-Sprache)
    de/index.html       Deutsch
    fr/index.html       Französisch
    legal.html          Impressum + Datenschutz (EN)
    de/legal.html       Impressum + Datenschutz (DE)
    fr/legal.html       Impressum + Datenschutz (FR)
    sitemap.xml
    robots.txt

Aufruf aus dem Projekt-Root:

    python3 build.py                    # produktive Seite, Theme aus config.json
    python3 build.py --theme tempo      # produktive Seite mit anderem Theme
    python3 build.py --previews         # zusätzlich den Alternativentwurf unter preview/

Es werden nur Module der Python-Standardbibliothek verwendet.
Die generierten HTML-Dateien NICHT von Hand bearbeiten – Änderungen gehören
in src/content.json (Texte), src/config.json (Termine, Kontakt),
src/base.css (Struktur) oder src/themes/<name>.css (Farben, Formen, Typo),
danach build.py erneut ausführen.
"""

from __future__ import annotations

import argparse
import datetime as dt
import html
import json
import re
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SRC = ROOT / "src"

# Theme -> Logo- und Favicon-Dateien unterhalb von assets/
THEMES = {
    "horizont": {
        "logo_light": "assets/logos/horizont-lockup-light.svg",
        "logo_dark": "assets/logos/horizont-lockup-dark.svg",
        "favicon": "assets/logos/horizont-mark.svg",
        "logo_w": 223, "logo_h": 64,
        "theme_color": "#163e5c",
        "label": "Horizont — See · Sonne · Himmel",
    },
    "tempo": {
        "logo_light": "assets/logos/tempo-lockup-light.svg",
        "logo_dark": "assets/logos/tempo-lockup-dark.svg",
        "favicon": "assets/logos/tempo-mark.svg",
        "logo_w": 300, "logo_h": 56,
        "theme_color": "#181613",
        "label": "Tempo — Tinte · Signal · Weiss",
    },
}

LANGS = ["en", "de", "fr"]
LANG_DIR = {"en": "", "de": "de", "fr": "fr"}

DATE_FMT = {
    "en": "%a %-d %b %Y",
    "de": "%a, %-d. %b %Y",
    "fr": "%a %-d %b %Y",
}
MONTHS = {
    "en": ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"],
    "de": ["Jan", "Feb", "Mär", "Apr", "Mai", "Jun", "Jul", "Aug", "Sep", "Okt", "Nov", "Dez"],
    "fr": ["janv", "févr", "mars", "avr", "mai", "juin", "juil", "août", "sept", "oct", "nov", "déc"],
}
WEEKDAYS = {
    "en": ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"],
    "de": ["Mo", "Di", "Mi", "Do", "Fr", "Sa", "So"],
    "fr": ["lun", "mar", "mer", "jeu", "ven", "sam", "dim"],
}

ICONS = {
    "map": '<path d="M9 20l-5.4 2.3A1 1 0 0 1 2 21.4V6.6a1 1 0 0 1 .6-.9L9 3m0 17l6-3m-6 3V3m6 14l5.4 2.3a1 1 0 0 0 1.6-.9V4.6a1 1 0 0 0-.6-.9L15 1m0 16V1m0 0L9 3"/>',
    "user": '<path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"/><circle cx="12" cy="7" r="4"/>',
    "users": '<path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/><path d="M23 21v-2a4 4 0 0 0-3-3.87M16 3.13a4 4 0 0 1 0 7.75"/>',
    "gift": '<path d="M20 12v10H4V12M2 7h20v5H2zM12 22V7M12 7H7.5a2.5 2.5 0 1 1 0-5C11 2 12 7 12 7zM12 7h4.5a2.5 2.5 0 1 0 0-5C13 2 12 7 12 7z"/>',
}

E = html.escape


def icon(name: str) -> str:
    body = ICONS.get(name, "")
    return (
        '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" '
        f'stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">{body}</svg>'
    )


def fmt_date(iso: str, lang: str) -> str:
    d = dt.date.fromisoformat(iso)
    wd = WEEKDAYS[lang][d.weekday()]
    mo = MONTHS[lang][d.month - 1]
    if lang == "de":
        return f"{wd}, {d.day}. {mo} {d.year}"
    return f"{wd} {d.day} {mo} {d.year}"


# Laufzeit-Kontext des aktuellen Builds (Theme, Pfad-Präfix für Assets)
BUILD = {"theme": "horizont", "asset_prefix": ""}


def rel(base: str, path: str) -> str:
    """Asset-Pfad relativ zur aktuellen Sprachebene und Ausgabetiefe."""
    up = "../" if base else ""
    return up + BUILD["asset_prefix"] + path


def theme_css() -> str:
    """Basis zuerst, Theme danach — damit Theme-Regeln die Basis überschreiben.
    Die :root-Tokens des Themes greifen trotzdem, weil die Basis keine setzt."""
    base = (SRC / "base.css").read_text(encoding="utf-8")
    theme = (SRC / "themes" / f"{BUILD['theme']}.css").read_text(encoding="utf-8")
    return base + "\n" + theme


def theme_meta(key: str) -> str:
    return THEMES[BUILD["theme"]][key]


def url_for(cfg: dict, lang: str, page: str = "") -> str:
    domain = cfg["site"]["domain"].rstrip("/")
    d = LANG_DIR[lang]
    if d:
        return f"{domain}/{d}/{page}" if page else f"{domain}/{d}/"
    return f"{domain}/{page}" if page else f"{domain}/"


# ── Bausteine ──────────────────────────────────────────────────────────────


def head(cfg, t, lang, *, page, title, description, base, extra_ld=""):
    domain = cfg["site"]["domain"].rstrip("/")
    og_image = f"{domain}/assets/images/hero/luzern-kapellbruecke.jpg"
    alternates = "\n".join(
        f'  <link rel="alternate" hreflang="{L}" href="{url_for(cfg, L, page)}" />'
        for L in LANGS
    )
    css = theme_css()
    # Das Hero-Bild ist das groesste sichtbare Element beim Seitenaufbau.
    # Vorladen verbessert den Largest Contentful Paint spuerbar.
    preload = "" if page else (
        '  <link rel="preload" as="image" fetchpriority="high"\n'
        f'        href="{rel(base, "assets/images/hero/luzern-kapellbruecke.webp")}"\n'
        f'        imagesrcset="{rel(base, "assets/images/hero/luzern-kapellbruecke-800.webp")} 800w, '
        f'{rel(base, "assets/images/hero/luzern-kapellbruecke-1280.webp")} 1280w, '
        f'{rel(base, "assets/images/hero/luzern-kapellbruecke.webp")} 1920w"\n'
        '        imagesizes="100vw" type="image/webp" />\n'
    )
    return f"""<!DOCTYPE html>
<html lang="{lang}">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>{E(title)}</title>
  <meta name="description" content="{E(description)}" />
  <meta name="robots" content="index, follow, max-image-preview:large" />

  <link rel="canonical" href="{url_for(cfg, lang, page)}" />
{alternates}
  <link rel="alternate" hreflang="x-default" href="{url_for(cfg, 'en', page)}" />

  <meta property="og:type" content="website" />
  <meta property="og:site_name" content="{E(cfg['site']['brand'])}" />
  <meta property="og:locale" content="{t['locale']}" />
  <meta property="og:url" content="{url_for(cfg, lang, page)}" />
  <meta property="og:title" content="{E(title)}" />
  <meta property="og:description" content="{E(description)}" />
  <meta property="og:image" content="{og_image}" />
  <meta property="og:image:width" content="1920" />
  <meta property="og:image:height" content="1080" />
  <meta property="og:image:alt" content="{E(t['og_image_alt'])}" />
  <meta name="twitter:card" content="summary_large_image" />
  <meta name="twitter:image" content="{og_image}" />
  <meta name="twitter:image:alt" content="{E(t['og_image_alt'])}" />

  <meta name="author" content="{E(cfg['site']['brand'])}" />
  <meta name="geo.region" content="CH-LU" />
  <meta name="geo.placename" content="Luzern" />
  <meta name="geo.position" content="{cfg['meeting_point']['lat']};{cfg['meeting_point']['lon']}" />
  <meta name="ICBM" content="{cfg['meeting_point']['lat']}, {cfg['meeting_point']['lon']}" />
{preload}
  <link rel="icon" type="image/svg+xml" href="{rel(base, theme_meta('favicon'))}" />
  <meta name="theme-color" content="{theme_meta('theme_color')}" />

  <style>
{css}
  </style>
{extra_ld}
</head>"""


def navbar(cfg, t, lang, base, *, page=""):
    nav = t["nav"]
    home = "index.html"   # jede Sprachebene hat ihre eigene index.html
    items = [
        (f"{home}#tours", nav["tours"]),
        (f"{home}#about", nav["about"]),
        (f"{home}#how", nav["how"]),
        (f"{home}#join", nav["join"]),
        (f"{home}#faq", nav["faq"]),
    ]
    links = "\n".join(
        f'        <li><a href="{h}">{E(label)}</a></li>' for h, label in items
    )
    lang_links = []
    for L in LANGS:
        d = LANG_DIR[L]
        target = page or "index.html"
        if L == lang:
            href = target
        elif base == "":
            href = f"{d}/{target}" if d else target
        else:
            href = f"../{d}/{target}" if d else f"../{target}"
        cur = ' aria-current="true"' if L == lang else ""
        lang_links.append(
            f'          <a href="{href}" hreflang="{L}" lang="{L}"{cur}>{L.upper()}</a>'
        )
    return f"""<nav id="navbar" aria-label="{E(nav.get('aria_main', 'Main navigation'))}">
  <div class="wrap">
    <a class="nav-logo" href="{home}" aria-label="{E(cfg['site']['brand'])}">
      <img class="logo-light" src="{rel(base, theme_meta('logo_light'))}" alt="{E(cfg['site']['brand'])}"
           width="{theme_meta('logo_w')}" height="{theme_meta('logo_h')}" />
      <img class="logo-dark" src="{rel(base, theme_meta('logo_dark'))}" alt="" aria-hidden="true"
           width="{theme_meta('logo_w')}" height="{theme_meta('logo_h')}" />
    </a>
    <ul class="nav-links" id="navLinks">
{links}
    </ul>
    <div class="nav-right">
      <div class="lang-switch" role="group" aria-label="{E(nav.get('aria_lang', 'Language'))}">
{chr(10).join(lang_links)}
      </div>
      <a class="btn btn-primary nav-cta" href="{home}#join">{E(nav['cta'])}</a>
      <button class="hamburger" id="hamburger" type="button"
              aria-label="{E(nav.get('aria_menu', 'Menu'))}" aria-controls="navLinks" aria-expanded="false">
        <span></span><span></span><span></span>
      </button>
    </div>
  </div>
</nav>"""


ARROW = ('<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" '
         'stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">'
         '<path d="M5 12h14M13 6l6 6-6 6"/></svg>')
ARROW_L = ('<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" '
           'stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">'
           '<path d="M19 12H5M11 18l-6-6 6-6"/></svg>')
# Anzeigebreite der Tourbilder je Fensterbreite — muss zu den Regeln
# fuer .carousel-track in src/base.css passen, sonst laedt der Browser
# unnoetig grosse Dateien.
TOUR_SIZES = ("(min-width: 1180px) 310px, (min-width: 1000px) 31vw, "
              "(min-width: 700px) 46vw, 82vw")

CHEVRON_DOWN = ('<svg viewBox="0 0 24 24" fill="none" stroke-width="2" stroke-linecap="round" '
                'stroke-linejoin="round" aria-hidden="true"><path d="M6 9l6 6 6-6"/></svg>')


def hero(t, base):
    h = t["hero"]
    lines = h.get("h1_lines") or [h["h1"]]
    line_html = "\n      ".join(
        f'<span class="line"><span>{E(l)}</span></span>' for l in lines
    )
    return f"""<section id="hero">
  <div class="hero-media">
    <picture>
      <!-- srcset mit Breitenangaben statt media-Queries: nur so trifft der
           Browser dieselbe Wahl wie der Preload im head, sonst wird das Bild
           zweimal geladen. -->
      <source type="image/webp" sizes="100vw"
              srcset="{rel(base, 'assets/images/hero/luzern-kapellbruecke-800.webp')} 800w,
                      {rel(base, 'assets/images/hero/luzern-kapellbruecke-1280.webp')} 1280w,
                      {rel(base, 'assets/images/hero/luzern-kapellbruecke.webp')} 1920w" />
      <img src="{rel(base, 'assets/images/hero/luzern-kapellbruecke.jpg')}" alt="{E(t['og_image_alt'])}"
           sizes="100vw"
           srcset="{rel(base, 'assets/images/hero/luzern-kapellbruecke-800.jpg')} 800w,
                   {rel(base, 'assets/images/hero/luzern-kapellbruecke-1280.jpg')} 1280w,
                   {rel(base, 'assets/images/hero/luzern-kapellbruecke.jpg')} 1920w"
           width="1920" height="1080" fetchpriority="high" decoding="async" />
    </picture>
  </div>
  <div class="wrap hero-inner">
    <p class="hero-badge"><span class="dot" aria-hidden="true"></span>{E(h['badge'])}</p>
    <h1>
      {line_html}
    </h1>
    <p class="hero-lead">{E(h['lead'])}</p>
    <div class="hero-actions">
      <a class="btn btn-primary" href="#join">{E(h['cta_primary'])}{ARROW}</a>
      <a class="btn btn-ghost" href="#tours">{E(h['cta_secondary'])}</a>
    </div>
  </div>
  <div class="hero-cue" aria-hidden="true">{CHEVRON_DOWN}</div>
</section>"""


def stats_section(content, t):
    nums = content["stats"]
    labels = t["stats_labels"]
    items = []
    for n, label in zip(nums, labels):
        unit = f'<span class="unit">{E(n["unit"])}</span>' if n["unit"] else ""
        items.append(
            f"""      <div class="stat reveal">
        <b><span class="count" data-to="{E(n['num'])}">0</span>{unit}</b>
        <span>{E(label)}</span>
      </div>"""
        )
    return f"""<section class="stats" aria-label="{E(t['nav']['tours'])}">
  <div class="wrap">
    <div class="stats-grid">
{chr(10).join(items)}
    </div>
  </div>
</section>"""


def sticky_cta(t):
    s = t["sticky"]
    return f"""<div class="sticky-cta" id="stickyCta">
  <span class="sticky-cta-text">{E(s['text'])}</span>
  <a class="btn btn-primary" href="#join">{E(s['button'])}{ARROW}</a>
</div>"""


def value_section(t):
    v = t["value"]
    items = "\n".join(
        f"""      <div class="value-item reveal{" reveal-d" + str(min(n, 3)) if n else ""}">
        <div class="value-icon">{icon(i['icon'])}</div>
        <h3>{E(i['title'])}</h3>
        <p>{E(i['text'])}</p>
      </div>"""
        for n, i in enumerate(v["items"])
    )
    return f"""<section id="why" aria-labelledby="why-h">
  <div class="wrap">
    <div class="section-head reveal">
      <div class="rule" aria-hidden="true"></div>
      <h2 id="why-h">{E(v['heading'])}</h2>
    </div>
    <div class="value-grid">
{items}
    </div>
  </div>
</section>"""


def tours_section(content, t, base):
    ts = t["tours_section"]
    level_label = {
        "green": ts["level_green"],
        "orange": ts["level_orange"],
        "red": ts["level_red"],
    }
    cards = []
    for tour in content["tours"]:
        loc = ts["items"][tour["id"]]
        facts = [
            (ts["label_distance"], tour["km"], tour["mi"]),
        ]
        if tour.get("pace"):
            facts.append((ts["label_pace"], tour["pace"], tour["pace_mi"]))
        if tour.get("elevation"):
            facts.append((ts["label_elevation"], tour["elevation"], ""))
        facts.append((ts["label_start"], " · ".join(tour["times"]), ""))
        fact_html = "\n".join(
            f"""          <div class="tour-fact"><dt>{E(k)}</dt>"""
            f"""<dd>{E(v)}{f' <span class="alt">({E(alt)})</span>' if alt else ''}</dd></div>"""
            for k, v, alt in facts
        )
        img = tour["image"]
        n = content["tours"].index(tour) + 1
        cards.append(
            f"""        <article class="tour-card" id="tour-{tour['id']}" aria-roledescription="slide"
                 aria-label="{n} / {len(content['tours'])}: {E(loc['name'])}">
          <div class="tour-media">
            <picture>
              <source type="image/webp" sizes="{TOUR_SIZES}"
                      srcset="{rel(base, f'assets/images/tours/{img}-480.webp')} 480w,
                              {rel(base, f'assets/images/tours/{img}.webp')} 800w" />
              <img src="{rel(base, f'assets/images/tours/{img}.jpg')}"
                   alt="{E(loc['name'])} — {E(loc.get('image_alt', loc['tagline']))}"
                   sizes="{TOUR_SIZES}"
                   srcset="{rel(base, f'assets/images/tours/{img}-480.jpg')} 480w,
                           {rel(base, f'assets/images/tours/{img}.jpg')} 800w"
                   width="800" height="600" loading="lazy" decoding="async" />
            </picture>
            <span class="tour-index">{n:02d}</span>
          </div>
          <div class="tour-body">
            <span class="badge badge-{tour['level']}">{E(level_label[tour['level']])}</span>
            <h3>{E(loc['name'])}</h3>
            <p class="tour-tagline">{E(loc['tagline'])}</p>
            <p class="tour-desc">{E(loc['text'])}</p>
            <dl class="tour-facts">
{fact_html}
            </dl>
          </div>
        </article>"""
        )

    car = t["carousel"]
    dot_list = []
    for i in range(len(content["tours"])):
        cur = ' aria-current="true"' if i == 0 else ""
        dot_list.append(
            f'        <button type="button" data-go="{i}" '
            f'aria-label="{E(car["goto"])} {i + 1}"{cur}></button>'
        )
    dots = "\n".join(dot_list)
    return f"""<section id="tours" class="alt" aria-labelledby="tours-h">
  <div class="wrap">
    <div class="section-head reveal">
      <div class="rule" aria-hidden="true"></div>
      <h2 id="tours-h">{E(ts['heading'])}</h2>
      <p>{E(ts['intro'])}</p>
    </div>

    <div class="carousel" id="tourCarousel">
      <div class="carousel-track" id="tourTrack" tabindex="0"
           role="group" aria-roledescription="carousel" aria-label="{E(car['label'])}">
{chr(10).join(cards)}
      </div>
      <div class="carousel-controls">
        <div class="carousel-nav">
          <p class="carousel-count" aria-hidden="true">
            <b id="tourCurrent">01</b><span>/ {len(content['tours']):02d}</span>
          </p>
          <div class="carousel-dots" id="tourDots">
{dots}
          </div>
        </div>
        <div class="carousel-arrows">
          <button type="button" id="tourPrev" aria-label="{E(car['prev'])}" aria-controls="tourTrack">{ARROW_L}</button>
          <button type="button" id="tourNext" aria-label="{E(car['next'])}" aria-controls="tourTrack">{ARROW}</button>
        </div>
      </div>
    </div>
  </div>
</section>"""


def practical_section(cfg, t, lang):
    """Ablauf, Treffpunkt und die praktischen Hinweise in einer Sektion."""
    h = t["how"]
    m = t["meeting"]
    mp = cfg["meeting_point"]
    detail = mp.get(f"detail_{lang}", mp.get("detail_en", ""))
    embed = f"https://www.google.com/maps?q={mp['lat']},{mp['lon']}&hl={lang}&z=16&output=embed"

    steps = "\n".join(
        f"""        <div class="step reveal{" reveal-d" + str(min(n, 3)) if n else ""}">"""
        f"""<h3>{E(s['title'])}</h3><p>{E(s['text'])}</p></div>"""
        for n, s in enumerate(h["steps"])
    )
    know = "\n".join(
        f"""        <div class="know-item"><h4>{E(i['title'])}</h4><p>{E(i['text'])}</p></div>"""
        for i in t["good_to_know"]["items"]
    )

    return f"""<section id="how" class="alt" aria-labelledby="how-h">
  <div class="wrap">
    <div class="section-head reveal">
      <div class="rule" aria-hidden="true"></div>
      <h2 id="how-h">{E(h['heading'])}</h2>
    </div>

    <div class="steps-wrap">
      <div class="steps-line" id="stepsLine" aria-hidden="true">
        <svg viewBox="0 0 1000 2" preserveAspectRatio="none">
          <path d="M40 1 H960" />
        </svg>
      </div>
      <div class="steps">
{steps}
      </div>
    </div>

    <div class="practical reveal">
      <div>
        <h3 class="subhead">{E(h['meet_heading'])}</h3>
        <p class="meet-address"><strong>{E(mp['name'])}</strong>{E(detail)}</p>
        <div class="map-shell" id="mapShell" data-src="{E(embed)}">
          <div class="map-consent" id="mapConsent">
            <h4>{E(m['map_consent_title'])}</h4>
            <p>{E(m['map_consent_text'])}</p>
            <button class="btn btn-outline" type="button" id="mapLoad">{E(m['map_consent_button'])}</button>
          </div>
        </div>
        <a class="ig-link" href="{E(mp['maps_url'])}" target="_blank" rel="noopener noreferrer">{E(m['open_in_maps'])}</a>
      </div>
      <div>
        <h3 class="subhead">{E(h['know_heading'])}</h3>
        <div class="know-grid">
{know}
        </div>
      </div>
    </div>
  </div>
</section>"""


def run_label(r, ts_items, fallback):
    """Namen der Routen eines Termins. Ist keine Route gesetzt, steht dort der
    Hinweistext 'Route offen' — der Termin findet trotzdem statt, die Route
    entscheidet die erste Anmeldung."""
    names = [ts_items[x]["name"] for x in r.get("tours", []) if x in ts_items]
    return " / ".join(names) if names else fallback


def upcoming_runs(cfg):
    today = dt.date.today()
    runs = []
    for r in cfg["schedule"].get("runs", []):
        try:
            d = dt.date.fromisoformat(r["date"])
        except (KeyError, ValueError):
            continue
        if d >= today:
            runs.append(r)
    runs.sort(key=lambda r: (r["date"], r.get("time", "")))
    return runs


def join_section(cfg, content, t, lang, base):
    j = t["join"]
    f = j["form"]
    ts_items = t["tours_section"]["items"]
    runs = upcoming_runs(cfg)

    if runs:
        rows = []
        for r in runs:
            names = run_label(r, ts_items, j["run_open"])
            rows.append(
                f"""        <div class="run-item">
          <div>
            <time class="run-when" datetime="{E(r['date'])}T{E(r.get('time', '00:00'))}">{E(fmt_date(r['date'], lang))}</time>
            <div class="run-what">{E(names)}</div>
          </div>
          <div class="run-time">{E(r.get('time', ''))}</div>
        </div>"""
            )
        has_open = any(
            not [tid for tid in r.get("tours", []) if tid in ts_items] for r in runs
        )
        open_note = (
            f'\n      <p class="run-note">{E(j["run_open_note"])}</p>' if has_open else ""
        )
        runs_block = f"""      <div class="run-list">
{chr(10).join(rows)}
      </div>{open_note}"""
        date_options = [
            f'<option value="{E(r["date"])} {E(r.get("time", ""))}">'
            f'{E(fmt_date(r["date"], lang))} – {E(r.get("time", ""))}</option>'
            for r in runs
        ]
    else:
        runs_block = f"""      <div class="run-empty">
        <h3>{E(j['empty_title'])}</h3>
        <p>{E(j['empty_text'])}</p>
      </div>"""
        date_options = []

    date_options.append(f'<option value="flexible">{E(f["date_flexible"])}</option>')

    tour_options = "\n".join(
        f'            <option value="{E(tour["id"])}">{E(ts_items[tour["id"]]["name"])}</option>'
        for tour in content["tours"]
    )

    lang_options = "\n".join(
        f'            <option value="{L}">{E(content["languages"][L]["lang_name"])}</option>'
        for L in LANGS
    )

    legal_href = "legal.html"   # liegt in jeder Sprachebene neben index.html

    return f"""<section id="join" aria-labelledby="join-h">
  <div class="wrap">
    <div class="section-head reveal">
      <div class="rule" aria-hidden="true"></div>
      <h2 id="join-h">{E(j['heading'])}</h2>
      <p>{E(j['intro'])}</p>
    </div>
    <div class="join-layout reveal">
      <div>
        <div class="countdown" id="countdown" hidden>
          <div class="countdown-label" id="countdown-label"></div>
          <div class="countdown-run" id="countdown-run"></div>
          <div class="countdown-clock" id="countdown-clock"></div>
        </div>
{runs_block}
      </div>

      <div class="form-card">
        <h3>{E(j['form_heading'])}</h3>
        <form id="joinForm" novalidate>
          <div class="hp" aria-hidden="true">
            <label for="company">Company</label>
            <input type="text" id="company" name="company" tabindex="-1" autocomplete="off" />
          </div>
          <div class="field-row">
            <div class="field">
              <label for="fname">{E(f['name'])} *</label>
              <input type="text" id="fname" name="name" required autocomplete="name" placeholder="{E(f['name_ph'])}" />
            </div>
            <div class="field">
              <label for="femail">{E(f['email'])} *</label>
              <input type="email" id="femail" name="email" required autocomplete="email" placeholder="{E(f['email_ph'])}" />
            </div>
          </div>
          <div class="field-row">
            <div class="field">
              <label for="fdate">{E(f['date'])}</label>
              <select id="fdate" name="date">
                {chr(10).join('            ' + o for o in date_options)}
              </select>
            </div>
            <div class="field">
              <label for="ftour">{E(f['tour'])}</label>
              <select id="ftour" name="tour">
                <option value="any">{E(f['tour_any'])}</option>
{tour_options}
              </select>
            </div>
          </div>
          <div class="field-row">
            <div class="field">
              <label for="fpeople">{E(f['people'])}</label>
              <input type="number" id="fpeople" name="people" min="1" max="12" value="1" inputmode="numeric" />
            </div>
            <div class="field">
              <label for="flang">{E(f['language'])}</label>
              <select id="flang" name="language">
{lang_options}
              </select>
            </div>
          </div>
          <div class="field">
            <label for="fmsg">{E(f['message'])}</label>
            <textarea id="fmsg" name="message" placeholder="{E(f['message_ph'])}"></textarea>
          </div>
          <label class="consent">
            <input type="checkbox" id="fconsent" name="consent" required />
            <span>{E(f['consent'])} <a href="{legal_href}#privacy">{E(f['consent_link'])}</a>.</span>
          </label>
          <button type="submit" class="btn btn-primary" id="submitBtn">{E(f['submit'])}</button>
          <p class="required-note">{E(f['required_note'])}</p>
          <p class="form-status" id="formStatus" role="status" aria-live="polite"></p>
        </form>
      </div>
    </div>
  </div>
</section>"""




def about_section(cfg, t, base):
    a = t["about"]
    return f"""<section id="about" aria-labelledby="about-h">
  <div class="wrap">
    <div class="section-head reveal">
      <div class="rule" aria-hidden="true"></div>
      <h2 id="about-h">{E(a['heading'])}</h2>
    </div>
    <div class="about-layout reveal">
      <picture>
        <source type="image/webp" srcset="{rel(base, 'assets/images/team/philippe.webp')}" />
        <img class="about-photo" src="{rel(base, 'assets/images/team/philippe.png')}"
             alt="{E(a['name'])}" width="560" height="560" loading="lazy" decoding="async" />
      </picture>
      <div>
        <h3>{E(a['name'])}</h3>
        <p>{E(a['text'])}</p>
        <p>{E(a['text_2'])}</p>
        <p class="about-meta"><b>{E(a['languages_label'])}:</b> {E(a['languages_value'])}</p>
        <a class="ig-link" href="{E(cfg['site']['instagram_url'])}" target="_blank" rel="noopener noreferrer">
          {icon('user')}{E(a['instagram_label'])}
        </a>
      </div>
    </div>
  </div>
</section>"""


def faq_section(t):
    fq = t["faq"]
    items = "\n".join(
        f"""      <details class="faq-item">
        <summary>{E(i['q'])}</summary>
        <div class="faq-answer-wrap"><div class="faq-answer"><p>{E(i['a'])}</p></div></div>
      </details>"""
        for i in fq["items"]
    )
    return f"""<section id="faq" class="alt" aria-labelledby="faq-h">
  <div class="wrap">
    <div class="section-head reveal">
      <div class="rule" aria-hidden="true"></div>
      <h2 id="faq-h">{E(fq['heading'])}</h2>
    </div>
    <div class="faq-list reveal">
{items}
    </div>
  </div>
</section>"""


def footer(cfg, t, lang, base, content):
    fo = t["footer"]
    nav = t["nav"]
    home = "index.html"   # jede Sprachebene hat ihre eigene index.html
    year = dt.date.today().year
    legal = "legal.html"
    site_links = "\n".join(
        f'        <li><a href="{home}#{anchor}">{E(nav[key])}</a></li>'
        for anchor, key in [("tours", "tours"), ("about", "about"), ("how", "how"), ("join", "join"), ("faq", "faq")]
    )
    lang_items = []
    for L in LANGS:
        d = LANG_DIR[L]
        if base == "":
            href = f"{d}/index.html" if d else "index.html"
        else:
            href = f"../{d}/index.html" if d else "../index.html"
        lang_items.append(f'        <li><a href="{href}" hreflang="{L}">{E(content["languages"][L]["lang_name"])}</a></li>')

    return f"""<footer>
  <div class="wrap">
    <div class="footer-grid">
      <div class="footer-brand">
        <img src="{rel(base, theme_meta('logo_light'))}" alt="{E(cfg['site']['brand'])}"
             width="{theme_meta('logo_w')}" height="{theme_meta('logo_h')}" />
        <p>{E(fo['tagline'])}</p>
      </div>
      <div>
        <h4>{E(fo['nav_heading'])}</h4>
        <ul>
{site_links}
        </ul>
      </div>
      <div>
        <h4>{E(fo['legal_heading'])}</h4>
        <ul>
          <li><a href="{legal}#imprint">{E(fo['imprint'])}</a></li>
          <li><a href="{legal}#privacy">{E(fo['privacy'])}</a></li>
          <li><a href="{E(cfg['site']['instagram_url'])}" target="_blank" rel="noopener noreferrer">Instagram</a></li>
        </ul>
      </div>
      <div>
        <h4>{E(fo['language_heading'])}</h4>
        <ul>
{chr(10).join(lang_items)}
        </ul>
      </div>
    </div>
    <div class="footer-bottom">
      <span>&copy; {year} {E(cfg['site']['brand'])}</span>
      <span>{E(fo['established'])} {cfg['site']['established']}</span>
    </div>
  </div>
</footer>"""


def page_script(cfg, content, t, lang):
    runs = upcoming_runs(cfg)
    ts_items = t["tours_section"]["items"]
    runs_js = [
        {
            "date": r["date"],
            "time": r.get("time", ""),
            "label": run_label(r, ts_items, t["join"]["run_open"]),
        }
        for r in runs
    ]
    labels = {
        "en": {"cd": "Next run in", "d": "days", "h": "hours", "m": "min"},
        "de": {"cd": "Nächster Run in", "d": "Tage", "h": "Std", "m": "Min"},
        "fr": {"cd": "Prochaine course dans", "d": "jours", "h": "h", "m": "min"},
    }[lang]

    cfgjs = json.dumps(
        {
            "provider": cfg["form"]["provider"],
            "endpoint": cfg["form"]["formspree_endpoint"],
            "email": cfg["site"]["contact_email"],
            "runs": runs_js,
            "labels": labels,
            "msgSuccess": t["join"]["form"]["success"],
            "msgError": t["join"]["form"]["error"],
            "msgSending": t["join"]["form"]["sending"],
            "msgSubmit": t["join"]["form"]["submit"],
            "brand": cfg["site"]["brand"],
        },
        ensure_ascii=False,
    )

    return """<script>
(function () {
  "use strict";
  var CFG = %s;

  /* ── Navbar: Scroll-Zustand ────────────────────────────────────────── */
  var navbar = document.getElementById("navbar");
  function onScroll() {
    navbar.classList.toggle("scrolled", window.scrollY > 40);
  }
  if (navbar && !document.body.classList.contains("legal-page")) {
    onScroll();
    window.addEventListener("scroll", onScroll, { passive: true });
  }

  /* ── Mobile-Menü ───────────────────────────────────────────────────── */
  var burger = document.getElementById("hamburger");
  var links = document.getElementById("navLinks");
  if (burger && links) {
    var setMenu = function (open) {
      links.classList.toggle("open", open);
      if (navbar) navbar.classList.toggle("menu-open", open);
      burger.setAttribute("aria-expanded", open ? "true" : "false");
    };
    burger.addEventListener("click", function () {
      setMenu(!links.classList.contains("open"));
    });
    links.querySelectorAll("a").forEach(function (a) {
      a.addEventListener("click", function () { setMenu(false); });
    });
    document.addEventListener("keydown", function (e) {
      if (e.key === "Escape" && links.classList.contains("open")) {
        setMenu(false);
        burger.focus();
      }
    });
  }

  /* ── Karte erst nach Klick laden (kein Google-Request vorher) ──────── */
  var mapBtn = document.getElementById("mapLoad");
  if (mapBtn) {
    mapBtn.addEventListener("click", function () {
      var shell = document.getElementById("mapShell");
      var consent = document.getElementById("mapConsent");
      var frame = document.createElement("iframe");
      frame.src = shell.getAttribute("data-src");
      frame.loading = "lazy";
      frame.title = "Google Maps";
      frame.setAttribute("referrerpolicy", "no-referrer-when-downgrade");
      frame.setAttribute("allowfullscreen", "");
      shell.appendChild(frame);
      if (consent) consent.remove();
    });
  }

  /* ── Countdown bis zum nächsten Run ────────────────────────────────── */
  var cd = document.getElementById("countdown");
  if (cd && CFG.runs.length) {
    var next = null;
    var now = new Date();
    for (var i = 0; i < CFG.runs.length; i++) {
      var r = CFG.runs[i];
      var when = new Date(r.date + "T" + (r.time || "00:00") + ":00");
      if (when > now) { next = { when: when, label: r.label }; break; }
    }
    if (next) {
      cd.hidden = false;
      document.getElementById("countdown-label").textContent = CFG.labels.cd;
      document.getElementById("countdown-run").textContent = next.label;
      var clock = document.getElementById("countdown-clock");
      var tick = function () {
        var diff = next.when - new Date();
        if (diff <= 0) { cd.hidden = true; return; }
        var d = Math.floor(diff / 86400000);
        var h = Math.floor((diff %% 86400000) / 3600000);
        var m = Math.floor((diff %% 3600000) / 60000);
        clock.innerHTML =
          "<div><b>" + d + "</b><span>" + CFG.labels.d + "</span></div>" +
          "<div><b>" + h + "</b><span>" + CFG.labels.h + "</span></div>" +
          "<div><b>" + m + "</b><span>" + CFG.labels.m + "</span></div>";
      };
      tick();
      setInterval(tick, 30000);
    }
  }

  /* ── Scroll-Reveal ─────────────────────────────────────────────────── */
  var reduced = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  var reveals = document.querySelectorAll(".reveal");
  if (reduced || !("IntersectionObserver" in window)) {
    reveals.forEach(function (el) { el.classList.add("in"); });
  } else {
    var ro = new IntersectionObserver(function (entries) {
      entries.forEach(function (e) {
        if (e.isIntersecting) { e.target.classList.add("in"); ro.unobserve(e.target); }
      });
    }, { rootMargin: "0px 0px -8%% 0px", threshold: 0.12 });
    reveals.forEach(function (el) { ro.observe(el); });
  }

  /* ── Zahlen hochzählen ─────────────────────────────────────────────── */
  document.querySelectorAll(".count").forEach(function (el) {
    var target = parseInt(el.getAttribute("data-to"), 10) || 0;
    if (reduced || !("IntersectionObserver" in window)) { el.textContent = target; return; }
    var seen = false;
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (e) {
        if (!e.isIntersecting || seen) return;
        seen = true; io.disconnect();
        var start = performance.now(), dur = 1100;
        var step = function (now) {
          var p = Math.min((now - start) / dur, 1);
          el.textContent = Math.round(target * (1 - Math.pow(1 - p, 3)));
          if (p < 1) requestAnimationFrame(step);
        };
        requestAnimationFrame(step);
      });
    }, { threshold: 0.6 });
    io.observe(el);
  });

  /* ── Verbindungslinie im Ablauf zeichnen ───────────────────────────── */
  var lineWrap = document.getElementById("stepsLine");
  if (lineWrap) {
    var path = lineWrap.querySelector("path");
    var len = 1000;
    path.style.setProperty("--dash", len);
    path.style.strokeDashoffset = reduced ? 0 : len;
    if (!reduced && "IntersectionObserver" in window) {
      var lo = new IntersectionObserver(function (entries) {
        entries.forEach(function (e) {
          if (e.isIntersecting) { path.style.strokeDashoffset = 0; lo.disconnect(); }
        });
      }, { threshold: 0.3 });
      lo.observe(lineWrap);
    }
  }

  /* ── Touren-Karussell ──────────────────────────────────────────────── */
  var track = document.getElementById("tourTrack");
  if (track) {
    var cards = Array.prototype.slice.call(track.children);
    var dots = Array.prototype.slice.call(document.querySelectorAll("#tourDots button"));
    var prev = document.getElementById("tourPrev");
    var next = document.getElementById("tourNext");

    var nearestIndex = function () {
      var best = 0, bestDist = Infinity;
      cards.forEach(function (c, i) {
        var d = Math.abs(c.offsetLeft - track.scrollLeft);
        if (d < bestDist) { bestDist = d; best = i; }
      });
      return best;
    };
    var goTo = function (i) {
      i = Math.max(0, Math.min(cards.length - 1, i));
      track.scrollTo({ left: cards[i].offsetLeft, behavior: reduced ? "auto" : "smooth" });
    };
    var counter = document.getElementById("tourCurrent");
    var sync = function () {
      var i = nearestIndex();
      dots.forEach(function (d, n) {
        if (n === i) d.setAttribute("aria-current", "true");
        else d.removeAttribute("aria-current");
      });
      if (counter) counter.textContent = ("0" + (i + 1)).slice(-2);
      var atStart = track.scrollLeft <= 2;
      var atEnd = track.scrollLeft + track.clientWidth >= track.scrollWidth - 2;
      prev.disabled = atStart;
      next.disabled = atEnd;
    };

    prev.addEventListener("click", function () { goTo(nearestIndex() - 1); });
    next.addEventListener("click", function () { goTo(nearestIndex() + 1); });
    dots.forEach(function (d) {
      d.addEventListener("click", function () { goTo(parseInt(d.getAttribute("data-go"), 10)); });
    });
    track.addEventListener("keydown", function (e) {
      if (e.key === "ArrowRight") { e.preventDefault(); goTo(nearestIndex() + 1); }
      if (e.key === "ArrowLeft")  { e.preventDefault(); goTo(nearestIndex() - 1); }
    });

    var raf = null;
    track.addEventListener("scroll", function () {
      if (raf) cancelAnimationFrame(raf);
      raf = requestAnimationFrame(sync);
    }, { passive: true });
    window.addEventListener("resize", sync, { passive: true });
    sync();
  }

  /* ── Aktiver Navigationspunkt ──────────────────────────────────────── */
  var navAnchors = Array.prototype.slice.call(
    document.querySelectorAll('.nav-links a[href*="#"]')
  );
  var sectionIds = ["tours", "how", "join", "about", "faq"];
  if (navAnchors.length && "IntersectionObserver" in window) {
    var so = new IntersectionObserver(function (entries) {
      entries.forEach(function (e) {
        if (!e.isIntersecting) return;
        navAnchors.forEach(function (a) {
          a.classList.toggle("active", a.getAttribute("href").indexOf("#" + e.target.id) > -1);
        });
      });
    }, { rootMargin: "-45%% 0px -50%% 0px" });
    sectionIds.forEach(function (id) {
      var el = document.getElementById(id);
      if (el) so.observe(el);
    });
  }

  /* ── Sticky-CTA auf Mobil ──────────────────────────────────────────── */
  var sticky = document.getElementById("stickyCta");
  var heroEl = document.getElementById("hero");
  var joinEl = document.getElementById("join");
  if (sticky && heroEl) {
    var updateSticky = function () {
      var pastHero = window.scrollY > heroEl.offsetHeight * 0.85;
      var inJoin = joinEl &&
        window.scrollY + window.innerHeight > joinEl.offsetTop + 120 &&
        window.scrollY < joinEl.offsetTop + joinEl.offsetHeight;
      sticky.classList.toggle("show", pastHero && !inJoin);
    };
    updateSticky();
    window.addEventListener("scroll", updateSticky, { passive: true });
  }

  /* ── Anmeldeformular ───────────────────────────────────────────────── */
  var form = document.getElementById("joinForm");
  if (!form) return;
  var status = document.getElementById("formStatus");
  var btn = document.getElementById("submitBtn");

  function show(kind, text) {
    status.className = "form-status " + kind;
    status.textContent = text;
  }

  function collect() {
    var fd = new FormData(form);
    var out = {};
    fd.forEach(function (v, k) { out[k] = v; });
    return out;
  }

  form.addEventListener("submit", function (e) {
    e.preventDefault();
    if (form.company && form.company.value) return;      // Honeypot: stiller Abbruch
    if (!form.reportValidity()) return;

    var data = collect();
    delete data.company;
    data.page = location.href;

    if (CFG.provider === "mailto") {
      var body = Object.keys(data).map(function (k) {
        return k + ": " + data[k];
      }).join("\\n");
      window.location.href =
        "mailto:" + CFG.email +
        "?subject=" + encodeURIComponent(CFG.brand + " – " + (data.name || "")) +
        "&body=" + encodeURIComponent(body);
      show("ok", CFG.msgSuccess);
      return;
    }

    btn.disabled = true;
    btn.textContent = CFG.msgSending;

    fetch(CFG.endpoint, {
      method: "POST",
      headers: { "Content-Type": "application/json", Accept: "application/json" },
      body: JSON.stringify(data)
    }).then(function (res) {
      if (!res.ok) throw new Error(res.status);
      form.reset();
      show("ok", CFG.msgSuccess);
    }).catch(function () {
      show("fail", CFG.msgError + " " + CFG.email);
    }).finally(function () {
      btn.disabled = false;
      btn.textContent = CFG.msgSubmit;
    });
  });
})();
</script>""" % cfgjs


def json_ld(cfg, content, t, lang):
    domain = cfg["site"]["domain"].rstrip("/")
    mp = cfg["meeting_point"]
    ts_items = t["tours_section"]["items"]
    hero = f"{domain}/assets/images/hero/luzern-kapellbruecke.jpg"
    same_as = [u for u in (cfg["site"].get("instagram_url"),
                           cfg["site"].get("strava_club_url")) if u]
    langs = ["en", "de", "gsw", "fr"]

    graph = [
        {
            "@type": "ImageObject",
            "@id": f"{domain}/#logo",
            "url": f"{domain}/{theme_meta('logo_dark')}",
            "contentUrl": f"{domain}/{theme_meta('logo_dark')}",
            "width": theme_meta("logo_w"),
            "height": theme_meta("logo_h"),
            "caption": cfg["site"]["brand"],
        },
        {
            "@type": "ImageObject",
            "@id": f"{domain}/#heroimage",
            "url": hero,
            "contentUrl": hero,
            "width": 1920,
            "height": 1080,
            "caption": t["og_image_alt"],
        },
        {
            # LocalBusiness + SportsActivityLocation, damit sowohl die lokale
            # Suche als auch Sport- und Freizeitverzeichnisse zugreifen koennen.
            "@type": ["LocalBusiness", "SportsActivityLocation"],
            "@id": f"{domain}/#business",
            "name": cfg["site"]["brand"],
            "alternateName": "Run & See",
            "description": t["meta_description"],
            "slogan": t["hero"]["h1"],
            "url": url_for(cfg, lang),
            "image": {"@id": f"{domain}/#heroimage"},
            "logo": {"@id": f"{domain}/#logo"},
            "sameAs": same_as,
            "email": cfg["site"]["contact_email"],
            "founder": {"@id": f"{domain}/#guide"},
            "foundingDate": str(cfg["site"]["established"]),
            "address": {
                "@type": "PostalAddress",
                "addressLocality": "Luzern",
                "addressRegion": "LU",
                "addressCountry": "CH",
            },
            "geo": {"@type": "GeoCoordinates", "latitude": mp["lat"], "longitude": mp["lon"]},
            "areaServed": [
                {"@type": "City", "name": "Lucerne"},
                {"@type": "AdministrativeArea", "name": "Central Switzerland"},
            ],
            "knowsLanguage": langs,
            "availableLanguage": langs,
            "isAccessibleForFree": True,
            "priceRange": "Free",
            "currenciesAccepted": "CHF",
            "keywords": (
                "running tour Lucerne, guided run Lucerne, free running tour Switzerland, "
                "sightseeing run Lucerne, Lauftour Luzern, running with a local Lucerne"
            ),
            "hasOfferCatalog": {"@id": f"{domain}/#tours"},
            "potentialAction": {
                "@type": "ReserveAction",
                "name": t["join"]["form_heading"],
                "target": url_for(cfg, lang) + "#join",
            },
        },
        {
            "@type": "OfferCatalog",
            "@id": f"{domain}/#tours",
            "name": t["tours_section"]["heading"],
            "numberOfItems": len(content["tours"]),
            "itemListElement": [
                {
                    "@type": "Offer",
                    "position": n + 1,
                    "price": "0",
                    "priceCurrency": "CHF",
                    "availability": "https://schema.org/InStock",
                    "url": url_for(cfg, lang) + f"#tour-{tour['id']}",
                    "itemOffered": {"@id": f"{domain}/#tour-{tour['id']}"},
                }
                for n, tour in enumerate(content["tours"])
            ],
        },
        {
            "@type": "WebSite",
            "@id": f"{domain}/#website",
            "url": domain + "/",
            "name": cfg["site"]["brand"],
            "inLanguage": langs,
            "publisher": {"@id": f"{domain}/#business"},
        },
        {
            "@type": "WebPage",
            "@id": url_for(cfg, lang) + "#webpage",
            "url": url_for(cfg, lang),
            "name": t["meta_title"],
            "description": t["meta_description"],
            "inLanguage": lang,
            "isPartOf": {"@id": f"{domain}/#website"},
            "about": {"@id": f"{domain}/#business"},
            "primaryImageOfPage": {"@id": f"{domain}/#heroimage"},
            "significantLink": url_for(cfg, lang) + "#join",
        },
        {
            "@type": "Person",
            "@id": f"{domain}/#guide",
            "name": "Philippe",
            "jobTitle": t["about"]["heading"],
            "description": t["about"]["text"],
            "knowsLanguage": langs,
            "homeLocation": {"@type": "City", "name": "Lucerne"},
            "worksFor": {"@id": f"{domain}/#business"},
        },
        {
            "@type": "FAQPage",
            "@id": f"{url_for(cfg, lang)}#faq",
            "inLanguage": lang,
            "isPartOf": {"@id": url_for(cfg, lang) + "#webpage"},
            "mainEntity": [
                {
                    "@type": "Question",
                    "name": i["q"],
                    "acceptedAnswer": {"@type": "Answer", "text": i["a"]},
                }
                for i in t["faq"]["items"]
            ],
        },
    ]

    for tour in content["tours"]:
        loc = ts_items[tour["id"]]
        graph.append(
            {
                "@type": "TouristTrip",
                "@id": f"{domain}/#tour-{tour['id']}",
                "name": loc["name"],
                "alternateName": loc["tagline"],
                "description": loc["text"],
                "url": url_for(cfg, lang) + f"#tour-{tour['id']}",
                "inLanguage": lang,
                "provider": {"@id": f"{domain}/#business"},
                "image": f"{domain}/assets/images/tours/{tour['image']}.jpg",
                "touristType": ["Runners", "Active travellers", "Business travellers"],
                "isAccessibleForFree": True,
                "additionalProperty": [
                    p for p in [
                        {"@type": "PropertyValue", "name": "Distance", "value": tour["km"]},
                        {"@type": "PropertyValue", "name": "Pace", "value": tour["pace"]} if tour.get("pace") else None,
                        {"@type": "PropertyValue", "name": "Elevation gain", "value": tour["elevation"]} if tour.get("elevation") else None,
                        {"@type": "PropertyValue", "name": "Start times", "value": ", ".join(tour["times"])},
                        {"@type": "PropertyValue", "name": "Level", "value": {
                            "green": t["tours_section"]["level_green"],
                            "orange": t["tours_section"]["level_orange"],
                            "red": t["tours_section"]["level_red"]}[tour["level"]]},
                    ] if p
                ],
                "itinerary": {
                    "@type": "Place",
                    "name": mp["name"],
                    "address": {"@type": "PostalAddress", "addressLocality": "Luzern", "addressCountry": "CH"},
                    "geo": {"@type": "GeoCoordinates", "latitude": mp["lat"], "longitude": mp["lon"]},
                },
                "offers": {
                    "@type": "Offer",
                    "price": "0",
                    "priceCurrency": "CHF",
                    "availability": "https://schema.org/InStock",
                    "url": url_for(cfg, lang) + "#join",
                },
            }
        )

    for r in upcoming_runs(cfg):
        names = run_label(r, ts_items, t["join"]["run_open"])
        start = f"{r['date']}T{r.get('time', '07:45')}:00+02:00"
        graph.append(
            {
                "@type": "Event",
                "@id": f"{domain}/#event-{r['date']}-{r.get('time','').replace(':','')}",
                "name": f"{cfg['site']['brand']} – {names}",
                "startDate": start,
                "eventStatus": "https://schema.org/EventScheduled",
                "eventAttendanceMode": "https://schema.org/OfflineEventAttendanceMode",
                "location": {
                    "@type": "Place",
                    "name": mp["name"],
                    "address": {"@type": "PostalAddress", "addressLocality": "Luzern", "addressCountry": "CH"},
                    "geo": {"@type": "GeoCoordinates", "latitude": mp["lat"], "longitude": mp["lon"]},
                },
                "organizer": {"@id": f"{domain}/#business"},
                "isAccessibleForFree": True,
                "offers": {
                    "@type": "Offer",
                    "price": "0",
                    "priceCurrency": "CHF",
                    "availability": "https://schema.org/InStock",
                    "url": url_for(cfg, lang) + "#join",
                    "validFrom": dt.date.today().isoformat(),
                },
            }
        )

    payload = json.dumps({"@context": "https://schema.org", "@graph": graph}, ensure_ascii=False, indent=2)
    return f'  <script type="application/ld+json">\n{payload}\n  </script>'


def build_home(cfg, content, lang):
    t = content["languages"][lang]
    base = LANG_DIR[lang]
    parts = [
        head(
            cfg, t, lang,
            page="",
            title=t["meta_title"],
            description=t["meta_description"],
            base=base,
            extra_ld=json_ld(cfg, content, t, lang),
        ),
        f'<body>\n<a class="skip-link" href="#main">{E(t["skip_link"])}</a>',
        navbar(cfg, t, lang, base),
        '<main id="main">',
        hero(t, base),
        stats_section(content, t),
        value_section(t),
        tours_section(content, t, base),
        about_section(cfg, t, base),
        practical_section(cfg, t, lang),
        join_section(cfg, content, t, lang, base),
        faq_section(t),
        "</main>",
        sticky_cta(t),
        footer(cfg, t, lang, base, content),
        page_script(cfg, content, t, lang),
        "</body>\n</html>",
    ]
    return "\n".join(parts) + "\n"


def build_legal(cfg, content, lang):
    t = content["languages"][lang]
    lp = t["legal_page"]
    base = LANG_DIR[lang]
    lg = cfg["legal"]
    sections = "\n".join(
        f"    <h3>{E(s['h'])}</h3>\n    <p>{E(s['p'])}</p>" for s in lp["privacy_sections"]
    )
    phone = f"<br />{E(lg['phone'])}" if lg.get("phone") else ""

    # Bildnachweis und Schriftenhinweis — beides gehört ins Impressum,
    # sobald fremde Fotos verwendet werden.
    imgs = cfg.get("images", {})
    credits_block = ""
    if imgs.get("show_in_imprint") and imgs.get("credits"):
        rows = "\n".join(
            f"      <li><code>{E(c.get('file', key))}</code> — {E(c.get('source', ''))}"
            + (f", {E(c['author'])}" if c.get("author") else "")
            + (f" ({E(c['licence'])})" if c.get("licence") else "")
            + "</li>"
            for key, c in imgs["credits"].items()
        )
        credits_block = f"""
    <h2 id="credits">{E(lp['credits_heading'])}</h2>
    <p>{E(lp['credits_intro'])}</p>
    <ul class="credits">
{rows}
    </ul>

    <h3>{E(lp['fonts_heading'])}</h3>
    <p>{E(lp['fonts_text'])}</p>
"""
    body = f"""<body class="legal-page">
<a class="skip-link" href="#main">{E(t['skip_link'])}</a>
{navbar(cfg, t, lang, base, page='legal.html')}
<main id="main">
  <div class="wrap legal-body">
    <a class="legal-back" href="index.html">&larr; {E(lp['back'])}</a>
    <h1>{E(lp['title'])}</h1>

    <h2 id="imprint">{E(lp['imprint_heading'])}</h2>
    <h3>{E(lp['imprint_responsible'])}</h3>
    <address>
      {E(cfg['site']['brand'])}<br />
      {E(lg['operator_name'])}<br />
      {E(lg['address_line'])}<br />
      {E(lg['postal_code'])} {E(lg['city'])}<br />
      {E(lg['country'])}
    </address>
    <h3>{E(lp['contact'])}</h3>
    <p><a href="mailto:{E(lg['email'])}">{E(lg['email'])}</a>{phone}</p>

    <h2>{E(lp['disclaimer_heading'])}</h2>
    <p>{E(lp['disclaimer_text'])}</p>

{credits_block}
    <h2 id="privacy">{E(lp['privacy_heading'])}</h2>
    <p>{E(lp['privacy_intro'])}</p>
{sections}
    <p>{E(lp['privacy_contact'])} <a href="mailto:{E(lg['email'])}">{E(lg['email'])}</a>.</p>
    <p><small>{E(lp['title'])} — {E(lg['last_updated'])}</small></p>
  </div>
</main>
{footer(cfg, t, lang, base, content)}
{page_script(cfg, content, t, lang)}
</body>
</html>
"""
    return head(
        cfg, t, lang,
        page="legal.html",
        title=f"{lp['title']} | {cfg['site']['brand']}",
        description=lp["meta_description"],
        base=base,
    ) + "\n" + body


def build_404(cfg, content):
    """Eigenstaendige Fehlerseite mit absoluten Pfaden — sie kann unter jeder
    beliebigen URL ausgeliefert werden, relative Verweise wuerden dort brechen."""
    css = theme_css()
    langs = "\n".join(
        f'      <a href="/{LANG_DIR[L] + "/" if LANG_DIR[L] else ""}">'
        f'{E(content["languages"][L]["lang_name"])}</a>'
        for L in LANGS
    )
    en = content["languages"]["en"]["notfound"]
    de = content["languages"]["de"]["notfound"]
    fr = content["languages"]["fr"]["notfound"]
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>404 — {E(cfg['site']['brand'])}</title>
  <meta name="robots" content="noindex, follow" />
  <link rel="icon" type="image/svg+xml" href="/{theme_meta('favicon')}" />
  <meta name="theme-color" content="{theme_meta('theme_color')}" />
  <style>
{css}
    .nf {{ min-height: 100svh; display: grid; place-content: center; text-align: center;
           gap: 1.1rem; padding: 2rem; }}
    .nf img {{ height: 56px; width: auto; margin-inline: auto; }}
    .nf .code {{ font-family: var(--font-mono); font-size: 0.78rem; letter-spacing: 0.2em;
                 text-transform: uppercase; color: var(--accent-ink); }}
    .nf h1 {{ font-size: clamp(1.9rem, 5vw, 2.9rem); }}
    .nf p {{ color: var(--ink-soft); max-width: 30rem; margin-inline: auto; }}
    .nf p + p {{ margin-top: -0.5rem; font-size: 0.95rem; }}
    .nf .btn {{ justify-self: center; margin-top: 0.6rem; }}
    .nf .langs {{ display: flex; gap: 1rem; justify-content: center; margin-top: 1.6rem;
                  font-size: 0.9rem; }}
  </style>
</head>
<body>
  <div class="nf">
    <img src="/{theme_meta('logo_dark')}" alt="{E(cfg['site']['brand'])}"
         width="{theme_meta('logo_w')}" height="{theme_meta('logo_h')}" />
    <p class="code">Error 404</p>
    <h1>{E(en['title'])}</h1>
    <p>{E(en['text'])}</p>
    <p>{E(de['text'])}<br />{E(fr['text'])}</p>
    <a class="btn btn-primary" href="/">{E(en['cta'])}</a>
    <div class="langs">
{langs}
    </div>
  </div>
</body>
</html>
"""


def build_sitemap(cfg, content):
    today = dt.date.today().isoformat()
    domain = cfg["site"]["domain"].rstrip("/")
    entries = []
    for page in ["", "legal.html"]:
        for lang in LANGS:
            alts = "\n".join(
                f'    <xhtml:link rel="alternate" hreflang="{L}" href="{url_for(cfg, L, page)}" />'
                for L in LANGS
            )
            prio = "1.0" if page == "" and lang == "en" else ("0.8" if page == "" else "0.3")
            # Bilder nur bei der Startseite melden — die Rechtsseite hat keine.
            images = ""
            if page == "":
                t = content["languages"][lang]
                items = [(
                    f"{domain}/assets/images/hero/luzern-kapellbruecke.jpg",
                    t["og_image_alt"],
                )]
                for tour in content["tours"]:
                    loc = t["tours_section"]["items"][tour["id"]]
                    items.append((
                        f"{domain}/assets/images/tours/{tour['image']}.jpg",
                        f"{loc['name']} — {loc.get('image_alt', loc['tagline'])}",
                    ))
                images = "\n" + "\n".join(
                    f"    <image:image>\n"
                    f"      <image:loc>{u}</image:loc>\n"
                    f"      <image:title>{html.escape(cap)}</image:title>\n"
                    f"    </image:image>"
                    for u, cap in items
                )
            entries.append(
                f"""  <url>
    <loc>{url_for(cfg, lang, page)}</loc>
    <lastmod>{today}</lastmod>
    <priority>{prio}</priority>
{alts}
    <xhtml:link rel="alternate" hreflang="x-default" href="{url_for(cfg, 'en', page)}" />{images}
  </url>"""
            )
    return (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"\n'
        '        xmlns:xhtml="http://www.w3.org/1999/xhtml"\n'
        '        xmlns:image="http://www.google.com/schemas/sitemap-image/1.1">\n'
        + "\n".join(entries)
        + "\n</urlset>\n"
    )


def build_robots(cfg):
    domain = cfg["site"]["domain"].rstrip("/")
    return f"""# Run & See Lucerne
# Die Seite soll gefunden werden — von Suchmaschinen und von KI-Assistenten.
# Alles ist bewusst freigegeben. Wer einzelne Bots aussperren will, ergaenzt
# hier einen Block mit Disallow; robots.txt ist allerdings nur eine Bitte,
# keine technische Sperre.

User-agent: *
Allow: /

# Klassische Suche
User-agent: Googlebot
Allow: /
User-agent: Bingbot
Allow: /

# KI-Assistenten, die live abrufen und Quellen verlinken.
# Diese ausdruecklich zuzulassen ist die Voraussetzung dafuer, in Antworten
# auf Fragen wie "free running tour Lucerne" ueberhaupt zitiert zu werden.
User-agent: OAI-SearchBot
Allow: /
User-agent: ChatGPT-User
Allow: /
User-agent: Claude-SearchBot
Allow: /
User-agent: Claude-User
Allow: /
User-agent: PerplexityBot
Allow: /
User-agent: Perplexity-User
Allow: /
User-agent: Google-Extended
Allow: /

# Trainings-Crawler. Ebenfalls erlaubt — bei einem kostenlosen Angebot ohne
# schuetzenswerte Inhalte ueberwiegt die Sichtbarkeit. Zum Aussperren
# "Allow: /" durch "Disallow: /" ersetzen.
User-agent: GPTBot
Allow: /
User-agent: ClaudeBot
Allow: /
User-agent: CCBot
Allow: /

Sitemap: {domain}/sitemap.xml
"""


def build_llms_txt(cfg, content):
    """Kurzfassung der Seite fuer KI-Assistenten (llms.txt).

    Der Vorschlag ist Stand August 2026 nicht standardisiert und wird von den
    grossen Crawlern kaum abgerufen — sie lesen das HTML. Die Datei kostet aber
    nichts und schadet nicht, deshalb liegt sie bei.
    """
    domain = cfg["site"]["domain"].rstrip("/")
    t = content["languages"]["en"]
    ts = t["tours_section"]["items"]
    mp = cfg["meeting_point"]

    tours = []
    for tour in content["tours"]:
        loc = ts[tour["id"]]
        facts = [tour["km"]]
        if tour.get("pace"):
            facts.append(tour["pace"])
        if tour.get("elevation"):
            facts.append(tour["elevation"])
        facts.append("start " + " / ".join(tour["times"]))
        tours.append(
            f"- [{loc['name']}]({domain}/#tour-{tour['id']}): {loc['text']} "
            f"({'; '.join(facts)})"
        )

    faq = "\n".join(f"- **{i['q']}** {i['a']}" for i in t["faq"]["items"])
    runs = upcoming_runs(cfg)
    if runs:
        dates = "\n".join(
            f"- {r['date']} at {r.get('time', '')}" for r in runs
        )
    else:
        dates = "- No dates published at the moment. Visitors can leave an email address to be notified."

    return f"""# {cfg['site']['brand']}

> Free guided running tours through Lucerne, Switzerland. Small groups, four
> routes, led by a local runner. No charge, no booking fee. Guided in English,
> German, Swiss German and French. All levels welcome.

Run & See Lucerne is not a commercial tour operator. Runs are free of charge;
tips are welcome but never expected. Groups are deliberately small and always
run at the pace of the slowest participant. Meeting point is the
{mp['name']} in the centre of Lucerne ({mp['lat']}, {mp['lon']}).

## Tours

{chr(10).join(tours)}

## Upcoming dates

{dates}

## Practical

- Price: free (CHF 0). Tipping optional.
- Languages: English, German, Swiss German, French.
- Meeting point: {mp['name']}, Lucerne — {mp['detail_en']}
- Booking: sign-up form at {domain}/#join
- Runs happen in any weather except genuinely unsafe conditions.

## Frequently asked questions

{faq}

## Pages

- [Home, English]({domain}/)
- [Startseite, Deutsch]({domain}/de/)
- [Accueil, Français]({domain}/fr/)
- [Imprint and privacy]({domain}/legal.html)

## Contact

{cfg['site']['contact_email']} · {cfg['site']['instagram_url']}
"""


def check_todos(cfg) -> list[str]:
    warnings = []
    blob = json.dumps(cfg, ensure_ascii=False)
    found = {m for m in re.findall(r"TODO_[^\"\s]+", blob) if m != "TODO_"}
    for m in sorted(found):
        warnings.append(f"Platzhalter in src/config.json noch nicht ersetzt: {m}")
    if not cfg["schedule"].get("runs"):
        warnings.append(
            "Keine Termine in src/config.json -> die Seite zeigt den 'Termine folgen'-Zustand."
        )
    if cfg["form"]["provider"] == "mailto":
        warnings.append(
            "Formular laeuft im mailto-Modus (oeffnet das Mailprogramm des Besuchers). "
            "Fuer echte Zustellung provider auf 'formspree' setzen und Endpoint eintragen."
        )
    return warnings


def build_site(cfg, content, target: Path, *, theme: str, asset_prefix: str,
               with_sitemap: bool) -> list[str]:
    """Erzeugt eine komplette dreisprachige Site unterhalb von `target`."""
    BUILD["theme"] = theme
    BUILD["asset_prefix"] = asset_prefix

    written = []
    for lang in LANGS:
        d = LANG_DIR[lang]
        outdir = target / d if d else target
        outdir.mkdir(parents=True, exist_ok=True)
        (outdir / "index.html").write_text(build_home(cfg, content, lang), encoding="utf-8")
        (outdir / "legal.html").write_text(build_legal(cfg, content, lang), encoding="utf-8")
        pre = f"{d}/" if d else ""
        written += [pre + "index.html", pre + "legal.html"]

    if with_sitemap:
        (target / "sitemap.xml").write_text(build_sitemap(cfg, content), encoding="utf-8")
        (target / "llms.txt").write_text(build_llms_txt(cfg, content), encoding="utf-8")
        (target / "404.html").write_text(build_404(cfg, content), encoding="utf-8")
        (target / "robots.txt").write_text(build_robots(cfg), encoding="utf-8")
        written += ["sitemap.xml", "robots.txt", "llms.txt", "404.html"]
    return written


PREVIEW_THEMES = ["tempo"]


def build_preview_index(cfg) -> str:
    """Kleine Auswahlseite, die beide Entwürfe nebeneinander verlinkt."""
    cards = []
    for name in PREVIEW_THEMES:
        m = THEMES[name]
        cards.append(f"""    <a class="opt" href="{name}/index.html">
      <span class="sw"><i style="background:{m['theme_color']}"></i></span>
      <h2>{E(name.capitalize())}</h2>
      <p>{E(m['label'])}</p>
      <span class="go">Entwurf ansehen &rarr;</span>
    </a>""")
    return f"""<!DOCTYPE html>
<html lang="de">
<head>
<meta charset="utf-8" />
<meta name="viewport" content="width=device-width, initial-scale=1" />
<title>Design-Entwürfe · {E(cfg['site']['brand'])}</title>
<meta name="robots" content="noindex" />
<style>
  * {{ box-sizing: border-box; margin: 0; padding: 0; }}
  body {{ font-family: system-ui, -apple-system, "Segoe UI", sans-serif; background: #f4f2ee;
         color: #1c1c1c; display: grid; place-items: center; min-height: 100svh; padding: 2rem; }}
  .wrap {{ max-width: 780px; width: 100%; }}
  h1 {{ font-size: clamp(1.6rem, 4vw, 2.3rem); margin-bottom: 0.5rem; }}
  .sub {{ color: #5c6470; margin-bottom: 2.5rem; }}
  .grid {{ display: grid; gap: 1.25rem; grid-template-columns: repeat(auto-fit, minmax(260px, 1fr)); }}
  .opt {{ display: block; background: #fff; border: 1px solid rgb(0 0 0 / 0.1); border-radius: 14px;
          padding: 1.6rem; text-decoration: none; color: inherit;
          transition: transform .2s ease, box-shadow .2s ease; }}
  .opt:hover {{ transform: translateY(-3px); box-shadow: 0 12px 32px rgb(0 0 0 / 0.1); }}
  .sw {{ display: flex; gap: .35rem; margin-bottom: 1rem; }}
  .sw i {{ width: 26px; height: 26px; border-radius: 7px; display: block; }}
  .opt h2 {{ font-size: 1.3rem; margin-bottom: .3rem; }}
  .opt p {{ color: #5c6470; font-size: .93rem; }}
  .go {{ display: inline-block; margin-top: 1.1rem; font-weight: 600; font-size: .9rem; color: #1f6f6f; }}
  .note {{ margin-top: 2.5rem; font-size: .85rem; color: #6b7280; line-height: 1.6; }}
</style>
</head>
<body>
  <div class="wrap">
    <h1>Zwei Design-Entwürfe</h1>
    <p class="sub">Beide zeigen dieselbe Website mit identischem Inhalt in drei Sprachen —
       nur Farbe, Form, Typografie und Logo unterscheiden sich.</p>
    <div class="grid">
{chr(10).join(cards)}
    </div>
    <p class="note">Diese Vorschau ist nicht Teil der produktiven Seite und wird nicht
       indexiert. Sobald du dich entschieden hast: <code>"theme"</code> in
       <code>src/config.json</code> setzen und <code>python3 build.py</code> ausführen.</p>
  </div>
</body>
</html>
"""


def main():
    ap = argparse.ArgumentParser(description="Run & See — Static-Site-Generator")
    ap.add_argument("--theme", choices=sorted(THEMES), default=None,
                    help="Theme für die produktive Seite (überschreibt config.json)")
    ap.add_argument("--previews", action="store_true",
                    help="zusätzlich preview/<theme>/ für alle Entwürfe erzeugen")
    ap.add_argument("--only-previews", action="store_true",
                    help="nur die Vorschauen bauen, produktive Seite unverändert lassen")
    args = ap.parse_args()

    cfg = json.loads((SRC / "config.json").read_text(encoding="utf-8"))
    content = json.loads((SRC / "content.json").read_text(encoding="utf-8"))

    theme = args.theme or cfg["site"].get("theme", "horizont")
    if theme not in THEMES:
        raise SystemExit(f"Unbekanntes Theme '{theme}'. Verfügbar: {', '.join(sorted(THEMES))}")

    if not args.only_previews:
        written = build_site(cfg, content, ROOT, theme=theme,
                             asset_prefix="", with_sitemap=True)
        print(f"Produktive Seite  ·  Theme: {theme} ({THEMES[theme]['label']})")
        for w in written:
            print("   ", w)

    if args.previews or args.only_previews:
        prev_root = ROOT / "preview"
        prev_root.mkdir(exist_ok=True)
        print("\nVorschauen:")
        for name in PREVIEW_THEMES:
            target = prev_root / name
            if target.exists():
                shutil.rmtree(target)
            build_site(cfg, content, target, theme=name,
                       asset_prefix="../../", with_sitemap=False)
            print(f"    preview/{name}/index.html   ({THEMES[name]['label']})")
        (prev_root / "index.html").write_text(build_preview_index(cfg), encoding="utf-8")
        print("    preview/index.html            (Auswahlseite)")

    warn = check_todos(cfg)
    if warn:
        print("\nOffene Punkte:")
        for w in warn:
            print("  ! " + w)


if __name__ == "__main__":
    main()
