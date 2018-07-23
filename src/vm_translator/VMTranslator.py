import os
import re
import sys
import pathlib

import parse


def strip_comments(line):
    return re.sub('//.*$', '', line)


def main(filename):
    result = []
    path = pathlib.Path(filename)
    if path.is_dir():
        result += initialize_memory_segments()
        dir_name = path
        filenames = path.iterdir()
        for fn in filenames:
            file_path = pathlib.Path(fn)
            if file_path.suffix == '.vm':
                result += [writefile(str(fn))]
    else:
        dir_name = path.parent
        result += [writefile(filename)]

    with open('%s/%s.asm' % (dir_name, path.stem), 'w') as f:
        f.write('\n'.join(result))


def initialize_memory_segments():
    return [
        '@256',
        'D=A',
        '@SP',
        'M=D',
    ] + parse.parse_cmd('call Sys.init 0', 'hSys.vm')


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
