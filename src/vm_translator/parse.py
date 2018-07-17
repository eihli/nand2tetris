def fill(list_, val, count):
    result = list_[:]
    while len(result) < count:
        result.append(val)
    return result


def get_y_and_x():
    """
    Sets the value of y in the D register
    and the value of x in Memory[A]
    """
    return [
        '@SP',
        'AM=M-1',
        'D=M',  # Save off y value
        '@SP',
        'A=M-1',
    ]


def parse_add(cmd):
    return get_y_and_x() + ['M=M+D']


def parse_sub(cmd):
    return get_y_and_x() + ['M=M-D']


def parse_neg(cmd):
    return [
        '@SP',
        'A=M-1',
        'M=-M',
    ]


bool_map = {
    'eq': 'D;JEQ',
    'gt': 'D;JGT',
    'lt': 'D;JLT',
}


jmp_ctr = 0


def get_jmp_label():
    global jmp_ctr
    jmp_ctr += 1
    return jmp_ctr


def parse_bool(cmp):
    jmp_label = get_jmp_label()
    return get_y_and_x() + [
        'D=M-D',  # Set D = x - y to determine > < or ==
        'M=-1',  # Set memory at stack pointer to true
        '@SETTRUE%s' % jmp_label,  # Skip setting to false if jump
        bool_map[cmp],
        '@SP',
        'A=M-1',
        'M=0',
        '(SETTRUE%s)' % jmp_label,
    ]


def parse_eq(cmd):
    return parse_bool('eq')


def parse_gt(cmd):
    return parse_bool('gt')


def parse_lt(cmd):
    return parse_bool('lt')


def parse_and(cmd):
    return get_y_and_x() + ['M=D&M']


def parse_or(cmd):
    return get_y_and_x() + ['M=D|M']


def parse_not(cmd):
    return [
        '@SP',
        'A=M-1',
        'M=!M',
    ]


def parse_push_constant(cmd):
    index = cmd[2]
    return [
        '@%s' % index,
        'D=A',
        '@SP',
        'A=M',
        'M=D',
        '@SP',
        'M=M+1',
    ]


def parse_push_temp(cmd):
    index = cmd[2]
    return [
        '@%s' % index,
        'D=A',
        '@R5',
        'A=D+A',  # We want the value at this address
        'D=M',
        '@SP',
        'A=M',
        'M=D',
        '@SP',
        'M=M+1',
    ]


def parse_push_pointer(cmd):
    index = cmd[2]
    return [
        '@%s' % index,
        'D=A',
        '@R3',
        'A=D+A',  # We want the value at this address
        'D=M',
        '@SP',
        'A=M',
        'M=D',
        '@SP',
        'M=M+1',
    ]


def get_static_var_counter():
    global static_var_counter
    r = static_var_counter
    static_var_counter += 1
    return r


def parse_push_static(cmd):
    fn = cmd[3]
    index = cmd[2]
    return [
        '@%s.%s' % (fn, index),
        'D=M',
        '@SP',
        'A=M',
        'M=D',
        '@SP',
        'M=M+1',
    ]


def parse_pop_static(cmd):
    index, fn = cmd[2], cmd[3]
    return [
        '@SP',
        'M=M-1',
        'A=M',
        'D=M',
        '@R14',
        'M=D',  # Value to pop in in R14 and D
        '@%s.%s' % (fn, index),
        'D=A',
        '@R13',
        'M=D',  # Address we want to populate is in R13 and D
        '@R14',
        'D=M',
        '@R13',
        'A=M',
        'M=D',
    ]


def parse_push_local(cmd):
    index = cmd[2]
    return [
        '@%s' % index,
        'D=A',
        '@LCL',
        'A=D+M',  # We want the value at this address
        'D=M',
        '@SP',
        'A=M',
        'M=D',
        '@SP',
        'M=M+1',
    ]


def parse_push_argument(cmd):
    index = cmd[2]
    return [
        '@%s' % index,
        'D=A',
        '@ARG',
        'A=D+M',  # We want the value at this address
        'D=M',
        '@SP',
        'A=M',
        'M=D',
        '@SP',
        'M=M+1',
    ]


def parse_push_this(cmd):
    index = cmd[2]
    return [
        '@%s' % index,
        'D=A',
        '@THIS',
        'A=D+M',  # We want the value at this address
        'D=M',
        '@SP',
        'A=M',
        'M=D',
        '@SP',
        'M=M+1',
    ]


