import re

from lip.lexer import Lexer
from lip.token import Token


class ListLexer(Lexer):
    NAME = 2
    OPEN_BRACKET = 3
    CLOSE_BRACKET = 4
    COMMA = 5
    TOKEN_NAMES = {
        Lexer.EOF_TYPE: "<EOF>",
        NAME: "NAME",
        OPEN_BRACKET: "OPEN_BRACKET",
        CLOSE_BRACKET: "CLOSE_BRACKET",
        COMMA: "COMMA",
    }

    def __init__(self, _input):
        super().__init__(_input)

    @classmethod
    def get_token_name(cls, _type):
        return cls.TOKEN_NAMES[_type]

    def next_token(self):
        while self.char != self.EOF_Char:
            if self.char in {' ', '\t', '\n', '\r'}:
                self.consume()
                continue
            elif self.char == ',':
                self.consume()
                return Token(self.COMMA, ',')
            elif self.char == '[':
                self.consume()
                return Token(self.OPEN_BRACKET, '[')
            elif self.char == ']':
                self.consume()
                return Token(self.CLOSE_BRACKET, ']')
            elif re.match(r'[a-zA-Z]', self.char):
                return self.name()
            else:
                raise Exception("invalid character: {}".format(self.char))
        return Token(self.EOF_TYPE, "<EOF>")

    def name(self):
        name = self.char
        self.consume()
        while re.match(r'[a-zA-Z]', self.char):
            name += self.char
            self.consume()
        return Token(self.NAME, name)
