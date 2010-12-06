#!/usr/bin/python
#-------------------------------------------------------------------------------
# Name:         scale.py
# Purpose:      music21 classes for representing scales
#
# Authors:      Michael Scott Cuthbert
#               Christopher Ariza
#
# Copyright:    (c) 2009-2010 The music21 Project
# License:      LGPL
#-------------------------------------------------------------------------------

'''Objects for defining scales. 
'''

import copy
import unittest, doctest

import music21
from music21 import common
from music21 import pitch
from music21 import interval
from music21 import intervalNetwork

from music21.musicxml import translate as musicxmlTranslate



#-------------------------------------------------------------------------------
class ScaleException(Exception):
    pass

class Scale(music21.Music21Object):
    '''
    Generic base class for all scales.
    '''
    def __init__(self):
        self.directionSensitive = False # can be true or false
        self.type = 'Scale' # could be mode, could be other indicator

    def _getName(self):
        '''Return or construct the name of this scale
        '''
        return self.type
        
    name = property(_getName, 
        doc = '''Return or construct the name of this scale.

        ''')


    def _extractPitchList(self, other, comparisonAttribute='nameWithOctave'):
        '''Given a data format, extract all unique pitch space or pitch class values.
        '''
        pre = []
        # if a ConcreteScale, Chord or Stream
        if hasattr(other, 'pitches'):
            pre = other.pitches
        # if a list
        elif common.isListLike(other):
            # assume a list of pitches; possible permit conversions?
            pre = other
        elif hasatter(other, 'pitch'):
            pre = [other.pitch] # get pitch attribute
        return pre




# instead of classes, these can be attributes on the scale object
# class DirectionlessScale(Scale):
#     '''A DirectionlessScale is the same ascending and descending.
#     For instance, the major scale.  
# 
#     A DirectionSensitiveScale has
#     two different forms.  For instance, the natural-minor scale.
#     
#     One could imagine more complex scales that have different forms
#     depending on what scale degree you've just landed on.  Some
#     Ragas might be expressible in that way.'''
#     
#     def ascending(self):
#         return self.pitches
#     
#     def descending(self):
#         tempScale = copy(self.pitches)
#         return tempScale.reverse()
#         ## we perform the reverse on a copy of the pitchList so that
#         ## in case we are multithreaded later in life, we do not have
#         ## a race condition where someone might get self.pitches as
#         ## reversed
# 
# class DirectionSensitiveScale(Scale):
#     pass


#-------------------------------------------------------------------------------
class AbstractScale(Scale):
    '''An abstract scale is specific scale formation, but does not have a defined pitch collection or pitch reference. For example, all Major scales can be represented by an AbstractScale; a ConcreteScale, however, is a specific Major Scale, such as G Major. 

    These classes primarily create and manipulate the stored IntervalNetwork object. Thus, they are rarely created or manipulated directly by most users.
    '''
    isConcrete = False
    def __init__(self):
        Scale.__init__(self)
        # store interval network within abstract scale
        self.net = None
        # in most cases tonic/final of scale is step one, but not always
        self.tonicStep = 1 # step of tonic

    def getStepMaxUnique(self):
        '''Return the maximum number of scale steps, or the number to use as a 
        modulus. 
        '''
        # access from property
        return self.net.stepMaxUnique

    def reverse(self):
        '''Reverse all intervals in this scale.
        '''
        pass

    def getRealization(self, pitchObj, stepOfPitch, 
                        minPitch=None, maxPitch=None):
        '''Realize the abstract scale as a list of pitch objects, given a pitch object, the step of that pitch object, and a min and max pitch.
        '''
        if self.net is None:
            raise ScaleException('no netowrk is defined.')

        return self.net.realizePitch(pitchObj, stepOfPitch, minPitch=minPitch, maxPitch=maxPitch)



