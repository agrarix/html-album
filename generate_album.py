#!/usr/bin/env python3
"""
generate_album.py — HTML Fotoalbum Generator
Genereert een HTML-album vergelijkbaar met alm.agrarix.net

Vereisten:
    pip install Pillow

Gebruik:
    python generate_album.py
    (leest album.json in dezelfde map)
"""

import json
import re
import shutil
import sys
from datetime import datetime
from pathlib import Path

# Forceer UTF-8 output zodat cmd/PowerShell niet crasht op speciale tekens
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

# Programma details voor de footer
PGM = "generate_album"
VERSION = "2.0"

# ---------------------------------------------------------------------------
# Pillow (voor thumbnails)
# ---------------------------------------------------------------------------
try:
    from PIL import Image
    HAS_PIL = True
except ImportError:
    HAS_PIL = False

# ---------------------------------------------------------------------------
# Configuratie inlezen uit album.json
# ---------------------------------------------------------------------------
SCRIPT_DIR = Path(__file__).parent
CONFIG_FILE = SCRIPT_DIR / "album.json"

DEFAULTS = {
    "SLIDES_DIR": "slides",
    "THUMBS_DIR": "thumbs",
    "EXCLUDED": ["res"],
    "THUMBNAIL": "140x140",
    "SOURCE_DIR": "",
    "OUTPUT_DIR": "",
    "INDEX_FILE": "index.html",
    "LOG_FILE": "generate_album.log",
}

def _laad_config(pad: Path) -> dict:
    """Lees album.json. Herstelt automatisch Windows-backslashes in paden."""
    with open(pad, encoding="utf-8") as f:
        inhoud = f.read()
    try:
        return json.loads(inhoud)
    except json.JSONDecodeError:
        # Vervang backslashes buiten escape-sequenties door forward slashes
        hersteld = re.sub(
            r'("[^"]*"\s*:\s*"[^"]*?)\\([^"]*")',
            lambda m: m.group(0).replace("\\", "/"),
            inhoud,
        )
        try:
            return json.loads(hersteld)
        except json.JSONDecodeError as e:
            print(f"FOUT: album.json is ongeldig: {e}")
            print("  Tip: gebruik forward slashes in paden: C:/pad/naar/map")
            print("  Tip: controleer of er komma's ontbreken tussen regels.")
            sys.exit(1)

if CONFIG_FILE.exists():
    cfg = {**DEFAULTS, **_laad_config(CONFIG_FILE)}
else:
    print("album.json niet gevonden, standaardwaarden worden gebruikt.")
    cfg = DEFAULTS

SLIDES_DIR_NAME: str = cfg["SLIDES_DIR"]
THUMBS_DIR_NAME: str = cfg["THUMBS_DIR"]
INDEX_FILE_NAME: str = cfg["INDEX_FILE"]
SOURCE_DIR = Path(cfg["SOURCE_DIR"].replace("\\", "/")) if cfg["SOURCE_DIR"] else Path()
OUTPUT_DIR = Path(cfg["OUTPUT_DIR"].replace("\\", "/")) if cfg["OUTPUT_DIR"] else Path()

try:
    _w, _h = map(int, cfg["THUMBNAIL"].lower().split("x"))
    THUMB_SIZE = (_w, _h)
except ValueError:
    THUMB_SIZE = (140, 140)

EXCLUDED: set[str] = set(cfg["EXCLUDED"]) | {SLIDES_DIR_NAME, THUMBS_DIR_NAME}
IMAGE_EXTS = {".jpg", ".jpeg", ".png", ".gif"}

# Bepaal het logbestand-pad. Als het een relatieve bestandsnaam is, zet het in SCRIPT_DIR (applicatie-root).
cfg_log_file = cfg.get("LOG_FILE", "generate_album.log")
if Path(cfg_log_file).is_absolute():
    LOG_FILE_PATH = Path(cfg_log_file.replace("\\", "/"))
else:
    LOG_FILE_PATH = SCRIPT_DIR / cfg_log_file

# Globale log-bestand handler
# (Wordt geïnitialiseerd in main)

