from lip.lexer import Lexer


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
                Lexer.token_names(x),
                Lexer.token_names(self.lookahead),
            )
            raise Exception(msg)
