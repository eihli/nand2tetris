import parser
from pathlib import Path
import sys
import xml.etree.ElementTree as ET


def indent(node, depth=0, ind='  '):
    newl = '' if node.text else '\n'
    out = ind * depth + '<{}>{}'.format(
        node.tag,
        newl,
    )
    for child in node:
        out += indent(child, depth + 1, ind=ind)
    if node.text:
        out += '{}'.format(node.text)
    else:
        out += ind * depth
    out += '</{}>\n'.format(node.tag)
    return out


if __name__ == "__main__":
    filepath = sys.argv[1]
    with open(filepath) as f:
        tokens = f.read()
    parsed = parser.parse(tokens)
    et = ET.fromstring(parsed)
    out = indent(et)
    p = Path(filepath)
    new_filepath = str(p.parents[0].joinpath(p.stem + 'MyT.xml'))
    with open(new_filepath, 'w') as f:
        f.write(out)
