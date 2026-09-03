# Zwei Design-Entwürfe und was sich sonst bewegt

Stand: 1. August 2026 · **Entschieden: Horizont ist produktiv.**

Tempo bleibt als Vergleich unter `preview/tempo/` erhalten und lässt sich jederzeit
über `site.theme` in `src/config.json` zurückholen.

Beide Entwürfe zeigen **dieselbe Website mit identischem Inhalt** in drei Sprachen.
Unterschiedlich sind nur Farbe, Form, Typografie, Logo und die Art der Bewegung.

Ansehen:

```bash
python3 build.py --previews
```

Dann `preview/index.html` im Browser öffnen — dort sind beide Entwürfe verlinkt.
Die produktive Seite im Projekt-Root bleibt davon unberührt.

Entscheidung übernehmen: in `src/config.json` unter `site.theme` `"horizont"` oder
`"tempo"` eintragen und `python3 build.py` ausführen.

---

## 01 — Horizont

Weiterentwicklung deiner Logo-Option „Horizont". Sonne über zwei Bergen, gespiegelt
im See.

| | |
|---|---|
| Navy | `#163E5C` — Fundament, Überschriften, Fusszeile |
| Sonnenorange | `#F2683C` — Aktion, Akzent, das kaufmännische Und |
| Eisblau | `#EAF1F4` — Wasser, ruhige Flächen |
| Sand | `#FBF9F5` — Grundfläche |

**Charakter:** ruhig, warm, offen. Runde Formen durchgehend — Radien von 10 bis 20 px,
Buttons als Pillen, Schrittzahlen als Kreise mit hellem Ring. Grosszügiger Weissraum,
gemischte Gross-/Kleinschreibung, weiche Verläufe statt harter Kanten.

**Aus dem Logo abgeleitet:** die Sektionsmarke über jeder Überschrift ist das
Sonne-über-Berg-Motiv in Miniatur — dasselbe Zeichen wie im Logo, auf 44 × 22 px
reduziert. Unter dem Hero läuft ein weicher Verlauf ins Sandfarbene aus, wie eine
Dunstschicht über dem See.

**Bewegung:** das Hero-Bild zoomt über 26 Sekunden fast unmerklich von 107 % auf 100 %.
Sonst nur ruhiges Einblenden.

**Logo:** kreisförmige Bildmarke plus Wortmarke, hell und dunkel
(`assets/logos/horizont-lockup-*.svg`, Bildmarke allein als `horizont-mark.svg`).

---

## 02 — Tempo

Weiterentwicklung deiner Logo-Option „Tempo". Wortmarke mit Speed-Linien, keine
Bildmarke.

| | |
|---|---|
| Tinte | `#181613` — Text, Rahmen, Kennzahlenband, Fusszeile |
| Signal | `#FF5630` — Aktion, Akzent, Speed-Linien |
| Papier | `#FFFFFF` / `#F6F4F1` — Flächen |

**Charakter:** redaktionell, kantig, hoher Kontrast. Radien praktisch bei null,
Überschriften in schweren Versalien mit enger Laufweite, Rahmen in 1,5 bis 2 px
Tinte statt weicher Schatten. Karten werfen einen harten Versatzschatten in Tinte,
die Formularkarte einen in Signal.

**Aus dem Logo abgeleitet:** die Sektionsmarke sind zwei gestaffelte Signal-Balken —
dieselben Speed-Linien wie im Logo. Sie wachsen von links ein, wenn die Sektion in
den Blick kommt.

**Bewegung:** die Hero-Zeilen fahren einzeln von unten ein, gestaffelt um je 0,1 s. Links neben der Hero-Spalte steht eine Signal-Kante.

**Logo:** reine Wortmarke mit Speed-Linien, hell und dunkel
(`assets/logos/tempo-lockup-*.svg`, Marke allein als `tempo-mark.svg`).

---

## Was in beiden Entwürfen neu ist

**Touren-Karussell.** Die vier Routen liegen in einer Spur mit Scroll-Snap. Auf dem
Desktop sind drei sichtbar, die vierte lugt hervor — das signalisiert, dass es
weitergeht. Auf dem Handy eine Karte plus Anschnitt. Pfeile und Fortschrittsbalken
darunter, Pfeile deaktivieren sich am Anfang und Ende. Bedienbar per Maus, Wischen,
Tastatur (Pfeiltasten) und Fortschrittsbalken. Ohne JavaScript bleibt es eine
wischbare Spur — nur die Pfeile fehlen dann.

**Kennzahlenband** mit vier Zahlen, die beim Erscheinen hochzählen: 4 Routen · CHF 0 ·
4 Sprachen · 300 m maximale Höhenmeter. Alles belegte Angaben, nichts erfunden.

**Verbindungslinie im Ablauf.** Zwischen den vier Schritten zeichnet sich eine
gestrichelte Linie von links nach rechts — die Laufstrecke als Bild. Nur auf
Bildschirmen ab 860 px sichtbar.

**Einblenden beim Scrollen.** Abschnitte steigen 18 px auf und blenden ein, Kacheln
gestaffelt um je 90 ms. Bewusst zurückhaltend.

**Sticky-Leiste auf dem Handy.** Sobald der Hero durchgescrollt ist, erscheint unten
ein Balken mit „Gratis · Kleine Gruppen" und der Anmelde-Schaltfläche. Sie
verschwindet wieder, sobald das Formular selbst im Bild ist.

**Aktiver Navigationspunkt.** Der Menüpunkt des Abschnitts, in dem du dich gerade
befindest, bekommt einen Unterstrich.

**Kleinigkeiten:** Pfeile in Buttons rücken beim Darüberfahren nach rechts, Tourbilder
zoomen sanft, FAQ-Antworten fahren in der Höhe auf statt zu springen, der Punkt im
Hero-Etikett pulsiert langsam, unter dem Hero zeigt ein Pfeil nach unten.

