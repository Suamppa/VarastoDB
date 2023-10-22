import datetime
from typing import Sequence
import pandas as pd
import random
import re
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
    
    @staticmethod
    def sanitize(string: str):
        """
        Sanitizes a string for use in SQL queries. Not bulletproof.

        Args:
            string (str): The string to sanitize.

        Returns:
            str: The sanitized string.
        """
        return (string.strip().replace("'", "''").replace('"', '""').replace(";", "")
                .replace("--", "").replace("/*", "").replace("*/", ""))
    
    def _query(self, query: str, params: dict|Sequence=()):
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
    
    def search_and_print(self, table_name: str, search_term: str, select: str="*"):
        """
        Search for a given search term in the specified table in the database.

        Args:
            table_name (str): The name of the table to search in.
            search_term (str): The search term to search for.
            select (str, optional): The columns to select. Defaults to "*".

        Returns:
            list: A list of tuples containing the search results.
        """
        table_name = self.sanitize(table_name)
        search_term = self.sanitize(search_term)
        select = self.sanitize(select)
        # cols is [(cid, col_name, data_type, not_null, default_value, pk)]
        cols = self._query("PRAGMA table_info({});".format(table_name))
        keys = ("cid", "col_name", "data_type", "not_null", "default_value", "pk")
        # Convert cols to a list of dictionaries with keys
        attrs = [dict(zip(keys, col)) for col in cols]
        num_types = ("INT", "REAL", "FLOAT", "DOUBLE", "NUMERIC", "DECIMAL")
        
        # Build the query, making sure data types are handled correctly
        query = "SELECT {} FROM {} WHERE ".format(select, table_name)
        for attr in attrs:
            if search_term.isdecimal():
                for num_type in num_types:
                    if attr["data_type"] in num_type:
                        # Numeric types are compared with = instead of LIKE
                        query += "({} = {}) OR ".format(attr["col_name"], search_term)
                        break
                else:
                    query += "({} LIKE '%{}%') OR ".format(attr["col_name"], search_term)
            else:
                query += "({} LIKE '%{}%') OR ".format(attr["col_name"], search_term)
        self.print_query(query[:-4] + ";")
    
    @staticmethod
    def build_where(compare_attrs: Sequence, comparators: tuple[str,...], logicals: tuple[str,...]):
        """
        Build a sequence of where clause statements with compared attributes and placeholders '?' around
        the comparators followed by the logicals. The number of logicals must be one less than the
        number of comparisons/comparators.

        Args:
            compare_attrs (tuple): A tuple of compared attributes to use in the where clause.
            comparators (tuple[str]): A tuple of comparator strings to use between the placeholders.
            logicals (tuple[str]): A tuple of logical strings to use between the comparisons.
        
        Returns:
            str: A string representing the statements for a where clause.
                 (Eg. "(? = ?) AND (? > ?)")
        
        Raises:
            ValueError: If the number of logicals is not one less than the number of comparators.
        """
        if len(compare_attrs) == len(comparators) != (len(logicals) + 1):
            raise ValueError("The number of logicals must be one less than the number of comparators.")
        where = ""
        for i, comp in enumerate(compare_attrs[:-1]):
            where += "({} {} ?) {} ".format(comp, comparators[i], logicals[i])
        where += "({} {} ?)".format(compare_attrs[-1], comparators[-1])
        return where
    
    def get_table(
        self, table_name: str, select: str="*", compare_attrs: Sequence=(), compare_to: Sequence=(),
        comparators: tuple[str,...]=(), logicals: tuple[str,...]=()
        ):
        """
        Retrieve data from a specified table in the database with an optional where clause.

        Args:
            table_name (str): The name of the table to retrieve data from.
            select (str, optional): The columns to retrieve. Defaults to "*".

        Returns:
            list: A list of tuples containing the retrieved data.
        """
        table_name = self.sanitize(table_name)
        select = self.sanitize(select)
        if len(compare_attrs) >= 2 and len(compare_to) >= 2:
            placeholders = self.build_where(compare_attrs, comparators, logicals)
            return self._query(
                "SELECT {} FROM {} WHERE {}".format(select, table_name, placeholders), compare_to
                )
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
        table_name = self.sanitize(table_name)
        select = self.sanitize(select)
        with self._conn as conn:
            print(pd.read_sql_query("SELECT {} FROM {}".format(select, table_name), conn))
        print()
    
    def print_query(self, query: str, params: tuple|dict=()):
        """
        Prints the result of a query.

        Args:
            query (str): The query to execute.
            params (tuple|dict, optional): The parameters to use in the query. Defaults to ().

        Returns:
            None
        """
        with self._conn as conn:
            res = pd.read_sql_query(query, conn, params=params)
            if res.empty:
                print("Ei tuloksia.")
            else:
                print(res)
        print()
    
    def location_is_free(self, location: int) -> int|None:
        res = self._query("SELECT Lavanumero FROM LAVAPAIKAT WHERE Sijainti_ID = ?", (location,))
        if not res:
            raise ValueError("Sijaintia ei ole olemassa.")
        return res[0][0]
    
    # TODO: Make use of _query()
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
    
    def add_entry(self, table_name: str, values: tuple):
        """
        Adds a new entry to the specified table in the database.

        Args:
            table_name (str): The name of the table to add the entry to.
            values (tuple): The values of the new entry.

        Returns:
            None
        """
        table_name = self.sanitize(table_name)
        values = tuple(self.sanitize(str(value)) for value in values)
        try:
            with self._conn as conn:
                cur = conn.cursor()
                cur.execute("INSERT INTO {} VALUES ({})".format(table_name, ", ".join("?"*len(values))), values)
        except sql.IntegrityError:
            print("Virhe: Tietue on jo olemassa.")
        except sql.OperationalError:
            print("Virhe: Tietueen lisääminen ei onnistunut.")
        else:
            conn.commit()
            print("{} lisätty tauluun {}.".format(", ".join(values), table_name.upper()))
    
    def delete_entry(self, table_name: str, key: str, value: str):
        """
        Deletes an entry from the specified table in the database.

        Args:
            table_name (str): The name of the table to delete the entry from.
            key (str): The name of the column to use as the key.
            value (str): The value of the key.

        Returns:
            None
        """
        table_name = self.sanitize(table_name)
        key = self.sanitize(key)
        value = self.sanitize(value)
        try:
            with self._conn as conn:
                cur = conn.cursor()
                cur.execute("DELETE FROM {} WHERE {} = ?".format(table_name, key), (value,))
        except sql.OperationalError:
            print("Virhe: Tietueen poistaminen ei onnistunut.")
        else:
            conn.commit()
            print("Tietue poistettu taulusta {}.".format(table_name.upper()))
    
    @staticmethod
    def is_location_format(location: str):
        """
        Check if the given location string is in the correct format.

        Args:
            location (str): The location string to check.

        Returns:
            tuple: A tuple containing two boolean values. The first value indicates if the
            location is in the correct format, and the second value indicates if the location
            is a floor unit (starting with "RU").
        """
        if bool(re.fullmatch(r"^RU\S+$", location)):
            return True, True
        return bool(re.fullmatch(r"^\d+-\d+-\d+$", location)), False
    
    @staticmethod
    def str_to_location(location: str):
        """
        Converts a string representation of a location into a tuple of aisle, section, floor, and floor_unit values.

        Args:
            location (str): A string representation of a location, in the format "aisle-section-floor" or
                            "floor_unit" (eg. "RU1234").

        Returns:
            tuple: A tuple of aisle, section, floor, and floor_unit values.
        """
        location = Database.sanitize(location).upper()
        shelf = tuple()
        valid, ru = Database.is_location_format(location)
        if valid:
            if ru:
                return None, None, None, location
            shelf = tuple(location.split("-"))
        return shelf + (None,) * (4 - len(shelf))
    
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

def handle_input(option_labels: Sequence[str], prompt="Valitse toiminto: ", back: str|None="0",
                 back_label: str="Takaisin", allow_empty=True, empty_label=""):
    """
    Displays a list of options to the user and prompts them to choose one.

    Args:
        option_labels (Sequence[str]): A sequence of strings representing the options to display.
        prompt (str, optional): The prompt to display to the user. Defaults to "Valitse toiminto: ".
        back (str|None, optional): The label for the "back" option, or None if no back option should be displayed.
                                   Defaults to "0".
        allow_empty (bool, optional): Whether to allow the user to choose an empty option. Defaults to True.

    Returns:
        str: The key of the chosen option.
    """
    options = {str(i+1): label for i, label in enumerate(option_labels)}
    if back:
        options[back] = back_label
    if allow_empty:
        options[""] = empty_label
    while True:
        for key, value in options.items():
            if allow_empty and key == "":
                continue
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
