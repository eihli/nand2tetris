class Lexer:
    EOF_TYPE = 1

    class EOF_Char:
        pass

    def __init__(self, _input):
        self._input = _input
        self.p = 0
        self.char = self._input[self.p]

    def consume(self):
        self.p += 1
        if self.p == len(self._input):
            self.char = self.EOF_Char
        else:
            self.char = self._input[self.p]

    def match(self, x):
        if self.char == x:
            self.consume()
        else:
            fmt_str = "Expecting {}. Found {}."
            msg = fmt_str.format(x, self.char)
            raise Exception(msg)

    def next_token(self):
        raise NotImplementedError()

    def get_token_name(self):
        raise NotImplementedError()
