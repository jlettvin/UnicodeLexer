#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""hello.py
This module tests the hello0 grammar an ASCII-only grammar.
"""

from antlr4         import *
from hello0Lexer    import (    hello0Lexer     )
from hello0Listener import (    hello0Listener  )
from hello0Parser   import (    hello0Parser    )

class hello0PrintListener(hello0Listener):
    def enterHello(self, ctx):
        print "[PASS] original: %s" % (ctx.ID())

if __name__ == "__main__":

    def main():
        lexer = hello0Lexer(StdinStream(encoding="utf8"))
        stream = CommonTokenStream(lexer)
        parser = hello0Parser(stream)
        tree = parser.prog()
        printer = hello0PrintListener()
        walker = ParseTreeWalker()
        walker.walk(printer, tree)

    try:
        main()
    except Exception as e:
        print '[FAIL] ' + str(e)
