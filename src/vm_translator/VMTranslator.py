import os
import re
import sys
import parse


def strip_comments(line):
    return re.sub('//.*$', '', line)


def main(filename):
    result = []
    fn = os.path.basename(filename).split('.')[0]
    with open(filename) as f:
        for line in f:
            line = strip_comments(line).strip()
            if line:
                result += parse.parse_cmd(line, fn)
    with open('%s/%s.asm' % (os.path.dirname(filename), fn), 'w') as f:
        f.write('\n'.join(result))


if __name__ == '__main__':
    main(*sys.argv[1:])
