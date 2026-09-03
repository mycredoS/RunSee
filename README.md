# Run & See Lucerne — Website

Kostenlose geführte Lauftouren in Luzern. Statische Website in drei Sprachen
(Englisch, Deutsch, Französisch). Kein Baukasten, kein Redaktionssystem, keine
laufenden Kosten — nur Dateien, die jeder Webhoster ausliefern kann.

---

## Die Seite anschauen

**Doppelklick auf `index.html`.** Das reicht. Die Seite öffnet sich im Browser und
funktioniert vollständig: Sprachumschalter, Touren-Karussell, Formular, Karte.
Es braucht keinen Server und keine Internetverbindung — ausser für die
Google-Maps-Karte, die ohnehin erst nach einem Klick lädt.

`index.html` ist die englische Fassung. Über den Umschalter oben rechts (EN · DE · FR)
kommst du zu den anderen. Direkt aufrufen kannst du sie auch:

| | |
|---|---|
| `index.html` | Englisch — die Hauptfassung |
| `de/index.html` | Deutsch |
| `fr/index.html` | Französisch |
| `legal.html` | Impressum und Datenschutz (je Sprache im gleichen Ordner) |

Ein Hinweis: beim Öffnen als Datei steht in der Adresszeile `file:///...` statt
`https://www.runandsee.ch`. Das ist normal und ändert nichts am Aussehen.

---

## Der wichtigste Grundsatz

**Die HTML-Dateien werden erzeugt, nicht geschrieben.**

`index.html`, `de/index.html`, `fr/index.html` und die drei `legal.html` entstehen
aus den Quelldateien im Ordner `src/`. Wer sie direkt bearbeitet, verliert seine
Änderungen beim nächsten Build.

Der Grund: drei Sprachen von Hand synchron zu halten funktioniert ein paar Wochen
lang, danach nicht mehr. So wird jeder Text genau einmal gepflegt.

Nach jeder Änderung an `src/`:

```bash
python3 build.py
```

Das dauert unter einer Sekunde und schreibt alle sechs Seiten neu. Am Ende listet
der Befehl unter „Offene Punkte" auf, was vor dem Live-Gang noch fehlt.

---

## Wo liegt was

```
📄 README.md            diese Datei
📄 CLAUDE.md            Arbeitsanweisungen für Claude Code
📄 build.py             der Generator — erzeugt alle Seiten

📁 src/                 ► HIER WIRD GEARBEITET
   config.json          Termine, Kontakt, Impressumsdaten, Formular, Theme
   content.json         sämtliche Texte in EN / DE / FR
   base.css             Layout und Komponenten (keine Farben)
   themes/
      horizont.css      das aktive Erscheinungsbild
      tempo.css         der Alternativentwurf, jederzeit umschaltbar

📁 input_pk/            ► DEINE UNTERLAGEN
   Word-Dokument, PowerPoint, Notizen — alles was von dir kommt.
   Wird nie überschrieben und nie veröffentlicht.

📁 docs/                ► DOKUMENTATION
   RECHTE.md            Schriften, Bilder, Datenschutz — was du klären musst
   SEO-UND-BEFUND.md    Stärken/Schwächen und die Auffindbarkeit
   RUECKMELDUNG.md      Befunde am alten Stand und die offenen Entscheidungen
   DESIGN.md            beide Entwürfe, Farben, Bewegung, was geprüft wurde
   INSTAGRAM.md         Profil, Redaktionsplan, erste zwölf Posts

📁 assets/              ► BILDER UND LOGOS
   images/_originals/   deine Originalfotos, unangetastet
   images/hero|tours|team/   die fürs Web optimierten Fassungen (erzeugt)
   logos/               Logos als SVG

📁 tools/
   optimize_images.py   erzeugt die Webfassungen aus den Originalen
   make_logo.py         erzeugt die Logo-Dateien als SVG-Pfade

📁 de/  📁 fr/          erzeugte Sprachfassungen — nicht bearbeiten
📄 index.html           erzeugt — nicht bearbeiten
📄 legal.html           erzeugt — nicht bearbeiten
📄 sitemap.xml          erzeugt — für Google, inkl. Bildverzeichnis
📄 robots.txt           erzeugt — erlaubt Such- und KI-Crawler ausdrücklich
📄 llms.txt             erzeugt — Kurzfassung der Seite für KI-Assistenten
📄 404.html             erzeugt — Fehlerseite in drei Sprachen
```

---

## Was du wo änderst

