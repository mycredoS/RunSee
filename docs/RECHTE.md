# Rechte: Schriften, Bilder, Karte, Daten

Stand: 1. August 2026

**Vorab, weil es wichtig ist:** ich bin kein Jurist. Was hier steht, ist eine
sachliche Einordnung nach bestem Wissen, keine Rechtsberatung. Bei den Punkten,
die mit ⚠️ markiert sind, geht es um echtes Haftungsrisiko — dort lohnt sich im
Zweifel eine Fachmeinung.

---

## 1. Schriften — hier ist alles sauber

Deine Sorge ist berechtigt: Schriften sind Software und lizenzpflichtig. Der
klassische Fehler ist, eine gekaufte oder gratis heruntergeladene Schriftdatei
auf den Server zu legen und per `@font-face` auszuliefern. Das ist
**Weiterverbreitung** und bei den meisten kommerziellen Lizenzen ohne Webfont-
Zusatzlizenz nicht gedeckt.

Diese Seite macht das nicht. Es gibt zwei Fälle:

### Fliesstext und Überschriften: gar keine Schriftdatei

Die Seite lädt **keine einzige Schriftdatei**. Sie sagt dem Browser nur, welche
Schriften sie bevorzugt, und der nimmt, was auf dem Gerät des Besuchers
installiert ist:

```css
--font-display: "Avenir Next", Avenir, "Segoe UI Variable Display",
                "Segoe UI", system-ui, -apple-system, "Helvetica Neue",
                Arial, sans-serif;
```

Auf einem Mac erscheint Avenir Next, auf Windows Segoe UI, auf Android Roboto.
Das ist lizenzrechtlich unproblematisch: du verbreitest nichts, du nutzt nichts —
der Besucher sieht seine eigene, von ihm selbst lizenzierte Schrift. Genau
deshalb sieht die Seite auf verschiedenen Geräten minim unterschiedlich aus.
Das ist der Preis, und er ist es wert.

**Nebeneffekt Datenschutz:** weil keine Google Fonts geladen werden, geht auch
keine IP-Adresse an Google. Das war in der alten Fassung anders und ist der
Grund, warum die Datenschutzerklärung so knapp ausfallen kann.

### Logo: Carlito, SIL Open Font License 1.1

Die Wortmarke „Run & See" ist als **Pfad** gezeichnet, nicht als Text. Die
Buchstabenformen stammen aus **Carlito Bold** von Łukasz Dziedzic. Ich habe die
Lizenzangabe direkt aus der Schriftdatei ausgelesen:

```
Copyright (c) 2010-2013 by tyPoland Lukasz Dziedzic
  with Reserved Font Name "Carlito".
Licensed under the SIL Open Font License, Version 1.1
  (http://scripts.sil.org/OFL)
```

Die SIL OFL erlaubt ausdrücklich kommerzielle Nutzung, Weitergabe und
Veränderung. Für dich relevant:

- Buchstaben in Pfade umzuwandeln und das Ergebnis als Logo zu verwenden ist
  gedeckt. Das entstandene Kunstwerk fällt nach dem Verständnis der OFL nicht
  selbst unter die OFL.
- Du musst die Schrift **nicht** nennen und **keine** Lizenzdatei mitliefern,
  solange du nicht die Schriftdatei selbst weitergibst.
- Der Name „Carlito" ist ein Reserved Font Name. Solange du nichts „Carlito"
  nennst, spielt das keine Rolle.

Ich habe im Impressum trotzdem einen kurzen Hinweis ergänzt — Höflichkeit
gegenüber dem Gestalter, und es beantwortet die Frage, bevor sie jemand stellt.

**Zu beachten:** ein Logo kann zusätzlich markenrechtlich geschützt werden. Das
ist unabhängig vom Urheberrecht an der Schrift. Wenn „Run & See" eine ernsthafte
Marke werden soll, wäre eine Markenrecherche beim IGE (Eidgenössisches Institut
für Geistiges Eigentum) der nächste Schritt — auch um sicherzugehen, dass der
Name nicht schon jemand anderem gehört.

### Falls du doch Space Grotesk willst

Space Grotesk aus deiner Logo-Vorlage steht ebenfalls unter der OFL. Du dürftest
sie also selbst hosten. `docs/DESIGN.md` beschreibt den Weg. Was du **nicht**
tun solltest: die Schrift über die Google-Fonts-URL einbinden — dann bist du
wieder beim Datenschutzproblem.

---

## 2. ⚠️ Bilder — hier liegt das eigentliche Risiko

