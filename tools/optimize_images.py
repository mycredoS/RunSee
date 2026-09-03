#!/usr/bin/env python3
"""
Bildoptimierung fuer Run & See Lucerne.

Liest die Originale aus assets/images/_originals/ und erzeugt daraus
web-taugliche Varianten (WebP + JPG-Fallback) in mehreren Breiten.

Aufruf (aus dem Projekt-Root):
    python3 tools/optimize_images.py

Voraussetzung: Pillow  ->  pip install Pillow
Die Originale werden nie veraendert. Die Ausgabe wird bei jedem Lauf neu erzeugt.
"""

from pathlib import Path
from PIL import Image, ImageOps

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "assets" / "images" / "_originals"
OUT = ROOT / "assets" / "images"

# name_im_original -> (zielordner, zielbasisname, [breiten], seitenverhaeltnis, farbkorrektur)
#
# farbkorrektur = (rot, gruen, blau) als Faktoren, (1, 1, 1) laesst das Bild
# unveraendert. Das Original auf der Platte wird nie angefasst — die Korrektur
# passiert nur beim Erzeugen der Webfassungen und ist damit jederzeit
# nachvollziehbar und umkehrbar.
JOBS = [
    ("luzern-kapellbruecke.jpg", "hero", "luzern-kapellbruecke", [1920, 1280, 800], (16, 9), (1, 1, 1)),
    ("tour-morning-run.jpg", "tours", "tour-morning-run", [800, 480], (4, 3), (1, 1, 1)),
    ("tour-heritage.jpg", "tours", "tour-heritage", [800, 480], (4, 3), (1, 1, 1)),
    ("tour-hidden-gems.jpg", "tours", "tour-hidden-gems", [800, 480], (4, 3), (1, 1, 1)),
    ("tour-top-views.jpg", "tours", "tour-top-views", [800, 480], (4, 3), (1, 1, 1)),
    ("philippe-final.png", "team", "philippe", [560, 280], (1, 1), (1, 1, 1)),
]

JPG_QUALITY = 78
WEBP_QUALITY = 76


def apply_gains(im, gains):
    """Weissabgleich über einfache Kanalfaktoren."""
    if gains == (1, 1, 1):
        return im
    alpha = im.getchannel("A") if im.mode in ("RGBA", "LA") else None
    rgb = im.convert("RGB")
    r, g, b = rgb.split()
    r = r.point(lambda v, f=gains[0]: min(255, int(v * f)))
    g = g.point(lambda v, f=gains[1]: min(255, int(v * f)))
    b = b.point(lambda v, f=gains[2]: min(255, int(v * f)))
    out = Image.merge("RGB", (r, g, b))
    if alpha is not None:
        out.putalpha(alpha)
    return out


def build(src_name, folder, base, widths, ratio, gains=(1, 1, 1)):
    src_path = SRC / src_name
    if not src_path.exists():
        print(f"  ! Original fehlt: {src_path}")
        return
    im = Image.open(src_path)
    im = ImageOps.exif_transpose(im)          # Handy-Fotos korrekt drehen
    im = apply_gains(im, gains)
    has_alpha = im.mode in ("RGBA", "LA")

    if ratio:
        target_ratio = ratio[0] / ratio[1]
        w, h = im.size
        if w / h > target_ratio:              # zu breit -> links/rechts beschneiden
            new_w = int(h * target_ratio)
            left = (w - new_w) // 2
            im = im.crop((left, 0, left + new_w, h))
        else:                                 # zu hoch -> oben/unten beschneiden
            new_h = int(w / target_ratio)
            top = int((h - new_h) * 0.35)     # leicht oberhalb der Mitte schneiden
            im = im.crop((0, top, w, top + new_h))

    outdir = OUT / folder
    outdir.mkdir(parents=True, exist_ok=True)

    for width in widths:
        scale = width / im.width
        size = (width, max(1, round(im.height * scale)))
        resized = im.resize(size, Image.LANCZOS)

        suffix = "" if width == max(widths) else f"-{width}"
        webp_path = outdir / f"{base}{suffix}.webp"
        resized.save(webp_path, "WEBP", quality=WEBP_QUALITY, method=6)

        if has_alpha:
            fallback = outdir / f"{base}{suffix}.png"
            resized.save(fallback, "PNG", optimize=True)
        else:
            fallback = outdir / f"{base}{suffix}.jpg"
            resized.convert("RGB").save(
                fallback, "JPEG", quality=JPG_QUALITY, optimize=True, progressive=True
            )
        print(
            f"  {webp_path.relative_to(ROOT)} "
            f"({size[0]}x{size[1]}, {webp_path.stat().st_size/1024:.0f} kB webp / "
            f"{fallback.stat().st_size/1024:.0f} kB fallback)"
        )


def main():
    print("Bildoptimierung Run & See")
    for job in JOBS:
        print(f"- {job[0]}")
        build(*job)
    print("\nFertig. Originale unverändert unter assets/images/_originals/")


if __name__ == "__main__":
    main()
