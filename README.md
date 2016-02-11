PyUACalc
=====

This is a python package what wraps around [UACalc](http://www.uacalc.org/) `.ua` (xml) files. Operations are converted to numpy arrays. You can download the compressed packadge or a windows installer at http://www.jamiewannenburg.com/binaries.


# Importing
Download the UACalc java program and create an algebra. Save the algebra as a .ua file. In the examples here `b1.ua` refers to the two element boolean algebra, with operations 'join', 'dot', 'neg' and distinguished element 'e'.

    from PyUACalc.pyuacalc import Algebra
    b2 = Algebra('b2.ua')
    print b2.cardinality
    # 2
    print b2.operations['join']
    # array([0,1],
    #       [1,1])


# Terms
The Algebra class can work with terms

    b2.substitute({'x':0},'join(x,e())')
    # 1
    
We can pretify terms (unary terms bind the strongest and binary terms go in the middle)

    b2.translate = {'e':' e ','dot':' \cdot ','join':' \vee ','neg':' \neg '}
    b2.make_readable('dot(x,y)')
    # '(x \cdot y)'
    b2.make_readable('join(neg(dot(x,y)),e())')
    # ( \neg (x \cdot y) \vee  e )
    
You can make your own term calculator by calling `UACalc.terms.make_expression(b1.arities)`, which returns a pyparsing expression.

# Drawing
You can generate a graphviz graph if you have the module installed and the algebra you are working woth is a lattice, that is has a join or meet operation.

    import os
    import pygraphviz as pgv
    G = b2.get_graph()
    for i in range(b2.cardinality):
        n = G.get_node(i)
        # add labels an so on
    
    G.write('b1.dot')
    G.draw('b1.svg',format="svg",prog='fdp')
    
    # this does a transitive closure of the graph just incase
    os.system('tred b1.dot > b1-reduced.dot')
    G1 = pgv.AGraph('b1-reduced.dot')
    G1.draw('b1-reduced.svg',format="svg",prog='fdp')
