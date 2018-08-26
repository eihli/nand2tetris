# list        : '[' elements ']' ;
# elements    : element (',' element)* ;
# element     : NAME | list ;
# NAME        : ('a'..'z'|'A'..'Z') ;
from lip.list_lexer import ListLexer


def fmt(t):
    return "<'{}', {}>".format(t.text, ListLexer.get_token_name(t.type))


def main():
    sample = "[krogoth, kestrel, ktulu, krocodile]"
    lexer = ListLexer(sample)
    t = lexer.next_token()
    while t.type != ListLexer.EOF_TYPE:
        print(fmt(t))
        t = lexer.next_token()
    print(fmt(t))


if __name__ == "__main__":
    main()