class AbstractDiatonicScale(AbstractScale):

    def __init__(self, mode=None):
        AbstractScale.__init__(self)
        self.type = 'Abstract Diatonic'
        self.tonicStep = None # step of tonic
        self.dominantStep = None # step of dominant

        if mode is not None:
            self.buildNetwork(mode=mode)

    def buildNetwork(self, mode=None):
        '''
        Given sub-class dependent parameters, build and assign the IntervalNetwork.

        >>> from music21 import *
        >>> sc = scale.AbstractDiatonicScale()
        >>> sc.buildNetwork('lydian')
        >>> sc.getRealization('f4', 1, 'f2', 'f6') 
        [F2, G2, A2, B2, C3, D3, E3, F3, G3, A3, B3, C4, D4, E4, F4, G4, A4, B4, C5, D5, E5, F5, G5, A5, B5, C6, D6, E6, F6]

        '''

        # nice reference here:
        # http://cnx.org/content/m11633/latest/
        # most diatonic scales will start with this collection
        srcList = ['M2', 'M2', 'm2', 'M2', 'M2', 'M2', 'm2']

        if mode in ['dorian']:
            intervalList = srcList[1:] + srcList[:1] # d to d
            self.tonicStep = 1
            self.dominantStep = 5

        elif mode in ['phrygian']:
            intervalList = srcList[2:] + srcList[:2] # e to e
            self.tonicStep = 1
            self.dominantStep = 5

        elif mode in ['lydian']:
            intervalList = srcList[3:] + srcList[:3] # f to f
            self.tonicStep = 1
            self.dominantStep = 5

        elif mode in ['mixolydian']:
            intervalList = srcList[4:] + srcList[:4] # g to g
            self.tonicStep = 1
            self.dominantStep = 5

        elif mode in ['hypodorian']:
            intervalList = srcList[5:] + srcList[:5] # a to a
            self.tonicStep = 4
            self.dominantStep = 6

        elif mode in ['hypophrygian']:
            intervalList = srcList[6:] + srcList[:6] # b to b
            self.tonicStep = 4
            self.dominantStep = 7

        elif mode in ['hypolydian']: # c to c
            intervalList = srcList
            self.tonicStep = 4
            self.dominantStep = 6

        elif mode in ['hypomixolydian']:
            intervalList = srcList[1:] + srcList[:1] # d to d
            self.tonicStep = 4
            self.dominantStep = 7


        elif mode in ['aeolian', 'minor']:
            intervalList = srcList[5:] + srcList[:5] # a to A
            self.tonicStep = 1
            self.dominantStep = 5

        elif mode in [None, 'major', 'ionian']: # c to C
            intervalList = srcList
            self.tonicStep = 1
            self.dominantStep = 5

        elif mode in ['locrian']:
            intervalList = srcList[6:] + srcList[:6] # b to B
            self.tonicStep = 1
            self.dominantStep = 5

        elif mode in ['hypoaeolian']:
            intervalList = srcList[2:] + srcList[:2] # e to e
            self.tonicStep = 4
            self.dominantStep = 6

        elif mode in ['hupomixolydian']:
            intervalList = srcList[3:] + srcList[:3] # f to f
            self.tonicStep = 4
            self.dominantStep = 7

        self.net = intervalNetwork.IntervalNetwork(intervalList)
        # might also set weights for tonic and dominant here










