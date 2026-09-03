# Run & See — Rückmeldung zur Website und nächste Schritte

Stand: 30. Juli 2026

---

## 1. Was ich am Bestand gefunden habe

Die alte `index.html` war eine 983-zeilige Einzeldatei. Design und Textgerüst waren
solide, aber es gab acht Probleme, von denen drei die Seite faktisch unbrauchbar
gemacht hätten.

### Blocker

**Das Hero-Bild war nicht sichtbar.** Das CSS verwies auf
`luzern-kapellbruecke.jpg`, die Datei auf der Festplatte hiess
`luzern-kapellbruecke.jpg.jpg`. Ein 404 — die Startseite hatte keinen Hintergrund.

**Das Anmeldeformular hat nie etwas gesendet.** Es trug das Attribut `netlify`
(ohne Wert, damit wirkungslos) und gleichzeitig `onsubmit="return false;"`.
Jeder Klick auf „Send Message" hat den Absendevorgang aktiv abgebrochen. Es gab
keine Rückmeldung an den Besucher, keine Fehlermeldung, kein Ziel.

**Die Seite wog 25 MB an Bildern.** Allein das Hero-Bild 7,6 MB (3852 × 2584 px),
ein Tourbild 9,9 MB. Über Mobilfunk hätte der Aufbau eine halbe Minute und mehr
gedauert. Das ist der teuerste einzelne SEO- und Conversion-Fehler, den eine
kleine Website machen kann.

### Weitere Befunde

**Die Testimonials waren erfunden.** „Amazing experience! — Maria, Spain",
„Best way to explore Lucerne! — James, UK". Ich habe sie entfernt. Erfundene
Kundenstimmen sind in der Schweiz nach UWG Art. 3 Abs. 1 lit. b problematisch, und
sie sind auch als Marketing schwach: drei generische Sätze ohne Foto und ohne
Nachprüfbarkeit senken das Vertrauen eher, als dass sie es heben. Sobald du echte
Rückmeldungen hast, gehören sie an genau diese Stelle zurück — mit Vorname,
Herkunftsland und Datum.

**Die Termine lagen in der Vergangenheit.** Angezeigt wurden Daten im Mai 2026,
heute ist Ende Juli. Ein Besucher hätte gesehen, dass hier seit Monaten nichts
läuft. Termine sind jetzt datengetrieben und werden im Browser automatisch
ausgeblendet, sobald sie vorbei sind.

**Die Mehrsprachigkeit war für Google unsichtbar.** Alle drei Sprachen steckten in
`data-lang-*`-Attributen auf einer einzigen URL, und die drei `hreflang`-Tags zeigten
alle auf dieselbe Adresse. Google konnte die deutsche und französische Fassung nicht
indexieren — sie existierten aus Suchmaschinensicht nicht. Zusätzlich hat die
Umschaltfunktion `textContent` verwendet, was jedes Kindelement eines übersetzten
Tags zerstört hätte, sobald mal ein Link oder ein `<strong>` in einem Absatz steht.

**Datenschutz.** Die Schriften wurden bei jedem Aufruf von Google Fonts geladen und
die Google-Maps-Karte lud ungefragt — beides überträgt die IP-Adresse des Besuchers
an Google, bevor er irgendetwas angeklickt hat. Dazu gab es kein Impressum und keine
Datenschutzerklärung, obwohl das Formular Namen und E-Mail-Adressen erhebt.

**Kein Inhalt für Suche und KI-Antworten.** Kein FAQ, keine praktischen Angaben, kein
`sitemap.xml`, kein `robots.txt`. Dein Input-Dokument notiert selbst „FAQ ist gut für
Google und KI-Suche" — das stimmt, und es fehlte komplett. Genau solche Frage-Antwort-
Blöcke sind das, was ein Sprachmodell zitiert, wenn jemand „free running tour Lucerne"
fragt.

---

## 2. Was ich geändert habe

Die Website ist jetzt ein kleiner Generator statt einer Einzeldatei. Du bearbeitest
Texte in einer JSON-Datei, führst einen Befehl aus, und alle drei Sprachversionen
werden neu erzeugt. Das klingt nach mehr Aufwand, ist aber der einzige Weg, drei
Sprachen synchron zu halten, ohne dreimal dasselbe von Hand zu pflegen.

```
build.py                    Generator
src/config.json             Termine, Kontakt, Impressum, Formular-Backend
src/content.json            alle Texte in EN / DE / FR
src/styles.css              Design
tools/optimize_images.py    Bildaufbereitung
CLAUDE.md                   Arbeitsanweisungen für Claude Code
```

