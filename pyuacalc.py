import os
import csv
import xml.sax
import re
import itertools

import numpy as np
import pyparsing as pp
from pprint import pprint

class Algebra:
    """Algebra class bringing in functionality from pyuacalc and terms"""
    def __init__(self,filename=None):
        self.name = ""
        self.description = ""
        self.cardinality = 0
        self.operations = {}
        self.arities = {}
        self.expr = None
        self.expr_str = None
        self.translate = {}
        self._substitution = {}
        if filename:
            self.load(filename)
        
    def load(self, filename):
        # create an XMLReader
        parser = xml.sax.make_parser()
        # turn off namepsaces
        parser.setFeature(xml.sax.handler.feature_namespaces, 0)

        # override the default ContextHandler
        Handler = AlgebraHandler()
        parser.setContentHandler( Handler )
        parser.parse(filename)
        self.name = Handler.name
        self.description = Handler.description
        self.cardinality = Handler.cardinality
        self.operations = Handler.operations
        for op in self.operations:
            operation = self.operations[op]
            if isinstance(operation,(int,float)):
                self.arities[op] = 0
            else:
                self.arities[op] = len(operation.shape)
        
        self.expr_str = make_expression(self.arities)
        self.expr_str.setParseAction( self._string_action )
        
        self.expr_sub = make_expression(self.arities)
        self.expr_sub.setParseAction( self._substitute_action )
    
    def _string_action(self,s,l,t):
        op = t[0]
        args = t[1:]
        try:
            arity = self.arities[op]
        except KeyError:
            return op
            
        try:
            if arity == 0:
                return self.translate[op]
            elif arity == 1:
                return self.translate[op]+args[0]
            elif arity == 2:
                return "("+args[0] + self.translate[op]+args[1]+")"
            else:
                return self.translate[op] + '(' + ','.join(args) + ')'
                
        except KeyError:
            return op + '(' + ','.join(args) + ')'
        
    def _substitute_action(self,s,l,t):
        op = t[0]
        args = t[1:]
        
        if op in self.arities:
            if self.arities[op] == 0:
                return self.operations[op]
            else:
                return self.operations[op][tuple(args)]
        
        else:
            try:
                return self._substitution[op]
            except KeyError:
                raise Exception("You did not supply a substitution for %s"%(op))
            
    def make_readable(self,my_string):
        parse_result = self.expr_str.parseString( my_string )
        return parse_result[0]
        
    def substitute(self,substitution,my_string):
        self._substitution = substitution
        parse_result = self.expr_sub.parseString( my_string )
        return parse_result[0]
    
    def get_graph(self,G = None):
        """Write elements to the given graph. Or write a new graph. Requires pygraphviz."""
        if not G:
            try:
                import pygraphviz as pgv
            except ImportError:
                raise Exception("Sorry, you need pygraphviz for this function.")
            G = pgv.AGraph('digraph G {rankdir="BT";}')
            G.node_attr['shape']='point'
            
        # Get lattice order
        op = ''
        if 'join' in self.operations:
            op = 'join'
            order_ind = (self.operations['join'].transpose()-np.arange(self.cardinality))==0
            order = order_ind.sum(1).argsort()[::-1]
        elif 'meet' in self.operations:
            op = 'meet'
            order_ind = (self.operations['join'].transpose()-np.arange(self.cardinality))==0
            order = order_ind.sum(1).argsort()
        else:
            raise Exception("Algebra needs to have join or meet operations.")
            
        # Add nodes
        for i in order:
            G.add_node(i)
            
        # Get edges
        for i,j in itertools.combinations(range(self.cardinality),2):
            element = self.operations[op][i][j]
            if element==i:
                if op =='join':
                    G.add_edge(j,element)
                else:
                    G.add_edge(element,j)
            elif element==j:
                if op =='join':
                    G.add_edge(i,element)
                else:
                    G.add_edge(element,i)
            
        return G
        
        
filler = np.frompyfunc(lambda x: list(), 1, 1)

