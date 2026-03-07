import sqlite3

def conectar():

    conn = sqlite3.connect("conexoes.db")

    conn.execute("""
    CREATE TABLE IF NOT EXISTS conexoes(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nome TEXT,
        host TEXT,
        usuario TEXT,
        senha TEXT,
        porta INTEGER,
        protocolo TEXT,
        grupo TEXT
    )
    """)
    conn.commit()
    return conn