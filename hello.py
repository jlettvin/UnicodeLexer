#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""hello.py
This module tests the hello grammar which imports the "classify" grammar.
"""

from antlr4 import *
from helloLexer import helloLexer
from helloListener import helloListener
from helloParser import helloParser

class helloPrintListener(helloListener):
    def enterHi(self, ctx):
        print "[PASS] classify: %s" % (ctx.ID())

if __name__ == "__main__":

    def main():
        lexer = helloLexer(StdinStream())
        stream = CommonTokenStream(lexer)
        parser = helloParser(stream)
        tree = parser.prog()
        printer = helloPrintListener()
        walker = ParseTreeWalker()
        walker.walk(printer, tree)

    try:
        main()
    except Exception as e:
        print '[FAIL] ' + str(e)
