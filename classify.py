#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""classify.py

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
"""

__module__     = "classify.py"
__author__     = "Jonathan D. Lettvin"
__copyright__  = "\
Copyright(C) 2016 Jonathan D. Lettvin, All Rights Reserved"
__credits__    = [ "Jonathan D. Lettvin" ]
__license__    = "GPLv3"
__version__    = "0.0.2"
__maintainer__ = "Jonathan D. Lettvin"
__email__      = "jlettvin@gmail.com"
__contact__    = "jlettvin@gmail.com"
__status__     = "Demonstration"
__date__       = "20161022"

from re     import (sub)
from bs4    import (BeautifulSoup)
from urllib import (urlopen)
from pprint import (pprint)
from docopt import (docopt)

class Codepoint(dict):

    ###########################################################################
    ftp = "ftp://ftp.unicode.org/Public/"

    URI = {
        "meta": "UnicodeData-3.0.0.html",
        "name": "PropertyValueAliases.txt",
        "data": "UnicodeData.txt",
        "lang": "Blocks.txt"
    }

    columnManifest = {
        "Code value"        :  0,
        "Character name"    :  1,
        "General Category"  :  2,
        "Unicode 1.0 Name"  : 10
    }

    ###########################################################################
    def report(self, title, content):
        if self.verbose:
            print('    verbose: %s' % (title))
            pprint(content)

    def _columns(self):
        """
        Columns in UnicodeData.txt are undocumented within the file.
        This method reads column labels from UnicodeData-3.0.0.html
        """

        # Establish instance containers
        self.column = {}
        self.combinations = {}
        self.keyName = {}

        specification = open(Codepoint.URI["name"]).read().splitlines()
        specification = [t for t in specification if t.startswith('gc ;')]
        self.report('New specification', specification)
        for line in specification:
            split1 = [s.strip() for s in line.split('#')]
            split2 = [s.strip() for s in split1[0].split(';')]
            if len(split1) == 2:  # There is a rule for the name
                split3 = [s.strip() for s in split1[1].split('|')]
                if not self.full21bit:
                    # Necessary for 16 bit Unicode, not for 21 bit
                    split3 = [s for s in split3 if s != 'Cn']
                self.combinations[split2[1]] = ' | '.join(split3)
            else:  # No rule proposed
                self.keyName[split2[1]] = split2[-1]
        self.report('Combinations', self.combinations)
        self.report('Key names', self.keyName)

        # Column names and class names are found in file UnicodeData-3.0.0.html
        soup = BeautifulSoup(open(Codepoint.URI["meta"]).read())

        # 1st table (border) lists indices and names for UnicodeData columns.
        rows = soup.find_all("table")[1].find_all("tr")
        for row in rows[1:]:
            # column index is found in a th, not a td.
            index = int(row.find_all("th")[0].text)
            col = row.find_all("td")
            # Column name is in the initial td.
            # Clean up whitespace problems in authority.
            self.column[index] = sub('\s+', ' ', col[0].text.strip())

        # See collected column names
        self.report('Column names', self.column)

        # Check needed column names against manifest constants for sanity.
        for k,v in Codepoint.columnManifest.iteritems():
            assert self.column[v] == k

        return self

    def _blocks(self):
        """
        Languages are arranged in sequential blocks of codepoints.
        Knowing the order of languages improves efficiency when
        generating an ANTLR or other grammar.
        """
        specification = open(Codepoint.URI["lang"]).read().splitlines()
        self.block = {}
        self.language = []
        if self.verbose:
            print('    verbose: Language blocks')
        for line in specification:
            if line.startswith('#'):
                continue
            if ".." in line:
                (block, language) = [s.strip() for s in line.split(';')]
                (init, fini) = [int(s, 0x10) for s in block.split("..")]
                self.block[language] = [init, fini]
                self.language.append(language)
                if self.verbose:
                    print("%04x..%04x %s" % (init, fini, language))

        return self

    def _classify(self):
        """
        Rows in UnicodeData contain metadata for all legal codepoints.
        Collected column names and abbreviations rule columns in this file.
        Codepoint class is in the 2nd "General Category" column.
        """
        
        # Establish instance containers
        self.keys = set()
        self.raw = {}
        self.name = {}
        self.reverse = {}
        self.keyRanges = {}

        # class keys are found in file UnicodeData.txt
        specification = open(Codepoint.URI["data"]).read().splitlines()

        current = None  # Needed to identify range class transitions
        for line in specification:
            field = line.split(';')
            (codepoint, name, key, control) = [field[i] for i in [0, 1, 2, 10]]
            # convert hex codepoint string value to internal integer
            codepoint = int(codepoint, 0x10)
            if codepoint > 0xFFFF and not self.full21bit:
                continue
            self.raw[codepoint] = key
            self.name[codepoint] = name.replace(' ', '_')
            # Unicode 1.0 named each character.  Unicode 3.0 does not.
            if codepoint < ord(' ') or codepoint > ord('~'):
                self.name[codepoint] = control.replace(' ', '_')
            self.keys.add(key)

            if key == current:
                # if within established range, update the range end.
                self.keyRanges[key][-1][1] = codepoint
            else:
                # if key changed, start a new range for that key.
                self.keyRanges[key] = self.keyRanges.get(key, [])
                self.keyRanges[key].append([codepoint, codepoint])
                current = key
        # Sort the keys leading to sorted tables in classifier.
        self.keys = sorted(list(self.keys))

        # Establish an error key (either 0 or len(self.keys))
        # Prepare key name and ranges to prevent lookup failurs.
        self.errname = "ERROR"
        self.keyName[self.errname] = self.errname
        self.keyRanges[self.errname] = []
        if self.zeroerror:
            self.ERROR = 0
            self.keys.insert(0, self.errname)
        else:
            self.ERROR = len(self.keys)
            self.keys.append(self.errname)

        # Set index of first non-classification table
        self.base = len(self.keys)
        # Enable using classification to lookup key index.
        self.reverse = {v:k for k,v in enumerate(self.keys)}

        return self

    def _tables(self):
        # base class tables are sticky.  Once classified, always classified.
        self.table = {}
        self.table['class'] = [[i]*128 for i in range(self.base)]

        # (codepoint>>14) & 0x7f
        self.table['class'].append([self.ERROR]*128)        # All is error
        self.table['class'][self.base+0][0] = self.base+1   # ASCII @ [0]

        # (codepoint>>7) & 0x7f
        self.table['class'].append([self.ERROR]*128)        # All is error
        self.table['class'][self.base+1][0] = self.base+2   # ASCII @ [0]

        # (codepoint>>0) & 0x7f
        # ASCII
        self.ASCII = len(self.table['class'])
        self.table['class'].append([self.ERROR]*128)        # All is error
        if self.verbose:
            print('    verbose: ASCII Codepoint classes')
        for codepoint in range(128):
            # If the raw contents exist for the codepoint
            if self.raw.get(codepoint, None):
                raw = self.raw[codepoint]       # Get the key
                reverse = self.reverse[raw]     # Get the index from the key
                # Insert the class index as the lookup return value
                self.table['class'][self.ASCII][codepoint] = reverse

                if self.verbose:
                    kind = self.keyName[raw]
                    name = self.name[codepoint]
                    print('%05x|%s|%2d|%22s|%s' % (
                            codepoint, raw, reverse, kind, name))

        return self

    ###########################################################################
    def __init__(self, **kw):
        self.__dict__ = self
        self.update(**kw)
        self._blocks()._columns()._classify()._tables()

    def findLanguage(self, codepoint):
        for language in self.language:
            (lo, hi) = self.block[language]
            if lo <= codepoint and codepoint <= hi:
                return language
        return "unknown"

    def g4(self):
        """%s
