#!/usr/bin/env python3
"""
Erzeugt die Logo-Dateien für das Theme „Horizont".

Die Wortmarke „Run & See" wird als **Pfade** ausgegeben, nicht als SVG-Text.
Grund: als Text hing das Aussehen von der Schrift des jeweiligen Rechners ab,
und die vorher nötige Breitenkorrektur (`textLength` mit `lengthAdjust`)
verzerrte einzelne Buchstaben unterschiedlich stark — „See" wirkte dadurch
breiter und schräger als „Run". Als Pfad sieht das Logo überall gleich aus.

Aufruf aus dem Projekt-Root:

    python3 tools/make_logo.py

Voraussetzung: fontTools  ->  pip install fonttools
Die Schriftdatei muss lokal vorhanden sein; welche verwendet wurde, steht in FONT.
"""

from pathlib import Path

from fontTools.misc.transform import Transform
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen
from fontTools.ttLib import TTFont

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "assets" / "logos"

# Carlito Bold — humanistische Grotesk, metrisch wie Calibri.
# Passt zur Systemschrift-Anmutung der Seite und ist frei lizenziert (SIL OFL).
FONT = "/usr/share/fonts/truetype/crosextra/Carlito-Bold.ttf"

NAVY = "#163e5c"
SUN = "#f2683c"
WHITE = "#ffffff"
ICE = "#eaf1f4"
MID = "#1f5478"

FONT_SIZE = 34          # Schriftgrad in viewBox-Einheiten
BASELINE = 44           # Grundlinie der Wortmarke
TEXT_X = 76             # linker Anfang der Wortmarke
TRACKING = -0.5         # leicht enger, passend zur Überschriften-Laufweite


def build_wordmark():
    font = TTFont(FONT)
    upm = font["head"].unitsPerEm
    cmap = font.getBestCmap()
    glyphs = font.getGlyphSet()
    hmtx = font["hmtx"]
    scale = FONT_SIZE / upm

    def run(text, x):
        parts = []
        for ch in text:
            gname = cmap.get(ord(ch))
            if gname is None:
                continue
            pen = SVGPathPen(glyphs)
            glyphs[gname].draw(
                TransformPen(pen, Transform(scale, 0, 0, -scale, x, BASELINE))
            )
            d = pen.getCommands()
            if d:
                parts.append(d)
            x += hmtx[gname][0] * scale + TRACKING
        return " ".join(parts), x

    d_run, x = run("Run ", TEXT_X)
    d_amp, x = run("&", x)
    d_see, x = run(" See", x)
    return d_run, d_amp, d_see, x


def badge(clip_id):
    """Kreisförmige Bildmarke: Sonne über zwei Bergen, gespiegelt im Wasser."""
    return f"""  <defs><clipPath id="{clip_id}"><circle cx="32" cy="32" r="27.5"/></clipPath></defs>
  <circle cx="32" cy="32" r="29.5" fill="{ICE}"/>
  <g clip-path="url(#{clip_id})">
    <circle cx="34" cy="26" r="10.5" fill="{SUN}"/>
    <path d="M4 42 L21 22 L38 42 Z" fill="{NAVY}"/>
    <path d="M28 42 L44 24 L62 42 Z" fill="{MID}"/>
    <rect x="2" y="42" width="60" height="2.4" fill="{NAVY}"/>
    <rect x="12" y="47.5" width="40" height="3" rx="1.5" fill="#7d97a8"/>
    <rect x="17" y="53" width="30" height="3" rx="1.5" fill="#9fb3c0"/>
  </g>"""


def lockup(text_colour, ring_colour, clip_id, d_run, d_amp, d_see, width):
    return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} 64"
     role="img" aria-label="Run &amp; See Lucerne">
{badge(clip_id)}
  <circle cx="32" cy="32" r="29.5" fill="none" stroke="{ring_colour}" stroke-width="3.5"/>
  <path fill="{text_colour}" d="{d_run}"/>
  <path fill="{SUN}" d="{d_amp}"/>
  <path fill="{text_colour}" d="{d_see}"/>
</svg>
"""


def main():
    d_run, d_amp, d_see, end_x = build_wordmark()
    width = round(end_x + 6)

    (OUT / "horizont-lockup-dark.svg").write_text(
        lockup(NAVY, NAVY, "hzD", d_run, d_amp, d_see, width), encoding="utf-8"
    )
    (OUT / "horizont-lockup-light.svg").write_text(
        lockup(WHITE, WHITE, "hzL", d_run, d_amp, d_see, width), encoding="utf-8"
    )
    (OUT / "horizont-mark.svg").write_text(
        f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64"
     role="img" aria-label="Run &amp; See">
{badge("hzM")}
  <circle cx="32" cy="32" r="29.5" fill="none" stroke="{NAVY}" stroke-width="3.5"/>
</svg>
""",
        encoding="utf-8",
    )

    print(f"Logo erzeugt · viewBox 0 0 {width} 64")
    print("  assets/logos/horizont-lockup-dark.svg")
    print("  assets/logos/horizont-lockup-light.svg")
    print("  assets/logos/horizont-mark.svg")
    print(f"\nIn build.py unter THEMES['horizont'] eintragen: logo_w={width}, logo_h=64")


if __name__ == "__main__":
    main()
