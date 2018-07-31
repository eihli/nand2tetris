import re
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
    def setUp(self):
        self.maxDiff = None

    def test_jrr_token(self):
        r = re.compile('\s+', re.MULTILINE)
        self.assertEqual(
            r.sub('', tokenize(expected_input)),
            r.sub('', expected_output),
        )
