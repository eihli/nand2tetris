from enum import Enum, auto
import sys
import xml.etree.ElementTree as ET


ID = 'identifier'
CVD = 'classVarDec'
SRD = 'subroutineDec'
KW = 'keyword'
PRML = 'parameterList'
LETS = 'letStatement'
VARD = 'varDec'


class Context(Enum):
    VAR = auto()
    ARG = auto()
    STATIC = auto()
    FIELD = auto()
    CLASS = auto()
    SUBR = auto()


def split(el, p):
    cur, res = [], []
    for e in el:
        if p(e):
            res.append(cur)
            cur = []
        else:
            cur.append(e)
    if cur:
        res.append(cur)
    return res


def declarations(cvd):
    pass


def cvd(et):
    return next(el for el in et if el.tag == CVD)


def srds(et):
    return [el for el in et if el.tag == SRD]


def let_stmnts(el):
    return list(next(e for e in el.iter() if e.tag == LETS))


def var_decs(el):
    return [e for e in el if e.tag == VARD]


def is_separator(el):
    return el.text.strip() == ';'


def symbolize(input_str):
    et = ET.fromstring(input_str)
    count = 0
    class_var_decs = [e for e in et if e.tag == CVD]
    for cvd in class_var_decs:
        cat = cvd[0].text.strip()
        tp = cvd[1].text.strip()
        count = 0
        vars = [e for e in cvd if e.tag == ID]
        for var in vars:
            var.set('category', cat)
            var.set('type', tp)
            var.set('number', str(count))
            count += 1
    subroutine_decs = srds(et)
    for srd in subroutine_decs:
        param_list = next(e for e in srd if e.tag == PRML)
        params = split(param_list, lambda x: x.text.strip() == ',')
        count = 0
        for param in params:
            tp = param[0].text.strip()
            ident = param[1]
            ident.set('category', 'argument')
            ident.set('type', tp)
            ident.set('number', str(count))
            count += 1
        subroutine_body = srd[-1]
        count = 0
        for var_dec in var_decs(subroutine_body):
            cat = var_dec[0].text.strip()
            tp = var_dec[1].text.strip()
            for e in [e for e in var_dec[2:] if e.tag == ID]:
                e.set('category', cat)
                e.set('type', tp)
                e.set('number', str(count))
                count += 1
    return ET.tostring(et).decode()


def main(input_str):
    return symbolize(input_str)


if __name__ == "__main__":
    args = sys.argv[1:]
    infile = args[0]
    with open(infile) as f:
        print(main(f.read()))
