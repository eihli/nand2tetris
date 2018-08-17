import re
import unittest as ut
import xml.etree.ElementTree as ET

from parse import indent
from symbolize import symbolize


class ParserTestCase(ut.TestCase):
    def setUp(self):
        self.maxDiff = None

    def assertXmlEqual(self, a, b):
        a, b = [
            re.sub('\s', '', x)
            for x in [a, b]
        ]
        a, b = [
            re.sub('\n+', '\n', x)
            for x in [a, b]
        ]

        a = ET.fromstring(a)
        for el in a.iter():
            a.text = ' {} '.format(a.text)
        a = indent(a)
        b = ET.fromstring(b)
        for el in b.iter():
            b.text = ' {} '.format(b.text)
        b = indent(b)
        self.assertEqual(a, b)


class TestSymbolize(ParserTestCase):
    def setUp(self):
        self.class_var_dec = """
        <classVarDec>
          <keyword> static </keyword>
          <keyword> boolean </keyword>
          <identifier> test </identifier>
          <symbol> ; </symbol>
        </classVarDec>
        """

    def test_class_var_dec(self):
        expected = {
            'test': {
                'type': 'boolean',
                'kind': 'static',
                'number': 0
            }
        }
        actual = symbolize(self.class_var_dec)
        self.assertEqual(
            actual,
            expected,
        )
