import os
import sqlite3

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)),"data","bytegasto.db")

def init_db():
    with sqlite3.connect(DB_PATH) as con:
        con.execute("""
        CREATE TABLE IF NOT EXISTS Gastos (
            Id INTEGER PRIMARY KEY AUTOINCREMENT,
            UserId INTEGER,
            Valor REAL,
            Categoria TEXT,
            Data TEXT,
            raw_texto TEXT
        )""")

def insert_gasto(user_id, valor, categoria, data, raw_texto):
    with sqlite3.connect(DB_PATH) as con:
        con.execute("""INSERT INTO Gastos
                    (UserId, Valor, Categoria, Data, raw_texto)
                    VALUES (?, ?, ?, ?, ?)""",
                    (user_id, valor, categoria, data, raw_texto))

def get_gastos(user_id):
    with sqlite3.connect(DB_PATH) as con:
        cursor = con.execute(
            "SELECT Valor, Categoria, Data, raw_texto FROM Gastos WHERE UserId = ?",
            (user_id,)
        )
        return cursor.fetchall()

def get_gastos_por_categoria(user_id):
    with sqlite3.connect(DB_PATH) as con:
        cursor = con.execute(
            "SELECT Categoria, SUM(Valor) FROM Gastos WHERE UserId = ? GROUP BY Categoria",
            (user_id,)
        )
        return cursor.fetchall()