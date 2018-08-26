# list        : '[' elements ']' ;
# elements    : element (',' element)* ;
# element     : NAME | list ;
# NAME        : ('a'..'z'|'A'..'Z') ;
from lexer import Lexer


def fmt(t):
    return "<'{}', {}>".format(t.text, Lexer.token_names(t.type))


def main():
    sample = "[krogoth, kestrel, ktulu, krocodile]"
    lexer = Lexer(sample)
    t = lexer.next_token()
    while t.type != Lexer.EOF:
        print(fmt(t))
        t = lexer.next_token()
    print(fmt(t))


if __name__ == "__main__":
    main()
