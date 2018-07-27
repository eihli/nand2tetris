import re


IF = r'if'
OP = r'\('
WS = r'\s'

def tokenize(input_str):
    if not input_str:
        return ''
    return _tokenize(input_str)


def _tokenize(input_str):
    if re.match(IF, input_str):
        return ('<keyword> if </keyword>\n' +
                tokenize(consume('if', input_str)))
    elif re.match(OP, input_str):
        return '<symbol> ( </symbol>\n'
    elif re.match(WS, input_str):
        return tokenize(
            consume(
                re.match(WS, input_str).group(),
                input_str,
            ),
        )
    else:
        return ''


def consume(part, whole):
    return whole[len(part):]