#-------------------------------------------------------------------------------
class ConcreteScale(Scale):
    '''A concrete scale is specific scale formation with a defined pitch collection (a `tonic` Pitch) that may or may not be bound by specific range. For example, a specific Major Scale, such as G Major, from G2 to G4.

    This class is not generally used directly but is used as a base class for all concrete scales.
    '''

    isConcrete = True

    def __init__(self, tonic=None):
        Scale.__init__(self)

        self.type = 'Concrete'

        # store an instance of an abstract scale
        # subclasses might use multiple abstract scales?
        self._abstract = None

        # determine wether this is a limited range
        self.boundRange = False

        # here, tonic is a pitch
        # the abstract scale defines what step the tonic is expected to be 
        # found on
        if tonic is None:
            self._tonic = pitch.Pitch()
        elif common.isStr(tonic):
            self._tonic = pitch.Pitch(tonic)
        elif hasattr(tonic, 'classes') and 'GeneralNote' in tonic.classes:
            self._tonic = tonic.pitch
        else: # assume this is a pitch object
            self._tonic = tonic


    def _getName(self):
        '''Return or construct the name of this scale
        '''
        return " ".join([self._tonic.name, self.type]) 

    name = property(_getName, 
        doc = '''Return or construct the name of this scale.

        >>> from music21 import *
        >>> sc = scale.DiatonicScale()
        >>> sc.name
        'C Concrete'
        ''')



    def __repr__(self):
        return '<music21.scale.%s %s %s>' % (self.__class__.__name__, self._tonic, self.type)




    def _getMusicXML(self):
        '''Return a complete musicxml representation as an xml string. This must call _getMX to get basic mxNote objects

        >>> from music21 import *
        '''
        from music21 import stream, note
        m = stream.Measure()
        for i in range(1, self._abstract.getStepMaxUnique()+1):
            p = self.pitchFromScaleDegree(i)
            n = note.Note()
            n.pitch = p

            if p.name == self.getTonic().name:
                n.quarterLength = 4 # set longer
            else:
                n.quarterLength = 1
            m.append(n)
        m.timeSignature = m.bestTimeSignature()
        return musicxmlTranslate.measureToMusicXML(m)

    musicxml = property(_getMusicXML, 
        doc = '''Return a complete musicxml representation.
        ''')    


    #---------------------------------------------------------------------------
    def getTonic(self):
        '''Return the tonic. 

        This method may be overridden by subclasses that have alternative definitions of tonic. 

        >>> from music21 import *
        >>> sc = scale.ConcreteScale('e-')
        >>> sc.getTonic()
        E-
        '''
        return self._tonic


    def getAbstract(self):
        '''Return the underlying abstract scale
        '''
        # TODO: make abstract a property?
        # copy before returning?
        return self._abstract

    def transpose(self, value, inPlace=False):
        '''Transpose this Scale by the given interval
        '''
        # note: it does not makes sense to transpose an abstract scale;
        # thus, only concrete scales can be transposed. 
        pass

    def getPitches(self, minPitch=None, maxPitch=None, direction=None):
        '''Return a list of Pitch objects, using a deepcopy of a cached version if available. 
        '''
        # get from interval network of abstract scale
        if self._abstract is not None:
            # TODO: get and store in cache; return a copy
            # or generate from network stored in abstract
            pitchObj = self._tonic
            stepOfPitch = self._abstract.tonicStep

            # this creates new pitches on each call
            return self._abstract.getRealization(pitchObj, stepOfPitch, 
                        minPitch=minPitch, maxPitch=maxPitch)

            #return self._abstract.net.realizePitch(self._tonic, 1)
        else:
            return []
        #raise ScaleException("Cannot generate a scale from a DiatonicScale class")

    pitches = property(getPitches, 
        doc ='''Get a default pitch list from this scale.
        ''')

    def pitchFromScaleDegree(self, degree, direction=None):        

        '''Given a scale degree, return the appropriate pitch. 

        >>> from music21 import *
        >>> sc = scale.MajorScale('e-')
        >>> sc.pitchFromScaleDegree(2)
        F4
        >>> sc.pitchFromScaleDegree(7)
        D5
        '''
        # TODO: rely here on intervalNetwork for caching
        post = self._abstract.net.getPitchFromNodeStep(
            pitchReference=self._tonic, # pitch defined here
            nodeName=self._abstract.tonicStep, # defined in abstract class
            nodeStepTarget=degree, # target looking for
            direction=direction, 
            minPitch=None, 
            maxPitch=None)
        return post

#         if 0 < degree <= self._abstract.getStepMaxUnique(): 
#             return self.getPitches()[degree - 1]
#         else: 
#             raise("Scale degree is out of bounds: must be between 1 and %s." % self._abstract.getStepMaxUnique())


    def getScaleDegreeFromPitch(self, pitchTarget, direction=None, 
            comparisonAttribute='pitchClass'):
        '''For a given pitch, return the appropriate scale degree. If no scale degree is available, None is returned.

        >>> from music21 import *
        >>> sc = scale.MajorScale('e-')
        >>> sc.getScaleDegreeFromPitch('e-2')
        1
        >>> sc.getScaleDegreeFromPitch('d')
        7
        >>> sc.getScaleDegreeFromPitch('d#', comparisonAttribute='name') == None
        True
        '''

        post = self._abstract.net.getRelativeNodeStep(
            pitchReference=self._tonic, 
            nodeName=self._abstract.tonicStep, 
            pitchTarget=pitchTarget,      
            comparisonAttribute=comparisonAttribute)
        return post


