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
	wiki.g4

TARGETS= \
	wiki.tokens \
	wikiLexer.py \
	wikiLexer.tokens \
	wikiListener.py \
	wikiParser.py \
	wikiVisitor.py

all: wiki.tokens
	@echo "make finished"

.PHONY:
test: $(GRAMMARS)
	./classify.py -u

.PHONY:
clean:
	@echo $@
	@rm -f $(SOURCES) $(TARGETS)

.PHONY:
UnicodeData.txt: FORCE
	@echo $@
	@wget -q -c -N $(FTP)UCD/latest/ucd/$@

.PHONY:
Blocks.txt: FORCE
	@echo $@
	@wget -q -c -N $(FTP)UCD/latest/ucd/$@

.PHONY:
PropertyValueAliases.txt: FORCE
	@echo $@
	@wget -q -c -N $(FTP)UCD/latest/ucd/$@

.PHONY:
UnicodeData-3.0.0.html: FORCE
	@echo $@
	@wget -q -c -N $(FTP)3.0-Update/$@

FORCE:

wiki.tokens: $(GRAMMARS) Makefile
	@echo $@
	@$(antlr4) -Dlanguage=Python2 -visitor wiki.g4

classify.g4 wiki.g4: classify.py $(SOURCES) Makefile
	@echo $@
	@./classify.py --zeroerror --enhance