Automatically generated Unicode codepoint classification grammar.
Generated by "classify.py".

Author: Jonathan D. Lettvin (jlettvin@gmail.com)
Date:   20161023

Legal:  Copyright(c) Jonathan D. Lettvin, All Rights Reserved
License:GPL 3.0"""
        if self.full21bit:
            self.bits = 21
            self.fmt1 = r" '\u%06x'             // %s"
            self.fmt2 = r" '\u%06x'..'\u%06x'   // %s"
        else:
            self.bits = 16
            self.fmt1 = r" '\u%04x'             // %s"
            self.fmt2 = r" '\u%04x'..'\u%04x'   // %s"
        self.fmt0 = '%-6s : %s;'
        self.g4name = 'classify%d.g4' % self.bits
        with open(self.g4name, 'w+') as self.grammar:
            self.g4echo('/** ')
            self.g4echo(Codepoint.g4.__doc__ % (self.g4name), 1)
            self.g4echo('Rules are generated by extracting from:', 1)
            self.g4echo('\n'.join(['%8s: %s' % (k,v) for k,v in Codepoint.URI.iteritems()]), 1)
            self.g4echo("See Makefile where wget downloads these files from", 1)
            self.g4echo("    site: ftp://ftp.unicode.org/Public/", 1)
            self.g4echo(' */', 1)
            self.g4echo("grammar classify;", 1)
            self.g4echo('codepoint:\n      ')
            self.g4echo('\n     | '.join([
                k + '  // ' + self.keyName[k]
                for k in sorted(self.keyRanges)
                if k is not self.errname]))
            self.g4echo("\n;", 1)

            rsep = ['  \n     | ', '  \n       ']
            for k in sorted(self.keyRanges):
                v = self.keyRanges[k]
                if k == self.errname:
                    continue
                self.g4echo('%-5s:     // %s' %(k, self.keyName[k]))
                for i, p in enumerate(v):
                    sep = rsep[i == 0]
                    language = "[>010000] "
                    if p[0] == p[1]:
                        if p[0] < 0x10000:
                            language = u'['+unichr(p[0])+'] '
                        language += self.findLanguage(p[0])
                        self.g4echo(sep + self.fmt1 % (p[0], language))
                    else:
                        if p[0] < 0x10000:
                            language = u'['+unichr(p[0])+'..'+unichr(p[1])+'] '
                        language += self.findLanguage(p[0])
                        self.g4echo(sep + self.fmt2 % (p[0], p[1], language))
                self.g4echo('\n;', 1)

            if self.enhance:
                self.g4enhance()
        if not self.full21bit:
            self.g4hello()
        return self

    def g4enhance(self):
        source = "from " + Codepoint.URI["name"];
        for rule, pattern in self.combinations.iteritems():
            widened = "%-32s  // %s" % (pattern, source)
            self.g4rule(rule, widened, 1)
        self.g4comment('End of Unicode codepoint classification', 1)
        #self.g4rule('WS0', '[ \t\r\n]          // hand-written rule', 1)
        self.g4rule('WS' , 'Z +        // hand-written rule', 1)
        self.g4rule("ID0", "L | '_'    // hand-written rule", 1)
        self.g4rule("ID1", "ID0 | N    // hand-written rule", 1)
        self.g4rule('ID' , "ID0 ID1 *  // hand-written rule", 1)

    def g4hello(self):
        """hello1.g4
