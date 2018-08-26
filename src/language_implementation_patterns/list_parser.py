class ListParser:
    def __init__(self, input_):
        self.input = input_
        self.lookahead = None

    def consume(self):
        self.lookahead = self.input.next_token()

    def match(self, x):
        if self.lookahead.type == x:
            self.consume()
        else:
            msg = "Expecting {} found {}"
            raise Exception(msg)
