# Project: HTML Fotoalbum Generator

## Doel
Een tool die automatisch een statisch HTML-fotoalbum genereert vanuit een map met JPEG-afbeeldingen. Gebaseerd op de stijl van [alm.agrarix.net](http://alm.agrarix.net).

---

## Projectstructuur

```
html-album/
├── .agents/
│   └── AGENTS.md          # Dit bestand (automatisch ingelezen door Antigravity)
├── README.md              # Projectdocumentatie voor mensen
├── html-album.rc          # Configuratiebestand
├── html-album.py          # Python-versie van het generatorscript (primair)
└── requirements.txt       # Python dependencies
```

---

## Configuratie (`html-album.rc`)

| Sleutel         | Beschrijving                                              | Huidige waarde                                 |
|-----------------|-----------------------------------------------------------|------------------------------------------------|
| `SOURCE_DIR`    | Bronmap met originele foto's                              | `Z:\WWW\domains\alm.agrarix.net\pages`         |
| `OUTPUT_DIR`    | Outputmap voor gegenereerd album                          | `D:\TEMP\html-album\output`                 |
| `INDEX_FILE`    | Bestandsnaam van de hoofdpagina                           | `index.html`                                   |
| `PICTURES_DIR`  | Submap voor individuele slidepagina's                     | `pictures`                                     |
| `THUMBS_DIR`    | Submap voor thumbnails                                    | `thumbs`                                       |
| `THUMBNAIL`     | Formaat van directory-thumbnails (ImageMagick-notatie)    | `140x140`                                      |
| `EXCLUDED`      | Mappen die overgeslagen worden                            | `["res"]`                                      |

---

## Technische details

- Taal van gegenereerde HTML: Nederlands (`lang="nl"`)
- Ondersteunde afbeeldingen: `.jpg` / `.jpeg` (hoofdletterongevoelig)
- Thumbnails worden bij voorkeur gegenereerd via **Pillow** (`PIL`) in Python, of anders via **ImageMagick** in Bash
- Slide-pagina's tonen geformatteerde EXIF-metadata (camera model, opnamedatum, sluitertijd, diafragma, ISO, brandpuntsafstand) indien beschikbaar
- Submappen krijgen een foldertegel met voorbeeldafbeelding (eerste foto uit submap)
- Recursieve verwerking van submappen (elk krijgt eigen `index.html` en navigatie)
- Op Linux-systemen worden relatieve configuratiebestanden (.rc) standaard gezocht in `$HOME/etc/` in plaats van de scriptdirectory (voor dual OS ondersteuning)

---

## Vereisten

- **Bash** (voor `__html-album.sh`)
- **Python** (voor `html-album.py`)
- **ImageMagick** (`convert`, `identify`)
- Unix-tools: `find`, `sort`

---

## Status & Openstaande punten

- De Python-versie (`html-album.py`) is het primaire script en wordt actief onderhouden.
- De Bash-versie (`__html-album.sh`) is verouderd (legacy) en hoeft niet meer bijgewerkt te worden.
- De gebruiker werkt hoofdzakelijk op **Windows**, maar het script is tevens geschikt voor **Linux** (dual OS), specifiek voor installatie op de server **xynix** (`192.168.178.8`) in de directory `scripts/`.
- Bij aanpassingen altijd `README.md` updaten als de functionaliteit wijzigt.
- De assistent voert code-aanpassingen, commits en pushes volledig zelfstandig uit. De generatie (`python html-album.py`) wordt door de gebruiker zelf handmatig gestart.

---

## Stijlregels

- Communiceer en beantwoord vragen altijd in het **Nederlands**
- Schrijf commentaar en documentatie in het **Nederlands**
- Houd de `README.md` gesynchroniseerd met de werkelijke functionaliteit
- Configuratie altijd via `html-album.rc`, nooit hardcoded in het script
- Stel geen tussentijdse verduidelijkingsvragen; voer wijzigingen direct autonoom door.
- Alle Git-handelingen (add, commit, push, etc.) mogen zonder bevestiging vooraf worden uitgevoerd.
- Maak geen implementatieplannen (zoals `implementation_plan.md`) en vraag niet om goedkeuring vooraf; ga direct over tot de uitvoering.
