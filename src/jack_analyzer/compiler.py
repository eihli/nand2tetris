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

    def __len__(self):
        return len(self.element)

    @property
    def type(self):
        return self.element.tag

    @property
    def text(self):
        return self.element.text.strip()

    @property
    def category(self):
        return self.element.attrib['category']

    @property
    def number(self):
        return self.element.attrib['number']


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
    @property
    def is_subroutine_call(self):
        if isinstance(list(self)[1], Node):
            import pdb; pdb.set_trace()


class Expr(Node):
    def __init__(self, element):
        super(Expr, self).__init__(element)
        self.children = list(self)

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
    def split(self):
        # Ignore the let and the ;
        els = [el_to_node(e) for e in list(self.element)[1:-1]]
        op_idx = index_of(
            els,
            lambda el: isinstance(el, EQ)
        )
        # left hand side could be 'x' or 'x[expr]'
        # right hand side is always just expr
        return els[:op_idx], els[op_idx + 1]


class DoStatement(Node):
    pass


class ReturnStatement(Node):
    pass


class WhileStatement(Node):
    pass


class KeywordConstant(Node):
    pass


class Identifier(Node):
    pass


class EQ(Node):
    pass


class OpenBracket(Node):
    pass


class OpenParen(Node):
    pass


class CloseParen(Node):
    pass


class ExprList(Node):
    pass


class Period(Node):
    pass


class ClassVarDec(Node):
    pass


class Comma(Node):
    pass


class SemiColon(Node):
    pass


class SubroutineDec(Node):
    pass


class ParameterList(Node):
    pass


class SubroutineBody(Node):
    pass


class OpenBrace(Node):
    pass


class CloseBrace(Node):
    pass


class Statements(Node):
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
        elif el.text.strip() == '.':
            return Period(el)
        elif el.text.strip() == '(':
            return OpenParen(el)
        elif el.text.strip() == ')':
            return CloseParen(el)
        elif el.text.strip() == ',':
            return Comma(el)
        elif el.text.strip() == ';':
            return SemiColon(el)
        elif el.text.strip() == '{':
            return OpenBrace(el)
        elif el.text.strip() == '}':
            return CloseBrace(el)
        else:
            raise Exception('Unhandled OP {}'.format(el.text))
    elif el.tag == 'expression':
        return Expr(el)
    elif el.tag == 'term':
        return Term(el)
    elif el.tag == 'letStatement':
        return LetStatement(el)
    elif el.tag == 'doStatement':
        return DoStatement(el)
    elif el.tag == 'returnStatement':
        return ReturnStatement(el)
    elif el.tag == 'whileStatement':
        return WhileStatement(el)
    elif el.tag == 'identifier':
        return Identifier(el)
    elif el.tag == 'keyword':
        return KeywordConstant(el)
    elif el.tag == 'expressionList':
        return ExprList(el)
    elif el.tag == 'classVarDec':
        return ClassVarDec(el)
    elif el.tag == 'subroutineDec':
        return SubroutineDec(el)
    elif el.tag == 'parameterList':
        return ParameterList(el)
    elif el.tag == 'subroutineBody':
        return SubroutineBody(el)
    elif el.tag == 'statements':
        return Statements(el)
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
            children = list(node)
            if len(children) > 1:
                # subroutine call or array access
                symbol = children[1]
                if isinstance(symbol, Period):
                    args = children[4]
                    self.generate(args)
                    class_name = children[0].text
                    subroutine_name = children[2].text
                    num_args = len(children[4])
                    self.emit_many([
                        'call {}.{} {}'.format(
                            class_name,
                            subroutine_name,
                            num_args
                        )
                    ])
                else:
                    raise Exception("ARRAY")
            else:
                for child in node:
                    self.generate(child)
        elif isinstance(node, LetStatement):
            lhs, rhs = node.split()
            if len(lhs) == 1:
                lhs_emit = 'pop {} {}'.format(
                    self.sym_tab[lhs[0].text]['kind'],
                    self.sym_tab[lhs[0].text]['number'],
                )
            else:
                lhs_emit = 'PUT ARR LET HERE'
            self.generate(rhs)
            self.emit(lhs_emit)
        elif isinstance(node, KeywordConstant):
            if node.text == 'null' or node.text == 'false':
                self.emit('push constant 0\n')
            elif node.text == 'true':
                self.emit('push constant 1\n')
                self.emit('neg\n')
            else:
                self.emit('push argument 0\n')
        elif isinstance(node, ExprList):
            for expr in node:
                self.generate(expr)
        elif isinstance(node, ClassVarDec):
            for e in [e for e in node if e.type == 'identifier']:
                self.sym_tab.cls[e.text] = {
                    'kind': e.category,
                    'number': e.number,
                }
        elif isinstance(node, ParameterList):
            for e in [e for e in node if e.type == 'identifier']:
                self.sym_tab.mth[e.text] = {
                    'kind': e.category,
                    'number': e.number,
                }
        elif isinstance(node, SubroutineDec):
            children = list(node)
            fn_type = children[0].text.strip()
            if fn_type == 'constructor':
                return_type = children[1].text.strip()
                subroutine_name = children[2].text.strip()
                param_list = children[4]
                self.generate(param_list)  # Populate sym table
                num_fields = len(list(
                    k for k, v in self.sym_tab.cls.items()
                    if v['kind'] == 'field'
                ))
                args = [e for e in param_list if e.type == 'identifier']
                self.emit_many([
                    'function {}.{} {}'.format(
                        return_type,
                        subroutine_name,
                        len(args),
                    )
                ])
                # Allocate memory for field variables
                self.emit('push {}'.format(num_fields))
                self.emit('call Memory.alloc 1')
                self.emit('pop pointer 0')
                subroutine_body = children[6]
                self.generate(subroutine_body)
                self.emit('push pointer 0')
        elif isinstance(node, SubroutineBody):
            children = list(node)
            statements = children[1]
            for statement in statements:
                self.generate(statement)
        elif isinstance(node, Identifier):
            self.emit(
                'push {} {}'.format(
                    self.sym_tab[node.text]['kind'],
                    self.sym_tab[node.text]['number']
                )
            )
        else:
            raise Exception('Unhandled node type {}'.format(
                node.__class__.__name__
            ))
