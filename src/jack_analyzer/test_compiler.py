import unittest as ut

from compiler import emit, out, get_terms


class TestEval(ut.TestCase):
    def test_expr(self):
        src = """
        <identifier> x </identifier>
        <symbol> + </symbol>
        <integerConstant> 5 </integerConstant>
        """


class TestHelper(ut.TestCase):
    def test_all(self):
        emit('foo')
        self.assertEqual(
            out.getvalue(),
            'foo\n'
        )

    def test_get_terms(self):
        terms = [
            '<term>',
            '<identifier> x </identifier>',
            '</term>',
            '<symbol> + </symbol>',
            '<term>',
            '<integerConstant> 5 </integerConstant>',
            '</term>',
        ]

        expected = [
            [
                '<term>',
                '<identifier> x </identifier>',
                '</term>',
            ],
            [
                '<term>',
                '<integerConstant> 5 </integerConstant>',
                '</term>',
            ]
        ]
        self.assertEqual(
            get_terms(terms),
            expected,
        )


@ut.skip('foo')
class TestCompile(ut.TestCase):
    def setUp(self):
        self.let_statement = """
        <letStatement>
            <keyword> let </keyword>
            <identifier> x </identifier>
            <symbol> = </symbol>
            <integerConstant> 1 </integerConstant>
            <symbol> ; </symbol>
        </letStatement>
        """
        self.symbol_table = {
            'x': {
                'type': 'int',
                'kind': 'static',
                'number': 0,
            }
        }

    def test_all(self):
        expected = '\n'.join([
            'push constant 0',
            'pop static 0'
        ])
        self.assertEqual(
            parse(self.let_statement),
            expected
        )
