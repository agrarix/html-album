# 📷 HTML Fotoalbum Generator

Een robuuste en snelle Python/Bash-tool die automatisch een statisch HTML-fotoalbum genereert vanuit een map met afbeeldingen. Gebaseerd op de stijl van [alm.agrarix.net](http://alm.agrarix.net).

Dit project biedt een actieve **Python-versie** (`html-album.py`, aanbevolen voor Windows/cross-platform) en een verouderde, niet langer onderhouden **Bash-versie** (`__html-album.sh`, legacy).

---

## Features

- **Recursief**: Verwerkt automatisch alle submappen en genereert in elke map een eigen `index.html`.
- **Navigatie & Toetsenbord**: Slide-pagina's ondersteunen `←` (vorige), `→` / `Spatiebalk` (volgende) en `Esc` / `Backspace` (terug naar overzicht) via het toetsenbord. Tevens ondersteunen index-pagina's (het mappen- en thumbnailsoverzicht) `Esc` / `Backspace` om terug te navigeren naar de bovenliggende map. Daarnaast kan men op de foto zelf klikken om te navigeren (linker- en rechterkant over de gehele hoogte voor vorige/volgende foto, het middelste-bovenste gedeelte om omhoog te navigeren naar het album, en optioneel het middelste-onderste gedeelte om de foto direct te downloaden indien downloaden is geactiveerd), waarbij de cursor en tooltip zich dynamisch aanpassen.
- **Volgnummers**: Slide-pagina's tonen het volgnummer van de huidige foto en het totale aantal foto's in de map (bijv. `(2/10)`) direct achter de mapnaam in de header (breadcrumbs).
- **Downloadknop**: Slide-pagina's bevatten optioneel een downloadknop met icoon om de originele foto in volledige resolutie rechtstreeks te downloaden (configureerbaar via `DOWNLOAD`).
- **EXIF-metadata**: Leest en toont automatisch camera-instellingen (cameramodel, opnamedatum, sluitertijd, diafragma, ISO en brandpuntsafstand) op de slide-pagina's indien beschikbaar.
- **Gescheiden mappen**: Originele foto's blijven onaangetast; de complete website wordt gegenereerd in de geconfigureerde `OUTPUT_DIR`.
- **Preview thumbnails**: Submappen worden op de hoofdpagina getoond met de eerste foto uit die submap als preview.
- **Mobielvriendelijk**: Volledige viewport-ondersteuning voor correcte schaling op mobiel, grotere tikbare navigatieknoppen, en een raster dat op mobiel automatisch schaalt naar 2 flexibele kolommen. Tevens zijn de breadcrumbs geoptimaliseerd voor kleine schermen door het weglaten van "Foto album :" op subpagina's en het toestaan van automatische tekstterugloop (wrapping) op afbreekstreepjes en slashes.
- **Logbestand**: Schrijft gedetailleerde logboeken naar een configureerbaar logbestand voor eenvoudige monitoring.
- **Schrijfbeveiligingscontrole**: Controleert bij de start automatisch of `INDEX_FILE` herschrijfbaar is; breekt direct af met een duidelijke foutmelding op de console en in het logbestand als het bestand ReadOnly / niet beschrijfbaar is.
- **Configureerbare voettekst**: De footer onderaan de indexpagina is volledig aan te passen via de configuratie en ondersteunt dynamische variabelen. De geformatteerde versie wordt tijdens het starten getoond in de console en meegeschreven in het logbestand.
- **Watermerk**: Ondersteunt een configureerbaar, semi-transparant watermerk (tekst) op slide-foto's via Pillow.
- **Automatische HEIC naar JPEG conversie**: Ondersteunt `.heic` en `.heif` (o.a. iPhone/Apple foto's). Converteert deze automatisch naar `.jpg` met behoud van alle EXIF-metadata (oriëntatie, opnamedatum, camera-instellingen) via `pillow-heif`.
- **Rclone synchronisatie**: Ondersteunt automatische synchronisatie van foto's vanuit cloudopslag (Google Drive, OneDrive) of lokale mappen via `rclone sync`. Verifieert vooraf dat de submappen exact overeenkomen, neemt ook lege submappen mee (`--create-empty-src-dirs`), schoont automatisch vervallen doelmappen op die niet meer in de bron bestaan, logt de volledige synchronisatieuitvoer in real-time naar het geconfigureerde logbestand en genereert na synchronisatie direct automatisch het album voor de betreffende map.
- **Webhook & Web UI integratie**: Bevat een HTTP webhook endpoint (`/hooks/html-album`) en een interactieve webpagina (`html-album.html`) op server `fabrix` om de generatie op afstand als `maarten@fabrix` te activeren (met configuratieselectie, opties voor `--all` en `async`, en live loguitvoer).

---

## 📁 Projectstructuur

```
html-album/
├── .agents/
│   └── AGENTS.md          # Instructies voor AI-assistenten
├── html-album.rc          # Configuratiebestand
├── html-album.py          # Python-generatorscript (primair)
├── run-html-album.sh      # Webhook runner script voor Linux / fabrix
└── requirements.txt       # Python-afhankelijkheden (Pillow)
```

---

## ⚙️ Configuratie

Alle instellingen worden gelezen uit `html-album.rc`:

| Sleutel | Beschrijving | Standaardwaarde |
|---|---|---|
| `SOURCE_DIR` | Bronmap met originele foto's en submappen (leeg of `.` = huidige werkmap) | `""` |
| `OUTPUT_DIR` | Uitvoerlocatie voor de gegenereerde website (leeg of `.` = huidige werkmap) | `""` |
| `INDEX_FILE` | Bestandsnaam van de gegenereerde indexpagina's | `index.html` |
| `PICTURES_DIR` | Naam van de submap voor individuele slidepagina's | `_pictures` |
| `THUMBS_DIR` | Naam van de submap voor de thumbnails | `_thumbs` |
| `THUMBNAIL` | Grootte van thumbnails (notatie: `breedtexhoogte`) | `140x140` |
| `PICTURE` | Maximale grootte van slide-afbeeldingen (leeg = originele grootte) | `""` |
| `ICON` | Bestandsnaam van het albumicoon / favicon (wordt nooit hernoemd en uitgesloten van de galerij) | `"Agrarix-Pingu_2017.jpg"` |
| `LOG_FILE` | Pad/naam van het logbestand (relatief aan script-dir, of $HOME/log op Linux) | `html-album.log` |
| `EXCLUDED` | Mapnamen die volledig genegeerd moeten worden | `["res"]` |
| `COLUMNS` | Vaste hoeveelheid kolommen in het raster (0 = auto-responsive flex) | `0` |
| `ROWS` | Hoeveelheid rijen (momenteel niet actief gebruikt, 0 = oneindig) | `0` |
| `RENAME` | Hernoem originele bestandsnamen in de output naar `YYMMDD_HHMMSS-<orig-naam>` op basis van EXIF of mtime | `false` |
| `DOWNLOAD` | Downloadknop tonen op slide-pagina's (`yes` / `no`) | `no` |
| `REVERSE` | Volgorde van mappen en foto's omkeren (`yes` / `no`) | `no` |
| `FOOTER` | Sjabloon voor de voettekst (optioneel, ondersteunt `${PGM}`, `${VER}`, `${DATE}`, `${TIME}`, `${OS}`, `${HOSTNAME}`). Standaard is dit dynamisch op basis van het OS. | `"Generated by ${PGM} ${VER} (${OS})"` (Windows) of `"Generated by ${PGM} ${VER} (${OS}) at ${HOSTNAME}"` (Linux) |
| `WATERMARK` | Tekst van het watermerk op slide-foto's (leeg = geen watermerk) | `""` |
| `WM_FONT` | Systeemlettertype voor het watermerk | `"Verdana"` |
| `WM_SIZE` | Lettergrootte van het watermerk in pixels | `12` |
| `WM_ICON_SIZE` | Lettergrootte van het watermerk op thumbnails/iconen (0 = geen watermerk op thumbnails) | `0` |
| `WM_TRANSPARANCY` | Transparantiegraad van het watermerk (bijv. `80%` of `0.80`) | `"80%"` |
| `WM_LOCATION` | Verticale positie van het watermerk als percentage vanaf de bovenkant (bijv. `90` voor 90%) | `90` |
| `WM_ALLIGNMENT` | Horizontale uitlijning van het watermerk (`left`, `center`, `right`) | `"center"` |
| `RCLONE` | Bestanden synchroniseren via `rclone sync` vóór generatie (`yes` / `no`) | `no` |
| `RCLONE_SRC` | Bronlocatie voor `rclone sync` (bijv. Google Drive/OneDrive pad) | `""` |
| `RCLONE_DST` | Doellocatie voor `rclone sync` (laatste submap moet exact gelijk zijn aan bron) | `""` |


### Voorbeeld `html-album.rc`

```shell
PICTURES_DIR="_pictures"
THUMBS_DIR="_thumbs"
EXCLUDED="res"
THUMBNAIL="140x140"
SOURCE_DIR="Z:/WWW/domains/alm.agrarix.net/pages"
OUTPUT_DIR="G:/Mijn Drive/Antigravity/html-album/output"
INDEX_FILE="index.html"
LOG_FILE="html-album.log"
COLUMNS="2"
ROWS="0"
RENAME="false"
DOWNLOAD="no"
WATERMARK="(c) Fam. de Boer - Wennink"
WM_FONT="Verdana"
WM_SIZE=12
WM_ICON_SIZE=0
WM_TRANSPARANCY=80%
WM_LOCATION=90
WM_ALLIGNMENT="center"
```
*Tip: Gebruik forward slashes (`/`) in paden, ook op Windows.*

> [!NOTE]
> - Regels in het `.rc`-bestand die beginnen met een `#` (al dan niet voorafgegaan door spaties) worden gezien als commentaar en overgeslagen.
> - Wanneer een variabele ontbreekt of is uitgecommentarieerd in het `.rc`-bestand, valt de generator automatisch terug op de gedefinieerde standaardwaarde (zoals `_pictures` voor `PICTURES_DIR` en `_thumbs` voor `THUMBS_DIR`).
> - Een configuratiebestand mag ook opgegeven worden zonder `.rc` extensie (bijv. `html-album huis`). Het script zoekt dan automatisch eerst naar `huis` en vervolgens naar `huis.rc`.
> - Als een opgegeven configuratiebestand niet wordt gevonden, toont het script een waarschuwing (`WARNING: Configuratiebestand <naam> niet gevonden.`), wacht 1 seconde, en valt daarna automatisch terug op het standaard `html-album.rc` configuratiebestand.

---

## 🚀 Gebruik

### Python (Aanbevolen, Dual OS: Windows & Linux)
1. Installeer de vereisten (eenmalig):
   - **Windows**:
     ```cmd
     pip install -r requirements.txt
     ```
   - **Linux** (bijvoorbeeld op server `xynix` in de map `scripts/`):
     ```bash
     pip3 install -r requirements.txt
     ```
2. Voer het script uit:
   - **Windows**:
     ```cmd
     python html-album.py
     ```
   - **Linux**:
     ```bash
     python3 html-album.py
     ```
   *Tip: Je kunt optioneel een specifiek configuratiebestand als argument opgeven, of help- en versie-informatie opvragen:*
   ```cmd
   # Gebruik een specifiek configuratiebestand (mag ook zonder .rc extensie)
   python html-album.py huis

   # Toon de help-informatie (werkt ook met -h, /help of /?)
   python html-album.py --help

   # Toon het versienummer (werkt ook met --version)
   python html-album.py -V

   # Genereer alle thumbnails en afbeeldingen opnieuw (overschrijf bestaande)
   python html-album.py --all

   # Volgorde van mappen en foto's achterstevoren (omgekeerd)
   python html-album.py -r
   # of: python html-album.py --reverse

   # Hernoem bestandsnamen naar YYMMDD_HHMMSS-<orig-name> in de output
   python html-album.py --rename

    # Toon een downloadknop op slide-pagina's
    python html-album.py -D
    # of: python html-album.py --download

     # Genereer alleen een specifieke (sub)directory
     python html-album.py -d 2024/vakantie
     # of: python html-album.py --directory 2024/vakantie

     # Synchroniseer via rclone sync en genereer aansluitend de gesynchroniseerde map
     python html-album.py --rclone "G:\Mijn Drive\Album\2026_Assisi" "W:\domains\albums.agrarix.net\pages\2026_Assisi"
     # of (indien RCLONE_SRC en RCLONE_DST in .rc geconfigureerd zijn):
     python html-album.py --rclone
     ```

*Zonder Pillow worden de originele bestanden direct als thumbnail gelinkt.*

### Bash (Linux / macOS / WSL) — Legacy / Niet meer bijgewerkt
1. Zorg dat `ImageMagick` (`convert` en `identify`) geïnstalleerd is.
2. Voer het script uit:
   ```bash
   bash __html-album.sh
   ```

---

## 🔧 Verwerkingsvolgorde (Wat doet de generator?)

Wanneer het script draait (optioneel voorafgegaan door `--rclone`), verloopt de verwerking strikt in deze stappen:

1. **Rclone synchronisatie (optioneel)**: Indien geconfigureerd (`RCLONE=yes` of `--rclone`), worden eerst alle bestanden gesynchroniseerd vanaf cloudopslag (bijv. Google Drive) naar de lokale doeldirectory.
2. **Configuratie & initialisatie**: Leest `html-album.rc`, controleert schrijfrechten op `INDEX_FILE`, en initialiseert logbestand en stijlen.
3. **Mappen scannen**: Zoekt recursief naar alle ondersteunde afbeeldingen (`.jpg`, `.jpeg`, `.heic`, `.heif`) in de bronmap.
4. **Automatische HEIC/HEIF conversie**:
   - Converteert elk `.heic` / `.heif` bestand naar `.jpg` met behoud van volledige EXIF-metadata en automatische oriëntatie (`exif_transpose`).
   - Hernoemt het bestand naar `.jpg`.
   - Verwijdert het originele `.heic` bestand in de doelmap om schijfruimte te besparen en duplicaten te voorkomen.
5. **Thumbnails & Slide-afbeeldingen**:
   - Genereert thumbnails in `_thumbs/` passend binnen `THUMBNAIL` afmetingen.
   - Indien `PICTURE` is ingesteld: verkleint slide-afbeelding en plaatst deze in `_pictures/`, eventueel voorzien van een watermerk (`WATERMARK`).
6. **Slides & Navigatie**: Genereert individuele HTML-slidepagina's per foto met EXIF-data, downloadknop en navigatie.
7. **Index & Raster**: Genereert `index.html` met responsive thumbnailgrid en preview-tegels voor submappen.
8. **Logging**: Rapporteert alle acties live in de console en in `LOG_FILE`.

---

## 🔄 Rclone Synchronisatie (Google Drive, OneDrive, Cloud & Lokaal)

Met de `--rclone` optie kan de generator foto's direct ophalen vanaf cloudopslag of een andere map vóórdat de albumgeneratie start.

### Hoe het werkt
1. **Veiligheidscontrole**: Het script controleert of de laatste submap van de bron en het doel exact overeenkomen (bijv. `.../2026_Assisi` en `.../2026_Assisi`). Als de mapnamen verschillen, breekt het script direct af met een foutmelding om verkeerde overschrijvingen te voorkomen.
2. **Synchronisatie & Logging**: Het script voert `rclone sync <BRON> <DOEL>` uit met `--create-empty-src-dirs` (zodat ook nieuw aangemaakte lege submappen gesynchroniseerd worden). Alle overdrachten, aangemaakte mappen en transferstatistieken worden regel voor regel in real-time weggeschreven naar het geconfigureerde `LOG_FILE` en getoond op het scherm/de webhook interface.
3. **Opschonen vervallen mappen**: Mappen die wel op de doellocatie aanwezig zijn maar niet (meer) in de bron bestaan (bijv. hernoemd of verwijderd in Google Drive), worden direct automatisch verwijderd inclusief eventuele restanten van gegenereerde thumbnails en slide-pagina's.
4. **Automatische albumverwerking**: Zodra `rclone sync` en het opschonen succesvol zijn voltooid, genereert het script direct automatisch het album voor die specifieke gesynchroniseerde map.

#### Voorbeeld rclone logregels in het logbestand (`LOG_FILE` / Web UI):
```text
[09:42:01] 🚀 Start rclone sync:
[09:42:01]    Bron : gdrive:Albums/2026_Assisi
[09:42:01]    Doel : /mnt/nas/WWW/domains/albums.agrarix.net/pages/2026_Assisi
[09:42:02]    [rclone] 10-01 San_Damiano Assisi: Made directory
[09:42:03]    [rclone] Assisi.jpg: Copied (new)
[09:42:04]    [rclone] Transferred: 129.220 KiB / 129.220 KiB, 100%, 3.891 KiB/s, ETA 0s
[09:42:04] ✓ rclone sync succesvol voltooid.
[09:42:04]    🧹 Vervallen map verwijderd (niet in bron): 01-09
```

### Gebruik
- **Via de commandline**:
  ```cmd
  python html-album.py --rclone "G:\Mijn Drive\Album\2026_Assisi" "W:\domains\albums.agrarix.net\pages\2026_Assisi"
  ```
- **Via `html-album.rc`**:
  ```shell
  RCLONE="yes"
  RCLONE_SRC="G:/Mijn Drive/Album/2026_Assisi"
  RCLONE_DST="W:/domains/albums.agrarix.net/pages/2026_Assisi"
  ```
  Vervolgens aanroepen met:
  ```cmd
  python html-album.py --rclone
  ```
  *(of gewoon `python html-album.py` als `RCLONE="yes"` in `.rc` staat)*

### 📦 Installatie van Rclone
- **Windows**:
  Installeer `rclone` eenmalig via Windows Package Manager:
  ```cmd
  winget install Rclone.Rclone
  ```
  *(Of download de ZIP vanaf [rclone.org](https://rclone.org) en zet `rclone.exe` in een map in je PATH).*
- **Linux** (bijv. op server `fabrix`):
  ```bash
  sudo apt install rclone
  ```

---

### 🔑 Exacte Stappen: Google Drive koppelen op headless Linux (`fabrix`)

Omdat de Linux-server geen grafische webbrowser heeft, gebruikt `rclone` een autorisatietoken dat je eenmalig ophaalt via je Windows-pc.

#### Stap 1: Start de wizard op Linux (`fabrix`)
Voer uit op de Linux server:
```bash
rclone config
```
Volg de vragen:
1. `n/s/q> ` -> Toets **`n`** (New remote) en druk op Enter.
2. `name> ` -> Typ **`gdrive`** en druk op Enter.
3. `Storage> ` -> Typ **`drive`** (of het nummer voor *Google Drive*) en druk op Enter.
4. `client_id> ` -> Druk direct op **Enter** (leeg laten voor standaard).
5. `client_secret> ` -> Druk direct op **Enter** (leeg laten voor standaard).
6. `scope> ` -> Typ **`1`** (Full access to all files) en druk op Enter.
7. `root_folder_id> ` -> Druk direct op **Enter** (leeg laten).
8. `service_account_file> ` -> Druk direct op **Enter** (leeg laten).
9. `Edit advanced config? ` -> Typ **`n`** (No) en druk op Enter.
10. `Use web browser to automatically authenticate? ` -> Typ **`n`** (No, want de server is headless/remote!) en druk op Enter.

De Linux-server toont nu een regel vergelijkbaar met:
```text
Execute the following on the machine with the web browser:
    rclone authorize "drive" "eyJzY29wZSI6ImRyaXZlIn0"
Then paste the result.
config_token>
```
*Laat dit Linux-scherm zo openstaan.*

#### Stap 2: Token genereren op Windows
1. Open op je Windows-pc een **Opdrachtprompt (CMD)**.
2. Plak en voer het commando uit dat Linux je zojuist gaf:
   ```cmd
   rclone authorize "drive" "eyJzY29wZSI6ImRyaXZlIn0"
   ```
3. Je standaardbrowser opent automatisch met het Google inlogscherm.
4. Kies je gewenste Google/Gmail-account en klik op **Toestaan** (Allow).
5. Ga terug naar je Windows CMD-scherm. Daar staat nu een JSON-tekst:
   ```json
   {"access_token":"ya29...","token_type":"Bearer","refresh_token":"1//...","expiry":"..."}
   ```
6. **Kopieer deze volledige regel** (vanaf de openingsaccolade `{` tot en met de sluitaccolade `}`).

#### Stap 3: Token invoeren op Linux
1. Ga terug naar je Linux-terminal waar `config_token>` staat.
2. Plak de gekopieerde JSON-tekst (via rechtermuisklik of `Shift + Insert`) en druk op **Enter**.
3. `Configure this as a Shared Drive (Team Drive)? ` -> Typ **`n`** (No, tenzij het om een zakelijke Google Workspace Team Drive gaat) en druk op Enter.
4. `Keep this "gdrive" remote? ` -> Typ **`y`** (Yes) en druk op Enter.
5. `e/n/d/r/c/s/q> ` -> Typ **`q`** (Quit config) om de wizard af te sluiten.

De configuratie staat nu permanent en veilig opgeslagen in `~/.config/rclone/rclone.conf`. Rclone ververst het authenticatietoken automatisch op de achtergrond; je hoeft dit nooit meer opnieuw te doen.

---

### ✅ Verbinding testen op Linux
Controleer of Linux nu rechtstreeks je Google Drive kan lezen:
```bash
rclone lsd gdrive:
```
Dit commando toont direct de hoofdmappen in je Google Drive (zoals `Albums`, `Vakantie`, etc.).

---

### 🚀 Gebruik met het album generator script
In je configuratiebestand (bijv. `assisi.rc` of `html-album.rc`):
```shell
RCLONE="yes"
RCLONE_SRC="gdrive:Albums/2026_Assisi"
RCLONE_DST="/var/www/albums.agrarix.net/pages/2026_Assisi"
```
Of direct via de commandline:
```bash
python3 html-album.py --rclone "gdrive:Albums/2026_Assisi" "/var/www/albums.agrarix.net/pages/2026_Assisi"
```
*Het script synchroniseert automatisch de nieuwste foto's vanuit Google Drive naar de lokale doeldirectory en bouwt aansluitend meteen het web-album.*

---

## 📄 Licentie & Footer
De gegenereerde pagina's bevatten in de footer een tekst die optioneel configureerbaar is via de `FOOTER` sleutel in `html-album.rc`. Als deze sleutel ontbreekt, wordt er automatisch een standaardtekst gebruikt.

Standaardwaarde:
- Op Windows: `Generated by html-album v2 (DD-MM-YYYY HH:MM) (Windows)`
- Op Linux: `Generated by html-album v2 (DD-MM-YYYY HH:MM) (Linux) at hostname`

De volgende variabelen worden automatisch vervangen:
- `${PGM}` (of `{PGM}`): Programmanaam (`html-album`)
- `${VER}` (of `{VER}` / `{VERSION}`): Versie en buildtijd (bijv. `v2 (07-07-2026 09:16)`)
- `${DATE}` (of `{date_str}`): Datum van generatie (`DD-MM-YYYY`)
- `${TIME}` (of `{time_str}`): Tijdstip van generatie (`HH:MM`)
- `${OS}` (of `{OS}`): Het besturingssysteem (`Windows` of `Linux`)
- `${HOSTNAME}` (of `{HOSTNAME}`): De hostnaam van de server (voornamelijk op Linux)

Bij het starten van de generator wordt er tevens een voorbeeld van de geformatteerde voettekst getoond op stdout (de console) en weggeschreven naar het logbestand.

---

## 🪝 Webhook & Web UI (fabrix)

Op de server **fabrix** kan het genereren van fotoalbums op afstand worden gestart via een webpagina of via een HTTP-aanroep.

### 1. Webpagina (`/var/www/html/html-album.html`)
Bereikbaar via `http://192.168.178.40/html-album.html` (of via *"Run html-album"* op de hoofdpagina van fabrix):
- **Configuratiekeuze**: Kies een albumconfiguratie uit `~/etc/*.rc` (zoals `assisi.rc`, `huis.rc`, `html-album.rc`, etc.) of voer handmatig een configuratienaam in.
- **Opties**: Vink optioneel *Forceer alles opnieuw genereren (`--all`)* aan.
- **Startknop**: Start het proces; live voortgang (synchronisatie, HEIC-conversie, thumbnails en paginaopbouw) wordt in real-time getoond in het ingebouwde terminal-venster met auto-scroll.
- **Testknop**: Direct testen of de achterliggende verbinding reageert via `-V`.

### 2. HTTP Endpoint (curl / automatisering)
Kan direct aangeroepen worden vanuit scripts, Home Assistant of via curl:

```bash
# Standaard album genereren
curl -X POST "http://fabrix/hooks/html-album"

# Specifieke configuratie draaien (bijv. Assisi met rclone synchronisatie)
curl -X POST "http://fabrix/hooks/html-album?config=assisi.rc"

# Geforceerd alles opnieuw genereren (--all)
curl -X POST "http://fabrix/hooks/html-album?config=assisi.rc&all=1"

# Asynchroon in de achtergrond starten
curl -X POST "http://fabrix/hooks/html-album?config=assisi.rc&async=1"
```

---

## 📝 Nog te doen

Hier staan de openstaande punten en ideeën voor de HTML Fotoalbum Generator.

### Openstaande taken
*(Geen openstaande taken momenteel)*

### Voltooide taken
- [x] Webhook trigger op fabrix: Knop/webhook op server fabrix om na de synchronisatie het album automatisch opnieuw te genereren.
- [x] Automatische conversie van `.HEIC` en `.heif` (o.a. iPhone) naar `.JPG` met behoud van EXIF-metadata via `pillow-heif`.
- [x] Synchronisatie via `rclone sync` (cloud/lokaal) vóór generatie via `--rclone` en submapcontrole.
- [x] Een watermerk met bijvoorbeeld `"(c) Fam. de Boer - Wennink"` (configureerbaar via de configuratie) onderin de foto zetten.
- [x] Foto's hernoemen op basis van de EXIF datum & tijd (`YYMMDD_HHMMSS-<orig-name>`) via de `--rename` optie.
- [x] `html-album.py` geschikt maken voor Linux (dual OS).
- [x] Downloadknop tonen op slide-pagina's via `DOWNLOAD` in RC of via de CLI optie `-D` / `--download`.
- [x] Specifieke (sub)directory verwerken via de CLI optie `-d` / `--directory`.
- [x] Automatische `.rc` extensie fallback en terugval naar `html-album.rc` bij ontbrekende configuratiebestanden.
- [x] Bij het opstarten controleren of `INDEX_FILE` herschrijfbaar is en stoppen bij ReadOnly (met melding op console & logbestand).
