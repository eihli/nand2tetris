import re
import sys
import xml.etree.ElementTree as ET

ID_RE = r'[a-zA-Z_][a-zA-Z_0-9]*'
TYPE_RE = r'(int|char|boolean|{})'.format(ID_RE)
INT_RE = r'[0-9]+'
OP_RE = r'[{}]'.format(''.join([
    r'\+', r'\-', r'\*', r'\/', r'\&',
    r'\|', r'\>', r'\<', r'\=', r'\~',
]))
STR_RE = r'"(.*?)"'
TERM_KW_RE = r'(true|false|null|this)'
EXPR_RE = r'({})'.format('|'.join([
    INT_RE,
    STR_RE,
    TERM_KW_RE,
]))

terms = [
    'integerConstant',
    'stringConstant',
    'keywordConstant',
    'identifier',
    'subroutineCall',
]

IDENTIFIER = 'identifier'
KEYWORD = 'keyword'
SYMBOL = 'symbol'
VAR = 'var'
KEYWORD_CONSTANTS = [
    'true',
    'false',
    'null',
    'this',
]
STRING_CONSTANT = 'stringConstant'
INTEGER_CONSTANT = 'integerConstant'
UNARY_OPS = ['-', '~']
OPS = ['+', '-', '*', '/', '&', '|', '<', '>', '=']
TYPE_CONSTANTS = [
    'int',
    'char',
    'boolean',
]


def cnsm_apnd(els, out, fn):
    el, els = fn(els)
    return apnd(el, els, out)


def apnd(el, els, out):
    out.append(el)
    return els, out


def cnsm_xtnd(els, out, fn):
    el, els = fn(els)
    return xtnd(el, els, out)


def xtnd(el, els, out):
    out.extend(el)
    return els, out


def asrt(fn, el, rx):
    txt = el.text.strip()
    try:
        assert fn(txt, rx), '{} !~ {}'.format(txt, rx)
    except AssertionError as e:
        import pdb; pdb.set_trace()
        raise e


def mch(txt, rx):
    return re.match(rx, txt.strip())


def is_text_in(el, it):
    text = el.text.strip()
    return text in it


# Terminal elements

def is_keyword_constant(els):
    el = pk(els)
    return (
        el.tag == KEYWORD
        and is_text_in(el, KEYWORD_CONSTANTS)
    )


def consume_keyword_constant(els):
    return car(els), cdr(els)


def is_unary_op(els):
    el = pk(els)
    return (
        el.tag == SYMBOL
        and is_text_in(el, UNARY_OPS)
    )


def consume_unary_op(els):
    return car(els), cdr(els)


def is_op(els):
    el = pk(els)
    return (
        el.tag == SYMBOL
        and is_text_in(el, OPS)
    )


def consume_op(els):
    return car(els), cdr(els)


def is_var_name(els):
    return is_identifier(car(els))


def consume_var_name(els):
    return car(els), cdr(els)


def is_class_name(els):
    assert pk(els).tag == IDENTIFIER
    return pk(els).tag == IDENTIFIER


def consume_class_name(els):
    return car(els), cdr(els)


def is_type(els):
    el = pk(els)
    return (
        is_class_name(els)
        or is_text_in(el, TYPE_CONSTANTS)
    )


def consume_type(els):
    return car(els), cdr(els)


def consume_any(els):
    return car(els), cdr(els)


def is_var_dec(els):
    el = pk(els)
    return el.tag == VAR


def create_var_dec():
    return ET.Element('varDec')


def is_comma(els):
    el = pk(els)
    return (
        el.tag == SYMBOL
        and el.text.strip() == ','
    )


def is_comma_or_close_paren(els):
    return is_comma(els) or is_close_paren(els)


def is_close_paren(els):
    return car(els).text.strip == ')'


def cnsm_apnd_any(els, out):
    return cnsm_apnd(els, out, consume_any)