def log_bericht(bericht: str) -> None:
    """Schrijft naar stdout én naar het logbestand generate_album.log."""
    # Print direct naar het scherm (UTF-8)
    print(bericht)
    sys.stdout.flush()
    
    # Schrijf naar logbestand in de uitvoermap (indien geconfigureerd en beschikbaar)
    if LOG_FILE_PATH:
        try:
            with open(LOG_FILE_PATH, "a", encoding="utf-8") as lf:
                # Strip eventuele ansi-achtige tekens of print gewoon platte tekst
                schoon_bericht = bericht.replace("\U0001f4c2", "[MAP]").replace("\u2713", "[OK]").replace("\u2705", "[KLAAR]")
                lf.write(f"[{datetime.now().strftime('%H:%M:%S')}] {schoon_bericht}\n")
        except Exception:
            pass

# ---------------------------------------------------------------------------
# Gedeelde CSS — inlinegeplaatst in elke gegenereerde pagina
# ---------------------------------------------------------------------------
CSS = """\
* { box-sizing: border-box; margin: 0; padding: 0; }
body {
    font-family: Verdana, Arial, Helvetica, sans-serif;
    font-size: 12px;
    color: #444;
    background-color: #cccccc;
    background-image: linear-gradient(to bottom, #aaaaaa 0px, #cccccc 80px);
    background-repeat: no-repeat;
    min-height: 100vh;
}
a { color: #444; text-decoration: none; }
a:hover { color: #000; text-decoration: underline; }

.page-wrap {
    max-width: 880px;
    margin: 0 auto;
    padding: 10px 10px 20px;
}

/* Header */
.album-header {
    display: flex;
    align-items: center;
    gap: 8px;
    background: linear-gradient(to bottom, #eeeeee 0%, #d4d4d4 100%);
    border: 1px solid #aaaaaa;
    border-radius: 4px;
    padding: 6px 10px;
    margin-bottom: 10px;
    min-height: 42px;
    box-shadow: 0 1px 3px rgba(0,0,0,0.15);
}
.nav-btn {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    width: 28px;
    height: 28px;
    background: linear-gradient(to bottom, #dddddd, #c0c0c0);
    border: 1px solid #999;
    border-radius: 3px;
    font-size: 16px;
    flex-shrink: 0;
    color: #333;
    cursor: pointer;
    user-select: none;
}
.nav-btn:hover {
    background: linear-gradient(to bottom, #cccccc, #b0b0b0);
    color: #000;
    text-decoration: none;
}
.nav-btn.disabled { opacity: 0.35; pointer-events: none; }
.header-title {
    flex-grow: 1;
    font-size: 14px;
    font-weight: bold;
    color: #222;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
}
.header-nav { display: flex; gap: 4px; flex-shrink: 0; }

/* Thumbnailraster */
.thumb-grid {
    display: flex;
    flex-wrap: wrap;
    gap: 5px;
}
.thumb-cell {
    width: 148px;
    background: #e8e8e8;
    border: 1px solid #bbbbbb;
    border-radius: 3px;
    padding: 4px;
    text-align: center;
    transition: border-color 0.15s, background 0.15s;
}
.thumb-cell:hover { border-color: #777; background: #ddd; }
.thumb-cell a { display: block; color: inherit; text-decoration: none; }
.thumb-cell a:hover { text-decoration: none; }

.thumb-img-wrap {
    width: 138px;
    height: 112px;
    display: flex;
    align-items: center;
    justify-content: center;
    overflow: hidden;
    margin: 0 auto;
    background: #d4d4d4;
}
.thumb-cell img {
    max-width: 138px;
    max-height: 112px;
    display: block;
}
.thumb-label {
    margin-top: 4px;
    font-size: 10px;
    color: #555;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
    max-width: 138px;
    padding: 0 2px;
}

/* Mappenkaartjes */
.thumb-cell.folder { background: #dce8f0; border-color: #a8c4d8; }
.thumb-cell.folder:hover { border-color: #5588aa; }
.folder-icon { font-size: 44px; line-height: 112px; }

/* Slideweergave */
.slide-wrap { text-align: center; margin-top: 4px; }
.slide-image {
    max-width: 100%;
    height: auto;
    border: 1px solid #aaaaaa;
    box-shadow: 0 2px 8px rgba(0,0,0,0.25);
}
.slide-info { margin-top: 8px; font-size: 11px; color: #666; }

/* Voettekst */
.footer { margin-top: 14px; font-size: 10px; color: #888; text-align: center; }
"""