#     def ascending(self):
#         '''Return ascending scale form.
#         '''
#         # get from pitch cache
#         return self.getPitches()
#     
#     def descending(self):
#         '''Return descending scale form.
#         '''
#         # get from pitch cache
#         tempScale = copy(self.getPitches())
#         tempScale.reverse()
#         return tempScale



    #---------------------------------------------------------------------------
    # comparison and evaluation

    def match(self, other, comparisonAttribute='pitchClass'):
        '''Given another object of various forms (e.g., a Stream, a ConcreteScale, a list of pitches), return a named dictionary of pitch lists with keys 'matched' and 'notMatched'.

        >>> from music21 import *
        >>> sc1 = scale.MajorScale('g')
        >>> sc2 = scale.MajorScale('d')
        >>> sc3 = scale.MajorScale('a')
        >>> sc4 = scale.MajorScale('e')
        >>> sc1.match(sc2)
        {'notMatched': [C#5], 'matched': [D, E4, F#4, G4, A4, B4, D5]}
        >>> sc2.match(sc3)
        {'notMatched': [G#5], 'matched': [A, B4, C#5, D5, E5, F#5, A5]}

        >>> sc1.match(sc4)
        {'notMatched': [G#4, C#5, D#5], 'matched': [E, F#4, A4, B4, E5]}

        '''

        # strip out unique pitches in a list
        # to do a pitch spa

        otherPitches = self._extractPitchList(other,
                        comparisonAttribute=comparisonAttribute)

        # need to deal with direction here? or get an aggregate scale
        matched, notMatched = self._abstract.net.match(
            pitchReference=self._tonic, 
            nodeId=self._abstract.tonicStep, 
            pitchTarget=otherPitches, # can supply a list here
            comparisonAttribute=comparisonAttribute)

        post = {}
        post['matched'] = matched
        post['notMatched'] = notMatched
        return post





    def deriveRanked(self, other, resultsReturned=4,
         comparisonAttribute='pitchClass'):
        '''Return a list of closest matching concrete scales given a collection of pitches, provided as a Stream, a ConcreteScale, a list of pitches)

        >>> from music21 import *
        >>> sc1 = scale.MajorScale('g')
        >>> sc1.deriveRanked(['c', 'e', 'b'])
        [(3, <music21.scale.MajorScale G major>), (3, <music21.scale.MajorScale C major>), (2, <music21.scale.MajorScale B major>), (2, <music21.scale.MajorScale A major>)]
        >>> sc1.deriveRanked(['c#', 'e', 'g#'])
        [(3, <music21.scale.MajorScale B major>), (3, <music21.scale.MajorScale A major>), (3, <music21.scale.MajorScale E major>), (3, <music21.scale.MajorScale C- major>)]

        '''
        otherPitches = self._extractPitchList(other,
                        comparisonAttribute=comparisonAttribute)

        pairs = self._abstract.net.find(pitchTarget=otherPitches,
                             resultsReturned=resultsReturned,
                             comparisonAttribute=comparisonAttribute)

        post = []
        for weight, p in pairs:
            sc = self.__class__(tonic=p)
            post.append((weight, sc))
        return post

    def derive(self, other, resultsReturned=4, 
        comparisonAttribute='pitchClass'):
        '''
        >>> from music21 import *
        >>> sc1 = scale.MajorScale('g')
        >>> sc1.derive(['c#', 'e', 'g#'])
        <music21.scale.MajorScale B major>
        >>> sc1.derive(['e-', 'b-', 'd'], comparisonAttribute='name')
        <music21.scale.MajorScale B- major>
        '''
        otherPitches = self._extractPitchList(other,
                        comparisonAttribute=comparisonAttribute)

        # weight target membership
        pairs = self._abstract.net.find(pitchTarget=otherPitches,
                             resultsReturned=resultsReturned,
                            comparisonAttribute=comparisonAttribute)


        return self.__class__(tonic=pairs[0][1])





