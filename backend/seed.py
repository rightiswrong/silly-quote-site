import requests
from database import SessionLocal, Quote

def seed_quotes():
    db = SessionLocal()
    try:
        print("Fetching quotes from web...")
        # Fetching from Quotable API (or similar)
        # Since we want a variety of starting letters, we fetch multiple batches
        for _ in range(15):
            response = requests.get("https://api.quotable.io/quotes/random?limit=50")
            if response.status_code == 200:
                data = response.json()
                for item in data['results']:
                    quote = Quote(text=item['content'], author=item['author'])
                    db.add(quote)
        db.commit()
        print("Database seeded successfully!")
    except Exception as e:
        print(f"Error seeding: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    seed_quotes()