# ---------------------------------------------------------------------------
# Controleer of thumbnail opnieuw gegenereerd moet worden
# ---------------------------------------------------------------------------
def needs_thumbnail_regeneration(thumb_path: Path) -> bool:
    if not thumb_path.exists():
        return True
    if not HAS_PIL:
        return False
    try:
        with Image.open(thumb_path) as img:
            return img.size != THUMB_SIZE
    except Exception:
        return True

# ---------------------------------------------------------------------------
# Thumbnail maken met Pillow (bijgesneden vulling)
# ---------------------------------------------------------------------------
def make_thumbnail(src: Path, dst: Path) -> None:
    if not HAS_PIL:
        try:
            shutil.copy2(src, dst)
        except Exception as e:
            log_bericht(f"    ⚠  Kon bestand niet kopiëren als thumbnail fallback: {e}")
        return
    try:
        with Image.open(src) as img:
            img = img.convert("RGB")
            tw, th = THUMB_SIZE
            img_ratio = img.width / img.height
            target_ratio = tw / th
            if img_ratio > target_ratio:
                new_h = th
                new_w = round(img.width * new_h / img.height)
            else:
                new_w = tw
                new_h = round(img.height * new_w / img.width)
            img = img.resize((new_w, new_h), Image.LANCZOS)
            left = (new_w - tw) // 2
            top  = (new_h - th) // 2
            img = img.crop((left, top, left + tw, top + th))
            img.save(dst, "JPEG", quality=85, optimize=True)
    except PermissionError as pe:
        log_bericht(f"    ⚠  Toegangsweigering (bestand in gebruik) bij maken thumbnail voor '{src.name}': {pe}")
    except Exception as exc:
        log_bericht(f"    ⚠  Thumbnail mislukt voor '{src.name}': {exc}")
        try:
            shutil.copy2(src, dst)
        except Exception:
            pass

# ---------------------------------------------------------------------------
# Genereer HTML voor één slide-pagina
# ---------------------------------------------------------------------------
def generate_slide_html(
    out_file: Path,
    img_fname: str,
    prev_slide: str,
    next_slide: str,
    index_href: str,
    album_title: str,
) -> None:
    prev_js = f'"{prev_slide}"' if prev_slide else "null"
    next_js = f'"{next_slide}"' if next_slide else "null"

    prev_btn = '<span class="nav-btn disabled" title="Geen vorige foto">&#8592;</span>'
    next_btn = '<span class="nav-btn disabled" title="Geen volgende foto">&#8594;</span>'
    if prev_slide:
        prev_btn = f'<a href="{prev_slide}" class="nav-btn" title="Vorige foto (&#8592;)">&#8592;</a>'
    if next_slide:
        next_btn = f'<a href="{next_slide}" class="nav-btn" title="Volgende foto (&#8594;)">&#8594;</a>'

    html = f"""\
<!DOCTYPE html>
<html lang="nl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{img_fname} \u2014 {album_title}</title>
    <style>
{CSS}
    </style>
</head>
<body>
<div class="page-wrap">
    <div class="album-header">
        <a href="{index_href}" class="nav-btn" title="Terug naar album (Esc)">&#8593;</a>
        <span class="header-title">{album_title} \u2014 {img_fname}</span>
        <div class="header-nav">
            {prev_btn}
            {next_btn}
        </div>
    </div>
    <div class="slide-wrap">
        <img src="../{img_fname}" alt="{img_fname}" class="slide-image">
        <div class="slide-info">{img_fname}</div>
    </div>
</div>
<script>
var prevSlide = {prev_js};
var nextSlide = {next_js};
document.addEventListener('keydown', function(e) {{
    switch (e.key) {{
        case 'ArrowLeft':  case 'a': case 'A':
            if (prevSlide) window.location = prevSlide; break;
        case 'ArrowRight': case 'd': case 'D': case ' ':
            if (nextSlide) window.location = nextSlide; break;
        case 'Backspace':  case 'Escape': case 'u': case 'U':
            window.location = '{index_href}'; break;
    }}
}});
</script>
</body>
</html>
"""
    out_file.write_text(html, encoding="utf-8")

