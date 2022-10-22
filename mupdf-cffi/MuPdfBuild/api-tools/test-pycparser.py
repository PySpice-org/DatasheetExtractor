####################################################################################################

import sys

####################################################################################################

from pycparser import parse_file, c_ast, c_generator

####################################################################################################

class NodeVisitor(c_ast.NodeVisitor):

    ##############################################

    def visit_FuncDecl(self, node):
        print('\nFunction Declaration at %s' % (node.coord))
        node.show()

####################################################################################################

if __name__ == "__main__":

    filename  = sys.argv[1]
    ast = parse_file(filename, use_cpp=False)

    # visitor = NodeVisitor()
    # visitor.visit(ast)

    generator = c_generator.CGenerator()
    print(generator.visit(ast))
