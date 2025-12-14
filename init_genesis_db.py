import os, sqlite3
db = os.getenv("GENESIS_DB_PATH", "./genesis.db")
conn = sqlite3.connect(db)
cur = conn.cursor()
cur.execute("""
CREATE TABLE IF NOT EXISTS events(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    topic TEXT NOT NULL,
    payload TEXT NOT NULL,
    ts TEXT NOT NULL
);""")
cur.execute("""
CREATE TABLE IF NOT EXISTS dedupe(
    key TEXT PRIMARY KEY,
    ts TEXT NOT NULL
);""")
conn.commit()
conn.close()
print("✔ Genesis tables created in", db)
