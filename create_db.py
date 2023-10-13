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
                    CONSTRAINT VARASTOPA PRIMARY KEY (VTunniste) );
                """)
    cur.execute("""
                CREATE TABLE SIJAINTI
                    (STunniste INT NOT NULL,
                     Hyllyväli INT,
                     Sektio INT,
                     Kerros INT,
                     Kuormaruutu VARCHAR(8),
                     Varasto INT,
                    CONSTRAINT SIJAINTIPA PRIMARY KEY (STunniste),
                    CONSTRAINT SIJVARVA
                    FOREIGN KEY (Varasto) REFERENCES VARASTO(VTunniste)
                                 ON DELETE SET NULL ON UPDATE CASCADE );
                """)
    cur.execute("""
                CREATE TABLE LAVA
                    (Lavanumero INT NOT NULL,
                     Tyyppi CHAR(3)
                            CHECK (Tyyppi = 'EUR' OR Tyyppi = 'FIN' OR Tyyppi = 'TEH')
                            NOT NULL DEFAULT 'EUR',
                     Sijainti INT,
                    CONSTRAINT LAVAPA PRIMARY KEY (Lavanumero),
                    CONSTRAINT LAVASIJVA
                    FOREIGN KEY (Sijainti) REFERENCES SIJAINTI(STunniste)
                                 ON DELETE SET NULL ON UPDATE CASCADE );
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
    cur.execute("""
                CREATE TABLE TUOTE
                    (Tuotenumero INT NOT NULL,
                     Nimi VARCHAR(50) NOT NULL,
                     Valmistaja VARCHAR(25),
                     Tuoteryhmä VARCHAR(50) NOT NULL DEFAULT 'Muut',
                     Säilytyslt INT NOT NULL DEFAULT 21,
                    CONSTRAINT TUOTEPA PRIMARY KEY (Tuotenumero),
                    CONSTRAINT TUOTETA UNIQUE (Nimi, Valmistaja) );
                """)
    cur.execute("""
                CREATE TABLE ERÄ
                    (Eränumero INT NOT NULL,
                     Tuotenumero INT NOT NULL,
                     PE_pvm CHAR(10) CHECK (PE_pvm LIKE '^\d{4}-\d{2}-\d{2}$'),
                     Myyntierät INT DEFAULT 0,
                     ME_yksikkö VARCHAR(4) DEFAULT 'pkt',
                     Paino DECIMAL(6,2) DEFAULT 0.,
                     Painoyks VARCHAR(2) DEFAULT 'kg',
                     Ltk_määrä DECIMAL(5,2) DEFAULT 0.,
                    CONSTRAINT ERÄPA PRIMARY KEY (Eränumero, Tuotenumero),
                    CONSTRAINT ERÄTUOTEVA
                    FOREIGN KEY (Tuotenumero) REFERENCES TUOTE(Tuotenumero)
                                 ON DELETE CASCADE ON UPDATE CASCADE );
                """)
    cur.execute("""
                CREATE TABLE ERÄ_LAVALLA
                    (Lavanumero INT NOT NULL,
                     Eränumero INT NOT NULL,
                    PRIMARY KEY (Lavanumero, Eränumero),
                    FOREIGN KEY (Lavanumero) REFERENCES LAVA(Lavanumero)
                                 ON DELETE CASCADE ON UPDATE CASCADE,
                    FOREIGN KEY (Eränumero) REFERENCES ERÄ(Eränumero)
                                 ON DELETE CASCADE ON UPDATE CASCADE );
                """)

if __name__ == "__main__":
    main()
