from lip.list_lexer import ListLexer


class Parser:
    def __init__(self, lexer):
        self.lexer = lexer
        self.lookahead = self.lexer.next_token()

    def consume(self):
        self.lookahead = self.lexer.next_token()

    def match(self, x):
        if self.lookahead.type == x:
            self.consume()
        else:
            template = "Expecting {} found {}"
            msg = template.format(
                ListLexer.token_names(x),
                ListLexer.get_token_name(x.type),
            )
            raise Exception(msg)