# ---------------------------------------------------------------------------
# Genereer index.html voor één map
# ---------------------------------------------------------------------------
def generate_index_html(
    index_file: Path,
    title: str,
    up_href: str,
    src_dir: Path,
    out_dir: Path,
) -> None:
    generated_date = datetime.now().strftime("%d-%m-%Y %H:%M")

    up_btn = ""
    if up_href:
        up_btn = f'<a href="{up_href}" class="nav-btn" title="Omhoog naar bovenliggende map">&#8593;</a>'

    images = sorted(
        [f for f in src_dir.iterdir() if f.is_file() and f.suffix.lower() in IMAGE_EXTS],
        key=lambda f: f.name.lower(),
    )

    img_cells: list[str] = []
    for img in images:
        fname       = img.name
        name_no_ext = img.stem
        thumb_rel   = f"{THUMBS_DIR_NAME}/{name_no_ext}_thumb.jpg"
        slide_rel   = f"{SLIDES_DIR_NAME}/{name_no_ext}.html"
        img_cells.append(
            f'        <div class="thumb-cell">\n'
            f'            <a href="{slide_rel}" title="{fname}">\n'
            f'                <div class="thumb-img-wrap">\n'
            f'                    <img src="{thumb_rel}" alt="{fname}" loading="lazy">\n'
            f'                </div>\n'
            f'                <div class="thumb-label">{fname}</div>\n'
            f'            </a>\n'
            f'        </div>'
        )

    subdirs = sorted(
        [d for d in src_dir.iterdir() if d.is_dir() and d.name not in EXCLUDED],
        key=lambda d: d.name.lower(),
    )

    dir_cells: list[str] = []
    for subdir in subdirs:
        dname            = subdir.name
        folder_thumb_dst = out_dir / THUMBS_DIR_NAME / f"folder_{dname}_thumb.jpg"

        first_img = next(
            (f for f in sorted(subdir.iterdir(), key=lambda x: x.name.lower()) if f.is_file() and f.suffix.lower() in IMAGE_EXTS),
            None,
        )

        if first_img:
            if needs_thumbnail_regeneration(folder_thumb_dst):
                make_thumbnail(first_img, folder_thumb_dst)
            thumb_tag = f'<img src="{THUMBS_DIR_NAME}/folder_{dname}_thumb.jpg" alt="{dname}" loading="lazy">'
            label = f"\U0001f4c1 {dname}"
        else:
            thumb_tag = '<div class="folder-icon">\U0001f4c1</div>'
            label     = dname

        dir_cells.append(
            f'        <div class="thumb-cell folder">\n'
            f'            <a href="{dname}/{INDEX_FILE_NAME}" title="{dname}">\n'
            f'                <div class="thumb-img-wrap">\n'
            f'                    {thumb_tag}\n'
            f'                </div>\n'
            f'                <div class="thumb-label">{label}</div>\n'
            f'            </a>\n'
            f'        </div>'
        )

    all_cells = "\n".join(img_cells + dir_cells)

    # Formateer datum en tijd
    now = datetime.now()
    date_str = now.strftime("%d-%m-%Y")
    time_str = now.strftime("%H:%M")

    html = f"""\
<!DOCTYPE html>
<html lang="nl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta name="keywords" content="fotoalbum,gallery,foto,online">
    <title>{title}</title>
    <style>
{CSS}
    </style>
</head>
<body>
<div class="page-wrap">
    <div class="album-header">
        {up_btn}
        <span class="header-title">\U0001f4f7 {title}</span>
    </div>
    <div class="thumb-grid">
{all_cells}
    </div>
    <div class="footer">Generated by {PGM} v{VERSION} {date_str} {time_str}</div>
</div>
</body>
</html>
"""
    index_file.write_text(html, encoding="utf-8")

