import os
import sqlite3 as sql

def main():
    if os.path.exists("varasto.db"):
        os.remove("varasto.db")
    connection = sql.connect("varasto.db")
    cur = connection.cursor()
    cur.execute("""
                CREATE TABLE VARASTO
                    (VTunniste      INT             NOT NULL,
                     Osoite         VARCHAR(100),
                    PRIMARY KEY (Tunniste) );
                """)
    cur.execute("""
                CREATE TABLE SIJAINTI
                    (STunniste      INT             NOT NULL,
                     Hyllyväli      INT,
                     Sektio         INT,
                     Kerros         INT,
                     Kuormaruutu    VARCHAR(8),
                     Varasto        INT,
                    PRIMARY KEY (STunniste),
                    FOREIGN KEY (Varasto) REFERENCES VARASTO(VTunniste)
                                 ON DELETE CASCADE      ON UPDATE CASCADE );
                """)
    
    # res = cur.execute("SELECT name FROM sqlite_master")
    # print(res.fetchone())

if __name__ == "__main__":
    main()