Erzeugt werden `index.html` (EN), `de/index.html`, `fr/index.html`, dazu je eine
`legal.html` pro Sprache sowie `sitemap.xml` und `robots.txt`.

**Bilder:** 25 MB → 2,7 MB. Jedes Bild liegt als WebP mit JPG-Fallback in zwei bis
drei Breiten vor, sauber auf 16:9 bzw. 4:3 zugeschnitten. Das Hero-Bild ist von
7,6 MB auf 318 kB. Die Originale liegen unangetastet in `assets/images/_originals/`.

**Struktur der Seite** (vorher vier Sektionen, jetzt neun):

Hero → Warum laufen statt spazieren → Vier Touren → So läuft's ab → Nächste Runs
mit Countdown und Anmeldeformular → Gut zu wissen → Treffpunkt → Dein Guide → FAQ

Der Inhalt der neuen Sektionen kommt aus deinem Input-Dokument: das
Lowest-Speed-Prinzip, „gratis, Trinkgeld erwünscht", kleine Gruppen als
Exklusivitäts-Argument, die Ausrüstungs-Frage, der Kaffee danach, die Give-away-Wahl,
Tempo in min/km und min/mile. Zehn FAQ-Einträge pro Sprache, ausschliesslich aus
Angaben, die in deinem Dokument stehen.

**Texte:** neu geschrieben, mit dem Fokus auf Nutzen statt Merkmalen — die Notiz
„Sell benefits, not features" aus deinem Dokument. Statt „5–6 km, flache Route" steht
jetzt „In einer Stunde zu Fuss schaffst du ein paar Gassen. Laufend schaffst du
Altstadt, Seepromenade und einen Aussichtspunkt — und bist vor dem ersten Termin
zurück." Die harten Zahlen stehen weiterhin daneben, aber als Faktentabelle unter dem
Fliesstext, nicht als Verkaufsargument.

**Formular:** funktioniert jetzt, mit drei wählbaren Backends (siehe Punkt 3),
Honeypot gegen Bots, sichtbarer Erfolgs- und Fehlermeldung, Pflichtfeld-Prüfung und
Einwilligungs-Checkbox mit Link auf die Datenschutzerklärung. Neu sind Felder für
Personenzahl, Wunschsprache und Give-away-Auswahl.

**Technik:** Google Fonts entfernt (Systemschriften), Maps lädt erst nach Klick,
Impressum und Datenschutzerklärung in drei Sprachen, korrekte `hreflang`-Verweise,
erweitertes JSON-LD (LocalBusiness, Person, FAQPage, vier TouristTrips, plus ein
Event-Eintrag pro Termin), Skip-Link, `aria-expanded` am Menü, sichtbarer Fokus,
`prefers-reduced-motion`.

---

## 3. Was du entscheiden musst

Diese Punkte konnte ich nicht für dich entscheiden, weil mir die Information fehlt.
`python3 build.py` listet sie am Ende jedes Laufs unter „Offene Punkte" auf.

### a) Widersprüchliche Startzeiten

Dein Input-Dokument und die alte Website widersprechen sich:

| Tour | Input-Dokument | Alte Website |
|---|---|---|
| Good Morning Scenic Run | 07:45 | 07:30 |
| Classic Heritage Run | 11:30 und 17:30 | 11:45 |
| Hidden Gems Run | 11:30 und 17:30 | 11:45 |

Ich habe die Werte aus dem Dokument übernommen, weil es die neuere Datei ist. Das ist
eine Annahme, keine Feststellung. Korrigieren in `src/content.json` → `tours` → `times`.
(Im Dokument steht unter „Ideen" nochmals „Start um 7:30" — dritter Wert, dritte Quelle.)

### b) Termine

`src/config.json` → `schedule.runs` ist leer. Die Seite zeigt deshalb „Termine folgen"
und sammelt stattdessen E-Mail-Adressen. Ich habe bewusst keine Termine erfunden.
Sobald du Daten hast:

```json
"runs": [
  { "date": "2026-08-06", "time": "07:45", "tours": ["morning"] },
  { "date": "2026-08-06", "time": "17:30", "tours": ["heritage", "hidden", "views"] }
]
```

Vergangene Termine verschwinden automatisch, der Countdown springt auf den nächsten.

### c) Formular-Backend

Aktuell steht `"provider": "mailto"` — der Besucher klickt „Anfrage senden" und sein
Mailprogramm öffnet sich mit vorausgefülltem Text. Funktioniert überall, ist aber die
schwächste Variante: auf manchen Geräten passiert scheinbar nichts, und du verlierst
Anfragen.

