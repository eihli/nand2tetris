import os
import re
import sys
import parse
import pathlib


def strip_comments(line):
    return re.sub('//.*$', '', line)


def main(filename):
    result = []
    path = pathlib.Path(filename)
    if path.is_dir():
        dir_name = path
        filenames = path.iterdir()
        for filename in filenames:
            file_path = pathlib.Path(filename)
            if file_path.suffix == '.vm':
                result += [writefile(filename)]
    else:
        dir_name = path.parent
        result += [writefile(filename)]

    with open('%s/%s.asm' % (dir_name, path.stem), 'w') as f:
        f.write('\n'.join(result))


def writefile(filename):
    result = []
    fn = os.path.basename(filename).split('.')[0]
    with open(filename) as f:
        for line in f:
            line = strip_comments(line).strip()
            if line:
                result += parse.parse_cmd(line, fn)
    return '\n'.join(result)


if __name__ == '__main__':
    main(*sys.argv[1:])
