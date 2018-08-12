import io
import unittest as ut
import xml.etree.ElementTree as ET

import compiler as cp


class TestCompiler(ut.TestCase):
    def setUp(self):
        self.stream = io.StringIO()
        self.generator = cp.CodeGenerator(self.stream)

    def test_integer(self):
        src = '<integerConstant> 5 </integerConstant>'
        element = ET.fromstring(src)
        node = cp.el_to_node(element)
        self.generator.generate(node)
        self.assertEqual(self.stream.getvalue(), 'push constant 5\n')

    def test_string(self):
        src = '<stringConstant> fo </stringConstant>'
        el = ET.fromstring(src)
        node = cp.el_to_node(el)
        self.generator.generate(node)
        self.assertEqual(
            self.stream.getvalue(),
            '\n'.join([
                'push constant 2',
                'String.new 1',
                'push constant 102',
                'String.appendChar 2',
                'push constant 111',
                'String.appendChar 2',
            ])
        )

    def test_op(self):
        src = '<symbol> * </symbol>'
        el = ET.fromstring(src)
        node = cp.el_to_node(el)
        self.generator.generate(node)
        self.assertEqual(
            self.stream.getvalue(),
            'mult\n',
        )

    def test_expr(self):
        src = '\n'.join([
            '<expression>',
            '<integerConstant> 8 </integerConstant>',
            '<symbol> * </symbol>',
            '<integerConstant> 5 </integerConstant>',
            '</expression>',
        ])
        el = ET.fromstring(src)
        node = cp.el_to_node(el)
        self.generator.generate(node)
        self.assertEqual(
            self.stream.getvalue(),
            '\n'.join([
                'push constant 8',
                'push constant 5',
                'mult\n',
            ])
        )
