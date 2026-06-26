#!/bin/bash

# Album Generator Script
# Generates an HTML photo album similar to alm.agrarix.net
# - Recursive: every subdirectory gets its own index.html
# - Separate OUTPUT_DIR from SOURCE_DIR
# - prev/next navigation on slide pages with keyboard support

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
CONFIG_FILE="$SCRIPT_DIR/album.json"
PGM="generate_album"
VERSION="2.0"

# ---------------------------------------------------------------------------
# Read configuration from album.json
# ---------------------------------------------------------------------------
if [ -f "$CONFIG_FILE" ]; then
    EXCLUDED=$(grep -o '"EXCLUDED"[[:space:]]*:[[:space:]]*\[.*\]' "$CONFIG_FILE" \
        | sed 's/.*\[\(.*\)\]/\1/' | tr -d '",' | tr -s ' ')
    THUMBNAIL=$(grep -o '"THUMBNAIL"[[:space:]]*:[[:space:]]*"[^"]*"' "$CONFIG_FILE" \
        | sed 's/.*"\([^"]*\)"/\1/')
    SOURCE_DIR=$(grep -o '"SOURCE_DIR"[[:space:]]*:[[:space:]]*"[^"]*"' "$CONFIG_FILE" \
        | sed 's/.*"\([^"]*\)"/\1/')
    OUTPUT_DIR=$(grep -o '"OUTPUT_DIR"[[:space:]]*:[[:space:]]*"[^"]*"' "$CONFIG_FILE" \
        | sed 's/.*"\([^"]*\)"/\1/')
    SLIDES_DIR_NAME=$(grep -o '"SLIDES_DIR"[[:space:]]*:[[:space:]]*"[^"]*"' "$CONFIG_FILE" \
        | sed 's/.*"\([^"]*\)"/\1/')
    THUMBS_DIR_NAME=$(grep -o '"THUMBS_DIR"[[:space:]]*:[[:space:]]*"[^"]*"' "$CONFIG_FILE" \
        | sed 's/.*"\([^"]*\)"/\1/')
    INDEX_FILE_NAME=$(grep -o '"INDEX_FILE"[[:space:]]*:[[:space:]]*"[^"]*"' "$CONFIG_FILE" \
        | sed 's/.*"\([^"]*\)"/\1/')
else
    echo "⚠  Configuratiebestand niet gevonden, standaardwaarden worden gebruikt."
    EXCLUDED="res"
    THUMBNAIL="140x140"
    SOURCE_DIR="/mnt/nas/WWW/domains/alm.agrarix.net/pages"
    OUTPUT_DIR="/tmp/album_output"
    SLIDES_DIR_NAME="slides"
    THUMBS_DIR_NAME="thumbs"
    INDEX_FILE_NAME="index.html"
fi

# Voeg slides/thumbs toe aan uitsluitlijst
EXCLUDED="$EXCLUDED $SLIDES_DIR_NAME $THUMBS_DIR_NAME"

echo "Album Generator"
echo "────────────────────────────────"
echo "Bron       : $SOURCE_DIR"
echo "Uitvoer    : $OUTPUT_DIR"
echo "Thumbnail  : $THUMBNAIL"
echo "Uitsluit   : $EXCLUDED"
echo "────────────────────────────────"
echo ""

# ---------------------------------------------------------------------------
# Hulpfuncties
# ---------------------------------------------------------------------------

# Genereer thumbnail; valt terug op kopie als ImageMagick niet beschikbaar is
generate_thumbnail() {
    local input="$1"
    local output="$2"
    # Probeer eerst bijgesneden (crop) thumbnail, dan gewone resize, dan gewoon kopiëren
    convert "$input" -thumbnail "${THUMBNAIL}^" -gravity center \
        -extent "$THUMBNAIL" "$output" 2>/dev/null \
    || convert "$input" -thumbnail "$THUMBNAIL" "$output" 2>/dev/null \
    || cp "$input" "$output"
}

# Controleer of een mapnaam in de uitsluitlijst staat
is_excluded() {
    local name="$1"
    for ex in $EXCLUDED; do
        [ "$name" = "$ex" ] && return 0
    done
    return 1
}

