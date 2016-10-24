#!/usr/bin/env make
# Makefile for "classify" grammar generator and tests
# Version 0.0.2
#
# Author    : Jonathan D. Lettvin (jlettvin@gmail.com)
# Date      : 20161023
# Legal     : Copyright(c) Jonathan D. Lettvin, All Rights Reserved
# License   : GPL 3.0
#
# Usage:
#     make [all]        Download resources, Generate grammar, Test
#     make test         Run simple generator internal tests
#     make clean        Remove temporary and unnecessary files
#     make help         Display this text
#     make version      Display version of this Makefile
#
# Description: See README.md

MANIFEST=                                   \
	MANIFEST Makefile README.md             \
	classify.py classify16.g4 classify21.g4 \
	hello1.py hello1.g4 hello0.py hello0.g4 \
	2001                                    \
	2001/codepoint.py                       \
	2001/xml.htm 2001/xmlextern.htm 2001/xmlmacro.htm 2001/xmlstatc.htm

FTP=ftp://ftp.unicode.org/Public/

SOURCES=                        \
	UnicodeData.txt             \
	Blocks.txt                  \
	PropertyValueAliases.txt    \
	UnicodeData-3.0.0.html

GRAMMARS=                                       \
	classify16.g4           classify21.g4       \
	hello0.g4               hello1.g4

TARGETS=                                        \
	hello0.tokens           hello1.tokens       \
	hello0Lexer.py          hello1Lexer.py      \
	hello0Lexer.tokens      hello1Lexer.tokens  \
	hello0Listener.py       hello1Listener.py   \
	hello0Parser.py         hello1Parser.py     \
	hello0Visitor.py        hello1Visitor.py

antlr4=java -jar /usr/local/lib/antlr-4.5.3-complete.jar

all: hello0.tokens hello0.tokens hello1.tokens
	@echo "make finished.  Creating MANIFEST"

.PHONY:
help:
	@cat Makefile|grep "^#"|cut -c3-|grep -v "/usr/bin/env"

.PHONY:
version:
	@echo "Makefile `cat Makefile|grep '^#'|cut -c3-|grep 'Version'`"
	@echo "classify Version `grep 'docopt.*vers' classify.py |cut -d'\"' -f 2`"

.PHONY:
test: $(GRAMMARS)
	./classify.py -u

.PHONY:
clean:
	@echo $@
	@rm -f MANIFEST
	@$(foreach item, $(MANIFEST), echo $(item) >> MANIFEST;)
	@echo "Try: @ls -1 | sort MANIFEST MANIFEST - | uniq -u | xargs rm -f"
	@rm -f $(SOURCES) $(TARGETS) *.pyc

.PHONY:
UnicodeData.txt:
	@echo $@
	@wget -q -c -N $(FTP)UCD/latest/ucd/$@

.PHONY:
Blocks.txt:
	@echo $@
	@wget -q -c -N $(FTP)UCD/latest/ucd/$@

.PHONY:
PropertyValueAliases.txt:
	@echo $@
	@wget -q -c -N $(FTP)UCD/latest/ucd/$@

.PHONY:
UnicodeData-3.0.0.html:
	@echo $@
	@wget -q -c -N $(FTP)3.0-Update/$@

hello0.tokens: $(GRAMMARS) hello0.py Makefile
	@echo $@
	@$(antlr4) -Dlanguage=Python2 -visitor hello0.g4
	@echo "Test ordinary lexer"
	@echo "hello original\nhello 愚公移山"   | ./hello0.py

hello1.tokens: $(GRAMMARS) hello1.py Makefile
	@echo $@
	@$(antlr4) -Dlanguage=Python2 -visitor hello1.g4
	@echo "Test classify lexer"
	@echo "hello classify\nhello 愚公移山"   | ./hello1.py

classify16.g4 classify21.g4 hello1.g4: classify.py $(SOURCES) Makefile
	@echo "$@"
	@echo "produce both 16 bit (ANTLR) and 21 bit (full21bit) grammars"
	@./classify.py --zeroerror --enhance
	@./classify.py --zeroerror --enhance --full21bit
