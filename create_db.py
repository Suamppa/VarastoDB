import os
import sqlite3 as sql

def main():
    if os.path.exists("varasto.db"):
        os.remove("varasto.db")
    connection = sql.connect("varasto.db")
    cur = connection.cursor()
    cur.execute("""
                CREATE TABLE VARASTO
                    (Tunniste       INT             NOT NULL,
                     Osoite         VARCHAR(100),
                    PRIMARY KEY (Tunniste) );
                """)
    res = cur.execute("SELECT name FROM sqlite_master")
    res.fetchone()

if __name__ == "__main__":
    main()
