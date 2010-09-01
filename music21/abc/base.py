#-------------------------------------------------------------------------------
# Name:         abc.base.py
# Purpose:      music21 classes for dealing with abc data
#
# Authors:      Christopher Ariza
#
# Copyright:    (c) 2010 The music21 Project
# License:      LGPL
#-------------------------------------------------------------------------------
'''
Objects and tools for processing ABC data. 

'''

import music21
import unittest
import re

try:
    import StringIO # python 2 
except:
    from io import StringIO # python3 (also in python 2.6+)


from music21 import common
from music21 import environment
_MOD = 'abc.base.py'
environLocal = environment.Environment(_MOD)

# for implementation
# see http://abcnotation.com/abc2mtex/abc.txt

# store symbol and m21 naming/class eq
ABC_BARS = [
           ('|]', 'thin-thick double bar line'),
           ('||', 'thin-thin double bar line'),
           ('[|', 'thick-thin double bar line'),
           (':|', 'left repeat'),
           ('|:', 'right repeat'),
           ('::', 'left-right repeat'),
            # for comparison, single chars must go last
           ('|', 'bar line'),
           ]

#-------------------------------------------------------------------------------
reMetadataTag = re.compile('[A-Z]:')

rePitchName = re.compile('[a-gA-Gz]')

reChordSymbol = re.compile('"[^"]*"') # non greedy

reChord = re.compile('[.*?]') # non greedy

#-------------------------------------------------------------------------------
class ABCObjectException(Exception):
    pass

class ABCHandlerException(Exception):
    pass


#-------------------------------------------------------------------------------
class ABCObject(object):
    def __init__(self, src=''):
        self.src = src # store source character sequence

    def stripComment(self, strSrc):
        '''
        removes ABC-style comments from a string:
        
        >>> ao = ABCObject()
        >>> ao.stripComment('asdf')
        'asdf'
        >>> ao.stripComment('asdf%234')
        'asdf'
        >>> ao.stripComment('asdf  %     234')
        'asdf  '
        
        >>> ao.stripComment('[ceg]% this chord appears 50% more often than other chords do')
        '[ceg]'
        '''
        if '%' in strSrc:
            return strSrc.split('%')[0] #
        return strSrc
    
    def preParse(self):
        '''Called before context adjustments. 
        '''
        pass

    def parse(self): 
        '''Read self.src and load attributes. Customize in subclasses.
        Called after context adjustments
        '''
        pass


class ABCMetadata(ABCObject):

    # given a logical unit, create an object
    # may be a chord, notes, metadata, bars
    def __init__(self, src):
        ABCObject.__init__(self, src)
        self.tag = None
        self.data = None

    def preParse(self):
        '''Called before context adjustments: need to have access to data
        '''
        div = reMetadataTag.match(self.src).end()
        strSrc = self.stripComment(self.src) # remove any comments
        self.tag = strSrc[:div-1] # do not get colon, :
        self.data = strSrc[div:].strip() # remove leading/trailing

    def parse(self):
        pass

    def isDefaultNoteLength(self):
        if self.tag == 'L': 
            return True
        return False

    def isMeter(self):
        if self.tag == 'M': 
            return True
        return False

    def getTimeSignature(self):
        '''If there is a time signature representation available, get a numerator and denominator

        >>> am = ABCMetadata('M:2/2')
        >>> am.preParse()
        >>> am.getTimeSignature()
        (2, 2, 'normal')

        >>> am = ABCMetadata('M:C|')
        >>> am.preParse()
        >>> am.getTimeSignature()
        (2, 2, 'cut')
        '''
        if self.isMeter():
            if self.data == 'C':
                n, d = 4, 4
                symbol = 'ccommon' # m21 compat
            elif self.data == 'C|':
                n, d = 2, 2
                symbol = 'cut' # m21 compat
            else:
                n, d = self.data.split('/')
                n = int(n.strip())
                d = int(d.strip())
                symbol = 'normal' # m21 compat
        else:       
            raise ABCObjectException('no time signature associated with this meta-data')

        return n, d, symbol

    def getDefaultQuarterLength(self):
        '''If there is a quarter length representation available, return it as a floating point value

        >>> am = ABCMetadata('L:1/2')
        >>> am.preParse()
        >>> am.getDefaultQuarterLength()
        2.0

        >>> am = ABCMetadata('L:1/8')
        >>> am.preParse()
        >>> am.getDefaultQuarterLength()
        0.5

        >>> am = ABCMetadata('M:C|')
        >>> am.preParse()
        >>> am.getDefaultQuarterLength()
        0.5

        >>> am = ABCMetadata('M:2/4')
        >>> am.preParse()
        >>> am.getDefaultQuarterLength()
        0.25

        >>> am = ABCMetadata('M:6/8')
        >>> am.preParse()
        >>> am.getDefaultQuarterLength()
        0.5

        '''
        if self.isDefaultNoteLength():
            # should be in L:1/4 form
            n, d = self.data.split('/')
            n = int(n.strip())
            d = int(d.strip())
            # 1/4 is 1, 1/8 is .5
            return (float(n) / d) * 4
            
        elif self.isMeter():
            # meter auto-set a default not length
            n, d, symbol = self.getTimeSignature()
            if float(n) / d < .75:
                return .25 # less than 0.75 the default is a sixteenth note
            else:
                return .5 # otherwiseit is an eighth note

        else:       
            raise ABCObjectException('no quarter length associated with this meta-data')