def is_semi_colon(els):
    el = pk(els)
    return (
        el.tag == SYMBOL
        and el.text.strip() == ';'
    )


def asrt_cnsm_apnd(fn, els, out):
    assert fn(els)
    return cnsm_apnd(els, out)


def consume_var_dec(els):
    out = ET.Element('varDec')
    el, els = chomp(els)
    out.append(el)
    asrt(mch, pk(els), TYPE_RE)
    el, els = chomp(els)
    out.append(el)
    asrt(mch, pk(els), ID_RE)
    el, els = chomp(els)
    out.append(el)
    more = mch(pk(els).text, r',')
    while more:
        el, els = chomp(els)
        out.append(el)
        asrt(mch, pk(els), ID_RE)
        el, els = chomp(els)
        out.append(el)
        more = mch(pk(els).text, r',')
    asrt(mch, pk(els), r';')
    el, els = chomp(els)
    out.append(el)
    return out, els


def is_string_constant(els):
    return pk(els).tag == STRING_CONSTANT


def is_integer_constant(els):
    return pk(els).tag == INTEGER_CONSTANT


def consume_expression_list(els):
    out = ET.Element('expressionList')
    el, els = consume_expression(els)
    if el:
        out.append(el)
    while is_comma_or_close_paren(els):
        while is_comma_or_close_paren(els):
            el, els = chomp(els)
            out.append(el)
        el, els = consume_expression(els)
        if el:
            out.append(el)
    return els, out


def consume_expression(els):
    out = ET.Element('expression')
    sub_el, els = consume_term(els)
    if sub_el:
        out.append(sub_el)
    more = is_operator(els)

    while more:
        els, out = cnsm_apnd_any(els, out)
        els, out = cnsm_apnd(els, out, consume_term)
        more = is_operator(els)
    return out, els


def is_operator(els):
    try:
        p = car(els).text.strip() in OPS
    except IndexError as e:
        # Hopefully this doesn't bit me.
        p = False
        pass
    return p


def consume_term(els):
    out = ET.Element('term')
    if is_integer_constant(els):
        els, out = cnsm_apnd_any(els, out)
    elif is_string_constant(els):
        els, out = cnsm_apnd_any(els, out)
    elif is_keyword_constant(els):
        els, out = cnsm_apnd_any(els, out)
    elif is_var_name(els) and pk(cdr(els)).text.strip() == '[':
        els, out = cnsm_apnd_any(els, out)
        els, out = cnsm_apnd_any(els, out)
        el, els = consume_expression(els)
        if el:
            out.append(el)
        els, out = cnsm_apnd_any(els, out)
    elif is_subroutine_call(els):
        el, els = consume_subroutine_call(els)
        out.extend(el)
    elif is_var_name(els):
        els, out = cnsm_apnd(els, out, consume_var_name)
    elif pk(els).text.strip() == '(':
        els, out = cnsm_apnd_any(els, out)
        el, els = consume_expression(els)
        if el:
            out.append(el)
        assert pk(els).text.strip() == ')'
        els, out = cnsm_apnd_any(els, out)
    elif is_unary_op(els):
        els, out = cnsm_apnd_any(els, out)
        el, els = consume_term(els)
        out.append(el)
    else:
        # Empty Term
        pass
    return out, els


def is_identifier(el):
    return el.tag == IDENTIFIER


def is_subroutine_call(els):
    return (
        is_identifier(car(els))
        and car(cdr(els)).text.strip() == '.'
    )


def pk(lst):
    return lst[0]


def cdr(lst):
    return lst[1:]


def car(lst):
    return lst[0]


def chomp(els):
    el = ET.Element(els[0].tag)
    el.text = els[0].text
    return el, els[1:]


def parse(input_str):
    try:
        result = _parse(input_str)
    except AssertionError as e:
        import pdb
        import sys
        t, v, tb = sys.exc_info()
        pdb.post_mortem(tb)
        raise e
    return result


