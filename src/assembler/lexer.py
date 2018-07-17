import sys
import io
import os
import enum
import re


predefined_symbols = {
    'SP': 0,
    'LCL': 1,
    'ARG': 2,
    'THIS': 3,
    'THAT': 4,
    'R0': 0,
    'R1': 1,
    'R2': 2,
    'R3': 3,
    'R4': 4,
    'R5': 5,
    'R6': 6,
    'R7': 7,
    'R8': 8,
    'R9': 9,
    'R10': 10,
    'R11': 11,
    'R12': 12,
    'R13': 13,
    'R14': 14,
    'R15': 15,
    'SCREEN': 16384,
    'KBD': 24567,
}


@enum.unique
class Token(enum.Enum):
    A = 'A Instruction'
    C = 'C Instruction'
    L = 'Open Label'
    CO = 'Comment'
    EL = 'Empty Line'


removeable_tokens = [Token.EL, Token.CO]
ram_pointer = 16
var_addr_map = {**predefined_symbols}


def get_var_addrs(input_, var_addr_map, ram_pointer):
    for line in input_:
        match = re.match(r'@([a-zA-Z][\d_.$:a-zA-Z].*)', line)
        if match and match.group(1) not in predefined_symbols:
            if not var_addr_map.get(match.group(1)):
                var_addr_map[match.group(1)] = ram_pointer
                ram_pointer += 1
    input_.seek(0)
    return var_addr_map


def strip_comments_and_whitespace(input_):
    output = io.StringIO()
    for line in input_:
        line = re.sub('//.*', '', line)
        line = re.sub(' ', '', line)
        line = re.sub('^\s$', '', line)
        output.write(re.sub(' ', '', line))
    output.seek(0)
    return output


def get_label_addrs(input_, addr_map):
    cleaned_input = strip_comments_and_whitespace(input_)
    rx = token_regexes[Token.L]
    i = 0
    for line in cleaned_input:
        match = re.match(rx, line)
        if match:
            addr_map[match.group(1)] = i
        else:
            i += 1
    input_.seek(0)
    return addr_map


def strip_labels(input_):
    output = io.StringIO()
    rx = token_regexes[Token.L]
    for line in input_:
        if not re.match(rx, line):
            output.write(line)
    output.seek(0)
    return output


def convert_vars(input_, addrs):
    print(addrs)
    output = io.StringIO()
    rx = r'@([a-zA-Z]+.*)'
    for line in input_:
        match = re.match(rx, line)
        if match and match.group(1) in addrs:
            output.write('@{}\n'.format(addrs[match.group(1)]))
        else:
            output.write(line)
    output.seek(0)
    return output


def parse_a(match):
    return '{0:016b}\n'.format(int(match.group(1)))


c_inst = {
    '0': '101010',
    '1': '111111',
    '-1': '111010',
    '^D$': '001100',
    '^[AM]$': '110000',
    '!D': '001101',
    '(!A|!M)': '110001',
    '-D': '001111',
    '(-A|-M)': '110011',
    '(D\+1|1\+D)': '011111',
    '(A\+1|1\+A|M\+1|1\+M)': '110111',
    'D-1': '001110',
    '(A-1|M-1)': '110010',
    '(D\+A|A\+D|D\+M|M\+D)': '000010',
    '(D-A|D-M)': '010011',
    '(A-D|M-D)': '000111',
    '(D&A|A&D|D&M|M&D)': '000000',
    '(D\|A|A\|D|D\|M|M\|D)': '010101',
}

dst_map = {
    '^M$': '001',
    '^D$': '010',
    '(^MD$|^DM$)': '011',
    '^A$': '100',
    '(^AM$|^MA$)': '101',
    '(^AD$|^DA$)': '110',
    '[^AMD$]{3}': '111',
}

jmp_map = {
    'JGT': '001',
    'JEQ': '010',
    'JGE': '011',
    'JLT': '100',
    'JNE': '101',
    'JLE': '110',
    'JMP': '111',
}


def parse_c(match):
    dst = match.group('dst')
    if dst:
        try:
            dst = next(v for k, v in dst_map.items() if re.match(k, dst))
        except StopIteration:
            import pdb; pdb.set_trace()

    else:
        dst = '000'
    cmp = match.group('cmp')
    cmp_m = re.search(r'M', cmp)
    try:
        cmp = next(v for k, v in c_inst.items() if re.match(k, cmp))
    except StopIteration:
        import pdb; pdb.set_trace()

    jmp = match.group('jmp')
    jmp = jmp_map.get(jmp, '000')

    a = 1 if cmp_m else 0

    return f'111{a}{cmp}{dst}{jmp}\n'


token_fns = {
    Token.A: parse_a,
    Token.C: parse_c,
}


token_regexes = {
    Token.A: r'^\@(.*)',
    Token.L: r'\((.*)\)',
    Token.CO: r'//.*',
    Token.EL: r'^\n',
    Token.C: r'(?P<dst>[MDA0]*)?=?(?P<cmp>[!01MDA\+\-\|&][^;J]*);?(?P<jmp>J..)?'
}


def parse_line(line):
    pass


class A:
    pattern = '^\@([0-9]+)'

    def __init__(self, string):
        self.string = string

    def parse(self):
        pass

    @property
    def match(self):
        return re.match(self.pattern, self.string)

    @property
    def value(self):
        return '{0:016b}\n'.format(int(self.match.group(1)))


def test():
    fp = os.path.abspath(
        os.path.join(os.path.dirname(__file__),
                     '../add/Add.asm'))
    with open(fp) as f:
        output = strip_comments_and_whitespace(f)
        addrs = get_label_addrs(output)
        output = strip_labels(output)
        output = convert_vars(output, addrs)

    output.seek(0)
    con = io.StringIO()
    for line in output:
        con.write(parse_line(line))
    con.seek(0)
    return con.read()


def assemble(fp, outf):
    with open(fp) as f:
        # strip comments and whitespace
        f = strip_comments_and_whitespace(f)
        # get addresses of labels
        label_addrs = get_label_addrs(f, {})
        # convert labels
        f = convert_vars(f, label_addrs)
        # get addresses of variables
        addrs = get_var_addrs(f, var_addr_map, ram_pointer)
        # convert addresses of variables
        f = convert_vars(f, addrs)
        # parse instructions
        print(addrs)
        f = strip_labels(f)
        print(f.read())
        f.seek(0)
        with open(f'{fp}.hack', 'w') as out:
            for line in f:
                if re.match(token_regexes[Token.A], line):
                    out.write(
                        parse_a(re.match(token_regexes[Token.A], line))
                    )
                else:
                    out.write(
                        parse_c(re.match(token_regexes[Token.C], line))
                    )
        with open(f'{fp}.hack') as f:
            print(f.read())


if __name__ == '__main__':
    assemble(sys.argv[1], sys.argv[2])
