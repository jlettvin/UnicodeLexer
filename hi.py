#!/usr/bin/env python

from antlr4 import *
from hiLexer import hiLexer
from hiListener import hiListener
from hiParser import hiParser

class hiPrintListener(hiListener):
    def enterHi(self, ctx):
        print "[PASS] original: %s" % (ctx.ID())

if __name__ == "__main__":

    def main():
        lexer = hiLexer(StdinStream())
        stream = CommonTokenStream(lexer)
        parser = hiParser(stream)
        tree = parser.prog()
        printer = hiPrintListener()
        walker = ParseTreeWalker()
        walker.walk(printer, tree)

    try:
        main()
    except Exception as e:
        print '[FAIL] ' + str(e)