def _parse(input_str):
    els = list(ET.fromstring(input_str).iter())[1:]
    asrt(mch, pk(els), r'class')
    out = ET.Element('class')
    el, els = chomp(els)
    out.append(el)
    asrt(mch, pk(els), ID_RE)
    el, els = chomp(els)
    out.append(el)
    asrt(mch, pk(els), r'{')
    el, els = chomp(els)
    out.append(el)

    more = mch(pk(els).text, r'(static|field)')
    while more:
        el, els = consume_class_var_dec(els)
        out.append(el)
        more = mch(pk(els).text, r'(static|field)')
    el = pk(els)
    more = mch(pk(els).text, r'(constructor|function|method)')
    while more:
        el, els = consume_subroutine_dec(els)
        out.append(el)
        more = mch(pk(els).text, r'(constructor|function|method)')
    asrt(mch, pk(els), r'}')
    el, els = chomp(els)
    out.append(el)
    out_str = ET.tostring(
        out, short_empty_elements=False
    ).decode(sys.getdefaultencoding())
    return out_str


def consume_class_var_dec(els):
    out = ET.Element('classVarDec')
    el, els = chomp(els)
    out.append(el)
    asrt(mch, pk(els), TYPE_RE)
    el, els = chomp(els)
    out.append(el)
    asrt(mch, pk(els), ID_RE)
    el, els = chomp(els)
    out.append(el)
    more = mch(pk(els).text, r',')
    while more:
        el, els = chomp(els)
        out.append(el)
        asrt(mch, pk(els), ID_RE)
        el, els = chomp(els)
        out.append(el)
        more = mch(pk(els).text, r',')
    asrt(mch, pk(els), r';')
    el, els = chomp(els)
    out.append(el)
    return out, els


def consume_subroutine_dec(els):
    out = ET.Element('subroutineDec')
    asrt(mch, pk(els), r'(constructor|function|method)')
    el, els = chomp(els)
    out.append(el)
    asrt(mch, pk(els), r'(void|{})'.format(TYPE_RE))
    el, els = chomp(els)
    out.append(el)
    asrt(mch, pk(els), ID_RE)
    el, els = chomp(els)
    out.append(el)
    asrt(mch, pk(els), r'\(')
    el, els = chomp(els)
    out.append(el)
    el, els = consume_parameter_list(els)
    out.append(el)
    asrt(mch, pk(els), r'\)')
    el, els = chomp(els)
    out.append(el)
    el, els = consume_subroutine_body(els)
    out.append(el)
    return out, els


def consume_parameter_list(els):
    out = ET.Element('parameterList')
    if mch(pk(els).text, TYPE_RE):
        el, els = chomp(els)
        out.append(el)
        el, els = asrt_chmp(els, ID_RE)
        out.append(el)
        more = mch(pk(els).text, r',')
        while more:
            el, els = chomp(els)
            out.append(el)
            el, els = asrt_chmp(els, TYPE_RE)
            out.append(el)
            el, els = asrt_chmp(els, ID_RE)
            out.append(el)
            more = mch(pk(els).text, r',')
    return out, els


def consume_subroutine_body(els):
    out = ET.Element('subroutineBody')
    asrt(mch, pk(els), r'\{')
    el, els = chomp(els)
    out.append(el)
    more = mch(pk(els).text, r'var')
    while more:
        el, els = consume_var_dec(els)
        out.append(el)
        more = mch(pk(els).text, r'var')
    el, els = consume_statements(els)
    out.append(el)
    asrt(mch, pk(els), r'\}')
    el, els = chomp(els)
    out.append(el)

    return out, els