**Ich weiss nicht, woher deine sechs Fotos stammen, und ich kann es nicht
herausfinden.** Die EXIF-Daten sind bei allen sechs Dateien vollständig leer:
keine Kamera, kein Datum, kein Urheber, kein GPS. Das ist typisch für Bilder,
die über eine Plattform hoch- und wieder heruntergeladen wurden — es passiert
aber genauso beim Export aus einem Bildbearbeitungsprogramm oder beim Versand
über einen Messenger.

Was die Bildgrössen andeuten (**Indizien, keine Belege**):

| Datei | Grösse | Deutung |
|---|---|---|
| `tour-morning-run.jpg` | 3024 × 4032 | klassisches Smartphone-Format, spricht für ein eigenes Foto |
| `tour-top-views.jpg` | 4032 × 3024 | dasselbe, quer |
| `luzern-kapellbruecke.jpg` | 3852 × 2584 | beschnitten, Herkunft offen |
| `tour-heritage.jpg` | 6016 × 3601 | Systemkamera, beschnitten |
| `tour-hidden-gems.jpg` | 5152 × 7728 | 40 Megapixel hoch — ungewöhnlich, Herkunft offen |
| `philippe-final.png` | 600 × 600 | freigestelltes Porträt |

**Warum das ernst ist:** Bilderklau ist der häufigste Abmahngrund bei kleinen
Websites. In der Schweiz greift Art. 62 URG (Unterlassung, Beseitigung,
Schadenersatz), und Bildagenturen suchen automatisiert nach ihren Motiven.
Ein einzelnes Bild kann vierstellig werden. Dass die Seite kostenlos ist und du
kein Geld verdienst, schützt dich nicht.

**Was zu tun ist:** In `src/config.json` gibt es jetzt einen Abschnitt `images`
mit einem Eintrag pro Foto:

```json
"tour-heritage": {
  "file": "assets/images/tours/tour-heritage.jpg",
  "source": "TODO_Herkunft",
  "author": "",
  "licence": ""
}
```

Trag dort für jedes Bild ein, woher es kommt:

- **Eigenes Foto** → `"source": "eigenes Foto", "author": "Philippe Kaufmann", "licence": "eigenes Werk"`
- **Von Unsplash/Pexels** → Plattform, Fotografenname und Lizenzbezeichnung. Die
  Lizenzen dieser Plattformen erlauben kommerzielle Nutzung ohne Namensnennung,
  aber du musst nachweisen können, woher das Bild stammt. Notiere zusätzlich den
  Link zur Bildseite.
- **Von jemandem geschenkt** → Name und Datum der schriftlichen Erlaubnis. Eine
  WhatsApp-Nachricht reicht als Beleg, wenn du sie aufbewahrst.
- **Herkunft unbekannt** → **ersetzen**. Nicht „wird schon gutgehen".

Der Build erinnert dich daran: solange `TODO_Herkunft` drinsteht, erscheint es
bei jedem `python3 build.py` unter „Offene Punkte". Sobald die Angaben stehen,
erscheinen sie automatisch im Impressum unter „Bildnachweis".

**Zusätzlich zu bedenken:**

- **Personen auf Fotos.** Sobald erkennbare Menschen abgebildet sind, brauchst du
  deren Einwilligung (Recht am eigenen Bild, Art. 28 ZGB). Auf den jetzigen
  Bildern sehe ich niemanden erkennbar — aber genau das wird sich ändern, sobald
  du Gruppenfotos von echten Runs verwendest. Frag vor Ort, am besten kurz
  schriftlich.
- **Das Löwendenkmal** auf `tour-heritage.jpg` ist von 1821, gemeinfrei. Kein
  Problem.
- **Die Kapellbrücke** ist ein Bauwerk im öffentlichen Raum. Die Schweiz kennt
  die Panoramafreiheit (Art. 27 URG): Aufnahmen von bleibend im öffentlichen
  Raum befindlichen Werken dürfen verbreitet werden. Auch kein Problem.
- **KI-generierte Bilder** wären eine Alternative, bringen aber eigene Fragen mit
  (Rechtelage je nach Anbieter unterschiedlich) — und für eine Seite, die von
  Authentizität lebt, wären sie ohnehin die falsche Wahl.

**Mein Rat:** Fotografiere die vier Routen selbst. Es kostet dich vier
Laufeinheiten mit dem Handy, löst das Rechtsthema restlos, und die Bilder wären
inhaltlich sowieso besser als Postkartenmotive.

---

## 3. Google Maps

