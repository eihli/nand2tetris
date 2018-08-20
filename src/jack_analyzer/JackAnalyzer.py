import io
from pathlib import Path
import sys
import compiler
from tokenizer import strip_comments, tokenize
from parser import parse
from symbolize import symbolize
import xml.etree.ElementTree as ET
from xml.sax.saxutils import escape


def indent(node, depth=0, ind='  '):
    newl = '' if node.text else '\r\n'
    out = ind * depth + '<{}>{}'.format(
        node.tag,
        newl,
    )
    for child in node:
        out += indent(child, depth + 1, ind=ind)
    if node.text:
        out += '{}'.format(escape(node.text))
    else:
        out += ind * depth
    out += '</{}>\r\n'.format(node.tag)
    return out


def tokenize_file(filename):
    with open(filename) as f:
        src = f.read()
    stripped = strip_comments(src)
    tokenized = tokenize(stripped)
    path = Path(filename)
    token_outfile = str(path.parents[0].joinpath(
        path.stem + 'T.xml'
    ))
    with open(token_outfile, 'w') as f:
        f.write(tokenized)


def parse_file(filename):
    with open(filename) as f:
        parsed = parse(f.read())
    et = ET.fromstring(parsed)
    out = indent(et)
    path = Path(filename)
    stem = path.stem
    grammar_outfile = str(path.parents[0].joinpath(
        '{}.xml'.format(stem[:-1])
    ))
    with open(grammar_outfile, 'w') as f:
        f.write(out)


def symbolize_file(filename):
    with open(filename) as f:
        out = symbolize(f.read())
    path = Path(filename)
    stem = path.stem
    sxml = str(path.parents[0].joinpath(
        '{}.sxml'.format(stem)
    ))
    with open(sxml, 'w') as f:
        f.write(out)


if __name__ == "__main__":
    filename, srcfile = sys.argv[1], sys.argv[1]
    path = Path(srcfile)
    if path.is_dir():
        for filename in path.iterdir():
            if filename.suffix == '.jack':
                tokenize_file(str(filename))
        for filename in path.iterdir():
            if (filename.suffix == '.xml' and filename.stem[-1] == 'T'):
                parse_file(str(filename))
        for filename in path.iterdir():
            if (filename.suffix == '.xml' and filename.stem[-1] != 'T'):
                symbolize_file(str(filename))
    else:
        tokenize_file(str(filename))
        txml = path.stem + 'T.xml'
        parse_file(txml)
        xml = path.stem + '.xml'
        symbolize_file(xml)
        with open(path.stem + '.sxml') as f:
            txt = f.read()
            result = compiler.main(txt)
        print(result)
