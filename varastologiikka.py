import datetime
import pandas as pd
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

class Database:
    def __init__(self, conn: Connection):
        """
        Initializes a new instance of the Database class.

        Args:
            conn (Connection): A reference to the connection to the database.
        """
        self._conn = conn
    
    def query(self, query: str, params: tuple=()):
        """
        Executes the given SQL query with the given parameters and returns the result set.

        Args:
            query (str): The SQL query to execute.
            params (tuple, optional): The parameters to use in the query. Defaults to ().

        Returns:
            list: The result set of the query.
        """
        with self._conn as conn:
            cur = conn.cursor()
            if not len(params):
                cur.execute(query)
            else:
                cur.execute(query, params)
            return cur.fetchall()
    
    def get_table(self, table_name: str, select: str="*"):
        """
        Retrieve data from a specified table in the database.

        Args:
            table_name (str): The name of the table to retrieve data from.
            select (str, optional): The columns to retrieve. Defaults to "*".

        Returns:
            list: A list of tuples containing the retrieved data.
        """
        with self._conn as conn:
            cur = conn.cursor()
            cur.execute("SELECT {} FROM {}".format(select, table_name))
            return cur.fetchall()
    
    def print_table(self, table_name: str, select="*"):
        """
        Prints the contents of a table.

        Args:
            table_name (str): The name of the table to print.
            select (str, optional): The columns to select. Defaults to "*".

        Returns:
            None
        """
        with self._conn as conn:
            print(pd.read_sql_query("SELECT {} FROM {}".format(select, table_name), conn))
        print()
    
    def location_to_str(self, location: tuple):
        if len(location) != 6:
            raise ValueError("Location must be a tuple of length 6.")
        if location[3] is None:
            return "{}-{}-{}".format(location[0], location[1], location[2])
        else:
            return location[3]

def handle_input(options: dict, prompt="Valitse toiminto: "):
    while True:
        for key, value in options.items():
            print("{}. {}".format(key, value))
        choice = input(prompt).lower()
        print()
        if choice in options:
            return choice
        print("Virheellinen syöte, yritä uudelleen.")

def move_pallet(database, pallet, move_to):
    """
    Moves a pallet to a new location in the warehouse and records the transaction in the database.

    Args:
        database (str): The filepath of the database.
        pallet (int): The ID of the pallet to be moved.
        move_to (int): The ID of the new location of the pallet.

    Returns:
        None
    """
    with Connection(database) as conn:
        cur = conn.cursor()
        cur.execute("UPDATE LAVA SET Sijainti = ? WHERE Lavanumero = ?", (move_to, pallet))
        cur.execute("INSERT INTO SIIRTOTAPAHTUMA VALUES (?, ?, ?)",
                    (datetime.datetime.now().isoformat(" ", "seconds"), pallet, move_to))
        conn.commit()

# Siirtoaika, Lavanumero, Sijainti
# def move_pallet(cur: sql.Cursor, pallet, move_to):
#     """
#     Moves a pallet from one location to another and logs the transaction in the database.

#     Args:
#         cur (sqlite3.Cursor): The cursor object for the database connection.
#         pallet (int): The pallet number to be moved.
#         move_to (int): The id of the new location of the pallet.

#     Returns:
#         None
#     """
#     cur.execute("UPDATE LAVA SET Sijainti = ? WHERE Lavanumero = ?", (move_to, pallet))
#     cur.execute("INSERT INTO SIIRTOTAPAHTUMA VALUES (?, ?, ?)",
#                 (datetime.datetime.now().isoformat(" ", "seconds"), pallet, move_to))

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
