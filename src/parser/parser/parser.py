import re
import sys
import xml.etree.ElementTree as ET
import xml.dom.minidom as md

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


def cnsm_apnd(els, out, fn):
    el, els = fn(els)
    return apnd(el, els, out)


def apnd(el, els, out):
    if el:
        out.append(el)
    return els, out


def asrt(fn, el, rx):
    txt = el.text.strip()
    assert fn(txt, rx), '{} !~ {}'.format(txt, rx)


def mch(txt, rx):
    return re.match(rx, txt.strip())


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
        import pdb, sys
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
        more = mch(pk(els), r',')
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
        el, els = consume_expr(els)
        out.append(el)
        el, els = asrt_chmp(els, r'\]')
        out.append(el)
    el, els = asrt_chmp(els, r'=')
    out.append(el)
    el, els = consume_expr(els)
    out.append(el)
    el, els = asrt_chmp(els, r'\;')
    out.append(el)
    return out, els


def consume_term(els):
    out = ET.Element('term')
    const_re = r'({})'.format('|'.join([
        INT_RE,
        STR_RE,
        TERM_KW_RE,
    ]))
    if mch(pk(els).text, const_re):
        el, els = chomp(els)
        out.append(el)
    if mch(pk(els).text, ID_RE):
        if mch(pk(cdr(els)).text, r'\['):
            el, els = chomp(els)
            out.append(el)
            el, els = chomp(els)
            out.append(el)
            el, els = consume_expr(els)
            out.append(el)
            el, els = asrt_chmp(els, r'\]')
            out.append(el)
        elif mch(pk(cdr(els)).text, r'\.'):
            el, els = consume_subroutine_call(els)
            out.extend(el)
        else:
            el, els = chomp(els)
            out.append(el)
    if mch(pk(els).text, r'\('):
        el, els = chomp(els)
        out.append(el)
        el, els = consume_expr(els)
        out.append(el)
        el, els = asrt_chmp(els, r'\)')
        out.append(el)
    return out, els


def consume_subroutine_call(els):
    out = ET.Element('subroutineCall')
    el, els = asrt_chmp(els, ID_RE)
    out.append(el)
    if mch(pk(els).text, r'\.'):
        el, els = chomp(els)
        out.append(el)
        el, els = asrt_chmp(els, ID_RE)
        out.append(el)
        el, els = asrt_chmp(els, r'\(')
        out.append(el)
        els, out = cnsm_apnd(els, out, consume_expr_list)
        el, els = asrt_chmp(els, r'\)')
        out.append(el)
    return out.getchildren(), els


def consume_expr_list(els):
    out = ET.Element('expressionList')
    more = mch(pk(els).text, EXPR_RE)
    if more:
        el, els = consume_expr(els)
        out.append(el)
    more = mch(pk(els).text, r',')
    while more:
        el, els = chomp(els)
        out.append(el)
        el, els = consume_expr(els)
        out.append(el)
        more = mch(pk(els).text, r',')
    return out, els


def consume_expr(els):
    out = ET.Element('expression')
    els, out = cnsm_apnd(els, out, consume_term)
    if mch(pk(els).text, OP_RE):
        el, els = chomp(els)
        out.append(el)
        el, els = consume_term(els)
        out.append(el)
    more = mch(pk(els).text, r',')
    while more:
        el, els = chomp(els)
        out.append(el)
        els, out = cnsm_apnd(els, out, consume_term)
        out.append(el)
        more = mch(pk(els).text, r',')
    return out, els


def consume_if_statement(els):
    out = ET.Element('ifStatement')
    el, els = asrt_chmp(els, r'if')
    out.append(el)
    el, els = asrt_chmp(els, r'\(')
    out.append(el)
    el, els = consume_expr(els)
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
    els, out = cnsm_apnd(els, out, consume_expr)
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
