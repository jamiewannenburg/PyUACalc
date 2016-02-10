"""run python -m unittest discover -f tests"""
import unittest
from pyuacalc import AlgebraHandler,Algebra,make_expression
import xml.sax

class TestAlgebraHandler(unittest.TestCase):
    
    @classmethod
    def setUpClass(cls):
        # create an XMLReader
        parser = xml.sax.make_parser()
        # turn off namepsaces
        parser.setFeature(xml.sax.handler.feature_namespaces, 0)

        # override the default ContextHandler
        cls.Handler = AlgebraHandler()
        parser.setContentHandler( cls.Handler )
        parser.parse('tests/examples/test.ua')

    def test_cardinality(self):
        self.assertEqual( self.Handler.cardinality, 300)
 
    def test_operations(self):
        self.assertItemsEqual(self.Handler.operations.keys(), ['e','neg','dot','R'])
        
    def test_arity(self):
        self.assertEqual( len(self.Handler.operations['neg'].shape), 1)
        self.assertEqual( len(self.Handler.operations['dot'].shape), 2)
        self.assertEqual( len(self.Handler.operations['R'].shape), 3)
 
class TestAlgebra(unittest.TestCase):
    
    def test_name(self):
        a = Algebra('tests/examples/small_test.ua')
        self.assertEqual( a.name, 'test3')
        
    def test_substitute(self):
        b = Algebra('tests/examples/b2.ua')
        result = b.substitute({'x':0},'join(x,e())')
        self.assertEqual( result, 1)
        
    def test_make_readable(self):
        b = Algebra('tests/examples/b2.ua')
        b.translate = {'e':r'e ','dot':r'\cdot ','join':r'\vee ','neg':r'\neg '}
        result = b.make_readable('join(neg(dot(x,y)),e())')
        self.assertEqual( result, r'(\neg (x\cdot y)\vee e )')

class TestMakeExpression(unittest.TestCase):
    
    def test_default_constants(self):
        e = make_expression({'e':0,'neg':1,'dot':2,'R':3})
        e.setParseAction(lambda s,l,t: t[0]+'('+','.join(t[1:])+')')
        result = e.parseString('dot(neg(e()),e())')[0]
        self.assertEqual(result, 'dot(neg(e()),e())')
        

