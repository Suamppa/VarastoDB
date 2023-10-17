import os
import sqlite3 as sql

def main():
    # Remove previous database when script is run
    if os.path.exists("varasto.db"):
        os.remove("varasto.db")
    
    connection = sql.connect("varasto.db")
    cur = connection.cursor()
    
    ### Create tables
    cur.execute("""
                CREATE TABLE VARASTO
                    (VTunniste INTEGER NOT NULL,
                     Osoite VARCHAR(100),
                    CONSTRAINT VARASTOPA PRIMARY KEY (VTunniste) );
                """)
    cur.execute("""
                CREATE TABLE SIJAINTI
                    (Hyllyväli INTEGER,
                     Sektio INTEGER,
                     Kerros INTEGER,
                     Kuormaruutu VARCHAR(8),
                     Varasto INTEGER,
                     STunniste INTEGER,
                    CONSTRAINT SIJAINTIPA PRIMARY KEY (STunniste),
                    CONSTRAINT HYLLYTA UNIQUE (Hyllyväli, Sektio, Kerros, Varasto),
                    CONSTRAINT RUTA UNIQUE (Kuormaruutu, Varasto),
                    CONSTRAINT SIJVARVA
                    FOREIGN KEY (Varasto) REFERENCES VARASTO(VTunniste)
                                 ON DELETE SET NULL ON UPDATE CASCADE );
                """)
    cur.execute("""
                CREATE TABLE LAVA
                    (Tyyppi CHAR(3)
                            CHECK (Tyyppi = 'EUR' OR Tyyppi = 'FIN' OR Tyyppi = 'TEH')
                            NOT NULL DEFAULT 'EUR',
                     Sijainti INTEGER,
                     Lavanumero INTEGER NOT NULL,
                    CONSTRAINT LAVAPA PRIMARY KEY (Lavanumero),
                    CONSTRAINT LAVASIJVA
                    FOREIGN KEY (Sijainti) REFERENCES SIJAINTI(STunniste)
                                 ON DELETE SET NULL ON UPDATE CASCADE );
                """)
    cur.execute("""
                CREATE TABLE SIIRTOTAPAHTUMA
                    (Siirtoaika VARCHAR(23)
                                CHECK (Siirtoaika LIKE
                                    '^\\d{4}-\\d{2}-\\d{2} \\d{2}:\\d{2}:\\d{2}(?:\\.\\d{3})?$'
                                ),
                     Lavanumero INTEGER NOT NULL,
                     Sijainti INTEGER NOT NULL,
                    PRIMARY KEY (Lavanumero, Sijainti),
                    FOREIGN KEY (Lavanumero) REFERENCES LAVA(Lavanumero)
                                 ON DELETE CASCADE ON UPDATE CASCADE,
                    FOREIGN KEY (Sijainti) REFERENCES SIJAINTI(STunniste)
                                 ON DELETE CASCADE ON UPDATE CASCADE );
                """)
    cur.execute("""
                CREATE TABLE TUOTE
                    (Tuotenumero INTEGER NOT NULL,
                     Nimi VARCHAR(50) NOT NULL,
                     Valmistaja VARCHAR(25),
                     Tuoteryhmä VARCHAR(50) NOT NULL DEFAULT 'Muut',
                     Säilytyslt INTEGER NOT NULL DEFAULT 21,
                    CONSTRAINT TUOTEPA PRIMARY KEY (Tuotenumero),
                    CONSTRAINT TUOTETA UNIQUE (Nimi, Valmistaja) );
                """)
    cur.execute("""
                CREATE TABLE ERÄ
                    (Eränumero INTEGER NOT NULL,
                     Tuotenumero INTEGER NOT NULL,
                     PE_pvm CHAR(10) CHECK (PE_pvm LIKE '^\\d{4}-\\d{2}-\\d{2}$'),
                     Myyntierät INTEGER DEFAULT 0,
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
                    (Lavanumero INTEGER NOT NULL,
                     Eränumero INTEGER NOT NULL,
                    PRIMARY KEY (Lavanumero, Eränumero),
                    FOREIGN KEY (Lavanumero) REFERENCES LAVA(Lavanumero)
                                 ON DELETE CASCADE ON UPDATE CASCADE,
                    FOREIGN KEY (Eränumero) REFERENCES ERÄ(Eränumero)
                                 ON DELETE CASCADE ON UPDATE CASCADE );
                """)
    connection.commit()
    
    ### Add some items to the tables
    cur.execute("""
                INSERT INTO VARASTO VALUES
                    (145, 'Varastotie 13, 60100 Seinäjoki'),
                    (113, 'Rekkaväylä 2, 60100 Seinäjoki');
                -- Values are fictional
                """)
    
    hyllyt = []
    for vali in range(1, 31):
        for sektio in range(1, 9):
            for kerros in range(1, 9):
                hyllyt.append((vali, sektio, kerros))
    hyllyt2 = []
    for vali in range(1, 11):
        for sektio in range(1, 13):
            for kerros in range(1, 6):
                hyllyt2.append((vali, sektio, kerros))
    ru_paikat = []
    for ru in range(1, 41):
        ru_paikat.append(("RU94{:d}".format(ru),))
    for ru in range(1, 21):
        ru_paikat.append(("RU200{:d}".format(ru),))
    cur.executemany("INSERT INTO SIJAINTI(Hyllyväli, Sektio, Kerros, Varasto) VALUES (?, ?, ?, 145);", hyllyt)
    cur.executemany("INSERT INTO SIJAINTI(Hyllyväli, Sektio, Kerros, Varasto) VALUES (?, ?, ?, 113);", hyllyt2)
    cur.executemany("INSERT INTO SIJAINTI(Kuormaruutu, Varasto) VALUES (?, 145);", ru_paikat)
    
    connection.commit()
    
    ### TESTS
    # for row in cur.execute("SELECT * FROM SIJAINTI WHERE (Hyllyväli BETWEEN 3 AND 5) AND Varasto = 145"):
    #     print(row)
    # for row in cur.execute("SELECT * FROM SIJAINTI WHERE (Kuormaruutu LIKE 'RU200%') AND Varasto = 145"):
    #     print(row)
    
    connection.close()

if __name__ == "__main__":
    main()
