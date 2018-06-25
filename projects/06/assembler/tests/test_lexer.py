import tempfile
import io
from unittest import TestCase
from .. import lexer


class TestAInstruction(TestCase):
    def test_parse_a_instruction(self):
        a_inst = '@2'
        a = lexer.A(a_inst)
        self.assertTrue(a.match)
        self.assertEqual(a.value, '0000000000000010\n')


class TestGetLabelLineNumbers(TestCase):
    def test_get_label_line_numbers(self):
        file = io.StringIO()
        file.write('// some comment\n')
        file.write('@500\n')
        file.write('(LABEL)\n')
        file.write('@20\n')
        file.write('D=M\n')
        file.write('(FOO)\n')
        file.seek(0)
        addrs = {}
        addrs = lexer.get_label_addrs(file, addrs)
        self.assertEqual(addrs.get('LABEL'), 1)
        self.assertEqual(addrs.get('FOO'), 3)


class TestStrip(TestCase):
    def test_strip_labels(self):
        file = io.StringIO()
        file.write('(LABEL)\n@foo\n')
        file.seek(0)
        file = lexer.strip_labels(file)
        self.assertEqual(file.read(), '@foo\n')

    def test_strip_comments_and_whitespace(self):
        file = io.StringIO()
        file.write('(LABEL)\n//foobar comment\n\n\n  \n@foobar\n')
        file.seek(0)
        self.assertEqual(
            lexer.strip_comments_and_whitespace(file).read(),
            '(LABEL)\n@foobar\n'
        )


class TestConvertVars(TestCase):
    def test_convert_vars(self):
        file = io.StringIO()
        file.write('@var\n')
        file.write('M=A\n')
        file.seek(0)
        self.assertEqual(
            lexer.convert_vars(file, {'var': 5}).read(),
            '@5\nM=A\n'
        )

    def test_get_var_addrs(self):
        file = io.StringIO()
        file.write('@var\n')
        file.write('M=A // foo comment\n')
        file.write('@W_ir.$d\n')
        file.seek(0)
        lexer.get_var_addrs(
            file,
            lexer.var_addr_map,
            lexer.ram_pointer,
        )
        self.assertEqual(lexer.var_addr_map['var'], 16)
        self.assertEqual(lexer.var_addr_map['W_ir.$d'], 17)

    def test_get_var_addrs_convert_vars(self):
        file = io.StringIO()
        file.write('@var\n')
        file.write('(LABEL)\n')
        file.write('@LABEL\n')
        file.seek(0)
        addrs = lexer.get_var_addrs(
            file, lexer.var_addr_map, lexer.ram_pointer,
        )
        addrs = lexer.get_label_addrs(file, addrs)
        file = lexer.strip_labels(file)
        file = lexer.convert_vars(file, addrs)
        self.assertEqual(file.read(), '@16\n@1\n')
