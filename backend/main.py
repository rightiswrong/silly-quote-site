from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from database import SessionLocal, Quote
import random

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/quote/{letter}")
def get_quote_by_letter(letter: str):
    db = SessionLocal()
    try:
        letter = letter.upper()
        quotes = db.query(Quote).filter(Quote.text.like(f"{letter}%")).all()
        
        if not quotes:
            return {"text": f"No quote found starting with {letter}, but keep seeking wisdom!", "author": "The Void"}
        
        return random.choice(quotes)
    finally:
        db.close()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
