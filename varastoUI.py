import varastologiikka as vl

def search_db(db: vl.Database):
    while True:
        print("Hae:")
        labels = ["Tuotteet", "Erät", "Lavapaikat", "Lavat", "Varastot", "Siirtotapahtumat"]
        options = {str(i+1): label for i, label in enumerate(labels)}
        options["0"] = "Palaa"
        choice = vl.handle_input(options)
        if choice == "0": # Palaa
            return
        elif choice == "1": # Tuotteet
            pass
        elif choice == "2": # Erät
            pass
        elif choice == "3": # Lavapaikat
            pass
        elif choice == "4": # Lavat
            pass
        elif choice == "5": # Varastot
            pass
        elif choice == "6": # Siirtotapahtumat
            pass

def scroll_info(db: vl.Database):
    while True: 
        print("Selaa:")
        labels = ["Tuotteet", "Erät", "Lavapaikat", "Lavat", "Varastot"]
        options = {str(i+1): label for i, label in enumerate(labels)}
        options["0"] = "Palaa"
        choice = vl.handle_input(options)
        if choice == "0": # Palaa
            return
        elif choice == "1": # Tuotteet
            table = ("""
                     TUOTE T LEFT OUTER JOIN ERÄ E ON T.Tuotenumero = E.Tuotenumero
                     GROUP BY T.Tuotenumero
                     """)
            select = "T.*, COUNT(E.Eränumero) AS Erämäärä"
            db.print_table(table, select)
        elif choice == "2": # Erät
            table = ("""
                     ERÄ E JOIN TUOTE T ON E.Tuotenumero = T.Tuotenumero
                     LEFT OUTER JOIN ERÄ_LAVALLA EL ON E.Eränumero = EL.Eränumero
                     LEFT OUTER JOIN LAVA L ON EL.Lavanumero = L.Lavanumero
                     LEFT OUTER JOIN SIJAINTI S ON L.Sijainti = S.STunniste
                     """)
            select = ("""
                      T.Nimi, T.Valmistaja, E.*, T.Tuoteryhmä, T.Säilytyslt, EL.Lavanumero, L.Tyyppi,
                      SIJAINTI_STR(S.Hyllyväli, S.Sektio, S.Kerros, S.Kuormaruutu) AS Sijainti,
                      S.Varasto
                      """)
            db.print_table(table, select)
        elif choice == "3": # Lavapaikat
            table = ("""
                     SIJAINTI S LEFT OUTER JOIN LAVA L ON S.STunniste = L.Sijainti
                     LEFT OUTER JOIN ERÄ_LAVALLA EL ON L.Lavanumero = EL.Lavanumero
                     LEFT OUTER JOIN ERÄ E ON EL.Eränumero = E.Eränumero
                     LEFT OUTER JOIN TUOTE T ON E.Tuotenumero = T.Tuotenumero
                     """)
            select = ("""
                      SIJAINTI_STR(S.Hyllyväli, S.Sektio, S.Kerros, S.Kuormaruutu) AS Sijainti,
                      S.Varasto, L.Lavanumero, L.Tyyppi, T.Nimi, E.PE_pvm, E.Ltk_määrä
                      """)
            db.print_table(table, select)
        elif choice == "4": # Lavat
            table = ("""
                     LAVA L LEFT OUTER JOIN SIJAINTI S ON L.Sijainti = S.STunniste
                     LEFT OUTER JOIN ERÄ_LAVALLA EL ON L.Lavanumero = EL.Lavanumero
                     LEFT OUTER JOIN ERÄ E ON EL.Eränumero = E.Eränumero
                     LEFT OUTER JOIN TUOTE T ON E.Tuotenumero = T.Tuotenumero
                     LEFT OUTER JOIN SIIRTOTAPAHTUMA ST ON L.Lavanumero = ST.Lavanumero
                     GROUP BY L.Lavanumero
                     """)
            select = ("""
                      L.Lavanumero, L.Tyyppi,
                      SIJAINTI_STR(S.Hyllyväli, S.Sektio, S.Kerros, S.Kuormaruutu) AS Sijainti,
                      E.Ltk_määrä, T.Nimi AS Tuotenimi, E.PE_pvm, ST.Siirtoaika
                      """)
            db.print_table(table, select)
        elif choice == "5": # Varastot
            db.print_table("VARASTO", "VTunniste AS Tunniste, Osoite")

def main():
    print("Tervetuloa varastonhallintajärjestelmään!\n")
    db = vl.Database(vl.Connection("varasto.db"))
    while True:
        options = {"1": "Haku", "2": "Selaa tietoja", "3": "Lisää tietoja", "0": "Poistu"}
        choice = vl.handle_input(options)
        
        if choice == "0": # Poistu
            break
        elif choice == "1": # Haku
            search_db(db)
        elif choice == "2": # Selaa tietoja
            scroll_info(db)
        elif choice == "3": # Lisää tietoja
            pass
        
    print("Järjestelmä suljetaan.")

if __name__ == "__main__":
    main()