def consume_statements(els):
    out = ET.Element('statements')
    rgx = r'({})'.format(
        '|'.join(['let', 'if', 'while', 'do', 'return'])
    )
    more = mch(pk(els).text, rgx)
    while more:
        if mch(pk(els).text, r'let'):
            el, els = consume_let_statement(els)
        elif mch(pk(els).text, r'if'):
            el, els = consume_if_statement(els)
        elif mch(pk(els).text, r'while'):
            el, els = consume_while_statement(els)
        elif mch(pk(els).text, r'do'):
            el, els = consume_do_statement(els)
        elif mch(pk(els).text, r'return'):
            el, els = consume_return_statement(els)
        else:
            raise Exception("Intentionally left blank...")
        out.append(el)
        more = mch(pk(els).text, rgx)
    return out, els


def consume_let_statement(els):
    out = ET.Element('letStatement')
    el, els = asrt_chmp(els, r'let')
    out.append(el)
    el, els = asrt_chmp(els, ID_RE)
    out.append(el)
    if mch(pk(els).text, r'\['):
        el, els = chomp(els)
        out.append(el)
        el, els = consume_expression(els)
        if el:
            out.append(el)
        el, els = asrt_chmp(els, r'\]')
        out.append(el)
    el, els = asrt_chmp(els, r'=')
    out.append(el)
    el, els = consume_expression(els)
    if el:
        out.append(el)
    el, els = asrt_chmp(els, r'\;')
    out.append(el)
    return out, els


def consume_subroutine_call(els):
    out = []
    el, els = asrt_chmp(els, ID_RE)
    out.append(el)
    if mch(pk(els).text, r'\.'):
        el, els = chomp(els)
        out.append(el)
        el, els = asrt_chmp(els, ID_RE)
        out.append(el)
    el, els = asrt_chmp(els, r'\(')
    out.append(el)
    els, el = consume_expression_list(els)
    out.append(el)
    el, els = asrt_chmp(els, r'\)')
    out.append(el)
    return out, els


def consume_if_statement(els):
    out = ET.Element('ifStatement')
    el, els = asrt_chmp(els, r'if')
    out.append(el)
    el, els = asrt_chmp(els, r'\(')
    out.append(el)
    el, els = consume_expression(els)
    if el:
        out.append(el)
    el, els = asrt_chmp(els, r'\)')
    out.append(el)
    el, els = asrt_chmp(els, r'\{')
    out.append(el)
    el, els = consume_statements(els)
    out.append(el)
    el, els = asrt_chmp(els, r'\}')
    out.append(el)
    if mch(pk(els).text, r'else'):
        el, els = chomp(els)
        out.append(el)
        el, els = asrt_chmp(els, r'\{')
        out.append(el)
        el, els = consume_statements(els)
        out.append(el)
        el, els = asrt_chmp(els, r'\}')
        out.append(el)
    return out, els


def consume_while_statement(els):
    out = ET.Element('whileStatement')
    el, els = asrt_chmp(els, r'while')
    out.append(el)
    el, els = asrt_chmp(els, r'\(')
    out.append(el)
    el, els = consume_expression(els)
    if el:
        out.append(el)
    el, els = asrt_chmp(els, r'\)')
    out.append(el)
    el, els = asrt_chmp(els, r'\{')
    out.append(el)
    el, els = consume_statements(els)
    out.append(el)
    el, els = asrt_chmp(els, r'\}')
    out.append(el)
    return out, els


def consume_do_statement(els):
    out = ET.Element('doStatement')
    el, els = asrt_chmp(els, r'do')
    out.append(el)
    el, els = consume_subroutine_call(els)
    out.extend(el)
    el, els = asrt_chmp(els, r';')
    out.append(el)
    return out, els


def consume_return_statement(els):
    out = ET.Element('returnStatement')
    el, els = asrt_chmp(els, r'return')
    out.append(el)
    el, els = consume_expression(els)
    if el:
        out.append(el)
    el, els = asrt_chmp(els, r';')
    out.append(el)
    return out, els


def asrt_chmp(els, rgx):
    try:
        asrt(mch, pk(els), rgx)
    except AssertionError as e:
        print([e.text for e in els[:3]])
        raise
    el, els = chomp(els)
    return el, els
