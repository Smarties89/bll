from plex import Lexicon, TEXT, IGNORE, Range, Rep, Str, AnyBut, Rep1, Any


letter = Range("AZaz")
digit = Range("09")
name = letter + Rep(letter | digit)
string = Str("\"") + Rep(AnyBut("\"")) + Str("\"")
number = Rep1(digit)
space = Any(" \t")
newline = Any("\n")
comment = Str("#") + Rep(AnyBut("\n")) + Str("\n")
resword = Str("on", "put", "output", "do")


lexicon = Lexicon([
    (resword,         TEXT),
    (name,            'ident'),
    (space | comment, IGNORE),
    (newline, 'newline'),
    (string, 'string'),
])
