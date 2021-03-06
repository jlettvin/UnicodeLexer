UnicodeLexer
============

Two implementations are stored here;
one from 2016 and one from 2001.

0: Highlights
=============
ANTLR4:
```
| ----------------- | --------------------------------------------------- |
| FILE              | CONTENTS                                            |
| ----------------- | --------------------------------------------------- |
| classify16.g4     | ANTLR4 import grammar for codepoint classification  |
| classify21.g4     | 21 bit import grammar for codepoint classification  |
| classify.py       | Code to generate classify*.g4                       |
| ----------------- | --------------------------------------------------- |
| hello0.g4         | Simple original g4 grammar for comparison test      |
| hello0.py         | Simple original g4 grammar test script              |
| ----------------- | --------------------------------------------------- |
| hello1.g4         | Simple classify g4 grammar for import testing       |
| hello1.py         | Simple classify g4 grammar test script              |
| ----------------- | --------------------------------------------------- |
| Makefile          | Script to download Unicode files, generate g4, test |
| README.md         | This file                                           |
| ----------------- | --------------------------------------------------- |
```

Historical:
```
| ----------------- | --------------------------------------------------- |
| FILE              | CONTENTS                                            |
| ----------------- | --------------------------------------------------- |
| 2001/codepoint.py | Hand-written modern update of tables                |
| 2001/xml.htm      | Root of historical lexer                            |
| 2001/xmlextrn.htm | External names of historical lexer                  |
| 2001/xmlmacro.htm | C macros implementing algorithms, historical lexer  |
| 2001/xmlstatc.htm | Hand-written tables used by historical lexer        |
| ----------------- | --------------------------------------------------- |
```

1: Codepoint classification grammar
===================================
2016 Automated Unicode codepoint classification ANTLR4 grammar writer.

Python code to convert authoritative unicode.org resource files into
a complete and commented grammar suitable for import into other grammars.
Similar tables are built within the python code for local testing.
This code is new to 2016, and supersedes the 2001 code.

TODO: Finish Python generation of classification table.
This compiled table (in .c or .js JIT) may outperform
other implementations including ANTLR4 grammar
possibly by an order of magnitude.


1.1: Makefile help
==================
```
$ make help
Makefile for "classify" grammar generator and tests
Version 0.0.2

Author    : Jonathan D. Lettvin (jlettvin@gmail.com)
Date      : 20161023
Legal     : Copyright(c) Jonathan D. Lettvin, All Rights Reserved
License   : GPL 3.0

Usage:
    make [all]        Download resources, Generate grammar, Test
    make test         Run simple generator internal tests
    make clean        Remove temporary and unnecessary files
    make help         Display this text
    make version      Display version of this Makefile

Description: See README.md
```

1.2: classify.py --help
=======================
```
$ ./classify.py --help
classify.py

Usage:
    classify.py [-acefktuz] [-v]
    classify.py (-h | --help)
    classify.py (--version)

Options:
    -a --showascii                  Show ASCII class/name
    -c --showcount                  Show key counts
    -e --enhance                    Add WS and ID rules
    -f --full21bit                  Express full 21 bit range 0 to 10FFFF
    -k --showkeys                   Show key names
    -t --showtables                 Show tables
    -u --unittest                   Run tests
    -z --zeroerror                  Use zero, not len as ERROR table index
    -v --verbose                    Show verbose output
    -h --help                       Show this Usage message
    --version                       Show version

Concepts:
    The authority for codepoint classification is unicode.org.
    One file (UnicodeData.txt) is the absolute authority.
    Each legal codepoint (Unicode character) is defined in its own line.
    Each line is semicolon separated and its columns are not labelled.
    A second file (UnicodeData-3.0.0) provides the correct column labels.
    It also provides Abbreviation Descriptions for each codepoint.

    Enhance (-e) causes additional rules to be moved
    from the file hello.g4 to the file classify.g4 where
    they can be imported into other grammars.

Author  : Jonathan D. Lettvin (jlettvin@gmail.com)
Date    : 20161023 
Legal   : Copyright(c) Jonathan D. Lettvin, All Rights Reserved
License : GPL 3.0
```

1.3: Instructions
=================
Quick:
* $ make clean
* $ make

Expect output of make to be:
```
UnicodeData.txt
Blocks.txt
PropertyValueAliases.txt
UnicodeData-3.0.0.html
classify16.g4
produce both 16 bit (ANTLR) and 21 bit (full21bit) grammars
hello0.tokens
Test ordinary lexer
line 2:6 token recognition error at: '愚'
line 2:7 token recognition error at: '公'
line 2:8 token recognition error at: '移'
line 2:9 token recognition error at: '山'
line 3:0 missing ID at '<EOF>'
[PASS] original: original
[PASS] original: <missing ID>
hello1.tokens
Test classify lexer
[PASS] classify: classify
[PASS] classify: 愚公移山
make finished.  Creating MANIFEST
```

Observe:
* The four unicode.org files are downoaded.
* The grammars are produced
* hello0 (the ASCII grammar) is executed with one PASS and one FAIL.
* hello1 (the class grammar) is executed with two PASSes
* A manifest of working files is produced

TODO: The [PASS] with &lt;missing ID&gt; is in error and needs correction.

Requirements:

command-line tools:
* antlr4
* wget

Python libraries:
* BeautifulSoup
* docopt

The Makefile performs several important functions.

Fetch/refresh local copies of unicode.org resource files:
* UnicodeData.txt (primary data for legal codepoint values)
* UnicodeData-3.0.0.html (column names for UnicodeData.txt)
* Blocks.txt (classification abbreviations for blocks of codepoints)
* PropertyValueAliases.txt (classification names for blocks)

Process:
* Extract data from resource files and construct grammars
* Test grammars by submission to ANTLR4

The resulting grammars include:
* classify*.g4 (grammars identifying all legal codepoint classifications)
* hello1.g4 (grammar which imports classify.g4)

In particular:
* classify16.g4 (16 bit unicode) is a limitation of ANTLR for java.
* classify21.g4 (21 bit unicode) is fully compliant with the unicode standard.

TODO: Finish generating a new independent classification table:
Once this internally constructed Table in classify.py is finished,
submitting a Unicode codepoint "u" to this lookup
yields the codepoint (character) class suitable for a lexer to use.
```
classification = Table[Table[Table[Base][(u>>14)&0x7f]][(u>>7)&0x7f]][u&0x7f]
```
This is approximately 11 Intel instructions in machine code:
* 2 shifts
* 3 masks
* 6 dereferences

The existing table performs well for all legal 21 bit unicode codepoints
but only classifies ASCII correctly.
When finished, operations and performance will be compared with
code generated by ANTLR4 and reported here.

2: old 2001 XML Unicode
=======================
2001 directory has all historical files with ".htm" extensions
and a Python script implementing the same tables for modern use.

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
