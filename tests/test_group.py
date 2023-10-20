import unittest
from test_create_db import TestCreateDB
from test_varastologiikka import TestVarastoLogiikka

class TestGroup(unittest.TestSuite):
    
    def __init__(self):
        super().__init__()
        self.addTest(unittest.makeSuite(TestCreateDB))
        self.addTest(unittest.makeSuite(TestVarastoLogiikka))