Automatically generated Unicode based hello grammar."""
        with open('hello1.g4', 'w+') as self.grammar:
            self.g4echo('/** \n' + Codepoint.g4hello.__doc__ + '\n */', 1)
            self.g4echo('grammar      hello1    ;', 1)
            self.g4echo('import       %10s;' % (self.g4name.split('.')[0]), 1)
            self.g4rule('prog', 'hello * EOF', 1)

            if not self.enhance:
                self.g4enhance()

            self.g4rule("hello", r"'hello' ID", 1)

            if False:
                self.g4rule("WS1", r"Z | [\t\r\n]", 1)
                self.g4rule("WS", r"WS1 + -> skip", 1)
            else:
                self.g4rule('WS', r"[ \t\r\n] + -> skip  // TODO classify rule", 1)

        return self

    def g4echo(self, text="", nl=0):
        print>>self.grammar, text.encode('utf-8'),
        self.g4line(nl)

    def g4line(self, count=1):
        for i in range(count):
            print>>self.grammar, "\n"

    def g4comment(self, text, nl=0):
        self.g4echo('/* %s */\n' % (text), nl)

    def g4rule(self, name, pattern, nl=0):
        self.g4echo('%-6s : %s\n;' % (name, pattern), nl)

    def showAscii(self):
        if self.showascii:
            print("    show: ASCII")
            for codepoint in range(128):
                if self.raw.get(codepoint, None):
                    raw = self.raw[codepoint]
                    reverse = self.reverse[raw]
                    print('0x%02x %s %2d' % (codepoint, raw, reverse))
        return self

    def showCount(self):
        if self.showcount:
            print("    show: Counts")
            for key in self.keys:
                count = len(self.keyRanges[key])
                typed = self.keyName[key]
                print("%5s %3d %s" % (key, count, typed))
        return self

    def showKeys(self):
        if self.showkeys:
            print('    show: %d keys: %s' % (len(self.keys), str(self.keys)))
            for k, v in self.keyRanges.iteritems():
                print(k, str(v))
        return self

    def showTable(self):
        if self.showtables:
            print("    show: Table")
            print(self.table)
        return self

    def test(self, sample=None):
        if self.unittest:
            if sample == None:
                # 1. all ASCII
                # 2. mixed with Chinese (CJK) characters
                # Run "make" then "./classify.py -u" to see results.
                # TODO Complete table population to classify CJK characters.
                self.test(u"hello world\n").test(u"hello 愚公移山\n")
            else:
                # What to do with non-empty samples
                T = table = self.table['class']
                S = base  = self.base
                print("    test: %s" % (sample))
                for u in [ord(c) for c in sample]:
                    # This next line is the complete code for classifying.
                    A = T[T[T[S][(u>>14)&0x7f]][(u>>7)&0x7f]][u&0x7f]
                    name = self.name.get(u, "non-ASCII")
                    print('%04x %s %s' % (u, self.keys[A], name))
                    # The code below spreads the operation out to enable
                    # A better grasp of the 3 stage table dereference.
                    # a, b, c = [(u>>(7*i))&0x7f for i in range(3)]
                    # C = table[self.base][c]
                    # B = table[C][b]
                    # A = table[B][a]
                    # fmt = '0x%04x %3d %3d %3d %3d %3d %2d %s %s'
                    # print(fmt % (u, c, b, a, C, B, A, self.keys[A], name))
        return self

    def shows(self):
        return self.showCount().showAscii().showKeys().showTable()

if __name__ == "__main__":

    import sys, unittest, inspect, string

    from cStringIO import StringIO
    from contextlib import contextmanager

    @contextmanager
    def capture(command, *args, **kwargs):
        """