class DiatonicScale(ConcreteScale):
    '''A concrete diatonic scale. Assumes that all such scales have 
    '''

    isConcrete = True

    def __init__(self, tonic=None):
        ConcreteScale.__init__(self, tonic=tonic)
        self._abstract = AbstractDiatonicScale()

    def getTonic(self):
        '''Return the dominant. 

        >>> from music21 import *
        >>> sc = scale.MajorScale('e-')
        >>> sc.getDominant()
        B-4
        >>> sc = scale.MajorScale('F#')
        >>> sc.getDominant()
        C#5
        '''
        # NOTE: override method on ConcreteScale that simply returns _tonic
        return self.pitchFromScaleDegree(self._abstract.tonicStep)

    def getDominant(self):
        '''Return the dominant. 

        >>> from music21 import *
        >>> sc = scale.MajorScale('e-')
        >>> sc.getDominant()
        B-4
        >>> sc = scale.MajorScale('F#')
        >>> sc.getDominant()
        C#5
        '''
        return self.pitchFromScaleDegree(self._abstract.dominantStep)
    

    def getLeadingTone(self):
        '''Return the leading tone. 

        >>> from music21 import *
        >>> sc = scale.MinorScale('c')
        >>> sc.pitchFromScaleDegree(7)
        B-4
        >>> sc.getLeadingTone()
        B4
        >>> sc.getDominant()
        G4

        '''
        # NOTE: must be adjust for modes that do not have a proper leading tone
        interval1to7 = interval.notesToInterval(self._tonic, 
                        self.pitchFromScaleDegree(7))
        if interval1to7.name != 'M7':
            # if not a major seventh from the tonic, get a pitch a M7 above
            return interval.transposePitch(self.pitchFromScaleDegree(1), "M7")
        else:
            return self.pitchFromScaleDegree(7)


    def _getMusicXML(self):
        '''Return a complete musicxml representation as an xml string. This must call _getMX to get basic mxNote objects

        >>> from music21 import *
        '''
        from music21 import stream, note
        m = stream.Measure()
        for i in range(1, self._abstract.getStepMaxUnique()+1):
            p = self.pitchFromScaleDegree(i)
            n = note.Note()
            n.pitch = p

            if p.name == self.getTonic().name:
                n.quarterLength = 4 # set longer
            elif p.name == self.getDominant().name:
                n.quarterLength = 2 # set longer
            else:
                n.quarterLength = 1
            m.append(n)
        m.timeSignature = m.bestTimeSignature()
        return musicxmlTranslate.measureToMusicXML(m)

    musicxml = property(_getMusicXML, 
        doc = '''Return a complete musicxml representation.
        ''')    



#-------------------------------------------------------------------------------
class MajorScale(DiatonicScale):
    '''A Major Scale

    >>> sc = MajorScale(pitch.Pitch('d'))
    >>> sc.pitchFromScaleDegree(7).name
    'C#'
    '''
    
    def __init__(self, tonic=None):

        DiatonicScale.__init__(self, tonic=tonic)
        self.type = "major"
        # build the network for the appropriate scale
        self._abstract.buildNetwork(self.type)


    def getRelativeMinor(self):
        '''Return a relative minor scale based on this concrete major scale.

        >>> sc1 = MajorScale(pitch.Pitch('a'))
        >>> sc1.pitches
        [A, B4, C#5, D5, E5, F#5, G#5, A5]
        >>> sc2 = sc1.getRelativeMinor()
        >>> sc2.pitches
        [F#5, G#5, A5, B5, C#6, D6, E6, F#6]
        '''
        return MinorScale(self.pitchFromScaleDegree(6))

    def getParallelMinor(self):
        '''Return a parallel minor scale based on this concrete major scale.

        >>> sc1 = MajorScale(pitch.Pitch('a'))
        >>> sc1.pitches
        [A, B4, C#5, D5, E5, F#5, G#5, A5]
        >>> sc2 = sc1.getParallelMinor()
        >>> sc2.pitches
        [A, B4, C5, D5, E5, F5, G5, A5]
        '''
        return MinorScale(self._tonic)




