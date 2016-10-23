#!/usr/bin/env make
# Makefile for "classify" grammar generator and tests
# Version 0.0.1
#
# Author: Jonathan D. Lettvin (jlettvin@gmail.com)
# Date:   20161023
# Legal:  Copyright(c) Jonathan D. Lettvin, All Rights Reserved
# License:GPL 3.0"""
#
# Usage:
# 	  make [all]				Download resources, Generate grammar, Test
# 	  make test					Run simple generator internal tests
# 	  make clean				Remove temporary and unnecessary files
#     make help					Display this text
#     make version				Display version of this Makefile

MANIFEST= \
	MANIFEST Makefile README.md \
	classify.py classify.g4 \
	hello.py hello.g4 hi.py hi.g4 \
	2001 \
	2001/codepoint.py \
	2001/xml.htm 2001/xmlextern.htm 2001/xmlmacro.htm 2001/xmlstatc.htm

FTP=ftp://ftp.unicode.org/Public/

SOURCES= 						\
	UnicodeData.txt 			\
	Blocks.txt 					\
	PropertyValueAliases.txt 	\
    UnicodeData-3.0.0.html

GRAMMARS= 		\
	classify.g4 \
	hello.g4 	\
	hi.g4

TARGETS= 									\
	hi.tokens			hello.tokens 		\
	hiLexer.py			helloLexer.py 		\
	hiLexer.tokens		helloLexer.tokens 	\
	hiListener.py		helloListener.py 	\
	hiParser.py			helloParser.py 		\
	hiVisitor.py		helloVisitor.py

antlr4=java -jar /usr/local/lib/antlr-4.5.3-complete.jar

all: hi.tokens hello.tokens
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
	# Try: @ls -1 | sort MANIFEST MANIFEST - | uniq -u | xargs rm -f
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
