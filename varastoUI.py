import varastologiikka as vl

def main():
    print("Tervetuloa varastonhallintajärjestelmään!\nYhdistetään tietokantaan...")
    with vl.Connection("varasto.db") as connection:
        print("Yhdistetty tietokantaan varasto.db.\n")
        
        options = {"1": "Selaa tietoja", "2": "Lisää tietoja", "0": "Poistu"}
        choice = vl.handle_input(options)
        
        while choice != "0":
            # if choice == "1":
            #     options = {"Selaa varastotilannetta": "1", "Selaa siirtotapahtumia": "2", "Takaisin": "0"}
            #     choice = vl.handle_input(options)
            #     while choice != "0":
            #         if choice == "1":
            #             vl.print_warehouse_status(cur)
            #         elif choice == "2":
            #             vl.print_movement_history(cur)
            #         choice = vl.handle_input(options)
            # elif choice == "2":
            #     options = {"Lisää tuote": "1", "Lisää erä": "2", "Lisää lava": "3", "Takaisin": "0"}
            #     choice = vl.handle_input(options)
            #     while choice != "0":
            #         if choice == "1":
            #             vl.add_product(cur)
            #         elif choice == "2":
            #             vl.add_batch(cur)
            #         elif choice == "3":
            #             vl.add_pallet(cur)
            #         choice = vl.handle_input(options)
            # choice = vl.handle_input(options)
            break
        
        connection.commit()
        print("Suljetaan yhteys tietokantaan...")
    print("Yhteys suljettu.")

if __name__ == "__main__":
    main()
