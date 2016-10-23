#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""hello.py
This module tests the hello1 grammar which imports the "classify" grammar.
"""

from antlr4         import *
from hello1Lexer    import (    hello1Lexer     )
from hello1Listener import (    hello1Listener  )
from hello1Parser   import (    hello1Parser    )

class hello1PrintListener(hello1Listener):
    def enterHello(self, ctx):
        print "[PASS] classify: %s" % (ctx.ID())

if __name__ == "__main__":

    def main():
        lexer = hello1Lexer(StdinStream(encoding="utf8"))
        stream = CommonTokenStream(lexer)
        parser = hello1Parser(stream)
        tree = parser.prog()
        printer = hello1PrintListener()
        walker = ParseTreeWalker()
        walker.walk(printer, tree)

    try:
        main()
    except Exception as e:
        print '[FAIL] ' + str(e)
