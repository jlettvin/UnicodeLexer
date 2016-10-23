#!/usr/bin/env make
# Author: Jonathan D. Lettvin (jlettvin@gmail.com)
# Date:   20161023
# Legal:  Copyright(c) Jonathan D. Lettvin, All Rights Reserved
# License:GPL 3.0"""

antlr4=java -jar /usr/local/lib/antlr-4.5.3-complete.jar

FTP=ftp://ftp.unicode.org/Public/

SOURCES= \
	UnicodeData.txt \
	Blocks.txt \
	PropertyValueAliases.txt \
    UnicodeData-3.0.0.html

GRAMMARS= \
	classify.g4 \
	hello.g4 \
	hi.g4

TARGETS= \
	hi.tokens			hello.tokens \
	hiLexer.py			helloLexer.py \
	hiLexer.tokens		helloLexer.tokens \
	hiListener.py		helloListener.py \
	hiParser.py			helloParser.py \
	hiVisitor.py		helloVisitor.py

all: hi.tokens hello.tokens
	@echo "make finished"

.PHONY:
test: $(GRAMMARS)
	./classify.py -u

.PHONY:
clean:
	@echo $@
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

hi.tokens:
	@echo $@
	@$(antlr4) -Dlanguage=Python2 -visitor hi.g4
	@echo "Test ordinary lexer"
	@-echo "hello original" 	 | ./hi.py
	@-echo "hello 愚公移山" 	 | ./hi.py

hello.tokens: $(GRAMMARS) Makefile
	@echo $@
	@$(antlr4) -Dlanguage=Python2 -visitor hello.g4
	@echo "Test classify lexer"
	@-echo "hello classify" 	 | ./hello.py
	@-echo "hello 愚公移山" 	 | ./hello.py

classify.g4 hello.g4: classify.py $(SOURCES) Makefile
	@echo $@
	@./classify.py --zeroerror --enhance
