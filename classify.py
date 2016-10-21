#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""classify.py

Usage:
    classify.py [-acektuz] [-v]
    classify.py (-h | --help)
    classify.py (--version)

Options:
    -a --showascii                  Show ASCII class/name
    -c --showcount                  Show key counts
    -e --enhance                    Add WS and ID rules
    -k --showkeys                   Show key names
    -t --showtables                 Show tables
    -u --unittest                   Run tests
    -z --zeroerror                  Use zero, not len
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
    from the file wiki.g4 to the file classify.g4 where
    they can be imported into other grammars.

"""

from re import (sub)
from bs4 import (BeautifulSoup)
from urllib import (urlopen)
from pprint import (pprint)
from docopt import (docopt)

class Codepoint(dict):

    ###########################################################################
    ftp = "ftp://ftp.unicode.org/Public/"

    URI = {
        # "meta": ftp + "3.0-Update/UnicodeData-3.0.0.html",
        # "name": ftp + "UCD/latest/ucd/PropertyValueAliases.txt",
        # "data": ftp + "UCD/latest/ucd/UnicodeData.txt",
        # "lang": ftp + "UCD/latest/ucd/Blocks.txt"
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
    def _columns(self):
        """
        Columns in UnicodeData.txt are undocumented within the file.
        This method reads column labels from UnicodeData-3.0.0.html
        """

        # Establish instance containers
        self.keyName = {}
        self.column = {}
        self.combinations = {}
        self.newrule = {}

        specification = open(Codepoint.URI["lang"]).read().splitlines()
        specification = [t for t in specification if t.startswith('gc ;')]
        if self.verbose:
            print '    New specification:'
            pprint(specification)
        for line in specification:
            combo = [s.strip() for s in line.split('#')]
            combo[0] = combo[0][5:7].strip()
            combo.append(combo[0][7:].strip())
            if len(combo) == 3:
                self.combinations[combo[0]] = combo[1]
            else:
                self.newrule[combo[0]] = combo[2]
        if self.verbose:
            print('    Combinations:')
            pprint(self.combinations)
            print('    New rules:')
            pprint(self.newrule)

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
        if self.verbose:
            print('    verbose: Column names:')
            pprint(self.column)

        # Check needed column names against manifest constants for sanity.
        for k,v in Codepoint.columnManifest.iteritems():
            assert self.column[v] == k

        # 2nd and 3ed table contain Abbreviations for codepoint classification.
        # These are the expected values found in column 2 of UnicodeData
        # also known as "General Category" (see columnManifest).
        for table in range(2,4):
            rows = soup.find_all("table")[table].find_all("tr")
            for row in rows[1:]:
                col = row.find_all("td")
                (key, name) = [col[i].text for i in range(2)]
                self.keyName[key] = name

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
            print '    verbose:Language blocks:'
        for line in specification:
            if line.startswith('#'):
                continue
            if ".." in line:
                (block, language) = [s.strip() for s in line.split(';')]
                (init, fini) = [int(s, 0x10) for s in block.split("..")]
                self.block[language] = [init, fini]
                self.language.append(language)
                if self.verbose:
                    print "%06x..%06x %s" % (init, fini, language)

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
            print '    verbose: ASCII Codepoint classes'
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
                    print '%05x|%s|%2d|%22s|%s' % (
                            codepoint, raw, reverse, kind, name)

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
        """classify.g4