class ABCBar(ABCObject):

    # given a logical unit, create an object
    # may be a chord, notes, metadata, bars
    def __init__(self, src):
        ABCObject.__init__(self, src)
        self.barType = None


class ABCTuplet(ABCObject):
    def __init__(self, src):
        ABCObject.__init__(self, src)


class ABCBrokenRhythmMarker(ABCObject):

    # given a logical unit, create an object
    # may be a chord, notes, metadata, bars
    def __init__(self, src):
        ABCObject.__init__(self, src)
        self.data = None

    def preParse(self):
        '''Called before context adjustments: need to have access to data

        >>> abrm = ABCBrokenRhythmMarker('>>>')
        >>> abrm.preParse()
        >>> abrm.data
        '>>>'
        '''
        self.data = self.src.strip()



class ABCNote(ABCObject):

    # given a logical unit, create an object
    # may be a chord, notes, bars

    def __init__(self, src=''):
        ABCObject.__init__(self, src)

        # context attributes
        self.inBar = None
        self.inBeam = None
        self.inSlur = None
        self.inGrace = None

        # store chord string if connected to this note
        self.chordSymbols = [] 
        
        # provide default duration from handler; may change during piece
        self.activeDefaultQuarterLength = None
        # store if a broken symbol applies; pair of symbol, position (left, right)
        self.brokenRhythmMarker = None

        # pitch/ duration attributes for m21 conversion
        self.pitchName = None # if None, a rest or chord
        self.quarterLength = None

    
    def _splitChordSymbols(self, strSrc):
        '''Split chord symbols from other string characteristics. Return list of chord symbols and clean, remain chars

        >>> an = ABCNote()
        >>> an._splitChordSymbols('"C"e2')
        (['"C"'], 'e2')
        >>> an._splitChordSymbols('b2')
        ([], 'b2')
        >>> an._splitChordSymbols('"D7""D"d2')
        (['"D7"', '"D"'], 'd2')
        '''
        if '"' in strSrc:
            chordSymbols = reChordSymbol.findall(strSrc)
            # might remove quotes from chord symbols here

            # index of end of last match
            i = [m for m in reChordSymbol.finditer(strSrc)][-1].end()
            return chordSymbols, strSrc[i:]
        else:
            return [], strSrc        


    def _getPitchName(self, strSrc):
        '''Given a note or rest string without a chord symbol, return pitch or None of a rest. 

        >>> an = ABCNote()
        >>> an._getPitchName('e2')
        'E5'
        >>> an._getPitchName('C')
        'C4'
        >>> an._getPitchName('B,,')
        'B2'
        >>> an._getPitchName('C,')
        'C3'
        >>> an._getPitchName('c')
        'C5'
        >>> an._getPitchName("c'")
        'C6'
        >>> an._getPitchName("c''")
        'C7'
        >>> an._getPitchName("^g")
        'G#5'
        >>> an._getPitchName("_g''")
        'G-7'
        >>> an._getPitchName("=c")
        'Cn5'
        >>> an._getPitchName("z4") == None
        True

        '''
        name = rePitchName.findall(strSrc)[0]
        if name == 'z':
            return None # designates a rest
        else:
            if name.islower():
                octave = 5
            else:
                octave = 4
        # look in source string for register modification
        octModUp = strSrc.count("'")
        octModDown = strSrc.count(",")
        octave -= octModDown
        octave += octModUp

        sharpCount = strSrc.count("^")
        flatCount = strSrc.count("_")
        naturalCount = strSrc.count("=")
        accString = ''
        for x in range(flatCount):
            accString += '-' # m21 symbols
        for x in range(sharpCount):
            accString += '#' # m21 symbols
        for x in range(naturalCount):
            accString += 'n' # m21 symbols

        return '%s%s%s' % (name.upper(), accString, octave)


    def _getQuarterLength(self, strSrc):
        '''Called with parse(), after context processing, to calculate duration

        >>> an = ABCNote()
        >>> an.activeDefaultQuarterLength = .5
        >>> an._getQuarterLength('e2')
        1.0
        >>> an._getQuarterLength('G')
        0.5
        >>> an._getQuarterLength('=c/2')
        0.25
        >>> an._getQuarterLength('A3/2')
        0.75
        >>> an._getQuarterLength('A/')
        0.25

        >>> an = ABCNote()
        >>> an.activeDefaultQuarterLength = .5
        >>> an.brokenRhythmMarker = ('>', 'left')
        >>> an._getQuarterLength('A')
        0.75
        >>> an.brokenRhythmMarker = ('>', 'right')
        >>> an._getQuarterLength('A')
        0.25

        >>> an.brokenRhythmMarker = ('<<<', 'left')
        >>> an._getQuarterLength('A')
        0.0625
        >>> an.brokenRhythmMarker = ('<<<', 'right')
        >>> an._getQuarterLength('A')
        0.9375

        '''
        if self.activeDefaultQuarterLength == None:
            raise ABCObjectException('cannot calculate quarter length without a default quarter length')

        numStr = []
        for c in strSrc:
            if c.isdigit() or c in '/':
                numStr.append(c)
        numStr = ''.join(numStr)

        # get default
        if numStr == '':
            ql = self.activeDefaultQuarterLength
        # if only, shorthand for /2
        elif numStr == '/':
            ql = self.activeDefaultQuarterLength * .5
        # if a half fraction
        elif numStr.startswith('/'):
            ql = self.activeDefaultQuarterLength / int(numStr.split('/')[1])
        # assume we have a complete fraction
        elif '/' in numStr:
            n, d = numStr.split('/')
            n = int(n.strip())
            d = int(d.strip())
            ql = self.activeDefaultQuarterLength * (float(n) / d)
        # not a fraction; a multiplier
        else: 
            ql = self.activeDefaultQuarterLength * int(numStr)


        if self.brokenRhythmMarker != None:
            symbol, direction = self.brokenRhythmMarker
            if symbol == '>':
                modPair = (1.5, .5)
            elif symbol == '<':
                modPair = (.5, 1.5)
            elif symbol == '>>':
                modPair = (1.75, .25)
            elif symbol == '<<':
                modPair = (.25, 1.75)
            elif symbol == '>>>':
                modPair = (1.875, .125)
            elif symbol == '<<<':
                modPair = (.125, 1.875)
            # apply based on direction
            if direction == 'left':
                ql *= modPair[0]
            elif direction == 'right':
                ql *= modPair[1]
            
        # need to look at tuplets lastly
        return ql


    def parse(self):
        self.chordSymbols, nonChordSymStr = self._splitChordSymbols(self.src)        
        # get pitch name form remaining string
        # rests will have a pitch name of None
        self.pitchName = self._getPitchName(nonChordSymStr)
        self.quarterLength = self._getQuarterLength(nonChordSymStr)

        # environLocal.printDebug(['ABCNote:', 'pitch name:', self.pitchName, 'ql:', self.quarterLength])


