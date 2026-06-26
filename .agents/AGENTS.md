# Project: HTML Fotoalbum Generator

## Doel
Een tool die automatisch een statisch HTML-fotoalbum genereert vanuit een map met JPEG-afbeeldingen. Gebaseerd op de stijl van [alm.agrarix.net](http://alm.agrarix.net).

---

## Projectstructuur

```
album/
├── .agents/
│   └── AGENTS.md          # Dit bestand (automatisch ingelezen door Antigravity)
├── README.md              # Projectdocumentatie voor mensen
├── album.json             # Configuratiebestand
├── generate_album.sh      # Bash-generatorscript (primair script)
├── generate_album.py      # Python-versie van het generatorscript
└── requirements.txt       # Python dependencies
```

---

## Configuratie (`album.json`)

| Sleutel         | Beschrijving                                              | Huidige waarde                                 |
|-----------------|-----------------------------------------------------------|------------------------------------------------|
| `SOURCE_DIR`    | Bronmap met originele foto's                              | `Z:\WWW\domains\alm.agrarix.net\pages`         |
| `OUTPUT_DIR`    | Outputmap voor gegenereerd album                          | `D:\TEMP\album\output`                         |
| `INDEX_FILE`    | Bestandsnaam van de hoofdpagina                           | `index.html`                                   |
| `SLIDES_DIR`    | Submap voor individuele slidepagina's                     | `slides`                                       |
| `THUMBS_DIR`    | Submap voor thumbnails                                    | `thumbs`                                       |
| `THUMBNAIL`     | Formaat van directory-thumbnails (ImageMagick-notatie)    | `140x140`                                      |
| `EXCLUDED`      | Mappen die overgeslagen worden                            | `["res"]`                                      |

---

## Technische details

- Taal van gegenereerde HTML: Nederlands (`lang="nl"`)
- Ondersteunde afbeeldingen: `.jpg` / `.jpeg` (hoofdletterongevoelig)
- Thumbnails worden gegenereerd via **ImageMagick** (`convert`, `identify`)
- Submappen krijgen een foldertegel met voorbeeldafbeelding (laatste foto uit submap)
- Geen recursieve verwerking van submappen

---

## Vereisten

- **Bash** (voor `generate_album.sh`)
- **Python** (voor `generate_album.py`)
- **ImageMagick** (`convert`, `identify`)
- Unix-tools: `find`, `sort`

---

## Status & Openstaande punten

- Er zijn twee versies van het generatorscript: Bash (`.sh`) en Python (`.py`)
- De gebruiker werkt op **Windows** — het Bash-script vereist WSL of Git Bash
- Bij aanpassingen altijd `README.md` updaten als de functionaliteit wijzigt

---

## Stijlregels

- Schrijf commentaar en documentatie in het **Nederlands**
- Houd de `README.md` gesynchroniseerd met de werkelijke functionaliteit
- Configuratie altijd via `album.json`, nooit hardcoded in het script
