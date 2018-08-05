from collections import namedtuple
from functools import partial
import re
import sys
from xml.sax.saxutils import escape


Token = namedtuple('Token', ['match', 'tag', 'text'])


def n_group_getter(n):
    return partial(lambda m: m.group(n))


g0 = n_group_getter(0)
g1 = n_group_getter(1)


KW_TOKEN_STRINGS = [
    'class', 'constructor', 'function',
    'method', 'field', 'static', 'var',
    'int', 'char', 'boolean', 'void', 'true',
    'false', 'null', 'this', 'let', 'do',
    'if', 'else', 'while', 'return',
]

SYM_TOKENS_STRINGS = [
    '{', '}', '(', ')', '[', ']', '.',
    ',', ';', '+', '-', '*', '/', '&',
    '|', '>', '<', '=', '~',
]


kw_re = r'(' + '|'.join(KW_TOKEN_STRINGS) + r')'
sym_re = (
    r'[' +
    ''.join(['\{}'.format(s) for s in SYM_TOKENS_STRINGS]) +
    r']'
)

TOKENS = [
    Token(re.compile(kw_re).match, 'keyword', g0),
    Token(re.compile(sym_re).match, 'symbol', g0),
    Token(re.compile(r'[a-zA-Z_][a-zA-Z_0-9]*').match, 'identifier', g0),
    Token(re.compile(r'[0-9]+').match, 'integerConstant', g0),
    Token(re.compile(r'"(.*?)"').match, 'stringConstant', g1),
]


def strip_comments(input_str):
    cr = r'(//.*$|/\*\*.*\*\/)'
    out = ''
    in_ml_cmnt = False
    for line in input_str.split('\n'):
        outline = re.sub(cr, '', line)
        if re.search(r'\/\*\*', line):
            in_ml_cmnt = True
        if not in_ml_cmnt:
            out += outline
        else:
            if re.search(r'\*\/', line):
                in_ml_cmnt = False
    return out


def tokenize(input_str):
    rest = input_str.lstrip()
    out = '<tokens>\r\n'
    # [out, token, rest :=
    #  tokenized input_str (xml) so far,
    #  next token (xml),
    #  remaining untokenized part of input_str]
    while rest:
        tag, text, to_consume = get_next_token(rest)
        out += format_token(tag, text)
        rest = consume_next_token(to_consume, rest)
    return out + '</tokens>\r\n'


def get_next_token(s):
    # [s has matching token ->
    #  tag, text, to_consume  :=
    #    tag that matches s, text to put in xml, text to consume from s
    #  tag, text, to_consume -> None, None, None]
    t = next((t for t in TOKENS if t.match(s)), None)
    if t is None:
        raise Exception(
            'Unhandled token {} near {}'.format(s.split(' ')[0], s[:10])
        )
    return t.tag, t.text(t.match(s)), t.match(s).group()


def consume_next_token(token, s):
    # [s := s with token and trailing whitespace removed from front]
    return s[len(token):].lstrip()


def format_token(tag, text):
    return '<{}> {} </{}>\r\n'.format(tag, escape(text), tag)


if __name__ == "__main__":
    infile = sys.argv[1]
    with open(infile) as f:
        input_str = f.read()
    decommented = strip_comments(input_str)
    tokenized = tokenize(decommented)
    print(tokenized)
