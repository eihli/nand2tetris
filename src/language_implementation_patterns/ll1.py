import re

# list        : '[' elements ']' ;
# elements    : element (',' element)* ;
# element     : NAME | list ;
# NAME        : ('a'..'z'|'A'..'Z') ;


class Token:
    def __init__(self, type_, text):
        self.type = type_
        self.text = text

    def __str__(self):
        return "<'{}', {}>".format(self.text, Lexer.token_names(self.type))


class Parser:
    pass


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


class Grammar(Parser):
    """
    Token type definitions
    Rule methods
    """
    def list():
        pass

    def elements():
        pass

    def element():
        pass


def main():
    sample = "[krogoth, kestrel, ktulu, krocodile]"
    lexer = Lexer(sample)
    t = lexer.next_token()
    while t.type != Lexer.EOF:
        print(t)
        t = lexer.next_token()
    print(t)


if __name__ == "__main__":
    main()
