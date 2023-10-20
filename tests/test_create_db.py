import os
import unittest

import create_db
import varastologiikka as vl

class TestCreateDB(unittest.TestCase):
    def setUp(self):
        # Remove previous database if it exists
        if os.path.exists("varasto.db"):
            os.remove("varasto.db")
        
        # Create a new database
        create_db.main()
    
    def test_database_exists(self):
        self.assertTrue(os.path.exists("varasto.db"))
    
    def test_tables_exist(self):
        with vl.Connection("varasto.db") as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
            tables = cursor.fetchall()
            self.assertIn(("VARASTO",), tables)
            self.assertIn(("SIJAINTI",), tables)
            self.assertIn(("LAVA",), tables)
            self.assertIn(("SIIRTOTAPAHTUMA",), tables)
            self.assertIn(("TUOTE",), tables)
            self.assertIn(("ERÄ",), tables)
            self.assertIn(("ERÄ_LAVALLA",), tables)
    
    def test_warehouse_entries(self):
        with vl.Connection("varasto.db") as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM VARASTO;")
            count = cursor.fetchone()[0]
            self.assertGreater(count, 0)
    
    def test_shelves_and_floor_units(self):
        with vl.Connection("varasto.db") as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM SIJAINTI;")
            count = cursor.fetchone()[0]
            self.assertGreater(count, 0)
    
    def tearDown(self):
        # Remove the database after all tests have run
        os.remove("varasto.db")


if __name__ == "__main__":
    unittest.main()