# ---------------------------------------------------------------------------
# CSS — gedeeld stijlblad (inlinegeplaatst in elke pagina)
# ---------------------------------------------------------------------------
get_css() {
cat << 'CSSEOF'
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

/* Paginakader */
.page-wrap {
    max-width: 880px;
    margin: 0 auto;
    padding: 10px 10px 20px;
}

/* ── Header ── */
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
.nav-btn:hover { background: linear-gradient(to bottom, #cccccc, #b0b0b0); color: #000; text-decoration: none; }
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

/* ── Thumbnailraster ── */
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

/* Map-specifiek */
.thumb-cell.folder { background: #dce8f0; border-color: #a8c4d8; }
.thumb-cell.folder:hover { border-color: #5588aa; }
.folder-icon {
    font-size: 44px;
    line-height: 112px;
}

/* ── Slideweergave ── */
.slide-wrap { text-align: center; margin-top: 4px; }
.slide-image {
    max-width: 100%;
    height: auto;
    border: 1px solid #aaaaaa;
    box-shadow: 0 2px 8px rgba(0,0,0,0.25);
}
.slide-info {
    margin-top: 8px;
    font-size: 11px;
    color: #666;
}

/* ── Voettekst ── */
.footer {
    margin-top: 14px;
    font-size: 10px;
    color: #888;
    text-align: center;
}
CSSEOF
}

# ---------------------------------------------------------------------------
# Genereer een slide-HTML-pagina voor één foto
# ---------------------------------------------------------------------------
# Argumenten:
#   $1  Uitvoerbestand (volledig pad)
#   $2  Bestandsnaam van de afbeelding (basename)
#   $3  Relatief pad naar vorige slide (of leeg)
#   $4  Relatief pad naar volgende slide (of leeg)
#   $5  Relatief pad terug naar index.html
#   $6  Albumnaam (voor titelbalk)
generate_slide() {
    local out_file="$1"
    local img_fname="$2"
    local prev_slide="$3"
    local next_slide="$4"
    local index_href="$5"
    local album_title="$6"

    local css
    css=$(get_css)

    # JavaScript-waarden voor keyboard-navigatie
    local prev_js="null"
    local next_js="null"
    [ -n "$prev_slide" ] && prev_js="\"$prev_slide\""
    [ -n "$next_slide" ] && next_js="\"$next_slide\""

    # HTML voor navigatieknoppen
    local prev_btn="<span class=\"nav-btn disabled\" title=\"Geen vorige foto\">&#8592;</span>"
    local next_btn="<span class=\"nav-btn disabled\" title=\"Geen volgende foto\">&#8594;</span>"
    [ -n "$prev_slide" ] && prev_btn="<a href=\"$prev_slide\" class=\"nav-btn\" title=\"Vorige foto (&#8592;)\">&#8592;</a>"
    [ -n "$next_slide" ] && next_btn="<a href=\"$next_slide\" class=\"nav-btn\" title=\"Volgende foto (&#8594;)\">&#8594;</a>"

    cat > "$out_file" << SLIDEEOF
<!DOCTYPE html>
<html lang="nl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>${img_fname} — ${album_title}</title>
    <style>
${css}
    </style>
</head>
<body>
<div class="page-wrap">
    <div class="album-header">
        <a href="${index_href}" class="nav-btn" title="Terug naar album (Esc)">&#8593;</a>
        <span class="header-title">${album_title} — ${img_fname}</span>
        <div class="header-nav">
            ${prev_btn}
            ${next_btn}
        </div>
    </div>
    <div class="slide-wrap">
        <img src="../${img_fname}" alt="${img_fname}" class="slide-image">
        <div class="slide-info">${img_fname}</div>
    </div>
</div>
<script>
var prevSlide = ${prev_js};
var nextSlide = ${next_js};
document.addEventListener('keydown', function(e) {
    switch (e.key) {
        case 'ArrowLeft':
        case 'a':
        case 'A':
            if (prevSlide) window.location = prevSlide;
            break;
        case 'ArrowRight':
        case 'd':
        case 'D':
        case ' ':
            if (nextSlide) window.location = nextSlide;
            break;
        case 'Backspace':
        case 'Escape':
        case 'u':
        case 'U':
            window.location = '${index_href}';
            break;
    }
});
</script>
</body>
</html>
SLIDEEOF
}

# ---------------------------------------------------------------------------
# Genereer index.html voor één map
# ---------------------------------------------------------------------------
# Argumenten:
#   $1  Uitvoerbestand (volledig pad)
#   $2  Maptitel
#   $3  Relatief pad naar bovenliggende index (of leeg bij root)
#   $4  Bronmap (voor zoeken naar bestanden)
#   $5  Uitvoermap (voor thumbnailpaden)
generate_index() {
    local index_file="$1"
    local title="$2"
    local up_href="$3"
    local src_dir="$4"
    local out_dir="$5"

    local css
    css=$(get_css)

    local date_str
    local time_str
    date_str=$(date '+%d-%m-%Y')
    time_str=$(date '+%H:%M')

    # Knop "omhoog" (alleen als er een bovenliggende map is)
    local up_btn=""
    [ -n "$up_href" ] && up_btn="<a href=\"${up_href}\" class=\"nav-btn\" title=\"Omhoog naar bovenliggende map\">&#8593;</a>"

    # ── Begin HTML ──────────────────────────────────────────────────────────
    cat > "$index_file" << IDXEOF
<!DOCTYPE html>
<html lang="nl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta name="keywords" content="fotoalbum,gallery,foto,online">
    <title>${title}</title>
    <style>
${css}
    </style>
</head>
<body>
<div class="page-wrap">
    <div class="album-header">
        ${up_btn}
        <span class="header-title">📷 ${title}</span>
    </div>
    <div class="thumb-grid">
IDXEOF

    # ── Foto's ──────────────────────────────────────────────────────────────
    while IFS= read -r -d '' img; do
        local fname
        fname=$(basename "$img")
        local name_no_ext="${fname%.*}"
        local thumb_rel="${THUMBS_DIR_NAME}/${name_no_ext}_thumb.jpg"
        local slide_rel="${SLIDES_DIR_NAME}/${name_no_ext}.html"

        cat >> "$index_file" << IMGEOF
        <div class="thumb-cell">
            <a href="${slide_rel}" title="${fname}">
                <div class="thumb-img-wrap">
                    <img src="${thumb_rel}" alt="${fname}" loading="lazy">
                </div>
                <div class="thumb-label">${fname}</div>
            </a>
        </div>
IMGEOF
    done < <(find "$src_dir" -maxdepth 1 -type f \
        \( -iname "*.jpg" -o -iname "*.jpeg" -o -iname "*.png" -o -iname "*.gif" \) \
        -print0 | sort -z)

    # ── Submappen ────────────────────────────────────────────────────────────
    while IFS= read -r -d '' subdir; do
        local dname
        dname=$(basename "$subdir")
        is_excluded "$dname" && continue

        # Zoek eerste foto in de submap als mappreview
        local first_img
        first_img=$(find "$subdir" -maxdepth 1 -type f \
            \( -iname "*.jpg" -o -iname "*.jpeg" -o -iname "*.png" \) \
            | sort | head -1)

        local folder_thumb="${out_dir}/${THUMBS_DIR_NAME}/folder_${dname}_thumb.jpg"

        if [ -n "$first_img" ]; then
            [ ! -f "$folder_thumb" ] && generate_thumbnail "$first_img" "$folder_thumb"
            cat >> "$index_file" << DIRIMGEOF
        <div class="thumb-cell folder">
            <a href="${dname}/${INDEX_FILE_NAME}" title="${dname}">
                <div class="thumb-img-wrap">
                    <img src="${THUMBS_DIR_NAME}/folder_${dname}_thumb.jpg" alt="${dname}" loading="lazy">
                </div>
                <div class="thumb-label">📁 ${dname}</div>
            </a>
        </div>
DIRIMGEOF
        else
            cat >> "$index_file" << DIRICNEOF
        <div class="thumb-cell folder">
            <a href="${dname}/${INDEX_FILE_NAME}" title="${dname}">
                <div class="thumb-img-wrap">
                    <div class="folder-icon">📁</div>
                </div>
                <div class="thumb-label">${dname}</div>
            </a>
        </div>
DIRICNEOF
        fi
    done < <(find "$src_dir" -maxdepth 1 -mindepth 1 -type d -print0 | sort -z)

    # ── Einde HTML ───────────────────────────────────────────────────────────
    cat >> "$index_file" << IDXENDEOF
    </div>
    <div class="footer">Generated by ${PGM} v${VERSION} ${date_str} ${time_str}</div>
</div>
</body>
</html>
IDXENDEOF
}

# ---------------------------------------------------------------------------
# Hoofdfunctie — recursief verwerken van een map
# ---------------------------------------------------------------------------
# Argumenten:
#   $1  Bronmap
#   $2  Uitvoermap
#   $3  Relatief pad naar bovenliggende index (of leeg bij root)
#   $4  Naam/titel van deze map
process_dir() {
    local src_dir="$1"
    local out_dir="$2"
    local parent_index="$3"
    local title="$4"

    echo "📂  $title"
    echo "    bron : $src_dir"
    echo "    doel : $out_dir"

    mkdir -p "$out_dir"
    mkdir -p "$out_dir/$SLIDES_DIR_NAME"
    mkdir -p "$out_dir/$THUMBS_DIR_NAME"

    # ── Verzamel gesorteerde lijst van afbeeldingen ──────────────────────────
    local images=()
    while IFS= read -r -d '' f; do
        images+=("$f")
    done < <(find "$src_dir" -maxdepth 1 -type f \
        \( -iname "*.jpg" -o -iname "*.jpeg" -o -iname "*.png" -o -iname "*.gif" \) \
        -print0 | sort -z)

    local count=${#images[@]}
    echo "    foto's: $count"

    # ── Genereer slide-pagina per foto ───────────────────────────────────────
    for (( i=0; i<count; i++ )); do
        local img="${images[$i]}"
        local fname
        fname=$(basename "$img")
        local name_no_ext="${fname%.*}"

        # Kopieer origineel naar uitvoermap
        cp -n "$img" "$out_dir/$fname"

        # Maak thumbnail (sla over als al bestaat)
        local thumb="$out_dir/$THUMBS_DIR_NAME/${name_no_ext}_thumb.jpg"
        [ ! -f "$thumb" ] && generate_thumbnail "$img" "$thumb"

        # Bepaal vorige/volgende slide
        local prev_slide=""
        local next_slide=""
        if (( i > 0 )); then
            local prev_name
            prev_name=$(basename "${images[$((i-1))]}")
            prev_slide="${prev_name%.*}.html"
        fi
        if (( i < count-1 )); then
            local next_name
            next_name=$(basename "${images[$((i+1))]}")
            next_slide="${next_name%.*}.html"
        fi

        generate_slide \
            "$out_dir/$SLIDES_DIR_NAME/${name_no_ext}.html" \
            "$fname" \
            "$prev_slide" \
            "$next_slide" \
            "../$INDEX_FILE_NAME" \
            "$title"

        echo "    ✓ $fname"
    done

    # ── Genereer index.html voor deze map ────────────────────────────────────
    generate_index \
        "$out_dir/$INDEX_FILE_NAME" \
        "$title" \
        "$parent_index" \
        "$src_dir" \
        "$out_dir"

    # ── Recursief verwerken van submappen ─────────────────────────────────────
    while IFS= read -r -d '' subdir; do
        local dname
        dname=$(basename "$subdir")
        is_excluded "$dname" && continue
        echo ""
        process_dir \
            "$subdir" \
            "$out_dir/$dname" \
            "../$INDEX_FILE_NAME" \
            "$dname"
    done < <(find "$src_dir" -maxdepth 1 -mindepth 1 -type d -print0 | sort -z)
}

# ---------------------------------------------------------------------------
# Startpunt
# ---------------------------------------------------------------------------
if [ ! -d "$SOURCE_DIR" ]; then
    echo "❌ Bronmap niet gevonden: $SOURCE_DIR"
    exit 1
fi

ROOT_TITLE=$(basename "$SOURCE_DIR")
process_dir "$SOURCE_DIR" "$OUTPUT_DIR" "" "$ROOT_TITLE"

echo ""
echo "════════════════════════════════"
echo "✅  Album gegenereerd!"
echo "    Open: $OUTPUT_DIR/$INDEX_FILE_NAME"
echo "════════════════════════════════"
