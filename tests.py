""" Tests for configure"""

from unittest import TestCase as BaseTestCase
from configure import Configuration, Ref, Obj

class A(object):

    def __init__(self, a, b=3):
        self.a = a
        self.b = b

def a(a, b=4):
    return A(a, b=b)

class TestCase(BaseTestCase):

    def config(self, v, ctx=None):
        return Configuration.from_string(v.strip(), ctx=ctx)

    def test_interpolation(self):
        c = self.config("""
a: "%(a)s"
b: "%(b)s"
        """, {"a": "aa", "b": "bb"})
        self.assertEqual(c.a, "aa")
        self.assertEqual(c.b, "bb")

    def test_ref(self):
        c = self.config("""
a: 1
b:
    c: !ref:a
    d: !ref:..a
e: !ref:.b
        """)
        self.assertEqual(c.a, 1)
        self.assertEqual(c.e(c), c.b)
        self.assertEqual(c.b.c(c.b), c.a)
        self.assertEqual(c.b.d(c.b), c.a)

    def test_obj(self):
        c = self.config("""
a1:
    a: 1
a2:
    a: 2
    b: 4
a3:
    a: 3
a4:
    a: 4
    b: 5
        """)
        o = Obj(A, c.a1)(c)
        self.assertTrue(isinstance(o, A))
        self.assertEqual(o.a, 1)
        self.assertEqual(o.b, 3)

        o = Obj(A, c.a2)(c)
        self.assertTrue(isinstance(o, A))
        self.assertEqual(o.a, 2)
        self.assertEqual(o.b, 4)

        o = Obj(a, c.a3)(c)
        self.assertTrue(isinstance(o, A))
        self.assertEqual(o.a, 3)
        self.assertEqual(o.b, 4)

        o = Obj(a, c.a4)(c)
        self.assertTrue(isinstance(o, A))
        self.assertEqual(o.a, 4)
        self.assertEqual(o.b, 5)

    def test_obj_graph(self):
        c = self.config("""
a: !obj:tests.A
    a: 1
    b: !ref:.b
b: !obj:tests.a
    a: 3
        """)
        c.configure()
        self.assertTrue(isinstance(c.a, A))
        self.assertEqual(c.a.a, 1)
        self.assertTrue(isinstance(c.b, A))
        self.assertEqual(c.b.a, 3)
        self.assertTrue(isinstance(c.a.b, A))
        self.assertEqual(c.a.b.a, c.b.a)
        self.assertEqual(c.a.b.b, c.b.b)
        self.assertTrue(c.a.b is c.b)