class AlgebraHandler( xml.sax.ContentHandler ):
    """A sax xml handler to get properties from a uacalc (.ua) file.
    
    Usage::

        >>> import xml
        >>> parser = xml.sax.make_parser()
        >>> parser.setFeature(xml.sax.handler.feature_namespaces, 0)
        >>> parser.setFeature(xml.sax.handler.feature_namespaces, 0)
        >>> import AlgebraHandler
        >>> Handler = AlgebraHandler()
        >>> parser.setContentHandler( Handler )
        >>> parser.parse('test.ua')
        
    :param name: Name of the algebra.
    :param description: Description of the algebra.
    :param cardinality: Number of elements in the algebra.
    :param operations: Dictionary where the key is name of the operation 
        and the value is the Cayley table of the operation, saved as 
        a numpy array of with dimension cardinality^arity.
        The values correspond to the indices of the array.
        If arity is 0 it is an int.
    """
    def __init__(self):
        self.name = ""
        self.description  = ""
        self.cardinality = ""
        self.operations = {}
        self._current_data = ""
        self._current_operation = ""
        self._current_row = 0
        self._current_arity = 0
        self._partial_row = []
        self._operation_builder = ''
        
    # # nice print
    # def __str__(self):
        # mystr = 'Aglebra '+self.name+'\n'
        # mystr += self.description+'\n'
        # mystr += 'cardinality: '+str(self.cardinality)+'\n'
        # mystr += 'opperations: \n    '
        # for key in self.operations:
            # mystr += key+' '
        # mystr += '\n'
        # return mystr

    # Call when an element starts
    def startElement(self, tag, attributes):
        self._current_data = tag
        if tag == "row":
            if 'r' in attributes:
                self._current_row = tuple(eval(attributes["r"]))
            else:
                self._current_row = 0
            

    # Call when an elements ends
    def endElement(self, tag):
        if tag == "op":
            if self._current_arity == 0:
                self.operations[self._current_operation] = int(self._operation_builder)
            elif self._current_arity == 1:
                self.operations[self._current_operation][:] = map( int, ''.join(self._operation_builder).split(',') )
            else:
                for t in itertools.product(range(self.cardinality), repeat=(self._current_arity-1)):
                    self.operations[self._current_operation][t] = map( int, ''.join(self._operation_builder[t]).split(',') )
                
            self._current_operation = ""
            self._current_row = 0
            self._current_arity = 0
        self._current_data = ""
        

    # Call when a character is read
    def characters(self, content):
        if self._current_data == "algName":
            self.name = content
            
        elif self._current_data == "desc":
            self.description = content
            
        elif self._current_data == "cardinality":
            self.cardinality = int(content)
            
        elif self._current_data == "opName":
            self._current_operation = content
            
        elif self._current_data == "arity":
            arity = int(content)
            self._current_arity = arity
            if arity > 0:
                one_less_dimension = np.empty([self.cardinality]*(arity-1),dtype=object)
                self._operation_builder = filler(one_less_dimension)
                self.operations[self._current_operation] = np.zeros([self.cardinality]*arity,dtype='uint32')
                
        elif self._current_data == "row":
            if self._current_arity < 1:
                self._operation_builder = content
            elif self._current_arity == 1:
                self._operation_builder.append( content )
            else:
                self._operation_builder[self._current_row].append( content )
                     
def csv_reader(f):
    """Return a csv reader for a file made with UACalc's export results method."""
    #skip first two garbage rows
    next(f,None)
    next(f,None)
    #reader = csv.DictReader(f)
    next(f,None)
    return csv.reader(f)
    
def make_expression(arities):
    """Takes dictionary with keys as operation names an arities as values."""
    
    expr = pp.Forward()
    op_list = []
    for op in arities:
        arity = arities[op]
        if arity == 0:
            op_expr = op+pp.Suppress('()')
        else:
            # op(expr,expr,... arity times)
            op_expr = op+pp.Suppress('(') + expr
            for i in range(arity-1):
                op_expr = op_expr + pp.Suppress(',') + expr
            op_expr = op_expr + pp.Suppress(')')
        op_list.append( op_expr.setName( op ) )
    combine = op_list[0]
    for op in op_list[1:]:
        combine = combine | op
    combine = combine | pp.Word(pp.alphas,pp.nums)
    expr << combine
    
    return expr
    