class BarTest(TestCase):
  def test_and_capture(self):
    with capture(callable, *args, **kwargs) as output:
      self.assertEquals("Expected output", output)
        """
        out, sys.stdout = sys.stdout, StringIO()
        try:
            command(*args, **kwargs)
            sys.stdout.seek(0)
            yield sys.stdout.read()
        finally:
            sys.stdout = out

    class TheTest(unittest.TestCase):

        def classify(self, u):
            T = table = TheTest.codepoint.table['class']
            S = base  = TheTest.codepoint.base
            for u in [ord(c) for c in sample]:
                A = T[T[T[S][(u>>14)&0x7f]][(u>>7)&0x7f]][u&0x7f]
                #name = self.name.get(u, "non-ASCII")
                #print('%04x %s %s' % (u, self.keys[A], name))

        def setUp(self):
            pass

        def tearDown(self):
            pass

        def test_001(self):
            TheTest.codepoint.test(u"Hello world\n")

        def test_002(self):
            TheTest.codepoint.test(u"Hello 愚公移山。\n")

    def main():
        "main is the traditional module entrypoint"

        # Convert command-line arguments to a dictionary suitable for members.
        kwargs = {
            k.strip('-'): w
            for k, w in docopt(__doc__, version="0.0.1").iteritems()
        }
        if kwargs["verbose"]:
            pprint(kwargs)

        # Initialize and process.
        codepoint = Codepoint(**kwargs)

        # Display internal data as flagged on the command-line.
        codepoint.shows()

        # Generate an ANTLR4 grammar
        codepoint.g4()

        if codepoint.unittest:
            # Run unit tests.
            TheTest.codepoint = codepoint

            # internal test
            codepoint.test()

            # using unittest
            if kwargs["verbose"]:
                unittest.main()

    main()

