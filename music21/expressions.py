#!/usr/bin/python
#-------------------------------------------------------------------------------
# Name:         expressions.py
# Purpose:      notation mods
#
# Authors:      Michael Scott Cuthbert
#               Christopher Ariza
#
# Copyright:    (c) 2009-2010 The music21 Project
# License:      LGPL
#-------------------------------------------------------------------------------

'''
This module provides object representations of expressions, that is
notational symbols such as Fermatas, Mordents, Trills, Turns, etc.
which are stored under a Music21Object's .notations attribute 
'''

import doctest, unittest

import music21
import music21.interval
from music21 import musicxml

_MOD = 'expressions'



class Ornament(music21.Music21Object):
    connectedToPrevious = True  # should follow directly on previous; true for most "ornaments".
    tieAttach = 'first' # attach to first note of a tied group.

class GeneralMordent(Ornament):
    direction = ""  # up or down
    size = None # music21.interval.Interval (General, etc.) class
    def __init__(self):
        self.size = music21.interval.GenericInterval(2)

class Mordent(GeneralMordent):
    direction = "down"
    def __init__(self):
        GeneralMordent.__init__(self)

class HalfStepMordent(Mordent):
    def __init__(self):
        self.size = music21.interval.stringToInterval("m2")

class WholeStepMordent(Mordent):
    def __init__(self):
        self.size = music21.interval.stringToInterval("M2")

class InvertedMordent(GeneralMordent):
    direction = "up"
    def __init__(self):
        GeneralMordent.__init__(self)

class HalfStepInvertedMordent(InvertedMordent):
    def __init__(self):
        self.size = music21.interval.stringToInterval("m2")

class WholeStepInvertedMordent(InvertedMordent):
    def __init__(self):
        self.size = music21.interval.stringToInterval("M2")

class Trill(Ornament):
    placement = None
    nachschlag = False
    tieAttach = 'all'

    def __init__(self):
        self.size = music21.interval.GenericInterval(2)

    def _getMX(self):
        '''
        Returns a musicxml.TrillMark object
        >>> a = Trill()
        >>> a.placement = 'above'
        >>> mxTrillMark = a.mx
        >>> mxTrillMark.get('placement')
        'above'
        '''
        mxTrillMark = musicxml.TrillMark()
        mxTrillMark.set('placement', self.placement)
        return mxTrillMark


    def _setMX(self, mxTrillMark):
        '''
        Given an mxTrillMark, load instance

        >>> mxTrillMark = musicxml.TrillMark()
        >>> mxTrillMark.set('placement', 'above')
        >>> a = Trill()
        >>> a.mx = mxTrillMark
        >>> a.placement
        'above'
        '''
        self.placement = mxTrillMark.get('placement')

    mx = property(_getMX, _setMX)


class HalfStepTrill(Trill):
    def __init__(self):
        self.size = music21.interval.stringToInterval("m2")

class WholeStepTrill(Trill):
    def __init__(self):
        self.size = music21.interval.stringToInterval("M2")

class Turn(Ornament):
    pass

class InvertedTurn(Ornament):
    pass



class Fermata(music21.Music21Object):
    '''
    Fermatas by default get appended to the last
    note if a note is split because of measures.
    To override this (for Fermatas or for any
    expression) set .tieAttach to 'all' or 'first'
    instead of 'last'. 
    
    >>> from music21 import *
    >>> p1 = stream.Part()
    >>> p1.append(meter.TimeSignature('6/8'))
    >>> n1 = note.Note("D-2")
    >>> n1.quarterLength = 6
    >>> n1.notations.append(expressions.Fermata())
    >>> p1.append(n1)
    >>> #_DOCS_SHOW p1.show()
    .. image:: images/expressionsFermata.*
         :width: 193
    '''
    shape = "normal"
    type  = "upright" # for musicmxml, can be upright, upright-inverted
    lily  = "\\fermata"
    tieAttach = 'last'

    def _getMX(self):
        '''
        Advanced feature: 
        
        As a getter gives the music21.musicxml object for the Fermata
        or as a setter changes the current fermata to have
        the characteristics of the musicxml object to fit this
        type:
        
        >>> from music21 import *
        >>> a = Fermata()
        >>> mxFermata = a.mx
        >>> mxFermata.get('type')
        'upright'

  
        >>> mxFermata2 = musicxml.Fermata()
        >>> mxFermata2.set('type', 'upright-inverted')
        >>> a.mx = mxFermata2
        >>> a.type
        'upright-inverted'

        '''
        mxFermata = musicxml.Fermata()
        mxFermata.set('type', self.type)
        return mxFermata

    def _setMX(self, mxFermata):
        self.type = mxFermata.get('type')

    mx = property(_getMX, _setMX)




#-------------------------------------------------------------------------------
class TestExternal(unittest.TestCase):
    
    def runTest(self):
        pass
    
    def testBasic(self):
        pass


class Test(unittest.TestCase):
    
    def runTest(self):
        pass
    
    def testBasic(self):
        pass

if __name__ == "__main__":
    music21.mainTest(Test)

#------------------------------------------------------------------------------
# eof