Automatically generated Unicode codepoint classification grammar.
        """
        with open('classify.g4', 'w+') as self.grammar:
            self.g4echo('/** ')
            self.g4echo(Codepoint.g4.__doc__)
            self.g4echo('Rules are generated by extracting from:\n')
            self.g4echo('\n'.join(['%8s: %s' % (k,v) for k,v in Codepoint.URI.iteritems()]))
            self.g4echo("\nSee Makefile where wget downloads these files from")
            self.g4echo("\n    site: ftp://ftp.unicode.org/Public/")
            self.g4echo('\n */')
            self.g4line(2)
            self.g4echo("grammar classify;")
            self.g4line(2)
            self.g4echo('codepoint:\n      ')
            self.g4echo('\n     | '.join([
                k + '  // ' + self.keyName[k]
                for k in sorted(self.keyRanges)
                if k is not self.errname]))
            self.g4echo("\n;")
            self.g4line()
            self.g4line()

            efmt = '%-6s : %s;'
            rfmt = r'[\u%06x-\u%06x]  // %s'
            sfmt = r'[\u%06x         ]  // %s'
            rsep = ['  \n     | ', '  \n       ']
            for k in sorted(self.keyRanges):
                v = self.keyRanges[k]
                if k == self.errname:
                    continue
                self.g4echo(k + ':')
                for i, p in enumerate(v):
                    sep = rsep[i == 0]
                    language = "[>010000] "
                    if p[0] == p[1]:
                        if p[0] < 0x10000:
                            language = u'['+unichr(p[0])+'] '
                        language += self.findLanguage(p[0])
                        self.g4echo(sep + sfmt % (p[0], language))
                    else:
                        if p[0] < 0x10000:
                            language = u'['+unichr(p[0])+'..'+unichr(p[1])+'] '
                        language += self.findLanguage(p[0])
                        self.g4echo(sep + rfmt % (p[0], p[1], language))
                self.g4echo('\n;')
                self.g4line(2)

            self.g4comment('End of Unicode codepoint classification')
            if self.enhance:
                self.g4enhance()
        self.g4wiki()
        return self

    def g4enhance(self):
        self.g4rule('WS', r'[ \u000008 | \u00000a | \u00000d | Zs ]')
        self.g4line(2)
        self.g4rule('LETTER', '[ Ll | Lm | Lo | Lt | Lu ]')
        self.g4line(2)
        self.g4rule("ID0"   , "[ LETTER | '_' ]")
        self.g4line(2)
        self.g4rule('DIGIT' , 'Nd')
        self.g4line(2)
        self.g4rule('ID'    , "ID0 [ ID0 | DIGIT ]*")
        self.g4line(2)

    def g4wiki(self):
        """wiki.g4
Automatically generated Unicode based wiki grammar."""
        with open('wiki.g4', 'w+') as self.grammar:
            self.g4echo('/** ')
            self.g4echo(Codepoint.g4wiki.__doc__)
            self.g4echo('\n */')
            self.g4line(2)
            self.g4echo('grammar      wiki;\n')
            self.g4line()
            self.g4echo('import       classify;\n')
            self.g4line()

            self.g4rule('prog', 'ID *')

            self.g4line(2)
            if not self.enhance:
                self.g4enhance()

            self.g4rule("DEFINE", "'&' ID '=' .*? ';'")
            self.g4line(2)
            self.g4rule("ENTITY", "'&' ID ';'")
        return self

    def g4echo(self, text=""):
        print>>self.grammar, text.encode('utf-8'),

    def g4line(self, count=1):
        for i in range(count):
            self.g4echo("\n")

    def g4comment(self, text):
        self.g4echo('/* %s */\n' % (text))

    def g4rule(self, name, pattern, code=""):
        self.g4echo('%-6s : %s\n;' % (name, pattern))

    def showAscii(self):
        if self.showascii:
            print "    show: ASCII"
            for codepoint in range(128):
                if self.raw.get(codepoint, None):
                    raw = self.raw[codepoint]
                    reverse = self.reverse[raw]
                    print '0x%02x %s %2d' % (codepoint, raw, reverse)
        return self

    def showCount(self):
        if self.showcount:
            print "    show: Counts"
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
            print "    show: Table"
            print(self.table)
        return self

    def test(self, sample):
        if self.unittest:
            table = self.table['class']
            print "    test: %s" % (sample)
            for u in [ord(c) for c in sample]:
                a, b, c = [(u>>(7*i))&0x7f for i in range(3)]
                C = table[self.base][c]
                B = table[C][b]
                A = table[B][a]
                name = self.name[u] if u < 128 else "non-ASCII"
                fmt = '0x%06x %3d %3d %3d %3d %3d %2d %s %s'
                print fmt % (u, c, b, a, C, B, A, self.keys[A], name)
        return self

    def shows(self):
        return self.showCount().showAscii().showKeys().showTable()

if __name__ == "__main__":

    def main():
        "main is the traditional module entrypoint"

        # Convert command-line arguments to a dictionary suitable for members.
        kwargs = {
            k.strip('-'): w
            for k, w in docopt(__doc__, version="0.0.1").iteritems()
        }
        # Initialize it all.
        codepoint = Codepoint(**kwargs)

        # Display internal data as flagged on the command-line.
        codepoint.shows()

        # Run a couple of tests.
        codepoint.test(u"Hello world\n").test(u"Hello 愚公移山。\n")

        # Generate an ANTLR4 grammar
        codepoint.g4()

    main()

