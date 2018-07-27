import unittest

from tokenizer.tokenizer import tokenize


expected_input = """
if (x < 0) {
   let state = "negative";
}
"""


expected_output = """
<tokens>
    <keyword> if </keyword>
    <symbol> ( </symbol>
    <identifier> x </identifier>
    <symbol> &lt; </symbol>
    <integerConstant> 0 </integerConstant>
    <symbol> ) </symbol>
    <symbol> { </symbol>
    <keyword> let </keyword>
    <identifier> state </identifier>
    <symbol> = </symbol>
    <stringConstant> negative </stringConstant>
    <symbol> ; </symbol>
    <symbol> } </symbol>
</tokens>
"""


class TestJRRToken(unittest.TestCase):
    def test_tokenize_keyword(self):
        self.assertEqual(
            tokenize('if'),
            '<keyword> if </keyword>\n',
        )

    def test_tokenize_open_paren(self):
        self.assertEqual(
            tokenize('if ('),
            '<keyword> if </keyword>\n<symbol> ( </symbol>\n',
        )

    @unittest.skip('temp')
    def test_jrr_token(self):
        self.assertEqual(
            tokenize(expected_input),
            expected_output,
        )
