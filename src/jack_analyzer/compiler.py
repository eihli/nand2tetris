import itertools as it
import xml.etree.ElementTree as ET

OP_SYMBOLS = [
    '-', '*',
]


class Node:
    def __init__(self, element):
        self.element = element

    @property
    def type(self):
        return self.element.tag

    @property
    def text(self):
        return self.element.text.strip()


class TokenTree:
    def __init__(self, etree):
        self.etree = etree

    @classmethod
    def from_file(cls, filename):
        with open(filename) as f:
            return cls(ET.fromstring(f.read()))


class IntegerNode(Node):
    pass


class StringNode(Node):
    pass


class OpNode(Node):
    pass


class Mult(OpNode):
    @property
    def text(self):
        return 'mult'


class Expr(Node):
    def __init__(self, element):
        super(Expr, self).__init__(element)
        self.children = [el_to_node(e) for e in list(element)]

    @property
    def first_term(self):
        return self.children[0]

    @property
    def op_terms(self):
        if len(self.children) > 1:
            ops = it.islice(self.children, 1, None, 2)
            terms = it.islice(self.children, 2, None, 2)
            return zip(ops, terms)
        else:
            return None


def el_to_node(el):
    if el.tag == 'integerConstant':
        return IntegerNode(el)
    elif el.tag == 'stringConstant':
        return StringNode(el)
    elif el.tag == 'symbol':
        if el.text.strip() == '*':
            return Mult(el)
        else:
            raise Exception('Unhandled OP {}'.format(el.text))
    elif el.tag == 'expression':
        return Expr(el)
    else:
        raise Exception('Unhandled el tag {}'.format(el.tag))


class CodeGenerator:
    """
    Read class and classVarDec to build a class symbol table.
    Read subroutineDec and paramList and build method symbol table.
    Generate code from subroutineBody and symbol tables
    """
    def __init__(self, stream):
        self.stream = stream

    def emit(self, txt):
        self.stream.write(txt)

    def generate(self, node):
        if isinstance(node, IntegerNode):
            self.emit('push constant {}\n'.format(node.text))
        elif isinstance(node, StringNode):
            out = [
                'push constant {}'.format(len(node.text)),
                'String.new 1',
            ]
            for char in node.text:
                out.extend([
                    'push constant {}'.format(ord(char)),
                    'String.appendChar 2',
                ])
            self.emit('\n'.join(out))
        elif isinstance(node, OpNode):
            self.emit('{}\n'.format(node.text))
        elif isinstance(node, Expr):
            self.generate(node.first_term)
            if node.op_terms:
                ops, terms = zip(*node.op_terms)
                for term in terms:
                    self.generate(term)
                for op in ops:
                    self.generate(op)
        else:
            raise Exception('Unhandled node type {}'.format(
                node.__class__.__name__
            ))
