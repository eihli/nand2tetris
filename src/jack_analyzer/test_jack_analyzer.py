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
        # We need to write then read this one so /r/n gets
        # converted to /n
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
        with open('test_data/parsed_cmp.xml') as expected:
            self.assertEqual(
                expected.read(),
                actual,
            )

    def test_symbolize(self):
        with open('test_data/parsed.xml') as p:
            actual = symbolize(p.read())
        with open('test_data/symbolized_cmp.sxml') as expected:
            self.assertEqual(
                expected.read(),
                actual,
            )

    def test_compiler(self):
        self.maxDiff = None
        with open('test_data/symbolized.sxml') as s:
            actual = compile(s.read())
        with open('test_data/compiled_cmp.vm') as expected:
            self.assertEqual(
                expected.read(),
                actual,
            )