Die Karte wird über den offiziellen Einbettungscode geladen und erst nach
einem ausdrücklichen Klick. Das ist von den Nutzungsbedingungen der Google Maps
Platform gedeckt, solange die Google-Attribution sichtbar bleibt — sie ist Teil
des eingebetteten Kartenbilds und darf nicht überdeckt werden. Ist sie nicht.

Wichtig ist der Klick davor: ohne ihn würde bei jedem Seitenaufruf die IP-Adresse
des Besuchers an Google gehen, ohne Rechtsgrundlage. Diese Zwei-Klick-Lösung
bitte nicht „vereinfachen".

---

## 4. Formulardaten und Datenschutz

Das Anmeldeformular erhebt Name, E-Mail und freiwillige Angaben. Damit gilt das
revidierte Datenschutzgesetz (revDSG, in Kraft seit 1. September 2023):

- **Datenschutzerklärung** — vorhanden, in drei Sprachen.
- **Einwilligung** — eine Checkbox mit Link auf die Datenschutzerklärung ist
  eingebaut und Pflichtfeld.
- **Auskunft und Löschung** — der Anspruch ist in der Erklärung genannt.

⚠️ **Was noch offen ist:** sobald du das Formular auf einen Dienstleister wie
Formspree umstellst, fliessen die Daten über dessen Server. Der Anbieter sitzt
in den USA. Dann brauchst du:

1. einen Hinweis in der Datenschutzerklärung, dass Daten an diesen Anbieter und
   damit ins Ausland gehen,
2. eine Rechtsgrundlage für den Auslandstransfer.

Das ist kein Hindernis, aber es muss in den Text. Sag mir Bescheid, welchen
Anbieter du nimmst, dann ergänze ich den Abschnitt. Alternativ: ein Formularziel
bei einem Schweizer Hoster, dann entfällt die Frage.

⚠️ **Haftung bei den Läufen selbst.** Das ist rechtlich der heikelste Punkt der
ganzen Sache und hat mit der Website nur am Rande zu tun. Du führst Fremde durch
die Stadt, es kann jemand stürzen oder von einem Auto erfasst werden. Der
Haftungsausschluss im Impressum ist eine sachliche Formulierung nach bestem
Wissen — aber ein Haftungsausschluss auf einer Website schliesst Haftung für
grobe Fahrlässigkeit nicht aus, und ob er im Streitfall trägt, kann ich nicht
beurteilen. **Kläre einmal mit deiner Versicherung**, ob deine private
Haftpflicht das abdeckt oder ob es eine Vereinsdeckung oder
Veranstalterhaftpflicht braucht. Das ist die eine Frage, bei der ich dir
wirklich zu einem Gespräch mit einem Menschen raten würde.

---

## 5. Weitere Punkte

**Impressumspflicht.** Websites, die geschäftsmässig betrieben werden, brauchen
nach UWG Art. 3 Abs. 1 lit. s Namen und Kontaktangaben. „Geschäftsmässig" wird
weit ausgelegt und dürfte auch auf ein kostenloses, aber regelmässiges Angebot
mit Trinkgeld zutreffen. Die Angaben stehen als `TODO_` in `src/config.json` und
müssen vor dem Live-Gang gefüllt werden.

**Fremde Marken.** Auf der Seite stehen Ortsnamen (Kapellbrücke, Museggmauer,
Gütsch) — das sind geografische Bezeichnungen, kein Problem. Nenne keine
Restaurants oder Cafés mit Logo, ohne zu fragen.

**Der Domainname.** `runandsee.ch` — prüfe vor der Registrierung, ob es
anderswo eine Marke „Run and See" gibt. Eine Recherche auf
[swissreg.ch](https://www.swissreg.ch) ist kostenlos und dauert fünf Minuten.

**Keine erfundenen Bewertungen.** Steht schon in `CLAUDE.md`, aber der Vollständigkeit
halber: erfundene Kundenstimmen verstossen gegen UWG Art. 3 Abs. 1 lit. b. Die
drei, die auf der alten Seite standen, habe ich deshalb entfernt.

---

## Checkliste vor dem Live-Gang

- [ ] Herkunft aller sechs Bilder in `src/config.json` eingetragen
- [ ] Bilder unklarer Herkunft ersetzt
- [ ] Impressumsangaben vollständig
- [ ] Versicherungsfrage für die Läufe geklärt
- [ ] Bei Formular-Dienstleister: Abschnitt zum Auslandstransfer ergänzt
- [ ] Markenrecherche für „Run & See" auf swissreg.ch
- [ ] `python3 build.py` zeigt keine offenen Punkte mehr
