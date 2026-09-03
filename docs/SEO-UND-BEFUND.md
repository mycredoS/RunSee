# Stärken, Schwächen und die Auffindbarkeit

Stand: 1. August 2026

---

## Teil 1 — Ehrliche Einschätzung der Seite

### Was stark ist

**Die Positionierung.** „Gratis geführte Lauftour mit einem Einheimischen" ist
ein Angebot, das es in Luzern so kaum gibt und das sich in einem Satz erklärt.
Das ist mehr wert als jede Designentscheidung. Der Preis von null ist dabei
nicht Schwäche, sondern das stärkste Argument — er nimmt jede Kaufhürde weg und
macht aus einer Buchung eine Verabredung.

**Die Struktur folgt der Entscheidung des Besuchers.** Warum überhaupt laufen →
welche Route → wer führt mich → wie läuft es ab → jetzt anmelden → offene Fragen.
Jede Sektion beantwortet die Frage, die nach der vorherigen entsteht. Das klingt
banal, machen aber die wenigsten kleinen Seiten.

**Technisch ist sie in einem Zustand, den die meisten KMU-Seiten nicht
erreichen.** 2,7 MB statt 25 MB Bilder, keine externen Anfragen, dreisprachig mit
korrekten `hreflang`-Verweisen, strukturierte Daten über zwölf verknüpfte
Knoten, Tastaturbedienung, `prefers-reduced-motion`, Skip-Link. Nichts davon
sieht man — alles davon wirkt.

**Kein laufender Aufwand.** Keine Plugin-Updates, keine Sicherheitslücken, keine
Abo-Gebühr. In fünf Jahren funktioniert diese Seite unverändert weiter. Das ist
bei WordPress nicht so.

**Der Ton.** Die Texte behaupten nichts, was nicht stimmt, und verkaufen über
konkrete Bilder statt über Superlative. „In einer Stunde zu Fuss schaffst du ein
paar Gassen" ist überzeugender als „einzigartiges Erlebnis".

### Was schwach ist

**Die Bilder sind das grösste Problem — inhaltlich, nicht nur rechtlich.** Vier
Landschafts- und Architekturmotive ohne einen einzigen Menschen verkaufen ein
soziales Erlebnis nicht. Deine eigene Notiz lautet „Sell benefits, not features"
und „meet like-minded people" — davon zeigt die Seite nichts. Ein Foto von fünf
verschwitzten, lachenden Leuten auf der Museggmauer würde mehr bewirken als jede
weitere Textänderung. Das ist meine deutlichste Empfehlung.

**Null Sozialbeweis.** Keine Bewertungen, keine Teilnehmerzahlen, keine
Gesichter ausser deinem. Für ein Gratisangebot von einer unbekannten Person ist
das die grösste verbleibende Hürde: „Ist das seriös oder steige ich hier in etwas
Komisches ein?" Erfundene Kundenstimmen habe ich bewusst entfernt — die Lösung
ist nicht, sie zurückzuholen, sondern echte zu sammeln.

**Keine Termine.** Solange „Termine folgen" steht, wirkt die Seite unfertig,
egal wie gut alles andere ist. Das ist der schnellste Hebel, den du hast.

**Das Formular führt ins Mailprogramm.** In der jetzigen Einstellung öffnet sich
beim Absenden das Mailprogramm des Besuchers. Auf manchen Geräten passiert
scheinbar nichts, und du verlierst die Anfrage. Bis das umgestellt ist, ist die
Anmeldestrecke die schwächste Stelle einer sonst runden Seite.

**Eine einzige Seite.** Alles steht auf der Startseite. Für den Anfang richtig —
für Suchmaschinen bedeutet es aber, dass du für alle Suchbegriffe mit derselben
Seite antrittst. Dazu unten mehr.

**Kein Impressum mit echten Daten.** Steht als Platzhalter drin. Das ist kein
Design-, sondern ein Rechtsthema, siehe `RECHTE.md`.

**Die französische Fassung ist ungeprüft.** Grammatikalisch sauber, aber
Marketingtexte in einer Fremdsprache profitieren von einem Muttersprachler.

### Was ich anders machen würde, wenn du fragst

