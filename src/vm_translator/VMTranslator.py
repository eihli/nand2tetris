import os
import re
import sys
import pathlib

import parse


def strip_comments(line):
    return re.sub('//.*$', '', line)


def main(filename):
    result = initialize_memory_segments()
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


def initialize_memory_segments():
    return [
        '@256',
        'D=A',
        '@SP',
        'M=D',
        '@400',
        'D=A',
        '@LCL',
        'M=D',
        '@500',
        'D=A',
        '@ARG',
        'M=D',
        '@3000',
        'D=A',
        '@THIS',
        'M=D',
        '@4000',
        'D=A',
        '@THAT',
        'M=D',
    ]


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
