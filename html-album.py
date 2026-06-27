#!/usr/bin/env python3
"""
html-album.py — HTML Fotoalbum Generator
Genereert een HTML-album vergelijkbaar met alm.agrarix.net

Vereisten:
    pip install Pillow

Gebruik:
    python html-album.py
    (leest html-album.json in dezelfde map)
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
PGM = "html-album"
VERSION = "2.0"

# ---------------------------------------------------------------------------
# Pillow (voor thumbnails)
# ---------------------------------------------------------------------------
try:
    from PIL import Image, ExifTags, ImageOps
    HAS_PIL = True
except ImportError:
    HAS_PIL = False

# ---------------------------------------------------------------------------
# Configuratie inlezen uit album.json
# ---------------------------------------------------------------------------
SCRIPT_DIR = Path(__file__).parent
CONFIG_FILE = SCRIPT_DIR / "html-album.json"

DEFAULTS = {
    "SLIDES_DIR": "slides",
    "THUMBS_DIR": "thumbs",
    "EXCLUDED": ["res"],
    "THUMBNAIL": "140x140",
    "SOURCE_DIR": "",
    "OUTPUT_DIR": "",
    "INDEX_FILE": "index.html",
    "LOG_FILE": "html-album.log",
}

def _laad_config(pad: Path) -> dict:
    """Lees html-album.json. Herstelt automatisch Windows-backslashes in paden."""
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
            print(f"FOUT: html-album.json is ongeldig: {e}")
            print("  Tip: gebruik forward slashes in paden: C:/pad/naar/map")
            print("  Tip: controleer of er komma's ontbreken tussen regels.")
            sys.exit(1)

if CONFIG_FILE.exists():
    cfg = {**DEFAULTS, **_laad_config(CONFIG_FILE)}
else:
    print("html-album.json niet gevonden, standaardwaarden worden gebruikt.")
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

EXCLUDED: set[str] = {
    x.lower() for x in (
        set(cfg["EXCLUDED"]) |
        {SLIDES_DIR_NAME, THUMBS_DIR_NAME, "slides", "thumbs", "slides_dir", "thumbs_dir"}
    )
}
IMAGE_EXTS = {".jpg", ".jpeg", ".png", ".gif"}

# Bepaal het logbestand-pad. Als het een relatieve bestandsnaam is, zet het in SCRIPT_DIR (applicatie-root).
cfg_log_file = cfg.get("LOG_FILE", "html-album.log")
if Path(cfg_log_file).is_absolute():
    LOG_FILE_PATH = Path(cfg_log_file.replace("\\", "/"))
else:
    LOG_FILE_PATH = SCRIPT_DIR / cfg_log_file

# Globale log-bestand handler
# (Wordt geïnitialiseerd in main)

def log_bericht(bericht: str) -> None:
    """Schrijft naar stdout én naar het logbestand html-album.log."""
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

def get_css() -> str:
    tw, th = THUMB_SIZE
    cell_w = tw + 10
    page_max_w = max(880, cell_w * 2 + 40)
    
    css_path = SCRIPT_DIR / "html-album.css"
    if css_path.exists():
        css_res = css_path.read_text(encoding="utf-8")
    else:
        css_res = "* { box-sizing: border-box; }"
    
    css_res = css_res.replace("max-width: 880px;", f"max-width: {page_max_w}px;")
    css_res = css_res.replace("width: 148px;", f"width: {cell_w}px;")
    css_res = css_res.replace("width: 138px;", f"width: {tw}px;")
    css_res = css_res.replace("height: 112px;", f"height: {th}px;")
    css_res = css_res.replace("max-width: 138px;", f"max-width: {tw}px;")
    css_res = css_res.replace("max-height: 112px;", f"max-height: {th}px;")
    css_res = css_res.replace("line-height: 112px;", f"line-height: {th}px;")
    
    if th > 140:
        folder_font_size = min(120, int(th * 0.4))
        css_res = css_res.replace("font-size: 44px;", f"font-size: {folder_font_size}px;")
        
    return css_res

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
            img = ImageOps.exif_transpose(img)
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

def get_exif_data(img_path: Path) -> dict:
    if not HAS_PIL:
        return {}
    try:
        with Image.open(img_path) as img:
            exif = img._getexif()
            if not exif:
                return {}
            data = {}
            for tag, val in exif.items():
                tag_name = ExifTags.TAGS.get(tag, tag)
                data[tag_name] = val
            return data
    except Exception:
        return {}

def get_formatted_exif(img_path: Path) -> str:
    raw_exif = get_exif_data(img_path)
    if not raw_exif:
        return ""
    
    parts = []
    
    # Camera model
    make = raw_exif.get("Make", "")
    model = raw_exif.get("Model", "")
    if model:
        model_str = str(model).strip()
        make_str = str(make).strip()
        if make_str and make_str.lower() not in model_str.lower():
            parts.append(f"📷 {make_str} {model_str}")
        else:
            parts.append(f"📷 {model_str}")
            
    # Datum / Tijd
    dt_orig = raw_exif.get("DateTimeOriginal")
    if dt_orig:
        try:
            dt = datetime.strptime(str(dt_orig).strip(), "%Y:%m:%d %H:%M:%S")
            parts.append(f"📅 {dt.strftime('%d-%m-%Y %H:%M')}")
        except Exception:
            parts.append(f"📅 {str(dt_orig).strip()}")
            
    # Belichtingsinstellingen (Aperture, Shutter, ISO, Focal Length)
    settings = []
    
    # Brandpuntsafstand
    focal = raw_exif.get("FocalLength")
    if focal is not None:
        try:
            if isinstance(focal, tuple) and len(focal) == 2:
                f_val = focal[0] / focal[1]
            else:
                f_val = float(focal)
            settings.append(f"{f_val:.0f}mm")
        except Exception:
            pass
            
    # Diafragma
    fnum = raw_exif.get("FNumber")
    if fnum is not None:
        try:
            if isinstance(fnum, tuple) and len(fnum) == 2:
                fn_val = fnum[0] / fnum[1]
            else:
                fn_val = float(fnum)
            settings.append(f"f/{fn_val:.1f}" if fn_val % 1 != 0 else f"f/{fn_val:.0f}")
        except Exception:
            pass
            
    # Sluitertijd
    exp = raw_exif.get("ExposureTime")
    if exp is not None:
        try:
            if isinstance(exp, tuple) and len(exp) == 2:
                num, den = exp
                if num == 1:
                    settings.append(f"1/{den}s")
                elif num > 1:
                    settings.append(f"{num/den:.1f}s")
                else:
                    settings.append(f"{num}/{den}s")
            else:
                exp_val = float(exp)
                if exp_val < 1.0:
                    recip = round(1.0 / exp_val)
                    settings.append(f"1/{recip}s")
                else:
                    settings.append(f"{exp_val:.1f}s")
        except Exception:
            pass
            
    # ISO
    iso = raw_exif.get("ISOSpeedRatings")
    if iso is not None:
        settings.append(f"ISO {iso}")
        
    if settings:
        parts.append("⚙️ " + " | ".join(settings))
        
    return "  •  ".join(parts)

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
    src_img_path: Path,
    css_href: str,
) -> None:
    prev_js = f'"{prev_slide}"' if prev_slide else "null"
    next_js = f'"{next_slide}"' if next_slide else "null"

    prev_btn = '<span class="nav-btn disabled" title="Geen vorige foto">&#8592;</span>'
    next_btn = '<span class="nav-btn disabled" title="Geen volgende foto">&#8594;</span>'
    if prev_slide:
        prev_btn = f'<a href="{prev_slide}" class="nav-btn" title="Vorige foto (&#8592;)">&#8592;</a>'
    if next_slide:
        next_btn = f'<a href="{next_slide}" class="nav-btn" title="Volgende foto (&#8594;)">&#8594;</a>'

    exif_str = get_formatted_exif(src_img_path)
    exif_html = f'<div class="slide-exif">{exif_str}</div>' if exif_str else ""

    html = f"""\
