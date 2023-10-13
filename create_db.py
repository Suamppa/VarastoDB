import os
import sqlite3 as sql

def main():
    if os.path.exists("varasto.db"):
        os.remove("varasto.db")
    connection = sql.connect("varasto.db")
    cur = connection.cursor()
    cur.execute("""
                CREATE TABLE VARASTO
                    (VTunniste INT NOT NULL,
                     Osoite VARCHAR(100),
                    PRIMARY KEY (VTunniste) );
                """)
    cur.execute("""
                CREATE TABLE SIJAINTI
                    (STunniste INT NOT NULL,
                     Hyllyväli INT,
                     Sektio INT,
                     Kerros INT,
                     Kuormaruutu VARCHAR(8),
                     Varasto INT,
                    PRIMARY KEY (STunniste),
                    FOREIGN KEY (Varasto) REFERENCES VARASTO(VTunniste)
                                 ON DELETE CASCADE ON UPDATE CASCADE );
                """)
    cur.execute("""
                CREATE TABLE LAVA
                    (Lavanumero INT NOT NULL,
                     Tyyppi CHAR(3)
                            CHECK (Tyyppi = 'EUR' OR Tyyppi = 'FIN' OR Tyyppi = 'TEH')
                            NOT NULL DEFAULT 'EUR',
                     Sijainti INT,
                    PRIMARY KEY (Lavanumero),
                    FOREIGN KEY (Sijainti) REFERENCES SIJAINTI(STunniste)
                                 ON DELETE CASCADE ON UPDATE CASCADE );
                """)
    cur.execute("""
                CREATE TABLE SIIRTOTAPAHTUMA
                    (Siirtoaika VARCHAR(23)
                                CHECK (Siirtoaika LIKE
                                    '^\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}(?:\.\d{3})?$'
                                ),
                     Lavanumero INT NOT NULL,
                     Sijainti INT NOT NULL,
                    PRIMARY KEY (Lavanumero, Sijainti),
                    FOREIGN KEY (Lavanumero) REFERENCES LAVA(Lavanumero)
                                 ON DELETE CASCADE ON UPDATE CASCADE,
                    FOREIGN KEY (Sijainti) REFERENCES SIJAINTI(STunniste)
                                 ON DELETE CASCADE ON UPDATE CASCADE );
                """)
    
    # res = cur.execute("SELECT name FROM sqlite_master")
    # print(res.fetchone())

if __name__ == "__main__":
    main()
