import sqlite3 as sql

def main():
    connection = sql.connect("varasto.db")
    cur = connection.cursor()

if __name__ == "__main__":
    main()
