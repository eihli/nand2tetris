class Token:
    def __init__(self, type_, text):
        self.type = type_
        self.text = text

    def __str__(self):
        return "<'{}', {}>".format(self.text, self.type)