class MinorScale(DiatonicScale):
    '''A natural minor scale, or the Aeolian mode.

    >>> sc = MinorScale(pitch.Pitch('g'))
    >>> sc.pitches
    [G, A4, B-4, C5, D5, E-5, F5, G5]
    '''
    def __init__(self, tonic=None):
        DiatonicScale.__init__(self, tonic=tonic)
        self.type = "minor"
        self._abstract.buildNetwork(self.type)

    def getRelativeMajor(self):
        '''Return a concrete relative major scale

        >>> sc1 = MinorScale(pitch.Pitch('g'))
        >>> sc1.pitches
        [G, A4, B-4, C5, D5, E-5, F5, G5]
        >>> sc2 = sc1.getRelativeMajor()
        >>> sc2.pitches
        [B-4, C5, D5, E-5, F5, G5, A5, B-5]
        '''
        return MajorScale(self.pitchFromScaleDegree(3))

    def getParallelMajor(self):
        '''Return a concrete relative major scale

        >>> sc1 = MinorScale(pitch.Pitch('g'))
        >>> sc1.pitches
        [G, A4, B-4, C5, D5, E-5, F5, G5]
        >>> sc2 = sc1.getParallelMajor()
        >>> sc2.pitches
        [G, A4, B4, C5, D5, E5, F#5, G5]
        '''
        return MajorScale(self._tonic)



class DorianScale(DiatonicScale):
    '''A natural minor scale, or the Aeolian mode.

    >>> sc = DorianScale(pitch.Pitch('d'))
    >>> sc.pitches
    [D, E4, F4, G4, A4, B4, C5, D5]
    '''
    def __init__(self, tonic=None):
        DiatonicScale.__init__(self, tonic=tonic)
        self.type = "dorian"
        self._abstract.buildNetwork(self.type)


class PhrygianScale(DiatonicScale):
    '''A phrygian scale

    >>> sc = PhrygianScale(pitch.Pitch('e'))
    >>> sc.pitches
    [E, F4, G4, A4, B4, C5, D5, E5]
    '''
    def __init__(self, tonic=None):
        DiatonicScale.__init__(self, tonic=tonic)
        self.type = "phrygian"
        self._abstract.buildNetwork(self.type)



class HypophrygianScale(DiatonicScale):
    '''A hypophrygian scale

    >>> sc = HypophrygianScale(pitch.Pitch('e'))
    >>> sc.pitches
    [B3, C4, D4, E, F4, G4, A4, B4]
    >>> sc.getTonic()
    E
    >>> sc.getDominant()
    A4
    >>> sc.pitchFromScaleDegree(1) # scale degree 1 is treated as lowest
    B3
    '''
    def __init__(self, tonic=None):
        DiatonicScale.__init__(self, tonic=tonic)
        self.type = "hypophrygian"
        self._abstract.buildNetwork(self.type)



#     def getConcreteHarmonicMinorScale(self):
#         scale = self.pitches[:]
#         scale[6] = self.getLeadingTone()
#         scale.append(interval.transposePitch(self._tonic, "P8"))
#         return scale

#     def getAbstractHarmonicMinorScale(self):
#         concrete = self.getConcreteHarmonicMinorScale()
#         abstract = copy.deepcopy(concrete)
#         for pitch1 in abstract:
#             pitch1.octave = 0 #octave 0 means "octaveless"
#         return abstract
# 

# melodic minor will be implemented in a different way
#     def getConcreteMelodicMinorScale(self):
#         scale = self.getConcreteHarmonicMinorScale()
#         scale[5] = interval.transposePitch(self.pitchFromScaleDegree(6), "A1")
#         for n in range(0, 7):
#             scale.append(self.pitchFromScaleDegree(7-n))
#         return scale
# 
#     def getAbstractMelodicMinorScale(self):
#         concrete = self.getConcreteMelodicMinorScale()
#         abstract = copy.deepcopy(concrete)
#         for pitch1 in abstract:
#             pitch1.octave = 0 #octave 0 means "octaveless"
#         return abstract






#-------------------------------------------------------------------------------
class Test(unittest.TestCase):
    
    def runTest(self):
        pass


    def testBasicLegacy(self):
        from music21 import note

        n1 = note.Note()
        
        CMajor = MajorScale(n1)
        
        assert CMajor.name == "C major"
        assert CMajor.getPitches()[6].step == "B"
        