Empfehlung: **Formspree** (kostenlos bis 50 Einsendungen/Monat, kein Server nötig, in
zwei Minuten eingerichtet). Konto anlegen, Endpoint-URL kopieren, in `src/config.json`
eintragen, `provider` auf `"formspree"` setzen. Alternativ Netlify Forms, falls du
ohnehin bei Netlify hostest — dann muss `build.py` leicht angepasst werden.

*Hinweis: Preise und Freikontingente von Formspree können sich geändert haben, ich
habe sie nicht nachgeprüft.*

### d) Impressumsangaben

`src/config.json` → `legal`: Name, Strasse, PLZ, E-Mail stehen als `TODO_`-Platzhalter
drin. Die Seite sollte nicht live gehen, bevor das ersetzt ist. In der Schweiz braucht
eine Website, die personenbezogene Daten erhebt, eine Datenschutzerklärung (revDSG,
in Kraft seit 1. September 2023), und geschäftsmässig betriebene Websites brauchen
Kontaktangaben (UWG Art. 3 Abs. 1 lit. s).

**Ich bin kein Jurist.** Der Text in `content.json` unter `legal_page` ist eine
sachliche Vorlage nach bestem Wissen, keine Rechtsberatung. Besonders der
Haftungsausschluss ist heikel: du führst Fremde durch die Stadt, es kann jemand
stürzen. Ob dein Text ausreicht und ob du eine Haftpflichtversicherung brauchst, lass
bitte einmal von jemandem prüfen, der das beurteilen kann.

### e) Koordinaten des Treffpunkts

Die alte Seite hatte 47.0502 / 8.3093. Das lag rund 200 m neben der Kapellbrücke.
Ich habe 47.05174 / 8.30772 eingesetzt — **ungeprüft**. Bitte in Google Maps
nachschauen und in `src/config.json` → `meeting_point` korrigieren.

### f) Ungeprüfte Angaben aus der alten Seite

Ich habe sie übernommen, aber verifizieren kann ich sie nicht:

- Instagram-Handle `@runandsee_lucerne` — existiert der Account?
- Domain `runandsee.ch` — registriert? Alle `hreflang`-, Canonical- und JSON-LD-Einträge
  hängen daran. Bei anderer Domain: `src/config.json` → `site.domain`.
- „Established 2025"

---

## 4. Was ich nicht prüfen konnte

**Ich habe die Seite nicht im Browser gesehen.** In meiner Umgebung liess sich kein
Browser installieren. Geprüft habe ich: HTML-Struktur (alle Tags korrekt geschlossen,
keine doppelten IDs), alle internen Links und Bildpfade lösen auf, JSON-LD ist
gültiges JSON, jede im HTML verwendete CSS-Klasse existiert im Stylesheet, der Build
läuft in allen drei Sprachen fehlerfrei durch. **Nicht geprüft: wie es aussieht.**
Öffne `index.html` bitte einmal im Browser, bevor du weiterarbeitest.

**Die französischen Texte stammen von mir.** Sie sind grammatikalisch sauber, aber
Marketingtexte in einer Fremdsprache profitieren von einem Muttersprachler. Falls du
jemanden kennst: `src/content.json` → `languages.fr`.

**Die Tourbeschreibungen nennen konkrete Orte** — Museggmauer, Gütsch, Konsi,
Löwendenkmal —, die aus deinem Input-Dokument stammen. Ob die Routen tatsächlich so
verlaufen, weiss nur du. Bitte einmal gegenlesen.

---

## 5. Anweisung für Claude Code

Der Block unten ist zum Kopieren. Führe ihn erst aus, nachdem du die Punkte unter 3
in `src/config.json` und `src/content.json` eingetragen hast — sonst arbeitet Claude
Code gegen Platzhalter.