Nicht mehr Text, nicht mehr Funktionen. Sondern: vier echte Fotos, vier Termine,
ein funktionierendes Formular. Danach die ersten fünf Google-Bewertungen. Das
sind die vier Dinge, die zwischen „sieht gut aus" und „bringt Anmeldungen"
stehen. Alles andere ist Feintuning.

---

## Teil 2 — Was ich für die Auffindbarkeit gemacht habe

### Strukturierte Daten

Die Seite liefert jetzt zwölf miteinander verknüpfte Schema.org-Knoten statt
sieben lose. Neu oder verbessert:

- **LocalBusiness + SportsActivityLocation** mit Koordinaten, Sprachen,
  Gründungsjahr, Logo, Gratis-Kennzeichnung (`isAccessibleForFree`) und einer
  `ReserveAction`, die auf das Anmeldeformular zeigt.
- **OfferCatalog** — die vier Touren als Angebotskatalog mit Position und Preis.
  Damit kann eine Suchmaschine „vier Touren, alle kostenlos" als Struktur lesen,
  nicht nur als Fliesstext.
- **TouristTrip je Tour** mit eigener `@id`, Bild, Anker-URL und den harten
  Fakten als `PropertyValue`: Distanz, Tempo, Höhenmeter, Startzeiten, Niveau.
  Genau diese Zahlen zitiert ein KI-Assistent, wenn jemand fragt „wie lang ist
  die Morgenrunde".
- **WebPage** und **ImageObject** für Logo und Hero, damit Bild- und Seitenbezug
  eindeutig sind.
- **Person** mit Beschreibung und Wohnort.
- **FAQPage** mit zehn Fragen — unverändert, aber jetzt korrekt in die Seite
  eingehängt.
- **Event** je Termin, sobald du Termine einträgst.

### Anker je Tour

Jede Tourkarte hat eine eigene Adresse: `#tour-morning`, `#tour-heritage`,
`#tour-hidden`, `#tour-views`. Das erlaubt Direktlinks, und KI-Antworten können
auf eine bestimmte Tour verweisen statt nur auf die Seite.

### robots.txt für KI-Crawler

Wichtiger Punkt, der oft falsch gemacht wird: **wer AI-Crawler pauschal
aussperrt, verschwindet aus KI-Antworten.** Die Anbieter trennen inzwischen
zwischen Trainings-Crawlern und Such-Crawlern, die live abrufen und Quellen
verlinken. Die `robots.txt` erlaubt jetzt beide ausdrücklich und benennt sie:
`OAI-SearchBot`, `ChatGPT-User`, `Claude-SearchBot`, `Claude-User`,
`PerplexityBot`, `Perplexity-User`, `Google-Extended`, dazu `GPTBot`,
`ClaudeBot`, `CCBot`.

Bei einem kostenlosen Angebot ohne schützenswerte Inhalte überwiegt die
Sichtbarkeit — deshalb sind auch die Trainings-Crawler erlaubt. Wenn du das
anders siehst, steht in der Datei, wie du sie aussperrst. Wichtig zu wissen:
`robots.txt` ist eine Bitte, keine technische Sperre.

### llms.txt — mit einer ehrlichen Einordnung

Ich habe eine `llms.txt` erzeugt: eine kompakte Textfassung der ganzen Seite,
gedacht als Kurzform für KI-Assistenten.

**Aber:** Der Vorschlag ist Stand August 2026 nicht formal standardisiert, und
die grossen Crawler rufen die Datei nach vorliegenden Auswertungen kaum ab — sie
lesen direkt das HTML. Google hat 2025 selbst solche Dateien veröffentlicht,
aber ausdrücklich klargestellt, dass sie nicht für AI Overviews verwendet werden.

Die Datei kostet nichts, schadet nicht und ist da, falls sich das ändert.
Verlass dich nicht darauf. Was tatsächlich zitiert wird, ist sauberes HTML mit
klaren Überschriften, Frage-Antwort-Blöcken und strukturierten Daten — und davon
hat die Seite reichlich.

### Weitere Massnahmen

- **Bild-Sitemap:** die `sitemap.xml` meldet jetzt alle fünf Fotos mit
  Bildunterschrift — relevant für die Bildersuche.