class ABCChord(ABCNote):

    # given a logical unit, create an object
    # may be a chord, notes, bars

    def __init__(self, src):
        ABCNote.__init__(self, src)
        # store a list of component objects
        self.noteObjects = []

    def parse(self):
        self.chordSymbols, nonChordSymStr = self._splitChordSymbols(self.src)        
        #environLocal.printDebug(['ABCChord:', nonChordSymStr])

        # create a handler for processing internal chord notes
        ah = ABCHandler()



#-------------------------------------------------------------------------------
class ABCHandler(object):

    # divide elements of a character stream into objects and handle
    # store in a list, and pass global information to compontns
    def __init__(self):
        # tokens are ABC objects in a linear stream
        self._tokens = []

    def _getLinearContext(self, strSrc, i):
        '''Find the local context of a string or list of ojbects. Returns charPrevNotSpace, charPrev, charThis, charNext, charNextNotSpace.


        >>> ah = ABCHandler()
        >>> ah._getLinearContext('12345', 0)
        (None, None, '1', '2', '2')
        >>> ah._getLinearContext('12345', 1)
        ('1', '1', '2', '3', '3')
        >>> ah._getLinearContext('12345', 3)
        ('3', '3', '4', '5', '5')
        >>> ah._getLinearContext('12345', 4)
        ('4', '4', '5', None, None)

        >>> ah._getLinearContext([32, None, 8, 11, 53], 4)
        (11, 11, 53, None, None)
        >>> ah._getLinearContext([32, None, 8, 11, 53], 2)
        (32, None, 8, 11, 11)
        >>> ah._getLinearContext([32, None, 8, 11, 53], 0)
        (None, None, 32, None, 8)


        '''            
        lastIndex = len(strSrc) - 1
        if i > lastIndex:
            raise ABCHandlerException
        # find local area of string
        if i > 0:
            charPrev = strSrc[i-1]
        else:      
            charPrev = None
        # get last char previous non-white; do not start with current
        # -1 goes to index 0
        charPrevNotSpace = None
        for j in range(i-1, -1, -1):
            # condition to break: find a something that is not None, or 
            # a string that is not a space
            if isinstance(strSrc[j], str):
                if not strSrc[j].isspace():
                    charPrevNotSpace = strSrc[j]
                    break
            else:
                if strSrc[j] != None:
                    charPrevNotSpace = strSrc[j]
                    break

        charThis = strSrc[i]
        if i < len(strSrc)-1:
            charNext = strSrc[i+1]
        else:      
            charNext = None
        charNextNotSpace = None
        # start at next index and look forward
        for j in range(i+1, len(strSrc)):
            if isinstance(strSrc[j], str):
                if not strSrc[j].isspace():
                    charNextNotSpace = strSrc[j]
                    break
            else:
                if strSrc[j] != None:
                    charNextNotSpace = strSrc[j]
                    break
        return charPrevNotSpace, charPrev, charThis, charNext, charNextNotSpace


    def _getNextLineBreak(self, strSrc, i):
        '''Return index of next line break.

        >>> ah = ABCHandler()
        >>> strSrc = 'de  we\\n wer bfg\\n'
        >>> ah._getNextLineBreak(strSrc, 0)
        6
        >>> strSrc[0:6]
        'de  we'
        >>> # from last line break
        >>> ah._getNextLineBreak(strSrc, 6)
        15
        >>> strSrc[ah._getNextLineBreak(strSrc, 0):]
        '\\n wer bfg\\n'
        '''
        lastIndex = len(strSrc) - 1
        j = i + 1 # start with next
        while True:
            if strSrc[j] == '\n' or j > lastIndex:
                return j # will increment to next char on loop
            j += 1

    def tokenize(self, strSrc):
        '''Walk the abc string, creating ABC objects along the way.
        '''
        i = 0
        collect = []
        lastIndex = len(strSrc) - 1

        activeChordSymbol = '' # accumulate, then prepend
        while True:    
            if i > lastIndex:
                break

            q = self._getLinearContext(strSrc, i)
            charPrevNotSpace, charPrev, charThis, charNext, charNextNotSpace = q
            
            # comment lines, also encoding defs
            if charThis == '%':
                j = self._getNextLineBreak(strSrc, i)
                environLocal.printDebug(['got comment:', repr(strSrc[i:j+1])])
                i = j+1 # skip \n char
                continue

            # metadata: capatal alpha, with next char as ':'
            # get metadata before others
            # some meta data might have bar symbols, for example
            if (charThis.isalpha() and charThis.isupper() 
                and charNext != None and charNext == ':'):
                # collect until end of line; add one to get line break
                j = self._getNextLineBreak(strSrc, i) + 1
                collect = strSrc[i:j].strip()
                #environLocal.printDebug(['got metadata:', repr(''.join(collect))])
                self._tokens.append(ABCMetadata(collect))
                i = j
                continue
            
            # get bars: if not a space and not alphanemeric
            if (not charThis.isspace() and not charThis.isalnum()
                and charThis not in ['~', '(']):
                matchBars = False
                for barIndex in range(len(ABC_BARS)):
                    # first of bars tuple is symbol to match
                    if charThis + charNext == ABC_BARS[barIndex][0]:
                        j = i + 2
                        matchBars = True 
                        break
                    # check for signle char bars
                    elif charThis == ABC_BARS[barIndex][0]:
                        j = i + 1
                        matchBars = True 
                        break
                if matchBars:
                    collect = strSrc[i:j]
                    #environLocal.printDebug(['got bars:', repr(collect)])  
                    self._tokens.append(ABCBar(collect))
                    i = j
                    continue
                    
            # get tuplet indicators: (2, (3
            # TODO: extended tuplets look like this: (p:q:r or (3::
            if (charThis == '(' and charNext != None and charNext.isdigit()):
                j = i + 2 # always two characters
                collect = strSrc[i:j]
                #environLocal.printDebug(['got tuplet start:', repr(collect)])
                self._tokens.append(ABCTuplet(collect))
                i = j
                continue

            # get broken rhythm modifiers: < or >, >>, up to <<<
            if charThis in '<>':
                j = i + 1
                while (j < lastIndex and strSrc[j] in '<>'):
                    j += 1
                collect = strSrc[i:j]
                #environLocal.printDebug(['got bidrectional rhythm mod:', repr(collect)])
                self._tokens.append(ABCBrokenRhythmMarker(collect))
                i = j
                continue

            # get chord symbols / guitar chords; collected and joined with
            # chord or notes
            if (charThis == '"'):
                j = i + 1
                while (j < lastIndex and strSrc[j] not in '"'):
                    j += 1
                j += 1 # need character that caused break
                # there may be more than one chord symbol: need to accumulate
                activeChordSymbol += strSrc[i:j]
                #environLocal.printDebug(['got chord symbol:', repr(activeChordSymbol)])
                i = j
                continue

            # get chords
            if (charThis == '['):
                j = i + 1
                while (j < lastIndex and strSrc[j] not in ']'):
                    j += 1
                j += 1 # need character that caused break
                # prepend chord symbol
                if activeChordSymbol != '':
                    collect = activeChordSymbol+strSrc[i:j]
                    activeChordSymbol = '' # reset
                else:
                    collect = strSrc[i:j]

                #environLocal.printDebug(['got chord:', repr(collect)])
                self._tokens.append(ABCChord(collect))

                i = j
                continue

            # get the start of a note event: alpha, or 
            # ~ tunr/ornament, accidentals ^, =, - as well as ^^
            if (charThis.isalpha() or charThis in '~^=_.'):
                # condition where we start with an alpha
                foundAlpha = charThis.isalpha() and charThis not in ['u', 'v']
                j = i + 1
                while True:
                    if j > lastIndex:
                        break
                    # ornaments may precede note names
                    # accidentals (^=_) staccato (.), up/down bow (u, v)
                    elif foundAlpha == False and strSrc[j] in '~=^_.uv':
                        j += 1
                        continue                    
                    # only allow one alpha to be a continue condition
                    elif (foundAlpha == False and strSrc[j].isalpha() 
                        and strSrc[j] not in ['u', 'v']):
                        foundAlpha = True
                        j += 1
                        continue                    
                    # continue condition after alpha: 
                    # , register modeifiaciton (, ') or number, rhythm
                    elif strSrc[j].isdigit() or strSrc[j] in ',/\'':
                        j += 1
                        continue                    
                    else: # space, all else: break
                        break
                # prepend chord symbol
                if activeChordSymbol != '':
                    collect = activeChordSymbol+strSrc[i:j]
                    activeChordSymbol = '' # reset
                else:
                    collect = strSrc[i:j]
                #environLocal.printDebug(['got note event:', repr(collect)])
                self._tokens.append(ABCNote(collect))
                i = j
                continue

            # look for white space: can be used to determine beam groups

            # no action: normal continuation of 1 char
            i += 1

    
    def tokenProcess(self):
        '''Process all token objects.
        '''
        # pre-parse : call on objects that need preliminary processing
        # metadata, for example, is parsed
        for t in self._tokens:
            t.preParse()

        # context: iterate through tokens, supplying contextual data as necessary to appropriate objects
        lastDefaultQL = None
        for i in range(len(self._tokens)):
            # get context of tokens
            q = self._getLinearContext(self._tokens, i)
            tPrevNotSpace, tPrev, t, tNext, tNextNotSpace = q
            
            if isinstance(t, ABCMetadata):
                if t.isMeter() or t.isDefaultNoteLength():
                    lastDefaultQL = t.getDefaultQuarterLength()
                continue

            # broken rhythms need to be applied to previous and next notes
            if isinstance(t, ABCBrokenRhythmMarker):
                if (isinstance(tPrev, ABCNote) and 
                isinstance(tNext, ABCNote)):
                    #environLocal.printDebug(['tokenProcess: got broken rhythm marker', t.src])       
                    tPrev.brokenRhythmMarker = (t.data, 'left')
                    tNext.brokenRhythmMarker = (t.data, 'right')
                else:
                    raise ABCHandlerException('broken rhythm marker (%s) not positioned between two notes or chords' % t.src)

            # ABCChord inherits ABCNote, thus getting note is enough
            if isinstance(t, ABCNote):
                if lastDefaultQL == None:
                    raise ABCHandlerException('no active defailt not length provided for note processing. %s' % t.src)
                t.activeDefaultQuarterLength = lastDefaultQL
                continue

        # parse : call methods to set attributes and parse string
        for t in self._tokens:
            t.parse()
            #print o.src

    def process(self, strSrc):
        self._tokens = []
        self.tokenize(strSrc)
        self.tokenProcess()
        # return list of tokens
        return self._tokens

