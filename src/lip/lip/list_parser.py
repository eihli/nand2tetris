from lip.lexer import Lexer
from lip.parser import Parser


def fmt(t):
    return "<'{}', {}>".format(t.text, Lexer.token_names(t.type))


class ListParser(Parser):
    def __init__(self, lexer):
        super().__init__(lexer)

    def list(self):
        self.match(Lexer.OPEN_BRACKET)
        self.elements()
        self.match(Lexer.CLOSE_BRACKET)

    def elements(self):
        self.element()
        while self.lookahead.type == Lexer.COMMA:
            self.match(Lexer.COMMA)
            self.element()

    def element(self):
        if self.lookahead.type == Lexer.NAME:
            self.match(Lexer.NAME)
        elif self.lookahead.type == Lexer.OPEN_BRACKET:
            self.list()
        else:
            fmt_str = "Expecting name or list. Found {}"
            msg = fmt_str.format(fmt(self.lookahead))
            raise Exception(msg)


def test():
    input_str = '[a, ]'
    lexer = Lexer(input_str)
    parser = ListParser(lexer)
    parser.list()
