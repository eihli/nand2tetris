import re

from token import Token


class EOF:
    pass


class Lexer:
    EOF = -1
    INVALID_TOKEN_TYPE = 0
    NAME = 1
    OPEN_BRACKET = 2
    CLOSE_BRACKET = 3
    COMMA = 4

    def __init__(self, input_):
        self.input = input_
        self.p = 0
        self.char = self.input[self.p]

    @staticmethod
    def token_names(type_):
        return {
            Lexer.EOF: "<EOF>",
            Lexer.INVALID_TOKEN_TYPE: "n/a",
            Lexer.NAME: "NAME",
            Lexer.OPEN_BRACKET: "OPEN_BRACKET",
            Lexer.CLOSE_BRACKET: "CLOSE_BRACKET",
            Lexer.COMMA: "COMMA",
        }[type_]

    def consume(self):
        self.p += 1
        if self.p == len(self.input):
            self.char = EOF
        else:
            self.char = self.input[self.p]

    def next_token(self):
        while self.char != EOF:
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
        return Token(self.EOF, "<EOF>")

    def name(self):
        name = self.char
        self.consume()
        while re.match(r'[a-zA-Z]', self.char):
            name += self.char
            self.consume()
        return Token(self.NAME, name)
