UnicodeLexer
============

Two implementations are stored here;
one from 2001 and one from 2016.

## 1: All the files with ".htm" extensions.
Hand-written tables as ".htm" files
implemented as both HTML and C code
from 2001 with a very efficient
stream converter for all 13 stream types
(variants of ASCII, UTF8, UTF16, and UTF32)
codepoint classifier, and rudimentary
lexer/parser for a proposed XML tree builder.
This code persists for historical reasons
and to guide development of the new code.
A small correction to the classification tables
was made to xmlstatc.htm.

## 2: Automated Unicode codepoint classification ANTLR4 grammar writer.
Python code to convert authoritative unicode.org resource files into
a complete and commented grammar suitable for import into other grammars.
Similar tables are built within the python code for local testing.
This code is new to 2016, and supersedes the 2001 code.

TODO: Finish classification table in Python
which may outperform other implementations
including ANTLR4 grammar.

1: XML Unicode
==============
In XML 1.0 Unicode 3.0 was employed. Unicode characters are called "codepoints".
XML 1.0 has explicit rules for all allowed listed codepoints.

Separate Unicode streams:
Unicode is defined as encoding characters as 21 bits.
XML 1.0 streams potentially deliver these 21 bits in a countable number of variations.
Each variation is reconstructed into a reliable 21 bit codepoint.
The reconstruction is highly optimized for each variation on delivery.
XML streams begin with the four characters "&lt;xml".
These four characters may be packed as ASCII, UTF8, UTF16, or UTF32,
and are sufficient to uniquely identify most stream characteristics.
Within the first tag may be a final stream {disambiguator}
found in the root tag
  &lt;xml version="1.0" encoding="{disambiguator}"&gt;.
Rule 81 of the XML 1.0 specification discusses allowed disambiguators.

Three 7-bit codepoint fragments:
Reconstructed codepoints are refragmented into three 7-bit indices.
All codepoints descend through a 3 layer table with these indices.
This descent causes discovery of all possible codepoint error states.
This descent causes discovery of all possible information relevant to lexer rules.
This includes codepoint candidacy for membership in an identifier, operator, or other token type.

Codepoint flags:
Codepoints are stored as 32-bit unsigned integers.
11 bits are available for flag information.
These 11 bits are filled during table descent in the previous step.

Lexer rules:
The lexer is always in a state.
When a codepoint is submitted to the lexer it can remain in that state or change to another state.
The possible state transitions are ordered according to probability.
The flags of the codepoint are used to identify the state change to make.

2: classify.py
==============
Requirements:
* antlr4
* wget

The Makefile performs several important functions.
* Fetch/refresh local copies of unicode.org resource files
** UnicodeData.txt (primary data for legal codepoint values)
** UnicodeData-3.0.0.html (column names for UnicodeData.txt)
** Blocks.txt (classification abbreviations for blocks of codepoints)
** PropertyValueAliases.txt (classification names for blocks)
* Extract data from resource files and construct grammars
* Test grammars by submission to ANTLR4

The resulting grammars include:
* classify.g4 (grammar identifying all legal codepoint classifications)
* wiki.g4 (grammar which imports classify.g4)