#         CScale = CMajor.getConcreteMajorScale()
#         assert CScale[7].step == "C"
#         assert CScale[7].octave == 5
#         
#         CScale2 = CMajor.getAbstractMajorScale()
#         
#         for note1 in CScale2:
#             assert note1.octave == 0
#             #assert note1.duration.type == ""
#         assert [note1.name for note1 in CScale] == ["C", "D", "E", "F", "G", "A", "B", "C"]
        
        seventh = CMajor.pitchFromScaleDegree(7)
        assert seventh.step == "B"
        
        dom = CMajor.getDominant()
        assert dom.step == "G"
        
        n2 = note.Note()
        n2.step = "A"
        
        aMinor = CMajor.getRelativeMinor()
        assert aMinor.name == "A minor", "Got a different name: " + aMinor.name
        
        notes = [note1.name for note1 in aMinor.getPitches()]
        self.assertEqual(notes, ["A", "B", "C", "D", "E", "F", "G", 'A'])
        
        n3 = note.Note()
        n3.name = "B-"
        n3.octave = 5
        
        bFlatMinor = MinorScale(n3)
        assert bFlatMinor.name == "B- minor", "Got a different name: " + bFlatMinor.name
        notes2 = [note1.name for note1 in bFlatMinor.getPitches()]
        self.assertEqual(notes2, ["B-", "C", "D-", "E-", "F", "G-", "A-", 'B-'])
        assert bFlatMinor.getPitches()[0] == n3
        assert bFlatMinor.getPitches()[6].octave == 6
        
#         harmonic = bFlatMinor.getConcreteHarmonicMinorScale()
#         niceHarmonic = [note1.name for note1 in harmonic]
#         assert niceHarmonic == ["B-", "C", "D-", "E-", "F", "G-", "A", "B-"]
#         
#         harmonic2 = bFlatMinor.getAbstractHarmonicMinorScale()
#         assert [note1.name for note1 in harmonic2] == niceHarmonic
#         for note1 in harmonic2:
#             assert note1.octave == 0
#             #assert note1.duration.type == ""
        
#         melodic = bFlatMinor.getConcreteMelodicMinorScale()
#         niceMelodic = [note1.name for note1 in melodic]
#         assert niceMelodic == ["B-", "C", "D-", "E-", "F", "G", "A", "B-", "A-", "G-", \
#                                "F", "E-", "D-", "C", "B-"]
        
#         melodic2 = bFlatMinor.getAbstractMelodicMinorScale()
#         assert [note1.name for note1 in melodic2] == niceMelodic
#         for note1 in melodic2:
#             assert note1.octave == 0
            #assert note1.duration.type == ""
        
        cNote = bFlatMinor.pitchFromScaleDegree(2)
        assert cNote.name == "C"
        fNote = bFlatMinor.getDominant()
        assert fNote.name == "F"
        
        bFlatMajor = bFlatMinor.getParallelMajor()
        assert bFlatMajor.name == "B- major"
#         scale = [note1.name for note1 in bFlatMajor.getConcreteMajorScale()]
#         assert scale == ["B-", "C", "D", "E-", "F", "G", "A", "B-"]
        
        dFlatMajor = bFlatMinor.getRelativeMajor()
        assert dFlatMajor.name == "D- major"
        assert dFlatMajor.getTonic().name == "D-"
        assert dFlatMajor.getDominant().name == "A-"





    def testDeriveA(self):
        # deriving a scale from a Stream

        from music21 import corpus
        s = corpus.parseWork('bwv66.6')

        # just get default, c-major, as derive will check all tonics

        sc1 = MajorScale()
        sc2 = MinorScale()
        sc3 = sc1.derive(s.parts['soprano'])
        self.assertEqual(str(sc3), '<music21.scale.MajorScale A major>')

        sc3 = sc1.derive(s.parts['tenor'])
        self.assertEqual(str(sc3), '<music21.scale.MajorScale A major>')

        sc3 = sc2.derive(s.parts['bass'])
        self.assertEqual(str(sc3), '<music21.scale.MinorScale F# minor>')



#-------------------------------------------------------------------------------
if __name__ == "__main__":
    import sys

    if len(sys.argv) == 1: # normal conditions
        music21.mainTest(Test)
    elif len(sys.argv) > 1:
        t = Test()



#------------------------------------------------------------------------------
# eof

