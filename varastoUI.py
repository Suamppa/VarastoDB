import varastologiikka as vl

def scroll_info(db: vl.Database):
    while True: 
        print("Selaa:")
        labels = ["Tuotteet", "Erät", "Lavapaikat", "Lavat", "Varastot"]
        options = {str(i+1): label for i, label in enumerate(labels)}
        options["0"] = "Palaa"
        choice = vl.handle_input(options)
        if choice == "0":
            return
        elif choice == "1":
            table = ("""
                     TUOTE T LEFT OUTER JOIN ERÄ E ON T.Tuotenumero = E.Tuotenumero
                     GROUP BY T.Tuotenumero
                     """)
            select = "T.*, COUNT(E.Eränumero) AS Erämäärä"
            db.print_table(table, select)
        elif choice == "2":
            table = ("""
                     ERÄ E JOIN TUOTE T ON E.Tuotenumero = T.Tuotenumero
                     LEFT OUTER JOIN ERÄ_LAVALLA EL ON E.Eränumero = EL.Eränumero
                     LEFT OUTER JOIN LAVA L ON EL.Lavanumero = L.Lavanumero
                     LEFT OUTER JOIN SIJAINTI S ON L.Sijainti = S.STunniste
                     """)
            select = ("""
                      T.Nimi, T.Valmistaja, E.*, T.Tuoteryhmä, T.Säilytyslt, EL.Lavanumero,
                      L.Tyyppi, S.Hyllyväli, S.Sektio, S.Kerros, S.Kuormaruutu, S.Varasto
                      """)
            db.print_table(table, select)
        elif choice == "3":
            table = ("""
                     SIJAINTI S LEFT OUTER JOIN LAVA L ON S.STunniste = L.Sijainti
                     LEFT OUTER JOIN ERÄ_LAVALLA EL ON L.Lavanumero = EL.Lavanumero
                     LEFT OUTER JOIN ERÄ E ON EL.Eränumero = E.Eränumero
                     LEFT OUTER JOIN TUOTE T ON E.Tuotenumero = T.Tuotenumero
                     """)
            select = ("""
                      S.Hyllyväli, S.Sektio, S.Kerros, S.Kuormaruutu, S.Varasto,
                      L.Lavanumero, L.Tyyppi, T.Nimi, E.PE_pvm, E.Ltk_määrä
                      """)
            db.print_table(table, select)
        elif choice == "4":
            table = ("""
                     LAVA L LEFT OUTER JOIN SIJAINTI S ON L.Sijainti = S.STunniste
                     LEFT OUTER JOIN ERÄ_LAVALLA EL ON L.Lavanumero = EL.Lavanumero
                     LEFT OUTER JOIN ERÄ E ON EL.Eränumero = E.Eränumero
                     LEFT OUTER JOIN TUOTE T ON E.Tuotenumero = T.Tuotenumero
                     LEFT OUTER JOIN SIIRTOTAPAHTUMA ST ON L.Lavanumero = ST.Lavanumero
                     GROUP BY L.Lavanumero
                     """)
            select = ("""
                      L.Lavanumero, L.Tyyppi, S.Hyllyväli, S.Sektio, S.Kerros, S.Kuormaruutu,
                      E.Ltk_määrä, T.Nimi, E.PE_pvm, ST.Siirtoaika
                      """)
            db.print_table(table, select)
        elif choice == "5":
            db.print_table("VARASTO", "VTunniste AS Tunniste, Osoite")

def main():
    print("Tervetuloa varastonhallintajärjestelmään!\n")
    db = vl.Database(vl.Connection("varasto.db"))
    while True:
        options = {"1": "Haku", "2": "Selaa tietoja", "3": "Lisää tietoja", "0": "Poistu"}
        choice = vl.handle_input(options)
        
        if choice == "0":
            break
        elif choice == "1":
            pass
        elif choice == "2":
            scroll_info(db)
        elif choice == "3":
            pass
        
    print("Järjestelmä suljetaan.")

if __name__ == "__main__":
    main()
