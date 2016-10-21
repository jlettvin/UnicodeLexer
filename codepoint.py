#!/usr/bin/env python
# -*- coding: utf8 -*-

"""
http://unicodebook.readthedocs.io/unicode_encodings.html

TODO: Put in guards against
1) buffer index out-of-bounds
2) surrogate value out of bounds on UTF16
"""

def modulate(p):
    """
    p is a list of (value,length) pairs.
    Return the concatenation of comprehensions formed from extents of values.
    """
    return sum([[v] * n for v, n in p], [])

def pepper(a, b, I):
    """
    Make a full extent of value a.
    Return that extent with substitution of value b for every index in I.
    """
    r = [a] * 128
    for i in I:
        r[i] = b
    return r

def stripes(a, b, sn):
    """
    Make a full extent of value a.
    Return that extent with substituion of value b in ranges specified in sn.
    """
    r = [a] * 128
    for s, n in sn:
        for i in range(s,n):
            r[i] = b
    return r

def constant(f):
    """
    Decorate BAD constants in XMLUnicode.
    """
    def fset(self, value):
        raise TypeError
    def fget(self):
        return f()
    return property(fget, fset)

class XMLUnicode(object):
    """
    """

    class BAD(object):
        "These constants mark bad unicode values in the XMLTypeTable."
        @constant
        def OOB(): return 0x00202000  # UNREACHABLE TABLE ENTRY (OUT OF BOUNDS)
        @constant
        def BOS(): return 0x00201000  # OUT-OF-RANGE: BEFORE BEGINNING OF STRING
        @constant
        def EOS(): return 0x00200800  # OUT-OF-RANGE: AFTER        END OF STRING
        @constant
        def BTS(): return 0x00200400  # BAD TRAIL BYTE INDEXED 2 FROM RIGHT END (S)
        @constant
        def BT2(): return 0x00200200  # BAD TRAIL BYTE INDEXED 2 FROM RIGHT END
        @constant
        def BT1(): return 0x00200100  # BAD TRAIL BYTE INDEXED 1 FROM RIGHT END
        @constant
        def BT0(): return 0x00200080  # BAD TRAIL BYTE INDEXED 0 FROM RIGHT END
        @constant
        def BL4(): return 0x00200040  # BAD LEAD BYTE FOR 4 BYTE ENCODING
        @constant
        def BL3(): return 0x00200020  # BAD LEAD BYTE FOR 3 BYTE ENCODING
        @constant
        def BL2(): return 0x00200010  # BAD LEAD BYTE FOR 2 BYTE ENCODING
        @constant
        def BAD(): return 0x00200008  # BAD LEAD BYTE (TOO HIGH)
        @constant
        def ILL(): return 0x00200004  # ILLEGAL UNICODE VALUE ENCODED
        @constant
        def END(): return 0x00200002  # WON'T START AT END OF STRING
        @constant
        def BAK(): return 0x00200001  # WON'T START IN MIDDLE OF UTF8 ENCODING
        @constant
        def ERR(): return 0x00200000  # UNIVERSAL ERROR BIT USED IN ALL ERRORS
        @constant
        def MAX(): return 0x0010FFFF  # MAXIMUM ENCODABLE VALUE (not an error)

    # first 4 bytes of stream identifies its UTF type.
    XMLIdentifyUTF = {
        "\x00\x00\x00\x00":  [ 0, 4, 4, 0, "Bad Stream"               ],
        "\xfe\xff\x3c\x00":  [ 1, 4, 4, 2, "UTF16 +BOM standard"      ],
        "\xff\xfe\x00\x3c":  [ 2, 4, 4, 2, "UTF16 +BOM swapped"       ],
        "\x3c\x00\x3f\x00":  [ 3, 4, 4, 0, "UTF16 -BOM standard"      ],
        "\x00\x3c\x00\x3f":  [ 4, 4, 4, 0, "UTF16 -BOM swapped"       ],
        "\x3c\x00\x00\x00":  [ 5, 4, 4, 0, "UTF32 -BOM 1234 standard" ],
        "\x00\x3c\x00\x00":  [ 6, 4, 4, 0, "UTF32 -BOM 3412"          ],
        "\x00\x00\x3c\x00":  [ 7, 4, 4, 0, "UTF32 -BOM 2143"          ],
        "\x00\x00\x00\x3c":  [ 8, 4, 4, 0, "UTF32 -BOM 4321"          ],
        "\xff\xfe\x00\x00":  [ 9 ,4, 4, 4, "UTF32 +BOM 1234 standard" ],
        "\x00\x00\xfe\xff":  [ 10,4, 4, 4, "UTF32 +BOM 4321"          ],
        #define UTF8_STREAM 11
        "\x3c\x3f\x78\x6d":  [ 11,4, 0, 0, "UTF8  -BOM standard"      ],
        "\xef\xbb\xbf\x3c":  [ 12,4, 0, 3, "UTF8  +BOM standard"      ]
        # ASCII is forced to be identified as UTF8 without consequence.
        #define ASCIISTREAM 13
        #,"\x3c\x3f\x78\x6d":  [ 13,4, 0, 0, "ASCII -BOM standard"      ]
    }

    # Character classification in ASCII
    # Order of names corresponds to numbered TYPE table entries
    # They also correspond to the third output of index/shift by function
    # identify_codepoint_type which gets values from XMLTypeTable
    # CAUTION: delete/insert/re-order at your peril.
    XML = [
        'UNUSED',       'ERROR',        'A-Za-z',       'BASECHAR',
        'IDEOGRAPHIC',  'NAMECHAR',     '0-9',          'DIGIT',
        'COMBINING',    'EXTENDER',     'TEXT',         'SPACE',
        'PUNCT',        'BOM',          'COLON',        'UNDERSCORE',
        'MINUS',        'DOT',          'BANG',         'DOUBLEQUOTE',
        'POUND',        'DOLLAR',       'PERCENT',      'AMPERSAND',
        'QUOTE',        'BACKSLASH',    'OPENPAREN',    'CLOSEPAREN',
        'STAR',         'PLUS',         'COMMA',        'SLASH',
        'SEMI',         'LESS',         'EQUALS',       'GREATER',
        'QUESTION',     'ATSIGN',       'OPENBRACKET',  'CLOSEBRACKET'
    ]

    # These TYPE numbers are hand-set in the tables
    TYPE = {number:name for number, name in enumerate(XML)}

    #**************************************************************************
    #* ZEROS to use for non-changing OR values */
    UTF8zeros = [0x00000000] * 256

    #**************************************************************************
    #* Lead byte starts with '10xxxxxx' pattern.  Backup. */
    UTF8backs = [BAD.BAK] * 256

    #**************************************************************************
    #* Decoding failed */
    UTF8error = [BAD.BAD] * 256

    #**************************************************************************
    #* Lead byte starts with '0xxxxxxx' pattern.  ASCII. */
    UTF8ascii = sum([range(128), [BAD.OOB]*128], [])

    #**************************************************************************
    #* Absolute  last byte in multi-byte encoding. */
    UTF8last0 = sum([[BAD.BT0]*128, range(64), [BAD.BT0]*64], [])

    #**************************************************************************
    #* Second to last byte in multi-byte encoding. */
    UTF8last1 = sum([[BAD.BT1]*128, range(0,0x1000,0x40), [BAD.BT1]*64], [])

    #**************************************************************************
    #* Third  to last byte in multi-byte encoding. */
    UTF8last2 = sum([[BAD.BT2]*128, range(0,0x40000,0x1000), [BAD.BT2]*64], [])

    #**************************************************************************
    #* Third  to last byte in multi-byte encoding (SPECIAL). */
    UTF8lasts = sum([[BAD.BTS]*128, range(0,0x10000,0x1000), [BAD.BTS]*112], [])

    #**************************************************************************
    #* First byte of   two byte encoding '110xxxxx'. */
    UTF8lead2 = sum([[BAD.BL2]*224, range(0,0x800,0x40)], [])

    #**************************************************************************
    #* First byte of three byte encoding '1110xxxx'. */
    UTF8lead3 = sum([[BAD.BL3]*240, range(0,0x10000,0x1000)], [])

    #**************************************************************************
    #* First byte of  four byte encoding '11110xxx'. */
    UTF8lead4 = sum([[BAD.BL4]*248, range(0,0x200000,0x10000), [BAD.BL4]*3], [])

    #**************************************************************************
    # This table of tables is used to decoded UTF8 into a codepoint
    XMLTypeTable = [
        sum([[13,53,54,56], [10]*64, [1]*60], []), #* Table 0 */
        [ 1] * 256,
        [ 2] * 256,
        [ 3] * 256,
        [ 4] * 256,
        [ 5] * 256,
        [ 6] * 256,
        [ 7] * 256,
        [ 8] * 256,
        [ 9] * 256,
        [10] * 256,
        [11] * 256,
        [12] * 256,
        sum([ #* Table 13 */
            range(14,28), [10] * 4,
            range(28,37), [10] * 1,
            range(37,41), [10] * 1,
            range(41,44), [10] * 24,
            [3,44,45,46,10,47,48,49], [10] * 28, [50,51,52], [10] * 28],
            []),
        [ #* Table 14 */
             1, 1, 1, 1,  1, 1, 1, 1,  1,11,11, 1,  1,11, 1, 1,
             1, 1, 1, 1,  1, 1, 1, 1,  1, 1, 1, 1,  1, 1, 1, 1,
            11,18,19,20, 21,22,23,24, 26,27,28,29, 30,16,17,31,
             6, 6, 6, 6,  6, 6, 6, 6,  6, 6,14,32, 33,34,35,36,
            37, 2, 2, 2,  2, 2, 2, 2,  2, 2, 2, 2,  2, 2, 2, 2,
             2, 2, 2, 2,  2, 2, 2, 2,  2, 2, 2,37, 12,38,12,15,
            12, 2, 2, 2,  2, 2, 2, 2,  2, 2, 2, 2,  2, 2, 2, 2,
             2, 2, 2, 2,  2, 2, 2, 2,  2, 2, 2,12, 12,12,12, 1
        ],
        modulate([(10,55),(9,1),(10,8),(3,23),(10,1),(3,31),(10,1),(3,8)]), #* Table 15 */
        modulate([(3,50),(10,2),(3,11),(10,2),(3,8),(10,1),(3,53),(10,1)]), #* Table 16 */
        modulate([(3,68),(10,9),(3,36),(10,3),(3,2),(10,4),(3,6)]), #* Table 17 */
        modulate([(3,24),(10,56),(3,48)]), #* Table 18 */
        [ #* Table 19 */
             3, 3, 3, 3,  3, 3, 3, 3,  3, 3, 3, 3,  3, 3, 3, 3,
             3, 3, 3, 3,  3, 3, 3, 3,  3, 3, 3, 3,  3, 3, 3, 3,
             3, 3, 3, 3,  3, 3, 3, 3,  3,10,10,10, 10,10,10,10,
            10,10,10,10, 10,10,10,10, 10,10,10, 3,  3, 3, 3, 3,
             3, 3,10,10, 10,10,10,10, 10,10,10,10, 10,10,10,10,
             9, 9,10,10, 10,10,10,10, 10,10,10,10, 10,10,10,10,
            10,10,10,10, 10,10,10,10, 10,10,10,10, 10,10,10,10,
            10,10,10,10, 10,10,10,10, 10,10,10,10, 10,10,10,10
        ],
        stripes(8,10,[(70,26),(98,128)]),  #* Table 20 */
        [ #* Table 21 */
            10,10,10,10, 10,10, 3, 9,  3, 3, 3,10,  3,10, 3, 3,
             3, 3, 3, 3,  3, 3, 3, 3,  3, 3, 3, 3,  3, 3, 3, 3,
             3, 3,10, 3,  3, 3, 3, 3,  3, 3, 3, 3,  3, 3, 3, 3,
             3, 3, 3, 3,  3, 3, 3, 3,  3, 3, 3, 3,  3, 3, 3, 3,
             3, 3, 3, 3,  3, 3, 3, 3,  3, 3, 3, 3,  3, 3, 3,10,
             3, 3, 3, 3,  3, 3, 3,10, 10,10, 3,10,  3,10, 3,10,
             3,10, 3, 3,  3, 3, 3, 3,  3, 3, 3, 3,  3, 3, 3, 3,
             3, 3, 3, 3, 10,10,10,10, 10,10,10,10, 10,10,10,10
        ],
        pepper(3,10,[0,13,80,93]),  #* Table 22 */
        [ #* Table 23 */
             3, 3,10, 8,  8, 8, 8,10, 10,10,10,10, 10,10,10,10,
             3, 3, 3, 3,  3, 3, 3, 3,  3, 3, 3, 3,  3, 3, 3, 3,
             3, 3, 3, 3,  3, 3, 3, 3,  3, 3, 3, 3,  3, 3, 3, 3,
             3, 3, 3, 3,  3, 3, 3, 3,  3, 3, 3, 3,  3, 3, 3, 3,
             3, 3, 3, 3,  3,10,10, 3,  3,10,10, 3,  3,10,10,10,
             3, 3, 3, 3,  3, 3, 3, 3,  3, 3, 3, 3,  3, 3, 3, 3,
             3, 3, 3, 3,  3, 3, 3, 3,  3, 3, 3, 3, 10,10, 3, 3,
             3, 3, 3, 3,  3, 3,10,10,  3, 3,10,10, 10,10,10,10
        ],
        stripes(10,3,[(65,103),(113,128)]),  #* Table 24 */
        [ #* Table 25 */
             3, 3, 3, 3,  3, 3, 3,10, 10,10,10,10, 10,10,10,10,
            10, 8, 8, 8,  8, 8, 8, 8,  8, 8, 8, 8,  8, 8, 8, 8,
             8, 8,10, 8,  8, 8, 8, 8,  8, 8, 8, 8,  8, 8, 8, 8,
             8, 8, 8, 8,  8, 8, 8, 8,  8, 8,10, 8,  8, 8,10, 8,
            10, 8, 8,10,  8,10,10,10, 10,10,10,10, 10,10,10,10,
             3, 3, 3, 3,  3, 3, 3, 3,  3, 3, 3, 3,  3, 3, 3, 3,
             3, 3, 3, 3,  3, 3, 3, 3,  3, 3, 3,10, 10,10,10,10,
             3, 3, 3,10, 10,10,10,10, 10,10,10,10, 10,10,10,10
        ], [ #* Table 26 */
            10,10,10,10, 10,10,10,10, 10,10,10,10, 10,10,10,10,
            10,10,10,10, 10,10,10,10, 10,10,10,10, 10,10,10,10,
            10, 3, 3, 3,  3, 3, 3, 3,  3, 3, 3, 3,  3, 3, 3, 3,
             3, 3, 3, 3,  3, 3, 3, 3,  3, 3, 3,10, 10,10,10,10,
             9, 3, 3, 3,  3, 3, 3, 3,  3, 3, 3, 8,  8, 8, 8, 8,
             8, 8, 8,10, 10,10,10,10, 10,10,10,10, 10,10,10,10,
             7, 7, 7, 7,  7, 7, 7, 7,  7, 7,10,10, 10,10,10,10,
             8, 3, 3, 3,  3, 3, 3, 3,  3, 3, 3, 3,  3, 3, 3, 3
        ], [ #* Table 27 */
             3, 3, 3, 3,  3, 3, 3, 3,  3, 3, 3, 3,  3, 3, 3, 3,
             3, 3, 3, 3,  3, 3, 3, 3,  3, 3, 3, 3,  3, 3, 3, 3,
             3, 3, 3, 3,  3, 3, 3, 3,  3, 3, 3, 3,  3, 3, 3, 3,
             3, 3, 3, 3,  3, 3, 3, 3, 10,10, 3, 3,  3, 3, 3,10,
             3, 3, 3, 3,  3, 3, 3, 3,  3, 3, 3, 3,  3, 3, 3,10,
             3, 3, 3, 3, 10, 3, 8, 8,  8, 8, 8, 8,  8, 8, 8, 8,
             8, 8, 8, 8,  8, 3, 3, 8,  8,10, 8, 8,  8, 8,10,10,
             7, 7, 7, 7,  7, 7, 7, 7,  7, 7,10,10, 10,10,10,10
        ], [ #* Table 28 */
             1, 8, 8, 8, 10, 3, 3, 3,  3, 3, 3, 3,  3, 3, 3, 3,
             3, 3, 3, 3,  3, 3, 3, 3,  3, 3, 3, 3,  3, 3, 3, 3,
             3, 3, 3, 3,  3, 3, 3, 3,  3, 3, 3, 3,  3, 3, 3, 3,
             3, 3, 3, 3,  3, 3, 3, 3,  3, 3,10,10,  8, 3, 8, 8,
             8, 8, 8, 8,  8, 8, 8, 8,  8, 8, 8, 8,  8, 8,10,10,
            10, 8, 8, 8,  8,10,10,10,  3, 3, 3, 3,  3, 3, 3, 3,
             3, 3, 8, 8, 10,10, 7, 7,  7, 7, 7, 7,  7, 7, 7, 7,
            10,10,10,10, 10,10,10,10, 10,10,10,10, 10,10,10,10
        ], [ #* Table 29 */
            10, 8, 8, 8, 10, 3, 3, 3,  3, 3, 3, 3,  3,10,10, 3,
             3,10,10, 3,  3, 3, 3, 3,  3, 3, 3, 3,  3, 3, 3, 3,
             3, 3, 3, 3,  3, 3, 3, 3,  3,10, 3, 3,  3, 3, 3, 3,
             3,10, 3,10, 10,10, 3, 3,  3, 3,10,10,  8,10, 8, 8,
             8, 8, 8, 8,  8,10,10, 8,  8,10,10, 8,  8, 8,10,10,
            10,10,10,10, 10,10,10, 8, 10,10,10,10,  3, 3,10, 3,
             3, 3, 8, 8, 10,10, 7, 7,  7, 7, 7, 7,  7, 7, 7, 7,
             3, 3,10,10, 10,10,10,10, 10,10,10,10, 10,10,10,10
        ], [ #* Table 30 */
            10,10, 8,10, 10, 3, 3, 3,  3, 3, 3,10, 10,10,10, 3,
             3,10,10, 3,  3, 3, 3, 3,  3, 3, 3, 3,  3, 3, 3, 3,
             3, 3, 3, 3,  3, 3, 3, 3,  3,10, 3, 3,  3, 3, 3, 3,
             3,10, 3, 3, 10, 3, 3,10,  3, 3,10,10,  8,10, 8, 8,
             8, 8, 8,10, 10,10,10, 8,  8,10,10, 8,  8, 8,10,10,
            10,10,10,10, 10,10,10,10, 10, 3, 3, 3,  3,10, 3,10,
            10,10,10,10, 10,10, 7, 7,  7, 7, 7, 7,  7, 7, 7, 7,
             8, 8, 3, 3,  3,10,10,10, 10,10,10,10, 10,10,10,10
        ], [ #* Table 31 */
            10, 8, 8, 8, 10, 3, 3, 3,  3, 3, 3, 3, 10, 3,10, 3,
             3, 3,10, 3,  3, 3, 3, 3,  3, 3, 3, 3,  3, 3, 3, 3,
             3, 3, 3, 3,  3, 3, 3, 3,  3,10, 3, 3,  3, 3, 3, 3,
             3,10, 3, 3, 10, 3, 3, 3,  3, 3,10,10,  8, 3, 8, 8,
             8, 8, 8, 8,  8, 8,10, 8,  8, 8,10, 8,  8, 8,10,10,
            10,10,10,10, 10,10,10,10, 10,10,10,10, 10,10,10,10,
             3,10,10,10, 10,10, 7, 7,  7, 7, 7, 7,  7, 7, 7, 7,
            10,10,10,10, 10,10,10,10, 10,10,10,10, 10,10,10,10
        ], [ #* Table 32 */
            10, 8, 8, 8, 10, 3, 3, 3,  3, 3, 3, 3,  3,10,10, 3,
             3,10,10, 3,  3, 3, 3, 3,  3, 3, 3, 3,  3, 3, 3, 3,
             3, 3, 3, 3,  3, 3, 3, 3,  3,10, 3, 3,  3, 3, 3, 3,
             3,10, 3, 3, 10,10, 3, 3,  3, 3,10,10,  8, 3, 8, 8,
             8, 8, 8, 8, 10,10,10, 8,  8,10,10, 8,  8, 8,10,10,
            10,10,10,10, 10,10, 8, 8, 10,10,10,10,  3, 3,10, 3,
             3, 3,10,10, 10,10, 7, 7,  7, 7, 7, 7,  7, 7, 7, 7,
            10,10,10,10, 10,10,10,10, 10,10,10,10, 10,10,10,10
        ], [ #* Table 33 */
            10,10, 8, 8, 10, 3, 3, 3,  3, 3, 3,10, 10,10, 3, 3,
             3,10, 3, 3,  3, 3,10,10, 10, 3, 3,10,  3,10, 3, 3,
            10,10,10, 3,  3,10,10,10,  3, 3, 3,10, 10,10, 3, 3,
             3, 3, 3, 3,  3, 3,10, 3,  3, 3,10,10, 10,10, 8, 8,
             8, 8, 8,10, 10,10, 8, 8,  8,10, 8, 8,  8, 8,10,10,
            10,10,10,10, 10,10,10, 8, 10,10,10,10, 10,10,10,10,
            10,10,10,10, 10,10,10, 7,  7, 7, 7, 7,  7, 7, 7, 7,
            10,10,10,10, 10,10,10,10, 10,10,10,10, 10,10,10,10
        ], [ #* Table 34 */
            10, 8, 8, 8, 10, 3, 3, 3,  3, 3, 3, 3,  3,10, 3, 3,
             3,10, 3, 3,  3, 3, 3, 3,  3, 3, 3, 3,  3, 3, 3, 3,
             3, 3, 3, 3,  3, 3, 3, 3,  3,10, 3, 3,  3, 3, 3, 3,
             3, 3, 3, 3, 10, 3, 3, 3,  3, 3,10,10, 10,10, 8, 8,
             8, 8, 8, 8,  8,10, 8, 8,  8,10, 8, 8,  8, 8,10,10,
            10,10,10,10, 10, 8, 8,10, 10,10,10,10, 10,10,10,10,
             3, 3,10,10, 10,10, 7, 7,  7, 7, 7, 7,  7, 7, 7, 7,
            10,10,10,10, 10,10,10,10, 10,10,10,10, 10,10,10,10
        ], [ #* Table 35 */
            10,10, 8, 8, 10, 3, 3, 3,  3, 3, 3, 3,  3,10, 3, 3,
             3,10, 3, 3,  3, 3, 3, 3,  3, 3, 3, 3,  3, 3, 3, 3,
             3, 3, 3, 3,  3, 3, 3, 3,  3,10, 3, 3,  3, 3, 3, 3,
             3, 3, 3, 3, 10, 3, 3, 3,  3, 3,10,10, 10,10, 8, 8,
             8, 8, 8, 8,  8,10, 8, 8,  8,10, 8, 8,  8, 8,10,10,
            10,10,10,10, 10, 8, 8,10, 10,10,10,10, 10,10, 3,10,
             3, 3,10,10, 10,10, 7, 7,  7, 7, 7, 7,  7, 7, 7, 7,
            10,10,10,10, 10,10,10,10, 10,10,10,10, 10,10,10,10
        ], [ #* Table 36 */
            10,10, 8, 8, 10, 3, 3, 3,  3, 3, 3, 3,  3,10, 3, 3,
             3,10, 3, 3,  3, 3, 3, 3,  3, 3, 3, 3,  3, 3, 3, 3,
             3, 3, 3, 3,  3, 3, 3, 3,  3,10, 3, 3,  3, 3, 3, 3,
             3, 3, 3, 3,  3, 3, 3, 3,  3, 3,10,10, 10,10, 8, 8,
             8, 8, 8, 8, 10,10, 8, 8,  8,10, 8, 8,  8, 8,10,10,
            10,10,10,10, 10,10,10, 8, 10,10,10,10, 10,10,10,10,
             3, 3,10,10, 10,10, 7, 7,  7, 7, 7, 7,  7, 7, 7, 7,
            10,10,10,10, 10,10,10,10, 10,10,10,10, 10,10,10,10
        ], [ #* Table 37 */
             1, 3, 3, 3,  3, 3, 3, 3,  3, 3, 3, 3,  3, 3, 3, 3,
             3, 3, 3, 3,  3, 3, 3, 3,  3, 3, 3, 3,  3, 3, 3, 3,
             3, 3, 3, 3,  3, 3, 3, 3,  3, 3, 3, 3,  3, 3, 3,10,
             3, 8, 3, 3,  8, 8, 8, 8,  8, 8, 8,10, 10,10,10,10,
             3, 3, 3, 3,  3, 3, 9, 8,  8, 8, 8, 8,  8, 8, 8,10,
             7, 7, 7, 7,  7, 7, 7, 7,  7, 7,10,10, 10,10,10,10,
            10,10,10,10, 10,10,10,10, 10,10,10,10, 10,10,10,10,
            10,10,10,10, 10,10,10,10, 10,10,10,10, 10,10,10,10
        ], [ #* Table 38 */
            10, 3, 3,10,  3,10,10, 3,  3,10, 3,10, 10, 3,10,10,
            10,10,10,10,  3, 3, 3, 3, 10, 3, 3, 3,  3, 3, 3, 3,
            10, 3, 3, 3, 10, 3,10, 3, 10,10, 3, 3, 10, 3, 3,10,
             3, 8, 3, 3,  8, 8, 8, 8,  8, 8,10, 8,  8, 3,10,10,
             3, 3, 3, 3,  3,10, 9,10,  8, 8, 8, 8,  8, 8,10,10,
             7, 7, 7, 7,  7, 7, 7, 7,  7, 7,10,10, 10,10,10,10,
            10,10,10,10, 10,10,10,10, 10,10,10,10, 10,10,10,10,
            10,10,10,10, 10,10,10,10, 10,10,10,10, 10,10,10,10
        ], [ #* Table 39 */
            10,10,10,10, 10,10,10,10, 10,10,10,10, 10,10,10,10,
            10,10,10,10, 10,10,10,10,  8, 8,10,10, 10,10,10,10,
             7, 7, 7, 7,  7, 7, 7, 7,  7, 7,10,10, 10,10,10,10,
            10,10,10,10, 10, 8,10, 8, 10, 8,10,10, 10,10, 8, 8,
             3, 3, 3, 3,  3, 3, 3, 3, 10, 3, 3, 3,  3, 3, 3, 3,
             3, 3, 3, 3,  3, 3, 3, 3,  3, 3, 3, 3,  3, 3, 3, 3,
             3, 3, 3, 3,  3, 3, 3, 3,  3, 3,10,10, 10,10,10,10,
            10, 8, 8, 8,  8, 8, 8, 8,  8, 8, 8, 8,  8, 8, 8, 8
        ],
        modulate([(8,5),(10,1),(8,6),(10,4),(8,6),(10,1),(8,1),(10,1),(8,21),(10,3),(8,7),(10,1),(8,1),(10,70)]), #* Table 40 */
        [ #* Table 41 */
             1, 1, 1, 1,  1, 1, 1, 1,  1, 1, 1, 1,  1, 1, 1, 1,
             1, 1, 1, 1,  1, 1, 1, 1,  1, 1, 1, 1,  1, 1, 1, 1,
             3, 3, 3, 3,  3, 3, 3, 3,  3, 3, 3, 3,  3, 3, 3, 3,
             3, 3, 3, 3,  3, 3, 3, 3,  3, 3, 3, 3,  3, 3, 3, 3,
             3, 3, 3, 3,  3, 3,10,10, 10,10,10,10, 10,10,10,10,
             3, 3, 3, 3,  3, 3, 3, 3,  3, 3, 3, 3,  3, 3, 3, 3,
             3, 3, 3, 3,  3, 3, 3, 3,  3, 3, 3, 3,  3, 3, 3, 3,
             3, 3, 3, 3,  3, 3, 3,10, 10,10,10,10, 10,10,10,10
        ], [ #* Table 42 */
             3,10, 3, 3, 10, 3, 3, 3, 10, 3,10, 3,  3,10, 3, 3,
             3, 3, 3,10, 10,10,10,10, 10,10,10,10, 10,10,10,10,
            10,10,10,10, 10,10,10,10, 10,10,10,10, 10,10,10,10,
            10,10,10,10, 10,10,10,10, 10,10,10,10,  3,10, 3,10,
             3,10,10,10, 10,10,10,10, 10,10,10,10,  3,10, 3,10,
             3,10,10,10,  3, 3,10,10, 10, 3,10,10, 10,10,10, 3,
             3, 3,10, 3, 10, 3,10, 3, 10, 3,10,10, 10, 3, 3,10,
            10,10, 3, 3, 10, 3,10,10, 10,10,10,10, 10,10,10,10
        ], [ #* Table 43 */
            10,10,10,10, 10,10,10,10, 10,10,10,10, 10,10,10,10,
            10,10,10,10, 10,10,10,10, 10,10,10,10, 10,10, 3,10,
            10,10,10,10, 10,10,10,10,  3,10,10, 3, 10,10, 3, 3,
            10,10,10,10, 10,10,10, 3,  3,10, 3,10,  3, 3, 3, 3,
             3, 3, 3,10, 10,10,10,10, 10,10,10,10, 10,10,10,10,
            10,10,10,10, 10,10,10,10, 10,10,10,10, 10,10,10,10,
            10,10,10,10, 10,10,10,10, 10,10,10, 3, 10,10,10,10,
             3,10,10,10, 10,10,10,10, 10, 3,10,10, 10,10,10,10
        ],
        stripes(3,10,[(28,32),(122,128)]),                      #* Table 44 */
        pepper(3,10,[23,24,30,31,70,71,82,83,92,94,96,98,126,127]),  #* Table 45 */
        pepper(3,10,[53,61,63,64,65,69,77,78,79,84,85,92,93,94,95,109,110,111,112,113,117,125,126,127]),  #* Table 46 */
        modulate([(1,80),(8,13),(10,4),(8,1),(10,30)]),         #* Table 47 */
        modulate([(10,38),(3,1),(10,3),(3,2),(10,2),(3,1),(10,81)]), #* Table 48 */
        stripes(10,3,[(0,3),]),                                 #* Table 49 */
        modulate([(1,5),(9,1),(10,1),(4,1),(10,25),(4,9),(8,6),(10,1),(9,5),(10,11),(3,63)]), #* Table 50 */
        modulate([(3,21),(10,4),(8,2),(10,2),(9,2),(10,2),(3,90),(10,1),(9,3),(10,1)]), #* Table 51 */
        stripes(10,3,[(5,45),]),                                #* Table 52 */
        modulate([(10,28),(4,100)]),                            #* Table 53 */
        modulate([(4,63),(55,1),(10,24),(3,40)]),               #* Table 54 */
        modulate([(4,38),(10,90)]),                             #* Table 55 */
        modulate([(3,47),(57,1),(1,16),(10,61),(58,1),(10,1),(59,1)]), #* Table 56 */
        modulate([(3,36),(10,92)]),                             #* Table 57 */
        pepper(10,13,(127,)),                                   #* Table 58 */
        pepper(10,3,(126,127))                                  #* Table 59 */
    ]

    # STATIC STATIC STATIC STATIC STATIC STATIC STATIC STATIC STATIC STATIC 
    # _____________________________________________________________________
    @staticmethod
    def identify_codepoint_type(codepoint):
        codepoint = long(codepoint <= 0x10FFFF) * codepoint
        index = 0
        index = XMLUnicode.XMLTypeTable[index][(codepoint >> 14) & 0x7f]
        index = XMLUnicode.XMLTypeTable[index][(codepoint >>  7) & 0x7f]
        index = XMLUnicode.XMLTypeTable[index][(codepoint      ) & 0x7f]
        return index

    # STATIC STATIC STATIC STATIC STATIC STATIC STATIC STATIC STATIC STATIC 
    # _____________________________________________________________________
    @staticmethod
    def identify_ASCII_type(codepoint):
        return XMLUnicode.XMLTypeTable[14][codepoint]

    # STATIC STATIC STATIC STATIC STATIC STATIC STATIC STATIC STATIC STATIC 
    # _____________________________________________________________________
    @staticmethod
    def UTFstream(first):
        identify = XMLUnicode.XMLIdentifyUTF
        BOM = first[0:4]
        bad = "\x00\x00\x00\x00"
        stream = identify.get(BOM, XMLUnicode.XMLIdentifyUTF[bad])
        doc = stream[4]
        #print doc
        assert doc[0:3] == "UTF", "Unidentified stream type"
        length = int(doc[3:6].strip())
        return {
            8 :XMLUnicode.UTF8,
            16:XMLUnicode.UTF16,
            32:XMLUnicode.UTF32
            }.get(length, XMLUnicode.UTF0)

    # STATIC STATIC STATIC STATIC STATIC STATIC STATIC STATIC STATIC STATIC 
    # _____________________________________________________________________
    @staticmethod
    def show(buffer):
        identify = XMLUnicode.identify_codepoint_type
        print "hex    dec    \t'char'\tcl class"
        print '\n'.join([
                ('%06x %07d\t' % (codepoint, codepoint)) +
                "'" + unichr(codepoint) + "'\t" +
                ('%02d ' % (identify(codepoint))) +
                XMLUnicode.TYPE[identify(codepoint)]
                for codepoint in buffer
            ])

    # UTF UTF UTF UTF UTF UTF UTF UTF UTF UTF UTF UTF UTF UTF UTF UTF UTF UTF
    # _______________________________________________________________________
    class UTF(object):
        def __init__(self, stream, first):
            self.source = stream

    # UTF UTF UTF UTF UTF UTF UTF UTF UTF UTF UTF UTF UTF UTF UTF UTF UTF UTF
    # _______________________________________________________________________
    class UTF32(UTF):
        "TODO: implement"

        def __init__(self, stream, first):
            super(XMLUnicode.UTF32, self).__init__(stream, first)
            self.order = [ord(c)-'1' for c in first[11:15]]

        def __call__(self):
            for line in self.source:
                display(line)

    # UTF UTF UTF UTF UTF UTF UTF UTF UTF UTF UTF UTF UTF UTF UTF UTF UTF UTF
    # _______________________________________________________________________
    class UTF16(UTF):

        """
        In UTF-16, characters in ranges U+0000—U+D7FF and U+E000—U+FFFD are
        stored as a single 16 bits unit. Non-BMP characters (range
        U+10000—U+10FFFF) are stored as “surrogate pairs”, two 16 bits units:
        an high surrogate (in range U+D800—U+DBFF) followed by a low surrogate
        (in range U+DC00—U+DFFF). A lone surrogate character is invalid in
        UTF-16, surrogate characters are always written as pairs (high followed
        by low).
        """

        surrogate = [0xd800, 0xdc00, 0xe000]
        replacement = 0xfffd  # unicode replacement char

        def __init__(self, stream, first):
            super(XMLUnicode.UTF16, self).__init__(stream, first)
            self.order = [0, 1] if first[11:] == "standard" else [1, 0]

        def __call__(self):
            "TODO validate calculations below; likely wrong."
            codepoints = []
            surrogate = UTF16.surrogate
            base = 0x10000
            mask = 0x3ff
            for line in self.source:
                i = 0
                (a, b) = self.order
                while i < len(line):
                    o = line[i]
                    lo_surrogate = ((o & surrogate[a]) == surrogate[0])
                    p = line[i+int(lo_surrogate)]
                    hi_surrogate = ((p & surrogate[b]) == surrogate[1])
                    codepoint = UTF16.replacement 
                    if lo_surrogate:
                        if hi_surrogate:
                            codepoint = ((o << 10) & mask) + (p & mask) + base
                        i = i + int(hi_surrogate) + 1
                    else:
                        codepoint = o
                        i = i + 1
                    codepoints.append(codepoint)
            return codepoints

    # UTF UTF UTF UTF UTF UTF UTF UTF UTF UTF UTF UTF UTF UTF UTF UTF UTF UTF
    # _______________________________________________________________________
    class UTF8(UTF):

        def __init__(self, stream, first):
            super(XMLUnicode.UTF8, self).__init__(stream, first)
            # Describe how the byte handling table will be filled
            # shiftmask[i][0] is the range to be filled (exclusive of high value)
            # shiftmask[i][1] is the set of mask and shift values
            # The constructed table eliminates one type of branch point
            # when ingesting bytes
            shiftmasks = [
                [[0x00, 0x080], [[ 0, 0xff]                                    ]],
                [[0x80, 0x0c0], [[ 6, 0x1f], [ 0, 0x3f]                        ]],
                [[0xc0, 0x0f0], [[12, 0x0f], [ 6, 0x3f], [ 0, 0x3f]            ]],
                [[0xf0, 0x100], [[18, 0x07], [12, 0x3f], [ 6, 0x3f], [ 0, 0x3f]]]
            ]
            last = 0x0
            for shiftmask in shiftmasks:
                limit = shiftmask[0]
                assert(limit[0] == last)
                last = limit[1]
            assert last == 0x100, "shiftmasks must have 256 contiguous lists"
            # Initialize the table
            self.hibits = []
            # Fill the table based on the shiftmasks
            for shiftmask in shiftmasks:
                limit = shiftmask[0]
                pattern = shiftmask[1]
                for i in xrange(limit[0], limit[1]):
                    self.hibits.append(pattern)
            assert len(self.hibits) == 256, "table filling failed"

        def __call__(self):
            codepoints = []
            for line in self.source:
                line = line.rstrip()
                i = 0
                while i < len(line):
                    codepoint = 0
                    for shift, mask in self.hibits[ord(line[i])]:
                        o = ord(line[i])
                        codepoint += int(o & mask) << shift
                        i = i + 1
                    codepoints.append(codepoint)
            return codepoints

    # UTF UTF UTF UTF UTF UTF UTF UTF UTF UTF UTF UTF UTF UTF UTF UTF UTF UTF
    # _______________________________________________________________________
    class UTF0(object):
        def __init__(self, source, first):
            pass
        def __call__(self):
            print "Failed lexer"

# MAIN MAIN MAIN MAIN MAIN MAIN MAIN MAIN MAIN MAIN MAIN MAIN MAIN MAIN MAIN 
# __________________________________________________________________________
if __name__ == "__main__":
    import sys

    if len(sys.argv) == 1:
        XMLUnicode.show([ord(c) for c in u'I am 愚公移山'])
    else:
        for arg in sys.argv[1:]:
            with open(arg, "rb") as src:
                first = src.readline()
                XMLUnicode.show(XMLUnicode.UTFstream(first)(src, first)())
