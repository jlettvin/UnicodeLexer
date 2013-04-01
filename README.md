UnicodeLexer
============

C code from 2001 implementing a very efficient Universal XML Unicode stream converter


XML Unicode:
In XML 1.0 Unicode 3.0 was employed. Unicode characters are called "codepoints".
XML 1.0 has explicit rules for all allowed listed codepoints.

Separate Unicode streams:
Unicode is defined as encoding characters as 21 bits.
XML 1.0 streams potentially deliver these 21 bits in a countable number of variations.
Each variation is reconstructed into a reliable 21 bit codepoint.
The reconstruction is highly optimized for each variation on delivery.
XML streams begin with the four characters "<xml".
These four characters may be packed as ASCII, UTF8, UTF16, or UTF32,
and are sufficient to uniquely identify most stream characteristics.
Within the first tag may be a final stream {disambiguator} found in the root tag
<xml version="1.0" encoding="{disambiguator}">.
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
