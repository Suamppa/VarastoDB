import datetime
import random
import sqlite3 as sql

class Connection:
    """
    A context manager for connecting to a SQLite database.

    Args:
        db_path (str): The path to the SQLite database file.

    Attributes:
        db_path (str): The path to the SQLite database file.
        _connection (sqlite3.Connection): The connection object to the database.

    Methods:
        __enter__(): Enters the context and returns the connection object.
        __exit__(exc_type, exc_val, exc_tb): Exits the context and closes the connection.
    """
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

def handle_input(options: dict, prompt="Valitse toiminto: "):
    while True:
        for key, value in options.items():
            print("{}. {}".format(key, value))
        choice = input(prompt).lower()
        if choice in options:
            return choice
        print("Virheellinen syöte, yritä uudelleen.")

# Siirtoaika, Lavanumero, Sijainti
def move_pallet(cur: sql.Cursor, pallet, move_to):
    """
    Moves a pallet from one location to another and logs the transaction in the database.

    Args:
        cur (sqlite3.Cursor): The cursor object for the database connection.
        pallet (int): The pallet number to be moved.
        move_to (int): The id of the new location of the pallet.

    Returns:
        None
    """
    cur.execute("UPDATE LAVA SET Sijainti = ? WHERE Lavanumero = ?", (move_to, pallet))
    cur.execute("INSERT INTO SIIRTOTAPAHTUMA VALUES (?, ?, ?)",
                (datetime.datetime.now().isoformat(" ", "seconds"), pallet, move_to))

def randdate(yrange=[2024, 2027], mrange=[1, 12], drange=[1, 31]):
    """
    Returns a random date as a string in ISO format (YYYY-MM-DD).

    Args:
        yrange (list): A list of two integers representing the range of years to choose from (inclusive).
        mrange (list): A list of two integers representing the range of months to choose from (inclusive).
        drange (list): A list of two integers representing the range of days to choose from (inclusive).

    Returns:
        str: A string representing a random date in ISO format (YYYY-MM-DD).
    """
    # Check that the ranges are valid
    if yrange[0] > yrange[1]:
        yrange = [yrange[1], yrange[0]]
    if mrange[0] > mrange[1]:
        mrange = [mrange[1], mrange[0]]
    if drange[0] > drange[1]:
        drange = [drange[1], drange[0]]
    if yrange[0] < datetime.MINYEAR:
        yrange[0] = datetime.MINYEAR
    if yrange[1] > datetime.MAXYEAR:
        yrange[1] = datetime.MAXYEAR
    if mrange[0] < 1:
        mrange[0] = 1
    if mrange[1] > 12:
        mrange[1] = 12
    if drange[0] < 1:
        drange[0] = 1
    if drange[1] > 31:
        drange[1] = 31
    
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