**Alles davon schaltet sich ab**, wenn im Betriebssystem „Bewegung reduzieren"
aktiviert ist. Geprüft: dann sind alle Abschnitte sofort sichtbar und die Zahlen
stehen direkt auf dem Endwert.

---

## Was geprüft ist — und was nicht

Beide Entwürfe wurden in einem echten Chromium gerendert und angesehen, in drei
Sprachen, bei 1440, 1024, 760 und 390 px Breite. Geprüft und behoben:

- kein horizontales Scrollen auf keiner Breite
- keine Fehler in der Browser-Konsole
- keine kaputten Bildverweise
- HTML-Struktur sauber, keine doppelten IDs, JSON-LD gültig
- Karussell scrollt, Pfeile und Fortschrittsbalken synchron, Tastatur funktioniert
- mobiles Menü öffnet und schliesst sauber, `aria-expanded` stimmt
- Modus „Bewegung reduzieren" funktioniert

Dabei gefunden und korrigiert: das Karussell scrollte nicht (Spalten schrumpften,
bis alle vier hineinpassten), die Theme-Regeln wurden von der Basis überschrieben,
die Kennzahlen erbten die Schriftgrösse ihrer Beschriftung, und das mobile Menü lugte
im geschlossenen Zustand oben ins Bild.

**Nicht geprüft:** Safari und Firefox. Gerendert wurde nur in Chromium. Und die
Schriften — siehe unten.

## Zur Schrift

Deine Logo-Vorlage nutzt **Space Grotesk** für „Horizont" und eine schwere Grotesk
für „Tempo". Beide Entwürfe verwenden stattdessen Systemschriften, weil die Seite
bewusst keine externen Anfragen stellt (kein Google Fonts, siehe Datenschutzerklärung)
und ich die Schriftdateien hier nicht selbst herunterladen konnte.

Das heisst: **die Entwürfe sehen auf deinem Rechner leicht anders aus als in der
PowerPoint.** Horizont nutzt Avenir Next (macOS) bzw. Segoe UI (Windows), Tempo nutzt
Helvetica bzw. Arial in Schnitt 900. Für Tempo ist das nah dran — die Vorlage selbst
verwendet Arial Bold. Für Horizont fehlt der Space-Grotesk-Charakter.

Space Grotesk nachrüsten, ohne den Datenschutz aufzugeben:

1. Schrift von der offiziellen Quelle als WOFF2 herunterladen
2. Dateien nach `assets/fonts/` legen
3. In `src/themes/horizont.css` `@font-face`-Regeln ergänzen und
   `--font-display` / `--font-body` auf `"Space Grotesk"` umstellen

Damit bleibt alles lokal ausgeliefert und die Aussage in der Datenschutzerklärung
(„Die Webschriften werden vom eigenen Server ausgeliefert") stimmt weiterhin.


---

## Änderungen vom 1. August 2026

Nach der Entscheidung für Horizont umgesetzt:

- **Horizont produktiv**, Tempo bleibt als Vorschau erhalten.
- **Laufband ersatzlos gestrichen** — samt der zugehörigen CSS-Regeln und
  Textbausteine, nicht nur ausgeblendet.
- **Logo entzerrt.** Die `width`- und `height`-Attribute im HTML standen auf
  160 × 42, das SVG hat aber 268 × 64. Da die Kopfzeile die Höhe vorgibt und die
  Breite automatisch berechnet, stauchte der Browser das Logo um rund 9 Prozent.
  Die Masse kommen jetzt pro Theme aus `build.py` und entsprechen dem viewBox.
- **Drei Sektionen zu einer zusammengelegt:** Ablauf, Treffpunkt und „Gut zu wissen"
  bilden jetzt „Bevor es losgeht" — die vier Schritte oben, darunter zweispaltig
  Karte und Hinweise.
- **Dein Guide nach oben**, an dritte Stelle. Neue Reihenfolge:
  Hero → Kennzahlen → Warum laufen → Dein Guide → Touren → Bevor es losgeht →
  Nächste Runs → FAQ.
- **Redundanzen entfernt.** „Gut zu wissen" ist von sechs auf zwei Punkte
  geschrumpft; gratis, kleine Gruppen, Ausrüstung, Kaffee und Wetter standen
  jeweils drei- bis viermal auf der Seite und stehen jetzt noch einmal in den
  Nutzenargumenten und einmal im FAQ. Zusätzlich gekürzt: Hero-Zusatzzeile
  entfernt, Nutzenargumente, Tour-Einleitung und Anmelde-Einleitung gestrafft.
- **Fusszeile gekürzt:** „Alle Rechte vorbehalten" und der Cookie-Hinweis sind raus,
  übrig bleiben Copyright und Gründungsjahr.
- **Gegründet 2026** statt 2025.

Die Startseite ist dadurch von 8157 auf 7193 Pixel Höhe geschrumpft, rund zwölf
Prozent kürzer — bei gleichem Informationsgehalt.

### Korrigierte Angaben

| | vorher | jetzt |
|---|---|---|
| Good Morning Scenic Run, Start | 07:45 | **07:15** |
| Hidden Gems Run, Distanz | 8–9 km | **7–8 km** |

**Eine abgeleitete Änderung, die du prüfen solltest:** die Beschreibung des Good
Morning Scenic Run nannte „zurück gegen 08:30". Mit Start um 07:15 und 5–6 km bei
6:00–6:30 min/km ergibt das rechnerisch eher 08:00, und darauf habe ich den Text
geändert. Falls unterwegs länger gehalten wird, gehört dort ein anderer Wert hin —
`src/content.json`, `tours_section.items.morning.text` in allen drei Sprachen.