```
Lies zuerst CLAUDE.md, dann build.py, src/config.json und src/content.json.

Die Website ist ein generierter Static Site mit drei Sprachversionen. Die HTML-Dateien
im Root sowie in de/ und fr/ sind Build-Artefakte und werden bei jedem Lauf
überschrieben — bearbeite sie nie direkt. Änderungen gehören in src/ oder build.py,
danach immer `python3 build.py` ausführen.

Aufgaben, in dieser Reihenfolge:

1. Öffne index.html, de/index.html und fr/index.html im Browser (Desktop 1440px und
   Mobil 390px) und mach Screenshots. Prüfe: Hero-Bild sichtbar, Navigation lesbar
   über dem Bild, Sprachumschalter funktioniert und führt auf die richtige Seite,
   Tourkarten gleich hoch, Formular auf Mobil nicht abgeschnitten, Footer intakt.
   Behebe gefundene Layoutfehler in src/styles.css, nicht im generierten HTML.

2. Prüfe die Konsole auf JavaScript-Fehler. Teste das Anmeldeformular: Absenden ohne
   Pflichtfelder muss eine Meldung zeigen, Absenden mit gültigen Daten muss die
   Erfolgsmeldung zeigen. Teste den Karten-Consent-Button.

3. Ergänze eine 404.html im Root, im gleichen Stil wie legal.html, mit Link zurück
   zur Startseite. Generiere sie über build.py, nicht von Hand.

4. Ergänze in build.py Open-Graph-Bildmasse (og:image:width 1920, og:image:height 1080)
   und ein <link rel="preload"> für das Hero-Bild in der jeweils passenden Breite.

5. Lege eine Deployment-Konfiguration an. Ich hoste noch nirgends. Schlag mir zwei
   Optionen vor (statisches Hosting mit eigener Domain), begründe kurz, und richte
   dann die von mir gewählte ein: nötige Konfigurationsdateien, Weiterleitung von
   nicht-www auf www oder umgekehrt, HTTPS, Caching-Header für assets/.

6. Führe python3 build.py aus und zeig mir die Liste der offenen TODO-Platzhalter.

Halte dich an die Konventionen in CLAUDE.md: keine externen Requests, keine
erfundenen Inhalte, alle drei Sprachen synchron, CSS-Variablen statt Hex-Werte.
Frag nach, statt Annahmen zu treffen, wenn dir eine Angabe fehlt.
```

---

## 6. Danach: was den Unterschied macht

Technisch ist die Seite jetzt in Ordnung. Was ihr noch fehlt, ist nichts, was sich
programmieren lässt:

**Echte Fotos von echten Runs.** Vier Landschaftsbilder ohne Menschen verkaufen ein
soziales Erlebnis nicht. Ein Gruppenfoto mit fünf verschwitzten, lachenden Leuten auf
der Museggmauer schlägt jedes Postkartenmotiv. Das ist die grösste offene Baustelle.

**Die ersten echten Bewertungen.** Google-Bewertungen sind für lokale Suche das
stärkste Signal überhaupt. Dein Dokument hat die Idee schon: QR-Code beim Treffpunkt
hinterlegen. Mach das ab dem ersten Run.

**Strava-Segmente oder GPX-Dateien pro Route.** Kostet dich wenig, ist für Läufer
sofort überzeugend und bringt Verlinkungen aus der Laufszene.

**Ein Google-Business-Profil.** Ohne das taucht „running tour Lucerne" in der lokalen
Suche kaum auf, egal wie gut die Seite ist.

Die Notiz „Verkaufe Status, nicht Commodity" aus deinem Dokument ist der beste
Gedanke darin, und die Seite setzt ihn erst halb um. „Kleine Gruppen" steht dreimal
da. Was fehlt, ist der Beweis: ein Foto, das zeigt, wie klein und wie gut die Gruppe
ist.

---

## Nachtrag, 1. August 2026 — Bewegung und zwei Design-Entwürfe

Ergänzt seit der ersten Fassung:

- **Zwei vollständige Design-Entwürfe** auf Basis deiner Logo-Optionen „Horizont"
  und „Tempo", jeweils dreisprachig. Bauen mit `python3 build.py --previews`,
  vergleichen unter `preview/index.html`. Details in `DESIGN.md`.
- **Touren-Karussell**, Lauftextband, Kennzahlen zum Hochzählen, animierte
  Verbindungslinie im Ablauf, Einblenden beim Scrollen, Sticky-Leiste auf dem Handy,
  aktiver Navigationspunkt. Alles schaltet sich bei „Bewegung reduzieren" ab.
- **Eigene Logos** für beide Entwürfe als SVG, hell und dunkel, plus Favicon.
- **Stylesheet getrennt** in `src/base.css` (Struktur) und `src/themes/*.css`
  (Farbe, Form, Typografie). Die alte `src/styles.css` wird nicht mehr verwendet.

**Punkt 4 der ersten Fassung ist überholt:** ich konnte inzwischen einen echten
Browser starten und beide Entwürfe in drei Sprachen bei vier Bildschirmbreiten
ansehen. Vier Fehler kamen dabei zum Vorschein und sind behoben — unter anderem ein
Karussell, das nicht scrollte, und ein mobiles Menü, das im geschlossenen Zustand
oben ins Bild lugte. Was weiterhin offen ist: geprüft wurde nur in Chromium, nicht
in Safari oder Firefox.

**Deine ursprünglichen Notizen** liegen unter `docs/` — das Word-Dokument unverändert,
dazu `docs/notizen-original.md` als wortgetreue Textfassung, damit sich der Inhalt
durchsuchen und versionieren lässt. Die Design-PowerPoint liegt ebenfalls dort.

Die offenen Entscheidungen aus Abschnitt 3 gelten unverändert.
