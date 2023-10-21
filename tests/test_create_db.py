import os
import unittest

import varastologiikka as vl

class TestCreateDB(unittest.TestCase):
    
    def setUp(self):
        # Remove previous database if it exists
        if os.path.exists("test.db"):
            os.remove("test.db")
        
        # Create a new database
        os.system("python create_db.py -t")
    
    def tearDown(self):
        # Remove the database after all tests have run
        if os.path.exists("test.db"):
            os.remove("test.db")
    
    def test_database_exists(self):
        self.assertTrue(os.path.exists("test.db"))
    
    def test_tables_exist(self):
        with vl._Connection("test.db") as conn:
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
        with vl._Connection("test.db") as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM VARASTO;")
            count = cursor.fetchone()[0]
            self.assertGreater(count, 0)
    
    def test_shelves_and_floor_units(self):
        with vl._Connection("test.db") as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM SIJAINTI;")
            count = cursor.fetchone()[0]
            self.assertGreater(count, 0)
    
    def test_pallet_entries(self):
        with vl._Connection("test.db") as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM LAVA;")
            count = cursor.fetchone()[0]
            self.assertGreater(count, 0)
    
    def test_movement_entries(self):
        with vl._Connection("test.db") as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM SIIRTOTAPAHTUMA;")
            count = cursor.fetchone()[0]
            self.assertGreater(count, 0)
    
    def test_product_entries(self):
        with vl._Connection("test.db") as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM TUOTE;")
            count = cursor.fetchone()[0]
            self.assertGreater(count, 0)
    
    def test_batch_entries(self):
        with vl._Connection("test.db") as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM ERÄ;")
            count = cursor.fetchone()[0]
            self.assertGreater(count, 0)
    
    def test_batches_on_pallets(self):
        with vl._Connection("test.db") as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM ERÄ_LAVALLA;")
            count = cursor.fetchone()[0]
            self.assertGreater(count, 0)

if __name__ == "__main__":
    unittest.main()
