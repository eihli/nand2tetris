import io
import os
import unittest as ut
import xml.etree.ElementTree as ET

import compiler as cp


class TestSquareSxml(ut.TestCase):
    @property
    def node(self):
        return cp.el_to_node(self.el)

    def setUp(self):
        fn = os.path.expanduser(
            '~/code/nand2tetris/src/jack_analyzer/Square.sxml'
        )
        with open(fn) as f:
            self.el = ET.fromstring(f.read())
        self.stream = io.StringIO()
        self.generator = cp.CodeGenerator(self.stream)


class TestClassVarDec(TestSquareSxml):
    def setUp(self):
        super(TestClassVarDec, self).setUp()
        self.el = next(e for e in self.el if e.tag == 'classVarDec')

    def test_class_var_dec(self):
        self.generator.generate(self.node)
        self.assertEqual(
            self.generator.sym_tab.x['kind'],
            'field'
        )


class TestSubroutineDec(TestSquareSxml):
    def setUp(self):
        super(TestSubroutineDec, self).setUp()
        self.class_var_decs = [e for e in self.el if e.tag == 'classVarDec']
        for cvd in self.class_var_decs:
            self.generator.generate(cp.el_to_node(cvd))
        self.el = next(e for e in self.el if e.tag == 'subroutineDec')

    def test_subroutine_dec(self):
        self.generator.generate(self.node)
        self.assertEqual(
            self.stream.getvalue(),
            '\n'.join([
                'function Square.new 3',
                'push 3',
                'call Memory.alloc 1',
                'pop pointer 0',
                'push argument 0',
                'pop this 0',
                'push argument 1',
                'pop this 1',
                'push argument 2',
                'pop this 2',
                'call draw 0',
                'push pointer 0\n',
            ])
        )

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
                'String.appendChar 2\n',
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
            '<term>',
            '<integerConstant> 8 </integerConstant>',
            '</term>',
            '<symbol> * </symbol>',
            '<term>',
            '<integerConstant> 5 </integerConstant>',
            '</term>',
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

    def test_term(self):
        src = '\n'.join([
            '<term>',
            '<integerConstant> 5 </integerConstant>',
            '</term>',
        ])
        el = ET.fromstring(src)
        node = cp.el_to_node(el)
        self.generator.generate(node)
        self.assertEqual(
            self.stream.getvalue(),
            'push constant 5\n',
        )

    def test_let(self):
        src = '\n'.join([
            '<letStatement>',
            '<keyword> let </keyword>',
            '<identifier> s </identifier>',
            '<symbol> = </symbol>',
            '<expression>',
            '<term>',
            '<keyword> null </keyword>',
            '</term>',
            '</expression>',
            '<symbol> ; </symbol>',
            '</letStatement>',
        ])
        el = ET.fromstring(src)
        node = cp.el_to_node(el)
        self.generator.sym_tab.mth = {
            's': {
                'kind': 'static',
                'number': '2',
            }
        }
        self.generator.generate(node)
        self.assertEqual(
            self.stream.getvalue(),
            '\n'.join([
                'push constant 0',
                'pop static 2\n',
            ])
        )

    def test_let_array(self):
        src = '\n'.join([
            '<letStatement>',
            '<keyword> let </keyword>',
            '<identifier> s </identifier>',
            '<symbol> [ </symbol>',
            '<expression>',
            '<term>',
            '<integerConstant> 19 </integerConstant>',
            '</term>',
            '</expression>',
            '<symbol> = </symbol>',
            '<expression>',
            '<term>',
            '<keyword> null </keyword>',
            '</term>',
            '</expression>',
            '<symbol> ; </symbol>',
            '</letStatement>',
        ])
        el = ET.fromstring(src)
        node = cp.el_to_node(el)
        self.generator.sym_tab.mth = {
            's': {
                'kind': 'local',
                'number': '2',
            }
        }
        self.generator.generate(node)
        self.assertEqual(
            self.stream.getvalue(),
            '\n'.join([
                'push local 2',
                'push constant 19',
                'add',
                'pop pointer 1',
                'push constant 0',
                'pop that 0\n',
            ])
        )


class TestFoo(ut.TestCase):
    def setUp(self):
        self.stream = io.StringIO()
        self.generator = cp.CodeGenerator(self.stream)

    def test_subroutine_call(self):
        src = '\n'.join([
            '<expression>',
            '<term>',
            '<identifier> SquareGame </identifier>',
            '<symbol> . </symbol>',
            '<identifier> new </identifier>',
            '<symbol> ( </symbol>',
            '<expressionList>',
            '<expression>',
            '<term>',
            '<integerConstant> 0 </integerConstant>',
            '</term>',
            '</expression>',
            '</expressionList>',
            '<symbol> ) </symbol>',
            '</term>',
            '</expression>',
        ])
        et = ET.fromstring(src)
        node = cp.el_to_node(et)
        self.generator.generate(node)
        self.assertEqual(
            self.stream.getvalue(),
            '\n'.join([
                'push constant 0',
                'call SquareGame.new 1\n',
            ])
        )
