import datetime
import random
import sqlite3 as sql

class Connection:
    def __init__(self, db_path):
        self.db_path = db_path
        self._connection = None

    def __enter__(self):
        self._connection = sql.connect(self.db_path)
        return self._connection

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self._connection is not None:
            self._connection.close()
            self._connection = None

# Siirtoaika, Lavanumero, Sijainti
def lavasiirto(cur: sql.Cursor, lava, minne):
    cur.execute("UPDATE LAVA SET Sijainti = ? WHERE Lavanumero = ?", (minne, lava))
    cur.execute("INSERT INTO SIIRTOTAPAHTUMA VALUES (?, ?, ?)",
                (datetime.datetime.now().isoformat(" ", "seconds"), lava, minne))

def randdate(yrange=[2024, 2027], mrange=[1, 12], drange=[1, 31]):
    y = random.randint(yrange[0], yrange[1])
    m = random.randint(mrange[0], mrange[1])
    if drange[1] > 28:
        if m == 2:
            drange[1] = 28
        elif drange[1] > 30 & m in [4, 6, 9, 11]:
            drange[1] = 30
    d = random.randint(drange[0], drange[1])
    return datetime.date(y, m, d).isoformat()

def main():
    print("Access these functions by importing this library.")

if __name__ == "__main__":
    main()