def parse_push_that(cmd):
    index = cmd[2]
    return [
        '@%s' % index,
        'D=A',
        '@THAT',
        'A=D+M',  # We want the value at this address
        'D=M',
        '@SP',
        'A=M',
        'M=D',
        '@SP',
        'M=M+1',
    ]


def parse_pop_local(cmd):
    index = cmd[2]
    return [
        '@SP',
        'M=M-1',
        'A=M',
        'D=M',
        '@R14',
        'M=D',  # Value to pop in in R14 and D
        '@LCL',
        'D=M',
        '@%s' % index,
        'D=D+A',
        '@R13',
        'M=D',  # Address we want to populate is in R13 and D
        '@R14',
        'D=M',
        '@R13',
        'A=M',
        'M=D',
    ]


def parse_pop_argument(cmd):
    index = cmd[2]
    return [
        '@SP',
        'M=M-1',
        'A=M',
        'D=M',
        '@R14',
        'M=D',  # Value to pop in in R14 and D
        '@ARG',
        'D=M',
        '@%s' % index,
        'D=D+A',
        '@R13',
        'M=D',  # Address we want to populate is in R13 and D
        '@R14',
        'D=M',
        '@R13',
        'A=M',
        'M=D',
    ]


def parse_pop_pointer(cmd):
    index = cmd[2]
    return [
        '@SP',
        'M=M-1',
        'A=M',
        'D=M',
        '@R14',
        'M=D',  # Value to pop in in R14 and D
        '@R3',  # Pointer base index
        'D=A',
        '@%s' % index,
        'D=D+A',
        '@R13',
        'M=D',  # Address we want to populate is in R13 and D
        '@R14',
        'D=M',
        '@R13',
        'A=M',
        'M=D',
    ]


def parse_pop_temp(cmd):
    index = cmd[2]
    return [
        '@SP',
        'M=M-1',
        'A=M',
        'D=M',
        '@R14',
        'M=D',  # Value to pop in in R14 and D
        '@R5',  # Pointer base index
        'D=A',
        '@%s' % index,
        'D=D+A',
        '@R13',
        'M=D',  # Address we want to populate is in R13 and D
        '@R14',
        'D=M',
        '@R13',
        'A=M',
        'M=D',
    ]


def parse_pop_this(cmd):
    index = cmd[2]
    return [
        '@SP',
        'M=M-1',
        'A=M',
        'D=M',
        '@R14',
        'M=D',  # Value to pop in in R14 and D
        '@THIS',
        'D=M',
        '@%s' % index,
        'D=D+A',
        '@R13',
        'M=D',  # Address we want to populate is in R13 and D
        '@R14',
        'D=M',
        '@R13',
        'A=M',
        'M=D',
    ]


def parse_pop_that(cmd):
    index = cmd[2]
    return [
        '@SP',
        'M=M-1',
        'A=M',
        'D=M',
        '@R14',
        'M=D',  # Value to pop in in R14 and D
        '@THAT',
        'D=M',
        '@%s' % index,
        'D=D+A',
        '@R13',
        'M=D',  # Address we want to populate is in R13 and D
        '@R14',
        'D=M',
        '@R13',
        'A=M',
        'M=D',
    ]


parse_map = {
    ('add', None): parse_add,
    ('sub', None): parse_sub,
    ('neg', None): parse_neg,
    ('eq', None): parse_eq,
    ('gt', None): parse_gt,
    ('lt', None): parse_lt,
    ('and', None): parse_and,
    ('or', None): parse_or,
    ('not', None): parse_not,
    ('push', 'constant'): parse_push_constant,
    ('push', 'argument'): parse_push_argument,
    ('push', 'local'): parse_push_local,
    ('push', 'temp'): parse_push_temp,
    ('push', 'this'): parse_push_this,
    ('push', 'that'): parse_push_that,
    ('push', 'pointer'): parse_push_pointer,
    ('push', 'static'): parse_push_static,
    ('pop', 'argument'): parse_pop_argument,
    ('pop', 'local'): parse_pop_local,
    ('pop', 'temp'): parse_pop_temp,
    ('pop', 'this'): parse_pop_this,
    ('pop', 'that'): parse_pop_that,
    ('pop', 'pointer'): parse_pop_pointer,
    ('pop', 'static'): parse_pop_static,
    ('label')
}


def parse_cmd(cmd, filename):
    fn, arg1, arg2 = fill(cmd.split(' '), None, 3)
    return parse_map[(fn, arg1)]((fn, arg1, arg2, filename))
