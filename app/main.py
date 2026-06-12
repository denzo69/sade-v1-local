from fastapi import FastAPI
from datetime import datetime

app = FastAPI(title="Säde v1")

@app.get("/")
def home():
    return {
        "name": "Säde v1",
        "status": "pesä online",
        "message": "Tämä on Säde v1:n ensimmäinen paikallinen palvelu.",
        "time": datetime.now().isoformat()
    }

@app.get("/health")
def health():
    return {
        "ok": True,
        "status": "alive",
        "service": "sade-v1"
    }

@app.get("/memory")
def memory():
    return {
        "message": "Muistijärjestelmän paikka on luotu. Varsinainen muistiluku lisätään myöhemmin."
    }