- **Alt-Texte neu geschrieben.** Sie beschreiben jetzt tatsächlich, was zu sehen
  ist, statt zu behaupten. Der alte Text des Hero-Bilds nannte einen Läufer bei
  Sonnenaufgang — auf dem Bild ist weder das eine noch das andere. Das war mein
  Fehler und ist korrigiert.
- **Geo-Metadaten** (`geo.region`, `geo.position`, `ICBM`) für lokale Dienste.
- **Open Graph** mit Bildmassen — Vorschaubilder in WhatsApp, LinkedIn und
  Slack laden dadurch zuverlässiger.
- **404-Seite** in drei Sprachen, `noindex`, mit Weg zurück.
- **Ladezeit:** das Hero-Bild wird jetzt vorgeladen. Dabei habe ich einen Fehler
  behoben — das Bild wäre sonst zweimal geladen worden, weil Preload und
  `<picture>` unterschiedliche Auswahlverfahren nutzten. Nachgemessen: es geht
  jetzt genau eine Anfrage raus.
- **Tourbilder** mit `sizes` passend zur tatsächlichen Anzeigebreite. Auf dem
  Handy lädt der Browser die 480-px-Fassung statt der 800er.
- **Termine als `<time>`** mit maschinenlesbarem Datum.

---

## Teil 3 — Was die Website allein nicht schafft

Hier bin ich am Ende dessen, was sich programmieren lässt. Für „running tour
Lucerne" konkurrierst du mit Tripadvisor, GetYourGuide und Luzern Tourismus.
Deren Vorsprung ist nicht technisch, sondern besteht aus Bewertungen und
Verlinkungen. Was hilft, in ungefährer Reihenfolge der Wirkung:

**1. Google-Unternehmensprofil.** Ohne Eintrag tauchst du in der lokalen Suche
und in der Karte praktisch nicht auf, egal wie gut die Seite ist. Kostenlos,
dauert eine halbe Stunde. Der einzelne grösste Hebel.

**2. Bewertungen.** Deine eigene Notiz hat es schon: QR-Code beim Treffpunkt.
Mach das ab dem ersten Run. Fünf echte Bewertungen schlagen jede
Suchmaschinenoptimierung. Danach dürfen die Zitate auch auf die Website — dann
mit Vorname, Herkunftsland und Datum.

**3. Strava.** Lege je Route eine Strecke an und verlinke sie. Läufer suchen
dort, die Strecken sind für sich auffindbar, und es beweist, dass es die Routen
wirklich gibt. In `src/config.json` ist das Feld `strava_club_url` schon
vorbereitet und fliesst automatisch in die strukturierten Daten.

**4. Verlinkungen aus der Laufszene.** Luzerner Laufgruppen, Hotelconcierges,
Hostels, Reiseblogs, das Stadtmagazin. Ein Link von einer Hotelseite ist mehr
wert als jede Meta-Angabe — und Hotels suchen ständig nach Tipps für ihre Gäste.

**5. Regelmässigkeit.** Termine, die tatsächlich stattfinden und auf der Seite
aktuell sind, sind das stärkste Signal für Mensch und Maschine, dass es dieses
Angebot gibt.

**Was ich nicht empfehle:** Keyword-Stopfen, gekaufte Links, KI-generierte
Blogartikel „10 Gründe, in Luzern zu laufen". Bei einer Seite dieser Grösse
schadet das mehr, als es hilft.

---

## Was geprüft ist

Alle Seiten in einem echten Chromium gerendert, drei Sprachen, Desktop und
Handy, dazu über einen lokalen Webserver:

- JSON-LD ist gültiges JSON, zwölf Knoten, `@id`-Verweise lösen intern auf
- HTML-Struktur sauber, keine doppelten IDs
- alle internen Links und Bildpfade auflösbar
- keine Fehler in der Browser-Konsole, kein horizontales Scrollen
- 404-Seite, `robots.txt`, `llms.txt`, `sitemap.xml` liefern Status 200
- Hero-Bild wird genau einmal geladen

**Nicht geprüft:** Ob die strukturierten Daten von Google akzeptiert werden —
das geht erst, wenn die Seite unter einer echten Adresse erreichbar ist. Dann
über den Rich-Results-Test und die Search Console prüfen. Und weiterhin: nur
Chromium, nicht Safari oder Firefox.