| Ich will ändern … | … in dieser Datei |
|---|---|
| Einen Text, eine FAQ-Antwort, eine Tourbeschreibung | `src/content.json` |
| Distanzen, Startzeiten, Schwierigkeitsgrade | `src/content.json` → `tours` |
| Die nächsten Lauftermine | `src/config.json` → `schedule.runs` |
| E-Mail-Adresse, Instagram, Impressumsangaben | `src/config.json` |
| Wohin das Anmeldeformular geht | `src/config.json` → `form` |
| Farben, Rundungen, Schriften | `src/themes/horizont.css` |
| Abstände, Raster, Komponenten | `src/base.css` |
| Eine neue Sektion, die Struktur einer Seite | `build.py` |
| Ein neues Foto | Original nach `assets/images/_originals/`, dann `python3 tools/optimize_images.py` |
| Farbstich eines Fotos | `tools/optimize_images.py` → `JOBS`, Faktoren (rot, grün, blau) |
| Das Logo | `tools/make_logo.py`, danach `python3 tools/make_logo.py` |
| Herkunft eines Fotos (Bildnachweis) | `src/config.json` → `images.credits` |

**Immer daran denken:** danach `python3 build.py` ausführen.

### Termine eintragen

In `src/config.json`:

```json
"schedule": {
  "runs": [
    { "date": "2026-08-06", "time": "07:15", "tours": ["morning"] },
    { "date": "2026-08-06", "time": "17:30", "tours": ["heritage", "hidden", "views"] }
  ]
}
```

Vergangene Termine blendet die Seite von selbst aus. Ist die Liste leer, zeigt sie
„Termine folgen" und sammelt stattdessen E-Mail-Adressen.

Die Kürzel für `tours` sind `morning`, `heritage`, `hidden` und `views`.

---

## Aufbau der Startseite

1. **Hero** — Bild, Versprechen, zwei Schaltflächen
2. **Kennzahlen** — 4 Routen · CHF 0 · 4 Sprachen · 300 Höhenmeter
3. **Warum laufen statt spazieren** — die vier Nutzenargumente
4. **Wähle deinen Run** — die vier Touren
5. **Dein Guide** — Foto und Vorstellung
6. **Bevor es losgeht** — Ablauf in vier Schritten, Treffpunkt mit Karte, praktische Hinweise
7. **Nächste Runs** — Termine, Countdown, Anmeldeformular
8. **Häufige Fragen** — zehn Einträge, wichtig für Google und KI-Suche
9. **Fusszeile** — Seitenlinks, Impressum, Sprachen

---

## Zwei Dinge, die bewusst so gebaut sind

**Keine externen Anfragen.** Keine Google Fonts, kein CDN, kein Analytics.
Die Google-Maps-Karte lädt erst, wenn ein Besucher sie ausdrücklich anklickt.
So verlässt keine IP-Adresse die Seite, ohne dass jemand zugestimmt hat — das ist
der Grund, warum die Datenschutzerklärung so knapp ausfallen kann.

**Keine erfundenen Inhalte.** Keine ausgedachten Kundenstimmen, keine geschätzten
Teilnehmerzahlen, keine Platzhalter-Termine. Fehlt eine Angabe, steht ein
`TODO_`-Vermerk in `src/config.json`, und der Build erinnert dich beim nächsten Lauf
daran.

---

## Bevor die Seite live geht

`python3 build.py` zeigt die Liste. Aktuell offen:

- **Herkunft aller Fotos** in `src/config.json` → `images.credits` eintragen.
  Das ist der wichtigste Punkt — siehe `docs/RECHTE.md`. Bilder mit unklarer
  Herkunft gehören ersetzt, nicht veröffentlicht.
- Impressumsangaben in `src/config.json` (Name, Adresse, E-Mail)
- Anmeldeformular auf ein echtes Backend umstellen — siehe `docs/RUECKMELDUNG.md`, Abschnitt 3c
- Termine eintragen
- Koordinaten des Treffpunkts prüfen
- Versicherungsfrage für die Läufe klären — `docs/RECHTE.md`, Abschnitt 4

Die ausführliche Begründung zu jedem Punkt steht in `docs/RUECKMELDUNG.md`
und `docs/RECHTE.md`.

---

## Den Alternativentwurf ansehen

Der zweite Designentwurf „Tempo" ist erhalten geblieben:

```bash
python3 build.py --previews
```

Erzeugt `preview/tempo/index.html`. Die produktive Seite bleibt unberührt.
Umschalten würdest du über `site.theme` in `src/config.json`.

---

## Voraussetzungen

- **Python 3** — für den Build. Auf macOS und Linux vorinstalliert,
  unter Windows über den Microsoft Store oder python.org.
- **Pillow** — nur für die Bildoptimierung, nicht für den normalen Build:
  `pip install Pillow`

Sonst nichts. Kein Node, kein npm, keine Abhängigkeiten, die veralten.
