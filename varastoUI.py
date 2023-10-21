import varastologiikka as vl

def main():
    print("Tervetuloa varastonhallintajärjestelmään!\n")
    while True:
        options = {"1": "Selaa tietoja", "2": "Lisää tietoja", "0": "Poistu"}
        choice = vl.handle_input(options)
        
        if choice == "0":
            break
        
    print("Järjestelmä suljetaan.")

if __name__ == "__main__":
    main()
