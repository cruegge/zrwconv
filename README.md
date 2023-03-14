# ZRW Konverter

Docx-nach-HTML-Konverter für die ZRW-Artikel der EZW-Webseite, basierend auf [Mammoth](https://github.com/mwilliamson/python-mammoth), mit [aiohttp](https://docs.aiohttp.org/en/stable) Web-Frontend (🥜🔨).

## Setup

- Virtualenv erstellen und aktivieren,
- `pip install -r requirements.txt`,
- `./start.sh` für lokalen Gunicorn-Server auf Port `8000`.

## Docker

Ein Docker-Container lässt sich über das mitgelieferte `Dockerfile` bauen, oder alternativ mit

```bash
docker pull cruegge/zrwconv:latest
```

runterladen. Beim Start muss ein Forward nach Port 80 eingerichtet werden:

```
docker run -p 8000:80 cruegge/zrwconv
```

## SSL

Das Web-Frontend muss für die Clipboard-API über SSL laufen. Der oben weitergeleitete Port 8000 liefert nur HTTP, muss also noch hinter einen Reverse Proxy.
