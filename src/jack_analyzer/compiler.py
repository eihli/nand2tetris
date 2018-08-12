from functools import partial as ptl
import io
import re


INTEGER_CONSTANT = 'integerConstant'
STRING_CONSTANT = 'stringConstant'
KEYWORD_CONSTANT = 'keywordConstant'
IDENTIFIER = 'identifier'
SYMBOL = 'symbol'
SUB = '-'
ADD = '+'
MULT = '*'
DIV = '/'
NOT = '~'

UNARY_OP_MAP = {
    SUB: 'neg',
    NOT: 'not',
}

OP_VM_MAP = {
    SUB: 'sub',
    ADD: 'add',
    MULT: 'mult'
}

out = io.StringIO()


class SymbolTable:
    cls = {}
    mth = {}

    def __getattr__(self, name):
        return self.mth.get(name, None) or self.cls.get(name, None)

    def __getitem__(self, name):
        return getattr(self, name)


def emit(ln):
    out.write('{}\n'.format(ln))


def get_terms(src):
    terms = []
    lines = src
    # [terms is a string that starts with <term> ->
    #  terms := list of outermost <term></term> from src]
    term = []
    depth = 0
    for line in lines:
        # [<term> in line -> depth +:= 1
        #  else -> I]
        if re.search(r'<term>', line):
            depth += 1

        # [depth > 0 -> term += line
        #  else -> I]
        if depth > 0:
            term.append(line)

        # [</term> in line -> depth -:= 1
        #  else -> I]
        if re.search('</term>', line):
            depth -= 1

        # [depth == 0 -> terms += term
        #  else -> I]
        if term and depth == 0:
            terms.append(term)
            term = []
    return terms


def terminal_content(tag, src):
    # [src is of type tag -> return src contents
    #  else -> return None]
    # [re_fmt, match :=
    #  regex with capture group for src contents,
    #  regex match object]
    re_fmt = r'<{}> (.*?) </{}>'
    match = re.match(re_fmt.format(tag, tag), src)
    # [if match -> return captured group]
    if match:
        return match.group(1)


def tc(tag):
    return ptl(terminal_content, tag)


def get_content(src):
    # [return content of first matching content fn]
    return next(
        (
            fn(src) for fn in [
                tc(INTEGER_CONSTANT),
                tc(STRING_CONSTANT),
                tc(KEYWORD_CONSTANT),
                tc(IDENTIFIER),
                tc(SYMBOL),
            ] if fn(src)
        ),
        None
    )


def eval_integer_constant(src):
    # [return vm translation of integerConstant]
    return 'push constant {}\n'.format(
        get_content(src)
    )


def eval_string_constant(src):
    # [return vm translation of stringConstant]
    # [content := text between stringConstant tags]
    content = get_content(src)
    # [out := vm initialization of new string]
    out = [
        'push constant {}'.format(len(content)),
        'String.new 1',
    ]
    # [out := vm translation of string]
    for char in content:
        # [out := vm translation of appending char]
        out.extend([
            'push constant {}'.format(ord(char)),
            'String.appendChar 2',
        ])
    return out


def eval_keyword_constant(src):
    content = get_content(src)
    if content == 'true':
        return ['push constant -1']
    elif content == 'false' or content == 'null':
        return ['push constant 0']
    elif content == 'this':
        return ['push argument 0']


def eval_var_name(src, sym_tab):
    content = get_content(src)
    kind = sym_tab[content]['kind']
    number = sym_tab[content]['number']
    out = [
        'push {} {}'.format(
            kind,
            number,
        )
    ]
    return out


def eval_unary_op(src):
    content = get_content(src)
    out = ['push {}'.format(
        UNARY_OP_MAP[content]
    )]
    return out


def eval_term(src):

def parse_expression(expr):
    terms = get_terms(expr)
    ops = get_ops(expr)
    for term in terms:
        parse_term(term)
    for op in ops:
        parse_op(op)


def get_text(el):
    return re.search(r' (.*?) ', el).group().strip()


def integer_constant(src):
    emit('push constant {}'.format(
        get_text(src)
    ))


TERMINAL_EXPRESSIONS = [
    'integerConstant',
]
