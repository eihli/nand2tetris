import unittest as ut


from compiler import compile
from parser import parse
from tokenizer import tokenize
from symbolize import symbolize


class TestJackAnalyzer(ut.TestCase):
    """
    These mainly just test for regressions.
    There are smaller unit tests at each individual step for narrowing
    in on specifics.
    """
    def setUp(self):
        super(TestJackAnalyzer, self).setUp()
        self.src_filename = 'Main.jack'
        with open(self.src_filename) as f:
            self.src = f.read()

    def test_tokenizer(self):
        tokenized = tokenize(self.src)
        with open('test_data/tokenized.xml', 'w') as f:
            f.write(tokenized)
        with open('test_data/tokenized_cmp.xml') as expected, \
             open('test_data/tokenized.xml') as actual:  # noqa: E127
            self.assertEqual(
                expected.read(),
                actual.read(),
            )

    def test_parser(self):
        with open('test_data/tokenized.xml') as t:
            actual = parse(t.read())
        with open('test_data/parsed_cmp.xml') as expected, \
             open('test_data/parsed.xml') as actual:  # noqa: E127
            self.assertEqual(
                expected.read(),
                actual.read(),
            )

    def test_symbolize(self):
        with open('test_data/parsed.xml') as p:
            actual = symbolize(p.read())
        with open('test_data/symbolized_cmp.sxml', 'w') as expected, \
             open('test_data/symbolized.sxml') as actual:  # noqa: E127
            self.assertEqual(
                expected.read(),
                actual.read(),
            )

    def test_compiler(self):
        with open('test_data/symbolized.sxml') as s:
            compiled = compile(s.read())
        with open('test_data/compiled.vm') as c:
            c.write(compiled)
        with open('test_data/compiled_cmp.vm', 'w') as expected, \
             open('test_data/compiled.vm') as actual:  # noqa: E127
            expected.write(compiled)
            self.assertEqual(
                expected.read(),
                actual.read(),
            )
