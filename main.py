from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import sqlite3

app = FastAPI()

# Création de la base de données SQLite
conn = sqlite3.connect("memory.db", check_same_thread=False)
cursor = conn.cursor()
cursor.execute("""
    CREATE TABLE IF NOT EXISTS memory (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        key TEXT UNIQUE,
        value TEXT
    )
""")
conn.commit()

class MemoryEntry(BaseModel):
    key: str
    value: str

@app.get("/")
def read_root():
    return {"message": "Hello, Railway!"}

@app.post("/memory")
def store_memory(entry: MemoryEntry):
    try:
        cursor.execute("INSERT INTO memory (key, value) VALUES (?, ?)", (entry.key, entry.value))
        conn.commit()
        return {"message": "Mémoire enregistrée", "key": entry.key, "value": entry.value}
    except sqlite3.IntegrityError:
        raise HTTPException(status_code=400, detail="Clé déjà existante")

@app.get("/memory/{key}")
def recall_memory(key: str):
    cursor.execute("SELECT value FROM memory WHERE key=?", (key,))
    result = cursor.fetchone()
    if result:
        return {"key": key, "value": result[0]}
    raise HTTPException(status_code=404, detail="Mémoire non trouvée")

@app.delete("/memory/{key}")
def delete_memory(key: str):
    cursor.execute("DELETE FROM memory WHERE key=?", (key,))
    conn.commit()
    return {"message": "Mémoire supprimée", "key": key}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
