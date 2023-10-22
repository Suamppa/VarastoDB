import varastologiikka as vl

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
            db.search("TUOTETIEDOT", search_term)
        elif choice == "2": # Erät
            db.search("TUOTEERÄT", search_term)
        elif choice == "3": # Lavapaikat
            db.search("LAVAPAIKAT", search_term)
        elif choice == "4": # Lavat
            db.search("LAVATIEDOT", search_term)
        elif choice == "5": # Varastot
            db.search("VARASTOTIEDOT", search_term)
        elif choice == "6": # Siirtotapahtumat
            db.search("LAVASIIRROT", search_term)
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
            pass
        
    print("Järjestelmä suljetaan.")

if __name__ == "__main__":
    main()
