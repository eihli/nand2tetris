from lip.list_lexer import ListLexer
from lip.parser import Parser


def fmt(t):
    return "<'{}', {}>".format(t.text, ListLexer.get_token_name(t.type))


class ListParser(Parser):
    def __init__(self, lexer):
        super().__init__(lexer)

    def list(self):
        self.match(ListLexer.OPEN_BRACKET)
        self.elements()
        self.match(ListLexer.CLOSE_BRACKET)

    def elements(self):
        self.element()
        while self.lookahead.type == ListLexer.COMMA:
            self.match(ListLexer.COMMA)
            self.element()

    def element(self):
        if self.lookahead.type == ListLexer.NAME:
            self.match(ListLexer.NAME)
        elif self.lookahead.type == ListLexer.OPEN_BRACKET:
            self.list()
        else:
            fmt_str = "Expecting name or list. Found {}"
            msg = fmt_str.format(fmt(self.lookahead))
            raise Exception(msg)


def test():
    input_str = '[a, b]'
    lexer = ListLexer(input_str)
    parser = ListParser(lexer)
    parser.list()
