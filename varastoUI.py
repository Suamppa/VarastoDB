import varastologiikka as vl

# Muokkaa tietoja
def edit_info(db: vl.Database):
    while True:
        print("Muokkaa:")
        options = ("Siirrä lava",)
        choice = vl.handle_input(options)
        
        if choice == "0" or choice == "": # Takaisin
            return
        elif choice == "1": # Siirrä lava
            varasto = input("Varasto: ")
            if varasto == "": # Peruuta
                continue
            varasto = db.sanitize(varasto)
            pallet_id = input("Lavanumero: ")
            if pallet_id == "": # Peruuta
                continue
            pallet_id = db.sanitize(pallet_id)
            pallet_id = int(pallet_id)
            to_location = ""
            while not db.is_location_format(to_location)[0]:
                to_location = input("Kohdesijainti: ")
                if to_location == "":
                    break
            if to_location == "": # Peruuta
                continue
            to_location = db.sanitize(to_location)
            location_id = db.get_table(
                "LAVAPAIKAT", "Sijainti_ID", ("Sijainti", "Varasto"), (to_location, varasto),
                comparators=("=", "="), logicals=("AND",)
                )
            if not location_id:
                print("Sijaintia {} ei löytynyt.".format(to_location))
                continue
            location_id = int(location_id[0][0])
            try:
                occupant = db.location_is_free(location_id)
            except ValueError as e:
                print(e)
                continue
            if occupant is None:
                db.move_pallet(pallet_id, location_id)
                print("Lava siirretty sijaintiin {}.".format(to_location))
            else:
                print("Lavaa ei voitu siirtää. Sijainti {} on jo varattu lavalle {}.".format(to_location, occupant))

# Haku
def search_db(db: vl.Database):
    while True:
        print("Hae:")
        options = ("Tuotteet", "Erät", "Lavapaikat", "Lavat", "Varastot", "Siirtotapahtumat")
        choice = vl.handle_input(options)
        
        if choice == "0" or choice == "": # Takaisin
            return
        
        print(options[int(choice)-1])
        search_term = input("Hakusana: ")
        if search_term == "": # Peruuta
            continue
        if choice == "1": # Tuotteet
            db.search_and_print("TUOTETIEDOT", search_term)
        elif choice == "2": # Erät
            db.search_and_print("TUOTEERÄT", search_term)
        elif choice == "3": # Lavapaikat
            db.search_and_print("LAVAPAIKAT", search_term)
        elif choice == "4": # Lavat
            db.search_and_print("LAVATIEDOT", search_term)
        elif choice == "5": # Varastot
            db.search_and_print("VARASTOTIEDOT", search_term)
        elif choice == "6": # Siirtotapahtumat
            db.search_and_print("LAVASIIRROT", search_term)
        input("Paina Enter jatkaaksesi...")

# Selaa tietoja
def scroll_info(db: vl.Database):
    while True: 
        print("Selaa:")
        options = ("Tuotteet", "Erät", "Lavapaikat", "Lavat", "Varastot")
        choice = vl.handle_input(options)
        
        if choice == "0" or choice == "": # Takaisin
            return
        elif choice == "1": # Tuotteet
            db.print_table("TUOTETIEDOT")
        elif choice == "2": # Erät
            db.print_table("TUOTEERÄT")
        elif choice == "3": # Lavapaikat
            db.print_table("LAVAPAIKAT")
        elif choice == "4": # Lavat
            db.print_table("LAVATIEDOT")
        elif choice == "5": # Varastot
            db.print_table("VARASTOTIEDOT")
        input("Paina Enter jatkaaksesi...")

def main():
    print("\nTervetuloa varastonhallintajärjestelmään!\n")
    db = vl.Database("varasto.db")
    while True:
        options = ("Haku", "Selaa tietoja", "Muokkaa tietoja")
        choice = vl.handle_input(options, back_label="Poistu")
        
        if choice == "0": # Poistu
            break
        elif choice == "1": # Haku
            search_db(db)
        elif choice == "2": # Selaa tietoja
            scroll_info(db)
        elif choice == "3": # Muokkaa tietoja
            edit_info(db)
        
    print("Järjestelmä suljetaan.")

if __name__ == "__main__":
    main()
