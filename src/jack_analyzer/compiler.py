import itertools as it
import xml.etree.ElementTree as ET

OP_SYMBOLS = [
    '-', '*', '=',
]

KEYWORD_CONSTANTS = [
    'true', 'false', 'null', 'this',
]


class SymbolTable:
    cls = {}
    mth = {}

    def __getattr__(self, name):
        return self.mth.get(name, None) or self.cls.get(name, None)

    def __getitem__(self, name):
        return getattr(self, name)


def take_until(iterable, until_fn):
    for el, p in [(el, until_fn(el)) for el in iterable]:
        if p:
            break
        else:
            yield el


def index_of(iterable, p):
    return next(
        (i for i, el in enumerate(iterable) if p(el)),
        None
    )


class Node:
    def __init__(self, element):
        self.element = element

    def __iter__(self):
        return iter(list(
            el_to_node(e) for e in self.element
        ))

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


class Term(Node):
    pass


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


class LetStatement(Node):
    def split(self, node_class):
        # Ignore the let and the ;
        els = list(self.element)[1:-1]
        op_idx = index_of(
            els,
            lambda el: isinstance(el_to_node(el), EQ)
        )
        return els[:op_idx], els[op_idx + 1]


class KeywordConstant(Node):
    pass


class Identifier(Node):
    pass


class EQ(Node):
    pass


class OpenBracket(Node):
    pass


def el_to_node(el):
    if el.tag == 'integerConstant':
        return IntegerNode(el)
    elif el.tag == 'stringConstant':
        return StringNode(el)
    elif el.tag == 'symbol':
        if el.text.strip() == '*':
            return Mult(el)
        elif el.text.strip() == '=':
            return EQ(el)
        elif el.text.strip() == '[':
            return OpenBracket(el)
        else:
            raise Exception('Unhandled OP {}'.format(el.text))
    elif el.tag == 'expression':
        return Expr(el)
    elif el.tag == 'term':
        return Term(el)
    elif el.tag == 'letStatement':
        return LetStatement(el)
    elif el.tag == 'identifier':
        return Identifier(el)
    elif el.tag == 'keyword':
        return KeywordConstant(el)
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
        self.sym_tab = SymbolTable()

    def emit(self, txt):
        normalized = txt.strip().split('\n')
        if len(normalized) > 1:
            self.emit_many(normalized)
        else:
            self.stream.write(txt.replace('\n', '') + '\n')

    def emit_many(self, txts):
        for txt in txts:
            self.emit(txt)

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
        elif isinstance(node, Term):
            for child in node:
                self.generate(child)
        elif isinstance(node, LetStatement):
            rhs, lhs = node.split(OpNode)
            if len(rhs) > 1:
                var = el_to_node(rhs[0])
                expr = el_to_node(rhs[2])
                self.emit_many([
                    'push {} {}'.format(
                        self.sym_tab[var.text]['kind'],
                        self.sym_tab[var.text]['number'],
                    )
                ])
                self.generate(expr)
                self.emit('add')
                self.emit('pop pointer 1')
                self.generate(el_to_node(lhs))
                self.emit('pop that 0\n')
            else:
                self.generate(el_to_node(lhs))
                node = el_to_node(rhs[0])
                self.emit('pop {} {}\n'.format(
                    self.sym_tab[node.text]['kind'],
                    self.sym_tab[node.text]['number'],
                ))
        elif isinstance(node, KeywordConstant):
            if node.text == 'null' or node.text == 'false':
                self.emit('push constant 0\n')
            elif node.text == 'true':
                self.emit('push constant 1\n')
                self.emit('neg\n')
            else:
                self.emit('push argument 0\n')
        else:
            raise Exception('Unhandled node type {}'.format(
                node.__class__.__name__
            ))
