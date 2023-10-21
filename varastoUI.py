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
        
        search_term = input("Hakusana: ")
        if choice == "1": # Tuotteet
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

# Selaa tietoja
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
            db.print_table("TUOTETIEDOT")
        elif choice == "2": # Erät
            db.print_table("TUOTEERÄT")
        elif choice == "3": # Lavapaikat
            db.print_table("LAVAPAIKAT")
        elif choice == "4": # Lavat
            db.print_table("LAVATIEDOT")
        elif choice == "5": # Varastot
            db.print_table("VARASTOTIEDOT")

def main():
    print("\nTervetuloa varastonhallintajärjestelmään!\n")
    db = vl.Database("varasto.db")
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