# ---------------------------------------------------------------------------
# Recursieve mapverwerking
# ---------------------------------------------------------------------------
def process_dir(
    src_dir: Path,
    out_dir: Path,
    parent_index: str,
    title: str,
) -> None:
    log_bericht(f"\U0001f4c2  {title}")
    log_bericht(f"    bron : {src_dir}")
    log_bericht(f"    doel : {out_dir}")

    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / SLIDES_DIR_NAME).mkdir(exist_ok=True)
    (out_dir / THUMBS_DIR_NAME).mkdir(exist_ok=True)

    images = sorted(
        [f for f in src_dir.iterdir() if f.is_file() and f.suffix.lower() in IMAGE_EXTS],
        key=lambda f: f.name.lower(),
    )
    log_bericht(f"    foto's: {len(images)}")

    for i, img in enumerate(images):
        fname       = img.name
        name_no_ext = img.stem

        dst_img = out_dir / fname
        if not dst_img.exists():
            try:
                shutil.copy2(img, dst_img)
            except PermissionError as pe:
                log_bericht(f"    ⚠  Toegangsweigering (bestand in gebruik) bij kopiëren van '{fname}': {pe}")
                continue
            except Exception as e:
                log_bericht(f"    ⚠  Fout bij kopiëren van '{fname}': {e}")
                continue

        thumb = out_dir / THUMBS_DIR_NAME / f"{name_no_ext}_thumb.jpg"
        if needs_thumbnail_regeneration(thumb):
            make_thumbnail(img, thumb)

        prev_slide = images[i - 1].stem + ".html" if i > 0 else ""
        next_slide = images[i + 1].stem + ".html" if i < len(images) - 1 else ""

        generate_slide_html(
            out_dir / SLIDES_DIR_NAME / f"{name_no_ext}.html",
            fname,
            prev_slide,
            next_slide,
            f"../{INDEX_FILE_NAME}",
            title,
        )
        log_bericht(f"    ✓ {fname}")

    generate_index_html(
        out_dir / INDEX_FILE_NAME,
        title,
        parent_index,
        src_dir,
        out_dir,
    )

    subdirs = sorted(
        [d for d in src_dir.iterdir() if d.is_dir() and d.name not in EXCLUDED],
        key=lambda d: d.name.lower(),
    )
    for subdir in subdirs:
        process_dir(
            subdir,
            out_dir / subdir.name,
            f"../{INDEX_FILE_NAME}",
            subdir.name,
        )

# ---------------------------------------------------------------------------
# Startpunt
# ---------------------------------------------------------------------------
def main() -> None:
    global LOG_FILE_PATH
    
    if not SOURCE_DIR or not SOURCE_DIR.exists():
        print(f"\n❌ Bronmap niet gevonden: {SOURCE_DIR}")
        print("   Pas SOURCE_DIR aan in album.json")
        sys.exit(1)

    if not OUTPUT_DIR or str(OUTPUT_DIR) in ("", "."):
        print("\n❌ OUTPUT_DIR is niet ingesteld in album.json")
        sys.exit(1)
        
    # Maak output directory alvast aan voor logbestand
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    if LOG_FILE_PATH:
        LOG_FILE_PATH.parent.mkdir(parents=True, exist_ok=True)
        try:
            with open(LOG_FILE_PATH, "w", encoding="utf-8") as lf:
                lf.write(f"=== Album Generator Log {datetime.now().strftime('%d-%m-%Y %H:%M:%S')} ===\n")
        except Exception as exc:
            print(f"Kon logbestand niet maken op {LOG_FILE_PATH}: {exc}")

    log_bericht("Album Generator")
    log_bericht("─" * 36)
    log_bericht(f"Bron      : {SOURCE_DIR}")
    log_bericht(f"Uitvoer   : {OUTPUT_DIR}")
    log_bericht(f"Logbestand: {LOG_FILE_PATH}")
    log_bericht(f"Thumbnail : {THUMB_SIZE[0]}x{THUMB_SIZE[1]}")
    log_bericht(f"Uitsluit  : {', '.join(sorted(EXCLUDED))}")
    if HAS_PIL:
        try:
            from PIL import __version__ as pil_ver
            log_bericht(f"Pillow    : ✓ (v{pil_ver})")
        except Exception:
            log_bericht("Pillow    : ✓")
    else:
        log_bericht("Pillow    : ✗ niet gevonden — installeer met: pip install Pillow")
        log_bericht("            Zonder Pillow worden originele bestanden als thumbnail gebruikt.")
    log_bericht("─" * 36)

    root_title = SOURCE_DIR.name
    process_dir(SOURCE_DIR, OUTPUT_DIR, "", root_title)

    log_bericht("\n" + "═" * 36)
    log_bericht("✅  Album gegenereerd!")
    log_bericht(f"    Open: {OUTPUT_DIR / INDEX_FILE_NAME}")
    log_bericht("═" * 36)

if __name__ == "__main__":
    main()
