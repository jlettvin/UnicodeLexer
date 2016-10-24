#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""hello.py
This module tests the hello0 grammar an ASCII-only grammar.
"""

from antlr4                     import *
from hello0Lexer                import (    hello0Lexer     )
from hello0Listener             import (    hello0Listener  )
from hello0Parser               import (    hello0Parser    )

"""
from anltr4.error.ErrorListener import (    ErrorListener   )

class hello0ErrorListener(ErrorListener):
    def __init__(self):
        super(hello0ErrorListener, self).__init__()

    def syntaxError(self, recognizer, offendingSymbol, line, col, msg, e):
        raise Exception(offendingSymbol)
"""

class hello0PrintListener(hello0Listener):

    def enterHello(self, ctx):
        print "[PASS] original: %s" % (ctx.ID())

    # Can't work.  No codepoint
    #def enterCodepoint(self, ctx):
        #print "[FAIL] classify: %s" % (ctx.ID())


if __name__ == "__main__":

    def main():
        lexer = hello0Lexer(StdinStream(encoding="utf8"))
        stream = CommonTokenStream(lexer)
        parser = hello0Parser(stream)
        # parser._listeners = [ hello0ErrorListener() ]
        tree = parser.prog()
        printer = hello0PrintListener()
        walker = ParseTreeWalker()
        walker.walk(printer, tree)

    try:
        main()
    except Exception as e:
        print '[FAIL] ' + str(e)
