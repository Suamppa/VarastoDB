import os
import unittest
import varastologiikka as vl

class TestVarastoLogiikka(unittest.TestCase):

    def setUp(self):
        self.db_path = "test.db"
        if os.path.exists(self.db_path):
            os.remove(self.db_path)
        
        with vl.Connection(self.db_path) as conn:
            cur = conn.cursor()
            cur.execute("""
                        CREATE TABLE LAVA
                            (Sijainti TEXT,
                             Lavanumero TEXT NOT NULL,
                            PRIMARY KEY (Lavanumero) );
                        """)
            cur.execute("""
                        CREATE TABLE SIIRTOTAPAHTUMA
                            (Siirtoaika VARCHAR(23) CHECK (Siirtoaika LIKE '____-__-__ __:__:__'),
                             Lavanumero TEXT NOT NULL,
                             Sijainti TEXT,
                            PRIMARY KEY (Lavanumero),
                            FOREIGN KEY (Lavanumero) REFERENCES LAVA(Lavanumero)
                                        ON DELETE CASCADE ON UPDATE CASCADE );
                        """)
            cur.execute("INSERT INTO LAVA(Lavanumero) VALUES ('LAVA1');")
            conn.commit()

    def tearDown(self):
        if os.path.exists(self.db_path):
            os.remove(self.db_path)

    def test_lavasiirto(self):
        with vl.Connection(self.db_path) as conn:
            cur = conn.cursor()
            vl.lavasiirto(cur, "LAVA1", "SIJAINTI1")
            cur.execute("SELECT * FROM LAVA")
            result = cur.fetchone()
            self.assertEqual(result[0], "SIJAINTI1")
            self.assertEqual(result[1], "LAVA1")

    def test_randdate(self):
        date = vl.randdate()
        self.assertIsInstance(date, str)
        self.assertRegex(date, r"\d{4}-\d{2}-\d{2}")

if __name__ == "__main__":
    unittest.main()
