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


dymx = [
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
    return dymx + [
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
        '// {}'.format(cmd),
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


stack_map = {
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
}


op_map = {
    'add': lambda: dymx + ['M=M+D'],
    'sub': lambda: dymx + ['M=M-D'],
    'neg': lambda: ['@SP', 'A=M-1', 'M=-M'],
    'eq': lambda: parse_bool('eq'),
    'gt': lambda: parse_bool('gt'),
    'lt': lambda: parse_bool('lt'),
    'and': lambda: dymx + ['M=D&M'],
    'or': lambda: dymx + ['M=D|M'],
    'not': lambda: ['@SP', 'A=M-1', 'M=!M'],
}


def parse_label(label):
    return ['({})'.format(label)]


def parse_goto_label(label):
    return [
        '@{}'.format(label),
        '0;JMP',
    ]


def parse_if_goto(label):
    """
    If the top value in the stack is 0,
    continue to the next command. Else, jump to label.
    """
    return [
        '@SP',
        'M=M-1',
        'A=M',
        'D=M',
        '@{}'.format(label),
        'D;JNE',
    ]


program_flow_map = {
    'if-goto': parse_if_goto,
    'goto': parse_goto_label,
    'label': parse_label,
}


def parse_function_def(cmd, fn):
    name, num_args = cmd[1:3]
    result = [
        '({})'.format(name),
    ]
    for i in range(int(num_args)):
        result += [
            '@SP',
            'A=M',
            'M=0',
            '@SP',
            'M=M+1',
        ]
    return result


return_addr_ctr = 0


def get_return_address():
    global return_addr_ctr
    result = 'RETURN_ADDR{}'.format(return_addr_ctr)
    return_addr_ctr += 1
    return result


parse_push_a = [
    'D=M',
    '@SP',
    'A=M',
    'M=D',
    '@SP',
    'M=M+1',
]


def parse_call(cmd, fn):
    name, num_args = cmd[1:3]
    result = [
        '@{}'.format(name),
    ]
    for a in ['@LCL', '@ARG', '@THIS', '@THAT']:
        result += [a] + parse_push_a
    # Reposition ARG
    result += [
        '@5',
        'D=A',
        '@R13',
        'M=D',
        '@{}'.format(num_args),
        'D=A',
        '@R13',
        'D=D+M',
        '@SP',
        'D=A-D',
        '@ARG',
        'M=D',
        '@SP',
        'D=A',
        '@LCL',
        'M=D',
    ]
    # goto f
    result += [
        '({})'.format(name)
    ]
    return result


#RETURN
#LCL
#ARG
#THIS
#THAT

def parse_return(cmd, fn):
    result = [
        '@LCL',
        'D=M',
        '@R14',  # R14 is "FRAME"
        'M=D',
        '// Put the return address in a temp var',
        '@5',
        'D=A',
        '@LCL',
        'D=M-D',
        '@R15',  # R15 is "RET"
        'M=D',
        '// Reposition the return value for the caller',
        '@SP',
        'A=M-1',
        'D=M',
        '@ARG',
        'A=M',
        'M=D',
        '// Restore stack pointer of the caller',
        '@ARG',
        'D=M+1',
        '@SP',
        'M=D',
        '// Restore THAT of the caller',
        '@R14',
        'D=M-1',
        'A=D',
        'D=M',
        '@THAT',
        'M=D',
        '// Restore THIS of caller',
        '@2',
        'D=A',
        '@R14',
        'D=M-D',
        'A=D',
        'D=M',
        '@THIS',
        'M=D',
        '// Restore ARG of caller',
        '@3',
        'D=A',
        '@R14',
        'D=M-D',
        'A=D',
        'D=M',
        '@ARG',
        'M=D',
        '// Restore LCL of caller',
        '@4',
        'D=A',
        '@R14',
        'D=M-D',
        'A=D',
        'D=M',
        '@LCL',
        'M=D',
        '// GOTO return address',
        '@R15',
        'A=M',
        '0;JMP',
    ]
    return result


parse_fn_map = {
    'function': parse_function_def,
    'call': parse_call,
    'return': parse_return,
}


class ParseNotImplemented(Exception):
    pass


def parse_cmd(cmd, filename):
    result = ['// start {}: {}'.format(filename, cmd)]
    fn, arg1, arg2 = fill(cmd.split(' '), None, 3)
    if fn in op_map:
        result += op_map[fn]()
    elif (fn, arg1) in stack_map:
        result += stack_map[(fn, arg1)]((fn, arg1, arg2, filename))
    elif fn in program_flow_map:
        result += program_flow_map[fn](arg1)
    elif fn in parse_fn_map:
        result += parse_fn_map[fn]((fn, arg1, arg2), filename)
    else:
        raise ParseNotImplemented(
            '{} {} {} not implemented'.format(fn, arg1, arg2)
        )
    result += ['// end {}: {}'.format(filename, cmd)]
    return result