#-------------------------------------------------------------------------------
class ABCFile(object):
    '''
    ABC File access

    '''
    
    def __init__(self): 
        pass

    def open(self, filename): 
        '''Open a file for reading
        '''
        self.file = open(filename, 'r') 

    def openFileLike(self, fileLike):
        '''Assign a file-like object, such as those provided by StringIO, as an open file object.

        >>> fileLikeOpen = StringIO.StringIO()
        '''
        self.file = fileLike
    
    def __repr__(self): 
        r = "<ABCFile>" 
        return r 
    
    def close(self): 
        self.file.close() 
    
    def read(self): 
        self.readstr(self.file.read()) 
    
    def readstr(self, str): 
        handler = ABCHandler()
        return.process(str)
    
#     def write(self): 
#         ws = self.writestr()
#         self.file.write(ws) 
#     
#     def writestr(self): 
#         pass










#-------------------------------------------------------------------------------
class Test(unittest.TestCase):

    def runTest(self):
        pass

    def testTokenization(self):
        from music21.abc import testFiles

        for (tf, countTokens, noteTokens, chrodTokens) in [
            (testFiles.fyrareprisarn, 236, 152, 0), 
            (testFiles.mysteryReel, 188, 153, 0), 
            (testFiles.aleIsDear, 291, 206, 32),
            (testFiles.testPrimitive, 94, 75, 2),
            (testFiles.kitchGirl, 125, 101, 2),
            (testFiles.williamAndNancy, 127, 93, 0),
                ]:

            handler = ABCHandler()
            handler.tokenize(tf)
            tokens = handler._tokens # get private for testing
            self.assertEqual(len(tokens), countTokens)
            countNotes = 0
            countChords = 0
            for o in tokens:
                if isinstance(o, ABCChord):
                    countChords += 1
                elif isinstance(o, ABCNote):
                    countNotes += 1

            self.assertEqual(countNotes, noteTokens)
            self.assertEqual(countChords, chrodTokens)
        

    def testRe(self):

        src = 'A: this is a test'
        post = reMetadataTag.match(src).end()
        self.assertEqual(src[:post], 'A:')
        self.assertEqual(src[post:], ' this is a test' )


        src = 'Q: this is a test % and a following comment'
        post = reMetadataTag.match(src).end()
        self.assertEqual(src[:post], 'Q:')


        # chord symbol matches
        src = 'd|"G"e2d B2d|"C"gfe "D7"d2d|"G"e2d B2d|"A7""C"gfe "D7""D"d2c|'
        post = reChordSymbol.findall(src)
        self.assertEqual(post, ['"G"', '"C"', '"D7"', '"G"', '"A7"', 
                                '"C"', '"D7"', '"D"'] )

        # get index of last match of many
        i = [m for m in reChordSymbol.finditer(src)][-1].end()

        src = '=d2'
        self.assertEqual(rePitchName.findall(src)[0], 'd')

        src = 'A3/2'
        self.assertEqual(rePitchName.findall(src)[0], 'A')


        

    def testTokenProcessMetadata(self):
        from music21.abc import testFiles

