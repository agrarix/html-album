# 📷 HTML Fotoalbum Generator

Een Bash-script dat automatisch een statisch HTML-fotoalbum genereert vanuit een map met JPEG-afbeeldingen. Gebaseerd op de stijl van [alm.agrarix.net](http://alm.agrarix.net).

---

## 📁 Projectstructuur

```
album/
├── album.json           # Configuratiebestand
└── generate_album.sh    # Generatorscript
```

---

## ⚙️ Configuratie

Alle instellingen worden gelezen uit `album.json`:

| Sleutel        | Beschrijving                                              | Standaardwaarde                              |
|----------------|-----------------------------------------------------------|----------------------------------------------|
| `SOURCE_DIR`   | Bronmap met originele foto's (en submappen)               | `/mnt/nas/WWW/domains/alm.agrarix.net/pages` |
| `INDEX_FILE`   | Bestandsnaam van de gegenereerde hoofdpagina              | `test.html`                                  |
| `SLIDES_DIR`   | Naam van de submap voor individuele slidepagina's         | `slides_dir`                                 |
| `THUMBS_DIR`   | Naam van de submap voor gegenereerde thumbnails           | `thumbs_dir`                                 |
| `DIR_THUMBNAIL`| Formaat van directory-thumbnails (ImageMagick-notatie)    | `500x300`                                    |
| `EXCLUDED`     | Lijst met mapnamen die overgeslagen worden                | `["res"]`                                    |

### Voorbeeld `album.json`

```json
{
  "SLIDES_DIR": "slides_dir",
  "THUMBS_DIR": "thumbs_dir",
  "EXCLUDED": ["res"],
  "DIR_THUMBNAIL": "500x300",
  "SOURCE_DIR": "/mnt/nas/WWW/domains/alm.agrarix.net/pages",
  "INDEX_FILE": "test.html"
}
```

---

## 🚀 Gebruik

```bash
bash generate_album.sh
```

Het script leest `album.json` vanuit dezelfde map als het script zelf. Als het configuratiebestand niet gevonden wordt, worden de ingebakken standaardwaarden gebruikt.

---

## 🔧 Wat doet het script?

1. **Leest de configuratie** uit `album.json`.
2. **Maakt outputmappen aan**: `slides_dir/` en `thumbs_dir/` binnen de bronmap.
3. **Verwerkt JPEG-afbeeldingen** (`.jpg` / `.jpeg`) op het hoogste niveau van de bronmap:
   - Kopieert het origineel naar de outputmap.
   - Genereert een thumbnail via ImageMagick.
   - Maakt een individuele HTML-slidepagina aan in `slides_dir/`.
   - Voegt een klikbare tegel toe aan de hoofdindex.
4. **Verwerkt submappen**:
   - Slaat uitgesloten mappen over (o.a. `res`, `slides_dir`, `thumbs_dir`).
   - Maakt een foldertegel met een voorbeeldafbeelding (de laatste foto uit de submap).
   - Als er geen foto's zijn, wordt een 📁-icoon getoond.
5. **Genereert de hoofdpagina** (`INDEX_FILE`) met een CSS-gridgalerij van alle foto's en mappen.

---

## 📦 Vereisten

| Tool           | Gebruik                                  |
|----------------|------------------------------------------|
| `bash`         | Uitvoeren van het script                 |
| `ImageMagick`  | Thumbnails genereren (`convert`, `identify`) |
| `find`, `sort` | Standaard Unix-hulpprogramma's           |

Zorg dat ImageMagick geïnstalleerd is:

```bash
# Debian/Ubuntu
sudo apt install imagemagick

# macOS (via Homebrew)
brew install imagemagick
```

---

## 📄 Gegenereerde uitvoer

Na uitvoering vind je het volgende in de `SOURCE_DIR`:

```
SOURCE_DIR/
├── test.html          # Hoofdgalerij-pagina
├── slides_dir/        # Individuele HTML-pagina per foto
│   ├── foto1.html
│   └── foto2.html
└── thumbs_dir/        # Thumbnails
    ├── foto1_thumb.jpg
    ├── foto2_thumb.jpg
    └── folder_mapnaam_thumb.jpg
```

Open `test.html` in een browser om het album te bekijken.

---

## 📝 Notities

- Het script verwerkt alleen `.jpg` en `.jpeg` bestanden (hoofdletterongevoelig).
- Submappen worden verwacht een eigen `index.html` te hebben (het script genereert deze **niet** recursief).
- De gegenereerde HTML gebruikt Nederlands als taal (`lang="nl"`).
