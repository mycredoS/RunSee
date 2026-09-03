# Run & See Lucerne — Arbeitsanweisungen

Statische Website für kostenlose geführte Lauftouren in Luzern. Drei Sprachversionen
(EN als Canonical, DE, FR). Kein Framework, kein Node, keine externen Abhängigkeiten
ausser Pillow für die Bildoptimierung.

## Wichtigste Regel

**Die HTML-Dateien im Projekt-Root und in `de/` und `fr/` sind generiert.
Sie werden bei jedem Build überschrieben. Niemals direkt bearbeiten.**

Alle Änderungen gehören in:

| Was ändern | Datei |
|---|---|
| Texte, Übersetzungen, FAQ, Tourbeschreibungen | `src/content.json` |
| Termine, Kontakt, Impressumsdaten, Formular-Backend, aktives Theme | `src/config.json` |
| Layout, Abstände, Komponenten (themeunabhängig) | `src/base.css` |
| Farben, Formen, Typografie eines Entwurfs | `src/themes/<name>.css` |
| HTML-Struktur, neue Sektionen, JSON-LD, JavaScript | `build.py` |
| Bildvarianten, Zuschnitt, Farbkorrektur | `tools/optimize_images.py` |
| Logo-Dateien | `tools/make_logo.py` |

Aktives Theme: **horizont** (`site.theme` in `src/config.json`).

Danach immer:

```bash
python3 build.py              # produktive Seite
python3 build.py --previews   # zusätzlich die Design-Entwürfe unter preview/
```

## Struktur

```
build.py                 Generator: erzeugt alle HTML-Dateien, sitemap.xml, robots.txt
src/config.json          Termine, Kontaktdaten, Formular-Provider, Impressum, Theme
src/content.json         Sämtliche Texte in en / de / fr
src/base.css             Struktur und Komponenten, ohne Farb- und Schriftwerte
src/themes/horizont.css  aktives Erscheinungsbild — See · Sonne · Himmel
src/themes/tempo.css     Alternativentwurf — Tinte · Signal · Weiss
tools/optimize_images.py Erzeugt WebP + JPG in mehreren Breiten aus den Originalen
tools/make_logo.py       Erzeugt die Logo-SVGs; Wortmarke als Pfade, nicht als Text

index.html               generiert · Englisch (Canonical)
de/index.html            generiert · Deutsch
fr/index.html            generiert · Französisch
legal.html               generiert · Impressum + Datenschutz je Sprache
sitemap.xml robots.txt   generiert
llms.txt 404.html        generiert
preview/<theme>/         generiert · Entwürfe zum Vergleichen, noindex, nicht deployen

input_pk/                Unterlagen von Philippe (Briefing, Notizen, Design-Vorlagen)
docs/                    RUECKMELDUNG.md und DESIGN.md — Befunde, offene Punkte, Designbeschrieb
README.md                Einstieg für Philippe: Aufbau, Ordner, Arbeitsweise
assets/images/_originals/  Originalfotos, unverändert, nicht verlinkt
assets/images/{hero,tours,team}/  optimierte Varianten (generiert)
assets/logos/            SVG, handgepflegt
```

## Themes

`build.py` setzt jede Seite aus `src/base.css` **plus** dem Theme-Stylesheet zusammen,
in genau dieser Reihenfolge — das Theme muss die Basis überschreiben können.

`src/base.css` enthält **keine** Farbwerte, Schriftnamen oder Radien. Alles läuft über
Custom Properties, die das Theme in `:root` setzt (`--accent`, `--font-display`,
`--radius`, `--h-transform`, …). Wer in `base.css` einen Hex-Wert einträgt, bricht die
Theme-Trennung.

Neues Theme anlegen: Datei unter `src/themes/` erstellen, alle Tokens aus einem
bestehenden Theme übernehmen, und in `build.py` einen Eintrag im `THEMES`-Dict mit
Logo-, Favicon- und Farbangaben ergänzen.

## Konventionen

- **Keine externen Requests.** Keine Google Fonts, kein CDN, kein Analytics-Snippet.
  Systemschriften über `--font-body` / `--font-display` im jeweiligen Theme.
  Die Google-Maps-Karte lädt erst nach explizitem Klick — dieses Verhalten nicht entfernen.
- **Bildnachweis ist Pflicht.** Jedes Foto braucht einen Eintrag unter
  `images.credits` in `src/config.json` mit Quelle, Urheber und Lizenz. Nie ein
  Bild einbinden, dessen Herkunft nicht dokumentiert ist. Hintergrund in
  `docs/RECHTE.md`.
- **Keine Schriftdateien ausliefern.** Fliesstext nutzt Systemschriften, die
  Wortmarke liegt als Pfad vor. Wer eine Schrift selbst hosten will, muss zuerst
  die Lizenz prüfen — Webfont-Nutzung ist bei vielen Lizenzen nicht gedeckt.
- **Keine erfundenen Inhalte.** Keine Testimonials, Bewertungen, Teilnehmerzahlen oder
  Termine erfinden. Fehlt eine Angabe, wird ein `TODO_`-Platzhalter in `src/config.json`
  gesetzt; `build.py` warnt beim Build darüber.
- **Sprachversionen bleiben synchron.** Jeder neue Text braucht einen Eintrag unter
  `languages.en`, `languages.de` und `languages.fr`. Fehlt einer, bricht der Build mit
  `KeyError` ab — das ist so gewollt.
- **CSS-Variablen statt Hex-Werte** in neuen Regeln.
- **Bilder immer als `<picture>`** mit WebP-Source und JPG/PNG-Fallback, mit `width`,
  `height`, `loading` und `decoding`.
- **Barrierefreiheit:** sichtbarer Fokus, `aria-expanded` am Hamburger-Menü,
  Skip-Link, Bezeichnungen für jedes Formularfeld. Nicht wegoptimieren.
- **Bewegung ist optional.** Jede Animation muss unter
  `@media (prefers-reduced-motion: reduce)` abgeschaltet sein, und jeder Inhalt muss
  ohne JavaScript lesbar bleiben. Das Karussell ist ein natives Scroll-Snap-Element:
  ohne JS lässt es sich immer noch wischen, nur die Pfeile fehlen.
- **Karussell-Spalten mit fester Breite.** `grid-auto-columns` niemals auf
  `minmax(0, …)` oder `1fr` setzen, solange gescrollt werden soll — dann
  schrumpfen die Karten, bis alle hineinpassen. Einzige Ausnahme ist die
  Regel ab 1180 px, wo alle vier Touren bewusst nebeneinander stehen und die
  Steuerung ausgeblendet wird.
- **Karten immer angeschnitten zeigen.** Solange das Karussell scrollt, muss
  die nächste Karte sichtbar hineinragen. Passen alle Karten exakt hinein,
  hält der Besucher es für eine vollständige Liste.
- **Kein SVG-Text im Logo.** Die Wortmarke liegt als Pfad vor. Text im SVG
  hängt von den Schriften des Besuchers ab, und die nötige Breitenkorrektur
  verzerrte einzelne Buchstaben. Änderungen laufen über `tools/make_logo.py`;
  ändert sich die Breite, muss `logo_w` im `THEMES`-Dict mitgezogen werden.

## Nach jeder Änderung prüfen

```bash
python3 build.py          # Build muss ohne Traceback durchlaufen
```

Der Build gibt am Ende unter „Offene Punkte" alle nicht ersetzten `TODO_`-Platzhalter
aus. Diese Liste sollte vor einem Live-Gang leer sein.
