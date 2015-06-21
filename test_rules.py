#!/usr/bin/env python3

import unittest

import rules as r

# Remove this
class TestTemplate(unittest.TestCase):
    def setUp(self):
        pass
    def test_all(self):
        pass

class TestContainment(unittest.TestCase):
    def test_call(self):
        rule = r.ContainmentRule("xo")
        self.assertTrue(rule("boxo"))
        self.assertTrue(rule("oxoooooooooooo"))
        self.assertFalse(rule("Xoo"))
        self.assertFalse(rule("x" * 100))

class TestConjunction(unittest.TestCase):
    def test_call(self):
        rule = r.ConjunctionRule(r.ContainmentRule("x"), r.ContainmentRule("he"))
        self.assertTrue(rule("xhe"))
        self.assertFalse(rule("hxe"))
        self.assertFalse(rule("hehehe"))

class TestDisjunction(unittest.TestCase):
    def test_call(self):
        rule = r.DisjunctionRule(r.ContainmentRule("x"), r.ContainmentRule("he"))
        self.assertTrue(rule("xhe"))
        self.assertTrue(rule("hxe"))
        self.assertTrue(rule("he"))
        self.assertFalse(rule("hzhzhz"))
        self.assertFalse(rule("az" * 100))

class TestXor(unittest.TestCase):
    def test_call(self):
        rule = r.XorRule(r.ContainmentRule("x"), r.ContainmentRule("he"))
        self.assertFalse(rule("xhe"))
        self.assertTrue(rule("hxe"))
        self.assertTrue(rule("he"))
        self.assertFalse(rule("hzhzhz"))
        self.assertFalse(rule("az" * 100))
        self.assertFalse(rule("xhe" * 100))

class TestLengthMin(unittest.TestCase):
    def test_call(self):
        rule = r.LengthMinimumRule(5)
        self.assertTrue(rule("12345"))
        self.assertTrue(rule("o" * 10))
        self.assertFalse(rule(""))
        self.assertFalse(rule("o" * 4))

class TestLengthMax(unittest.TestCase):
    def test_call(self):
        rule = r.LengthMaximumRule(5)
        self.assertTrue(rule("12345"))
        self.assertFalse(rule("o" * 10))
        self.assertTrue(rule(""))
        self.assertTrue(rule("o" * 4))

if __name__ == "__main__":
	unittest.main()