#'Full Rigged Ship', '6/8', 'G'
        for (tf, titleEncoded, meterEncoded, keyEncoded) in [
            (testFiles.fyrareprisarn, 'Fyrareprisarn', '3/4', 'F'), 
            (testFiles.mysteryReel, 'Mystery Reel', 'C|', 'G'), 
            (testFiles.aleIsDear, 'Ale is Dear, the', '4/4', 'D', ),
            (testFiles.kitchGirl, 'Kitchen Girl', '4/4', 'D'),
            (testFiles.williamAndNancy, 'William and Nancy', '6/8', 'G'),
            ]:

            handler = ABCHandler()
            handler.tokenize(tf)
            handler.tokenProcess()

            tokens = handler._tokens # get private for testing
            for t in tokens:
                if isinstance(t, ABCMetadata):
                    if t.tag == 'T':
                        self.assertEqual(t.data, titleEncoded)
                    elif t.tag == 'M':
                        self.assertEqual(t.data, meterEncoded)
                    elif t.tag == 'K':
                        self.assertEqual(t.data, keyEncoded)



    def testTokenProcess(self):
        from music21.abc import testFiles

        for tf in [
            testFiles.fyrareprisarn,
            testFiles.mysteryReel,
            testFiles.aleIsDear, 
            testFiles.testPrimitive,
            testFiles.kitchGirl,
            testFiles.williamAndNancy,
            ]:

            handler = ABCHandler()
            handler.tokenize(tf)
            handler.tokenProcess()


if __name__ == "__main__":
    music21.mainTest(Test)








