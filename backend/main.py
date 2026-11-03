import os
import threading
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

import store


@asynccontextmanager
async def lifespan(_app):
    conn = store.connect()
    store.seed_bundled(conn)  # instant and offline-safe
    conn.close()
    threading.Thread(target=store.seed_from_web, daemon=True).start()  # then grow from the web
    yield


app = FastAPI(title="Silly Quote Site", lifespan=lifespan)
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])


@app.get("/api/quotes")
def quotes_for_name(name: str = Query(..., min_length=1, max_length=80)):
    conn = store.connect()
    try:
        quotes = store.quotes_for_name(conn, name)
    finally:
        conn.close()
    if quotes is None:
        raise HTTPException(400, "Please enter a name containing letters.")
    return {"name": name, "quotes": quotes}


@app.get("/api/stats")
def stats():
    conn = store.connect()
    try:
        return {"total": conn.execute("SELECT COUNT(*) FROM quotes").fetchone()[0]}
    finally:
        conn.close()


# Serve the built React app when present (single-process deploy)
DIST = os.path.join(store.HERE, "..", "frontend", "dist")
if os.path.isdir(os.path.join(DIST, "assets")):
    app.mount("/assets", StaticFiles(directory=os.path.join(DIST, "assets")), name="assets")

    @app.get("/{path:path}")
    def spa(path: str):
        f = os.path.join(DIST, path)
        return FileResponse(f if path and os.path.isfile(f) else os.path.join(DIST, "index.html"))


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
