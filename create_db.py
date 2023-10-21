import os
import random
import sys
import varastologiikka as vl

def create_db():
    db_name = "varasto.db"
    populate_db = True
    args = sys.argv[1:]
    if len(args) > 0:
        if "-t" in args or "--test" in args:
            db_name = "test.db"
        if "-e" in args or "--empty" in args:
            populate_db = False
    
    print("Luodaan tietokanta '{}'...".format(db_name))
    
    # Remove previous database when script is run
    if os.path.exists(db_name):
        os.remove(db_name)
    
    db = vl.Database(vl.Connection(db_name))
    with db._conn as connection:
        cur = connection.cursor()
    
        ### Create tables
        cur.execute("""
                    CREATE TABLE VARASTO
                        (VTunniste INTEGER NOT NULL,
                         Osoite VARCHAR(100) COLLATE NOCASE,
                        CONSTRAINT VARASTOPA PRIMARY KEY (VTunniste) );
                    """)
        cur.execute("""
                    CREATE TABLE SIJAINTI
                        (Hyllyväli INTEGER,
                         Sektio INTEGER,
                         Kerros INTEGER,
                         Kuormaruutu VARCHAR(8) COLLATE NOCASE,
                         Varasto INTEGER,
                         STunniste INTEGER NOT NULL,
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
                                NOT NULL DEFAULT 'EUR' COLLATE NOCASE,
                         Sijainti INTEGER,
                         Lavanumero INTEGER NOT NULL,
                        CONSTRAINT LAVAPA PRIMARY KEY (Lavanumero),
                        CONSTRAINT LAVASIJVA
                        FOREIGN KEY (Sijainti) REFERENCES SIJAINTI(STunniste)
                                    ON DELETE SET NULL ON UPDATE CASCADE );
                    """)
        cur.execute("""
                    CREATE TABLE SIIRTOTAPAHTUMA
                        (Siirtoaika VARCHAR(23) CHECK (Siirtoaika LIKE '____-__-__ __:__:__'),
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
                         Nimi VARCHAR(50) NOT NULL COLLATE NOCASE,
                         Valmistaja VARCHAR(25) COLLATE NOCASE,
                         Tuoteryhmä VARCHAR(50) NOT NULL DEFAULT 'Muut' COLLATE NOCASE,
                         Säilytyslt INTEGER NOT NULL DEFAULT 21,
                        CONSTRAINT TUOTEPA PRIMARY KEY (Tuotenumero),
                        CONSTRAINT TUOTETA UNIQUE (Nimi, Valmistaja) );
                    """)
        cur.execute("""
                    CREATE TABLE ERÄ
                        (Eränumero INTEGER NOT NULL,
                         Tuotenumero INTEGER NOT NULL,
                         PE_pvm CHAR(10) CHECK (PE_pvm LIKE '____-__-__'),
                         Myyntierät INTEGER DEFAULT 0,
                         ME_yksikkö VARCHAR(4) DEFAULT 'pkt' COLLATE NOCASE,
                         Määrä DECIMAL(6,2) DEFAULT 0.,
                         Määräyks VARCHAR(2) DEFAULT 'kg' COLLATE NOCASE,
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
        
        ### Create views
        cur.execute("""
                    CREATE VIEW TUOTETIEDOT AS
                    SELECT T.*, COUNT(E.Eränumero) AS Erämäärä
                    FROM TUOTE T LEFT OUTER JOIN ERÄ E ON T.Tuotenumero = E.Tuotenumero
                    GROUP BY T.Tuotenumero;
                    """)
        cur.execute("""
                    CREATE VIEW TUOTEERÄT AS
                    SELECT T.Nimi, T.Valmistaja, E.*, T.Tuoteryhmä, T.Säilytyslt, EL.Lavanumero, L.Tyyppi,
                           SIJAINTI_STR(S.Hyllyväli, S.Sektio, S.Kerros, S.Kuormaruutu) AS Sijainti, S.Varasto
                    FROM ERÄ E JOIN TUOTE T ON E.Tuotenumero = T.Tuotenumero
                    LEFT OUTER JOIN ERÄ_LAVALLA EL ON E.Eränumero = EL.Eränumero
                    LEFT OUTER JOIN LAVA L ON EL.Lavanumero = L.Lavanumero
                    LEFT OUTER JOIN SIJAINTI S ON L.Sijainti = S.STunniste;
                    """)
        cur.execute("""
                    CREATE VIEW LAVAPAIKAT AS
                    SELECT SIJAINTI_STR(S.Hyllyväli, S.Sektio, S.Kerros, S.Kuormaruutu) AS Sijainti,
                           S.Varasto, L.Lavanumero, L.Tyyppi, T.Nimi, E.PE_pvm, E.Ltk_määrä
                    FROM SIJAINTI S LEFT OUTER JOIN LAVA L ON S.STunniste = L.Sijainti
                    LEFT OUTER JOIN ERÄ_LAVALLA EL ON L.Lavanumero = EL.Lavanumero
                    LEFT OUTER JOIN ERÄ E ON EL.Eränumero = E.Eränumero
                    LEFT OUTER JOIN TUOTE T ON E.Tuotenumero = T.Tuotenumero;
                    """)
        cur.execute("""
                    CREATE VIEW LAVATIEDOT AS
                    SELECT L.Lavanumero, L.Tyyppi,
                           SIJAINTI_STR(S.Hyllyväli, S.Sektio, S.Kerros, S.Kuormaruutu) AS Sijainti,
                           E.Ltk_määrä, T.Nimi AS Tuotenimi, E.PE_pvm, ST.Siirtoaika
                    FROM LAVA L LEFT OUTER JOIN SIJAINTI S ON L.Sijainti = S.STunniste
                    LEFT OUTER JOIN ERÄ_LAVALLA EL ON L.Lavanumero = EL.Lavanumero
                    LEFT OUTER JOIN ERÄ E ON EL.Eränumero = E.Eränumero
                    LEFT OUTER JOIN TUOTE T ON E.Tuotenumero = T.Tuotenumero
                    LEFT OUTER JOIN SIIRTOTAPAHTUMA ST ON L.Lavanumero = ST.Lavanumero
                    GROUP BY L.Lavanumero;
                    """)
        cur.execute("""
                    CREATE VIEW VARASTOTIEDOT AS
                    SELECT V.VTunniste AS Tunniste, V.Osoite, COUNT(L.Lavanumero) AS Lavat,
                           COUNT(S.STunniste) AS Lavapaikat
                    FROM VARASTO V LEFT OUTER JOIN SIJAINTI S ON V.VTunniste = S.Varasto
                    LEFT OUTER JOIN LAVA L ON S.STunniste = L.Sijainti
                    GROUP BY V.VTunniste;
                    """)
        
        connection.commit()
    if not populate_db:
        return
    
    with db._conn as connection:
        cur = connection.cursor()
        
        ### Add some items to the tables
        # Add a couple of warehouse entries
        # VTunniste, Osoite
        cur.execute("""
                    INSERT INTO VARASTO VALUES
                        (145, 'Varastotie 13, 60100 Seinäjoki'),
                        (113, 'Rekkaväylä 2, 60100 Seinäjoki');
                    -- Values are fictional
                    """)
        
        # Add some shelves and floor units
        # Hyllyväli, Sektio, Kerros, Kuormaruutu, Varasto, STunniste
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
        
        # Add some pallets
        # Tyyppi, Sijainti, Lavanumero
        sijainnit = cur.execute("SELECT STunniste FROM SIJAINTI;")
        sijainnit = sijainnit.fetchall()
        paikat = random.sample(sijainnit, k=200)
        for i in range(220):
            cur.execute("INSERT INTO LAVA(Tyyppi) VALUES (?);", (random.choice(["EUR", "FIN", "TEH"]),))
        lavat = cur.execute("SELECT Lavanumero FROM LAVA;")
        lavat = lavat.fetchall()
        connection.commit()
        
    for i, paikka in enumerate(paikat):
        db.move_pallet(lavat[i][0], paikka[0])
        # cur.execute("UPDATE LAVA SET Sijainti = ? WHERE Lavanumero = ?", (paikka[0], lavat[i][0]))
        # cur.execute("INSERT INTO SIIRTOTAPAHTUMA VALUES (?, ?, ?)",
        #             (datetime.datetime.now().isoformat(" ", "seconds"), lavat[i][0], paikka[0]))
        
    # Add some products
    # Tuotenumero, Nimi, Valmistaja, Tuoteryhmä, Säilytyslt
    with db._conn as connection:
        cur = connection.cursor()
        cur.execute("""
                    INSERT INTO TUOTE(Nimi, Valmistaja, Tuoteryhmä, Säilytyslt) VALUES
                        ('Luuton joulukinkku n. 5kg', 'Atria', 'Lihapakasteet', -18),
                        ('Amppari-juomajää', 'Pirkka', 'Jäätelöt ja mehujäät', -18),
                        ('Cocktail-perunapiirakka', 'Myllyn Paras', 'Leivät ja leivokset', -18),
                        ('Pingviini vaniljajäätelö', 'Froneri', 'Jäätelöt ja mehujäät', -18);
                    """)
        
        # Add some product batches
        # Eränumero, Tuotenumero, PE_pvm, Myyntierät, ME_yksikkö, Määrä, Määräyks, Ltk_määrä
        tuotteet = cur.execute("SELECT Tuotenumero FROM TUOTE;")
        tuotteet = tuotteet.fetchall()
        erat = []
        ind = 0
        met = (60, 300, 200, 500)
        meyks = ("kpl", "pkt", "pss", "pkt")
        maara = (met[0] * 5., met[1] * 0.83, met[2] * 0.45, met[3])
        maarayks = ("kg", "kg", "kg", "l")
        ltk = (met[0] / 3, met[1] / 6, met[2] / 4, met[3] / 5)
        for ind, tuote in enumerate(tuotteet):
            eramaara = random.randint(10, 30)
            for x in range(eramaara):
                pe = vl.randdate()
                erat.append(
                    (random.randint(1, 999999), tuote[0], pe, met[ind],
                     meyks[ind], maara[ind], maarayks[ind], ltk[ind])
                    )
        cur.executemany("""
                        INSERT INTO ERÄ(Eränumero, Tuotenumero, PE_pvm, Myyntierät,
                        ME_yksikkö, Määrä, Määräyks, Ltk_määrä)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?);
                        """, erat)
        
        # Bind most batches to pallets
        # Lavanumero, Eränumero
        erat = cur.execute("SELECT Eränumero FROM ERÄ;")
        erat = erat.fetchall()
        siirto_lkm = int(len(erat) * (7/8))
        val_lavat = random.sample(lavat, k=siirto_lkm)
        val_erat = random.sample(erat, k=siirto_lkm)
        siirrot = []
        for i in range(siirto_lkm):
            siirrot.append((val_lavat[i][0], val_erat[i][0]))
        cur.executemany("INSERT INTO ERÄ_LAVALLA(Lavanumero, Eränumero) VALUES (?, ?);", siirrot)
        
        connection.commit()
    print("Tietokanta '{}' luotu.".format(db_name))

if __name__ == "__main__":
    create_db()
