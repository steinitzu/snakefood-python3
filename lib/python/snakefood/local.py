from __future__ import print_function, absolute_import

"""Code for checking for local names and superfluous import statements.

This code provides searches for local symbols in the AST, assignments and such
things.
"""
# This file is part of the Snakefood open source package.
# See http://furius.ca/snakefood/ for licensing details.

from snakefood.six.moves import range
from ast import Store, Name, List, Tuple, Str, NodeVisitor
from _ast import Attribute, Load

__all__ = ('get_names_from_ast', 'filter_unused_imports',
           'NamesVisitor', 'AssignVisitor', 'AllVisitor')


def get_names_from_ast(ast_):
    "Find all the names being referenced/used."
    vis = NamesVisitor()
    vis.visit(ast_)
    dotted_names, simple_names = vis.finalize()
    return (dotted_names, simple_names)


def filter_unused_imports(ast_, found_imports):
    """
    Given the ast and the list of found imports in the file, find out which of
    the imports are not used and return two lists: a list of used imports, and a
    list of unused imports.
    """
    used_imports, unused_imports = [], []

    # Find all the names being referenced/used.
    dotted_names, simple_names = get_names_from_ast(ast_)

    # Find all the names being exported via __all__.
    vis = AllVisitor()
    vis.visit(ast_)
    exported = vis.finalize()

    # Check that all imports have been referenced at least once.
    usednames = set(x[0] for x in dotted_names)
    usednames.update(exported)
    used_imports = []
    for x in found_imports:
        _, _, lname, lineno, _,  _ = x
        if lname is not None and lname not in usednames:
            unused_imports.append(x)
        else:
            used_imports.append(x)

    return used_imports, unused_imports


class Visitor(NodeVisitor):
    "Base class for our visitors."
    def continue_(self, node):
        for child in node.getChildNodes():
            self.visit(child)


class NamesVisitor(NodeVisitor):
    """AST visitor that finds all the identifier references that are defined,
    including dotted references. This includes all free names and names with
    attribute references.
    """
    def __init__(self):
        self.dotted = []
        self.simple = []
        self.attributes = []

    def visit_Name(self, node):
        if isinstance(node.ctx, Load):
            self.attributes.append(node.id)
            self.attributes.reverse()
            attribs = self.attributes
            for i in range(1, len(attribs)+1):
                self.dotted.append(('.'.join(attribs[0:i]), node.lineno))
            self.simple.append((attribs[0], node.lineno))
        self.attributes = []
        NodeVisitor.generic_visit(self, node)
    
    def visit_Attribute(self, node):
        self.attributes.append(node.attr)
        NodeVisitor.generic_visit(self, node)
        
    def finalize(self):
        return self.dotted, self.simple

class AssignVisitor(Visitor):
    """AST visitor that builds a list of all potential names that are being
    assigned to. This is used later to heuristically figure out if a name being
    refered to is never assigned to nor in the imports."""

    def __init__(self):
        self.assnames = []
        self.in_class = False

    def visit_Name(self, node):
        if node.ctx == Store:
            self.assnames.append((node.id, node.lineno))

    def visit_ClassDef(self, node):
        self.assnames.append((node.name, node.lineno))
        prev, self.in_class = self.in_class, True
        self.continue_(node)
        self.in_class = prev

    def visit_FunctionDef(self, node):
        # Avoid method definitions.
        if not self.in_class:
            self.assnames.append((node.name, node.lineno))
        self.continue_(node)

    def finalize(self):
        return self.assnames


class AllVisitor(NodeVisitor):
    """AST visitor that find an __all__ directive and accumulates the list of
    constants in it."""

    def __init__(self):
        self.all = []

    def visit_Assign(self, node):
        # TODO copy duplication with snakefood.find
        lhs = node.targets
        if (len(lhs) == 1 and
            isinstance(lhs[0], Name) and
            lhs[0].id == '__all__' and 
            isinstance(lhs[0].ctx, Store)
            ):

            rhs = node.value
            if isinstance(rhs, (List, Tuple)):
                for namenode in rhs.elts:
                    # Note: maybe we should handle the case of non-consts.
                    if isinstance(namenode, Str):
                        self.all.append(namenode.s)

    def finalize(self):
        return self.all
