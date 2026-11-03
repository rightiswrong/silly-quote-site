This is a silly website creator that Gemma4 built through prompting and overworking two tired GTX 1080Tis and one RTX 3070.

Download a release and see what happens! It's fun.

# Wisdom in your Name

Type your name; every letter gets a quote that starts with that letter.

- **Frontend:** React (Vite), plain CSS. Follows your OS light/dark theme. Hero text is 48px on viewports under 1024px wide and 60px above. Laid out to fit a 1920x1080 screen without scrolling (up to 16 letters).
- **Backend:** FastAPI + a flat-file SQLite database (`backend/quotes.db`, created on first run).
- **Quotes:** a small bundled seed (A-Z, public-domain/proverbs) loads instantly and works offline. On startup the server also pulls a larger set from the web (`https://dummyjson.com/quotes`, override with `QUOTES_URL`) into the same database. If the web is unreachable it carries on with what it has.

## Run it

```bash
# 1. build the frontend
cd frontend && npm install && npm run build && cd ..

# 2. start the server (serves the API and the built app)
pip install -r backend/requirements.txt
python backend/main.py        # http://localhost:8000
```

Development with hot reload: run `python backend/main.py` and, in `frontend/`, `npm run dev` (proxies `/api` to port 8000).

## API

- `GET /api/quotes?name=Nick` returns `{ "quotes": [{ "letter", "text", "author" }, ...] }`, one per letter.
- `GET /api/stats` returns the number of stored quotes.

Quotes longer than 160 characters are skipped so every card stays readable on one screen. Letters with no quote at all (rare, e.g. X before the web pull) get a friendly placeholder.
