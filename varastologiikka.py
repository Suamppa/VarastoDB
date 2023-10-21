import datetime
import pandas as pd
import random
import sqlite3 as sql

class _Connection:
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
        self._connection.create_function("SIJAINTI_STR", 4, location_to_str, deterministic=True)
        return self._connection

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self._connection is not None:
            self._connection.close()
            self._connection = None

class Database:
    """
    A class representing a SQLite database.

    Attributes:
        _conn (_Connection): The connection to the SQLite database.
    """

    def __init__(self, db_path: str):
        """
        Initializes a new instance of the Database class.

        Args:
            db_path (str): The path to the SQLite database file.
        """
        self._conn = _Connection(db_path)
    
    def _sanitize(self, string: str):
        """
        Sanitizes a string for use in SQL queries. Not bulletproof.

        Args:
            string (str): The string to sanitize.

        Returns:
            str: The sanitized string.
        """
        return (string.strip().replace("'", "''").replace('"', '""').replace(";", "")
                .replace("--", "").replace("/*", "").replace("*/", ""))
    
    def _query(self, query: str, params: tuple|dict=()):
        """
        Executes the given SQL query with the given parameters and returns the result set.

        Args:
            query (str): The SQL query to execute.
            params (tuple|dict, optional): The parameters to use in the query. Defaults to ().

        Returns:
            list: The result set of the query.
        """
        with self._conn as conn:
            cur = conn.cursor()
            cur.execute(query, params)
            return cur.fetchall()
    
    def search(self, table_name: str, search_term: str, select: str="*"):
        """
        Search for a given search term in the specified table in the database.

        Args:
            table_name (str): The name of the table to search in.
            search_term (str): The search term to search for.
            select (str, optional): The columns to select. Defaults to "*".

        Returns:
            list: A list of tuples containing the search results.
        """
        table_name = self._sanitize(table_name)
        search_term = self._sanitize(search_term)
        select = self._sanitize(select)
        return self._query("SELECT {0} FROM {1} WHERE * LIKE '%{2}%'".format(select, table_name, search_term))
    
    def get_table(self, table_name: str, select: str="*"):
        """
        Retrieve data from a specified table in the database.

        Args:
            table_name (str): The name of the table to retrieve data from.
            select (str, optional): The columns to retrieve. Defaults to "*".

        Returns:
            list: A list of tuples containing the retrieved data.
        """
        table_name = self._sanitize(table_name)
        select = self._sanitize(select)
        return self._query("SELECT {} FROM {}".format(select, table_name))
    
    def print_table(self, table_name: str, select="*"):
        """
        Prints the contents of a table.

        Args:
            table_name (str): The name of the table to print.
            select (str, optional): The columns to select. Defaults to "*".

        Returns:
            None
        """
        table_name = self._sanitize(table_name)
        select = self._sanitize(select)
        with self._conn as conn:
            print(pd.read_sql_query("SELECT {} FROM {}".format(select, table_name), conn))
        print()
    
    def move_pallet(self, pallet: int, move_to: int):
        """
        Moves a pallet to a new location in the warehouse and records the transaction in the database.

        Args:
            pallet (int): The ID of the pallet to be moved.
            move_to (int): The ID of the new location of the pallet.

        Returns:
            None
        """
        with self._conn as conn:
            cur = conn.cursor()
            cur.execute("UPDATE LAVA SET Sijainti = ? WHERE Lavanumero = ?", (move_to, pallet))
            cur.execute("INSERT INTO SIIRTOTAPAHTUMA VALUES (?, ?, ?)",
                        (datetime.datetime.now().isoformat(" ", "seconds"), pallet, move_to))
            conn.commit()
    
def location_to_str(aisle: int|None, section: int|None, floor: int|None, floor_unit: str|None):
    """
    Converts the given aisle, section, floor, and floor_unit values into a string representation of a location.

    Args:
        aisle (int|None): The aisle number of the location.
        section (int|None): The section number of the location.
        floor (int|None): The floor number of the location.
        floor_unit (str|None): The floor unit of the location.

    Returns:
        str: A string representation of the location, in the format "aisle-section-floor" if all values are not
        None, or just the floor_unit if any of the other values are None.
    """
    if aisle is None or section is None or floor is None:
        return floor_unit
    return "{}-{}-{}".format(aisle, section, floor)

def handle_input(options: dict[str, str], prompt="Valitse toiminto: "):
    """
    Displays a list of options and prompts the user to choose one.
    
    Args:
        options (dict[str, str]): A dictionary of options to choose from, where the keys are the option codes and the values are the option descriptions.
        prompt (str): The prompt to display to the user.
    
    Returns:
        str: The code of the chosen option.
    """
    while True:
        for key, value in options.items():
            print("{}. {}".format(key, value))
        choice = input(prompt).lower()
        print()
        if choice in options:
            return choice
        print("Virheellinen syöte, yritä uudelleen.")

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
