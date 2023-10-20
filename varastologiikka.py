from datetime import date
import random
import sqlite3 as sql



def randdate(yrange=[2024, 2027], mrange=[1, 12], drange=[1, 31]):
    y = random.randint(yrange[0], yrange[1])
    m = random.randint(mrange[0], mrange[1])
    if drange[1] > 28:
        if m == 2:
            drange[1] = 28
        elif drange[1] > 30 & m in [4, 6, 9, 11]:
            drange[1] = 30
    d = random.randint(drange[0], drange[1])
    return date(y, m, d).isoformat()

def main():
    print("Access these functions by importing this library.")

if __name__ == "__main__":
    main()
