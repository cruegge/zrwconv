# ZRW Konverter

Docx-nach-HTML-Konverter für die ZRW-Artikel der EZW-Webseite, basierend auf [Mammoth](https://github.com/mwilliamson/python-mammoth), mit [aiohttp](https://docs.aiohttp.org/en/stable) Web-Frontend (🥜🔨).

## Setup

- Virtualenv erstellen und aktivieren,
- `pip install -r requirements.txt`,
- `./start.sh` für lokalen Gunicorn-Server auf Port `8000`.

Das Web-Frontend benötigt SSL für die Clipboard-Integration, entweder per Reverse Proxy, oder direkt per Gunicorn ([Dokumentation dazu](https://docs.gunicorn.org/en/20.1.0/settings.html#ssl), ungetestet).