<!DOCTYPE html>
<html lang="nl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{img_fname} \u2014 {album_title}</title>
    <link rel="stylesheet" href="{css_href}">
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
        {exif_html}
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
    css_href: str,
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
        [d for d in src_dir.iterdir() if d.is_dir() and d.name.lower() not in EXCLUDED],
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
    <link rel="stylesheet" href="{css_href}">
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

    # Bereken relatieve pad naar OUTPUT_DIR root voor CSS link
    rel_parts = [p for p in out_dir.relative_to(OUTPUT_DIR).parts if p not in ('.', '/')]
    relative_path_to_root = "../" * len(rel_parts)
    
    index_css_href = f"{relative_path_to_root}html-album.css"
    slide_css_href = f"../{relative_path_to_root}html-album.css"

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
            img,
            slide_css_href,
        )
        log_bericht(f"    ✓ {fname}")

    generate_index_html(
        out_dir / INDEX_FILE_NAME,
        title,
        parent_index,
        src_dir,
        out_dir,
        index_css_href,
    )

    subdirs = sorted(
        [d for d in src_dir.iterdir() if d.is_dir() and d.name.lower() not in EXCLUDED],
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
        print("   Pas SOURCE_DIR aan in html-album.json")
        sys.exit(1)

    if not OUTPUT_DIR or str(OUTPUT_DIR) in ("", "."):
        print("\n❌ OUTPUT_DIR is niet ingesteld in html-album.json")
        sys.exit(1)
        
    # Maak output directory alvast aan voor logbestand
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    
    # Genereer en schrijf html-album.css naar de output directory
    try:
        (OUTPUT_DIR / "html-album.css").write_text(get_css(), encoding="utf-8")
    except Exception as exc:
        print(f"Kon html-album.css niet schrijven naar {OUTPUT_DIR}: {exc}")
    if LOG_FILE_PATH:
        LOG_FILE_PATH.parent.mkdir(parents=True, exist_ok=True)
        try:
            with open(LOG_FILE_PATH, "w", encoding="utf-8") as lf:
                lf.write(f"=== Album Generator Log {datetime.now().strftime('%d-%m-%Y %H:%M:%S')} ===\n")
        except Exception as exc:
            print(f"Kon logbestand niet maken op {LOG_FILE_PATH}: {exc}")

    log_bericht("HTML Fotoalbum Generator")
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
