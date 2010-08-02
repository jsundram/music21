#!/usr/bin/python
#-------------------------------------------------------------------------------
# Name:         windowed.py
# Purpose:      Framework for modular, windowed analysis
#
# Authors:      Jared Sadoian
# Authors:      Christopher Ariza
#
# Copyright:    (c) 2010 The music21 Project
# License:      LGPL
#-------------------------------------------------------------------------------

'''Modular analysis procedures for use alone or applied with :class:`music21.analysis.windowed.WindowedAnalysis` class. 

All procedures should inherit from :class:`music21.analysis.discrete.DiscreteAnalysis`, or provide a similar interface. 

The :class:`music21.analysis.discrete.KrumhanslSchmuckler` (for algorithmic key detection) and :class:`music21.analysis.discrete.SadoianAmbitus` (for pitch range analysis) provide examples.
'''

import unittest
import sys
import music21

from music21 import meter
from music21.pitch import Pitch
from music21 import stream 



from music21 import environment
_MOD = 'discrete.py'
environLocal = environment.Environment(_MOD)



#------------------------------------------------------------------------------
class DiscreteAnalysisException(Exception):
    pass

class DiscreteAnalysis(object):
    ''' Parent class for analytical methods.

    Each analytical method returns a discrete numerical (or other) results as well as a color. Colors can be used in mapping output.

    Analytical methods may make use of a `referenceStream` to configure the processor on initialization. 
    '''
    def __init__(self, referenceStream=None):
        # store a reference stream if needed
        self._referenceStream = referenceStream

        # store unique solutions encountered over a single run; this can be used
        # to configure the generation of a legend based only on the values 
        # that have been produced.
        # store pairs of sol, color
        self._solutionsFound = []

    def _rgbToHex(self, rgb):
        '''Utility conversion method
        '''
        rgb = int(round(rgb[0])), int(round(rgb[1])), int(round(rgb[2]))
        return '#%02x%02x%02x' % rgb    

    def _hexToRgb(self, value):
        '''Utility conversion method    
        >>> da = DiscreteAnalysis()
        >>> da._hexToRgb('#ffffff')
        [255, 255, 255]
        >>> da._hexToRgb('#000000')
        [0, 0, 0]
        '''
        value = value.lstrip('#')
        lv = len(value)
        return list(int(value[i:i+lv/3], 16) for i in range(0, lv, lv/3))

    def _rgbLimit(self, value):
        '''Utility conversion method    
        >>> da = DiscreteAnalysis()
        >>> da._rgbLimit(300)
        255
        >>> da._rgbLimit(-30)
        0
        '''
        if value < 0:
            value = 0
        elif value > 255:
            value = 255
        return value


    def clearSolutionsFound(self):
        '''Clear all stored solutions 
        '''
        self._solutionsFound = []

    def getColorsUsed(self):
        '''Based on solutions found so far with with this processor, return the colors that have been used.
        '''
        post = []
        for solution, color in self._solutionsFound:
            if color not in post:
                post.append(color)
        return post    

    def solutionLegend(self, compress=False):
        '''A list of pairs showing all discrete results and the assigned color. Data should be organized to be passed to :class:`music21.graph.GraphColorGridLegend`.

        If `compress` is True, the legend will only show values for solutions that have been encountered. 
        '''
        pass
    
    def solutionToColor(self, result):
        '''Given a analysis specific result, return the appropriate color. Must be able to handle None in the case that there is no result.
        '''
        pass
    
    def process(self, subStream):
        '''For a given Stream, apply the analysis to all components of this Stream.
        '''
        pass


    def getSolution(self, subStream):
        '''For a given Stream, apply the analysis and return the best solution.
        '''
        pass


#------------------------------------------------------------------------------
class KrumhanslSchmuckler(DiscreteAnalysis):
    ''' Implementation of the Krumhansl-Schmuckler key determination algorithm
    '''
    _DOC_ALL_INHERITED = False

    name = 'Krumhansl Schmuckler Key Analysis'

    def __init__(self, referenceStream=None):
        DiscreteAnalysis.__init__(self, referenceStream=referenceStream)
        
        # need a presentation order for legend; not alphabetical
        self._keySortOrder = ['C-', 'C', 'C#',
                              'D-', 'D', 'D#',
                              'E-', 'E', 'E#',
                              'F-', 'F', 'F#',
                              'G-', 'G', 'G#',
                              'A-', 'A', 'A#',
                              'B-', 'B', 'B#',
                            ]

    def _getWeights(self, weightType='major'): 
        ''' Returns either the a weight key profile as described by Sapp and others
            
        >>> a = KrumhanslSchmuckler()
        >>> len(a._getWeights('major'))
        12
        >>> len(a._getWeights('minor'))
        12            
        '''
        weightType = weightType.lower()
        if weightType == 'major':
            return [6.35, 2.33, 3.48, 2.33, 4.38, 4.09, 2.52, 5.19, 2.39, 3.66, 2.29, 2.88]
        elif weightType == 'minor':
            return [6.33, 2.68, 3.52, 5.38, 2.60, 3.53, 2.54, 4.75, 3.98, 2.69, 3.34, 3.17]    
        else:
            raise DiscreteAnalysisException('no weights defined for weight type: %s' % weightType)

    def _getPitchClassDistribution(self, streamObj):
        '''Given a flat Stream, obtain a pitch class distribution. The value of each pitch class is scaled by its duration in quarter lengths.

        >>> from music21 import note, stream, chord
        >>> a = KrumhanslSchmuckler()
        >>> s = stream.Stream()
        >>> n1 = note.Note('c')
        >>> n1.quarterLength = 3
        >>> n2 = note.Note('f#')
        >>> n2.quarterLength = 2
        >>> s.append(n1)
        >>> s.append(n2)
        >>> a._getPitchClassDistribution(s)
        [3, 0, 0, 0, 0, 0, 2, 0, 0, 0, 0, 0]
        >>> c1 = chord.Chord(['d', 'e', 'b-'])
        >>> c1.quarterLength = 1.5
        >>> s.append(c1)
        >>> a._getPitchClassDistribution(s)
        [3, 0, 1.5, 0, 1.5, 0, 2, 0, 0, 0, 1.5, 0]
        '''
        pcDist = [0]*12
        
        for n in streamObj.notes:        
            if not n.isRest:
                length = n.quarterLength
                if n.isChord:
                    for m in n.pitchClasses:
                        pcDist[m] = pcDist[m] + (1 * length)
                else:
                    pcDist[n.pitchClass] = pcDist[n.pitchClass] + (1 * length)
        
        return pcDist


    def _convoluteDistribution(self, pcDistribution, weightType='major'):
        ''' Takes in a pitch class distribution as a list and convolutes it
            over Sapp's given distribution for finding key, returning the result. 
        '''
        soln = [0] * 12
        toneWeights = self._getWeights(weightType)
                
        for i in range(len(soln)):
            for j in range(len(pcDistribution)):
                soln[i] = soln[i] + (toneWeights[(j - i) % 12] * pcDistribution[j])
            
        return soln  
    
    def _getLikelyKeys(self, keyResults, differences):
        ''' Takes in a list of probably key results in points and returns a
            list of keys in letters, sorted from most likely to least likely
        '''
        likelyKeys = [0] * 12
        a = sorted(keyResults)
        a.reverse()
        
        #Return pairs, the pitch class and the correlation value, in order by point value
        for i in range(len(a)):
            likelyKeys[i] = (Pitch(keyResults.index(a[i])), differences[keyResults.index(a[i])])
        
        return likelyKeys
        
        
    def _getDifference(self, keyResults, pcDistribution, weightType):
        ''' Takes in a list of numerical probable key results and returns the
            difference of the top two keys
        '''
            
        soln = [0]*12
        top = [0]*12
        bottomRight = [0]*12
        bottomLeft = [0]*12
            
        toneWeights = self._getWeights(weightType)

        profileAverage = float(sum(toneWeights))/len(toneWeights)
        histogramAverage = float(sum(pcDistribution))/len(pcDistribution) 
            
        for i in range(len(soln)):
            for j in range(len(toneWeights)):
                top[i] = top[i] + ((
                    toneWeights[(j - i) % 12]-profileAverage) * (
                    pcDistribution[j]-histogramAverage))

                bottomRight[i] = bottomRight[i] + ((
                    toneWeights[(j-i)%12]-profileAverage)**2)

                bottomLeft[i] = bottomLeft[i] + ((
                    pcDistribution[j]-histogramAverage)**2)

                if (bottomRight[i] == 0 or bottomLeft[i] == 0):
                    soln[i] = 0
                else:
                    soln[i] = float(top[i]) / ((bottomRight[i]*bottomLeft[i])**.5)
        return soln    

    def solutionLegend(self, compress=False):
        ''' Returns a list of lists of possible results for the creation of a legend.

        >>> from music21 import *
        >>> p = analysis.discrete.KrumhanslSchmuckler()
        >>> post = p.solutionLegend()

        '''
        if compress:
            colorsUsed = self.getColorsUsed()
            environLocal.printDebug(['colors used:', colorsUsed])

        data = []
        for yLabel in ['Major', 'Minor']:
            row = []
            row.append(yLabel)
            pairs = []
            for key in self._keySortOrder:
                color = self.solutionToColor([key, yLabel])
                if compress:
                    if color not in colorsUsed:
                        # set as white so as to maintain spacing
                        color = '#ffffff' 
                # replace all '-' with 'b' (or proper flat symbol)
                key = key.replace('-', 'b')
                # make minor keys in lower case
                if yLabel == 'Minor':
                    key = key.lower()
                pairs.append((key, color))
            row.append(pairs)
            data.append(row)    
        return data
    
    def solutionToColorBright(self, solution):
        '''For a given solution, return the color.
        '''

        # store color grid information to associate particular keys to colors
        # note: these colors were manually selected to optimize distinguishing
        # characteristics. do not change without good reason
        majorKeyColors = {'E-':'#D60000',
                 'E':'#FF0000',
                 'E#':'#FF2B00',
                 'B-':'#FF5600',
                 'B':'#FF8000',
                 'B#':'#FFAB00',
                 'F-':'#FFD600', # was #FFFD600
                 'F':'#FFFF00',
                 'F#':'#AAFF00',
                 'C-':'#55FF00',
                 'C':'#00FF00',
                 'C#':'#00AA55',
                 'G-':'#0055AA',
                 'G':'#0000FF',
                 'G#':'#2B00FF',
                 'D-':'#5600FF',
                 'D':'#8000FF',
                 'D#':'#AB00FF',
                 'A-':'#D600FF',
                 'A':'#FF00FF',
                 'A#':'#FF55FF'}
        minorKeyColors = {'E-':'#720000',
                 'E':'#9b0000',
                 'E#':'#9b0000',
                 'B-':'#9b0000',
                 'B':'#9b2400',
                 'B#':'#9b4700',
                 'F-':'#9b7200',
                 'F':'#9b9b00',
                 'F#':'#469b00',
                 'C-':'#009b00',
                 'C':'#009b00',
                 'C#':'#004600',
                 'G-':'#000046',
                 'G':'#00009B',
                 'G#':'#00009B',
                 'D-':'#00009b',
                 'D':'#24009b',
                 'D#':'#47009b',
                 'A-':'#72009b',
                 'A':'#9b009b',
                 'A#':'#9b009b'}


        key = solution[0]
        modality = solution[1].lower()
        if modality == "major":
            return majorKeyColors[str(key)]
        elif modality == "minor":
            return minorKeyColors[str(key)]
        
    
    def solutionToColor(self, solution):

        key = solution[0]
        modality = solution[1].lower()

        # for each step, assign a color
        # names taken from http://chaos2.org/misc/rgb.html
        # idea is basically:
        # red, orange, yellow, green, cyan, blue, purple, pink
        stepLib = {'C': '#CD4F39', # tomato3
                'D': '#DAA520', # goldenrod
              #  'E': '#CDBE70', # LightGoldenrod1
                'E': '#BCEE68', # DarkOliveGreen2
                'F': '#96CDCD', # PaleTurquoise3
                'G': '#6495ED', # cornflower blue
                'A': '#8968CD', # MediumPurple3
                'B': '#FF83FA', # orchid1

                } 
        # first char is always step
        step = key[0]

        rgbStep = self._hexToRgb(stepLib[step])


        # make all the colors a but lighter
        for i in range(len(rgbStep)):
            rgbStep[i] = self._rgbLimit(rgbStep[i] + 30)


        #make minor darker
        if modality == 'minor':
            for i in range(len(rgbStep)):
                rgbStep[i] = self._rgbLimit(rgbStep[i] - 80)

        if len(key) > 1:
            if key[1] == '-':
                # index and value shift
                shiftLib = {0: 10, 1: 15, 2:-15}                   
            elif key[1] == '#':                   
                shiftLib = {0: -10, 1: -15, 2:15}      
             
            for i in shiftLib.keys():
                rgbStep[i] = self._rgbLimit(rgbStep[i] + shiftLib[i])


        return self._rgbToHex(rgbStep)


    def getSolution(self, sStream):
        ''' procedure to only return a text solution
        >>> from music21 import *
        >>> s = corpus.parseWork('bach/bwv66.6')
        >>> p = KrumhanslSchmuckler()
        >>> p.getSolution(s) # this seems correct
        ('F#', 'minor', 0.81547089257624916)

        >>> s = corpus.parseWork('bach/bwv57.8')
        >>> p = KrumhanslSchmuckler()
        >>> p.getSolution(s) # should be b- major
        ('A#', 'major', 0.89772788962941652)

        '''
        # always take a flat version here, otherwise likely to get nothing
        solution, color = self.process(sStream.flat)
        return solution
    
    
    def process(self, sStream):    
        ''' Takes in a Stream or sub-Stream and performs analysis on all contents of the Stream. A windowing system can be used to get partial results. 

        Returns two values, a data list and a color string.

        The data list contains a key (as a string), a mode (as a string), and a correlation value (degree of certainty)
        '''
    
        # this is the sample distribution used in the paper, for some testing purposes
        #pcDistribution = [7,0,5,0,7,16,0,16,0,15,6,0]
        
        # this is the distribution for the melody of "happy birthday"
        #pcDistribution = [9,0,3,0,2,5,0,2,0,2,2,0]
    
        pcDistribution = self._getPitchClassDistribution(sStream)
    
        keyResultsMajor = self._convoluteDistribution(pcDistribution,'major')
        differenceMajor = self._getDifference(keyResultsMajor, 
                         pcDistribution, 'major')
        likelyKeysMajor = self._getLikelyKeys(keyResultsMajor, differenceMajor)
        

        keyResultsMinor = self._convoluteDistribution(pcDistribution,'minor')   
        differenceMinor = self._getDifference(keyResultsMinor, 
                          pcDistribution, 'minor')
        likelyKeysMinor = self._getLikelyKeys(keyResultsMinor, differenceMinor)
        
        #find the largest correlation value to use to select major or minor as the resulting key
        if likelyKeysMajor[0][1] > likelyKeysMinor[0][1]:
            solution = (str(likelyKeysMajor[0][0]), "major", likelyKeysMajor[0][1])
        else:
            solution = (str(likelyKeysMinor[0][0]), "minor", likelyKeysMinor[0][1])
            
        color = self.solutionToColor(solution)

        # store solutions for compressed legend generation
        self._solutionsFound.append((solution, color))
        return solution, color        
    


#------------------------------------------------------------------------------
class SadoianAmbitus(DiscreteAnalysis):
    '''An basic analysis method for measuring register. 
    '''
    _DOC_ALL_INHERITED = False

    name = 'Sadoian Ambitus Analysis'

    def __init__(self, referenceStream=None):
        DiscreteAnalysis.__init__(self, referenceStream=referenceStream)
        self._pitchSpanColors = {}
        self._generateColors()


    def _generateColors(self, numColors=None):
        '''Provide uniformly distributed colors across the entire range.
        '''
        if numColors == None:
            if self._referenceStream != None:
                # get total range for entire piece
                min, max = self._getPitchRanges(self._referenceStream)
            else:
                min, max = 0, 130 # a large default
        else: # create min max
            min, max = 0, numColors

        valueRange = max - min
        step = 0
        antiBlack = 25
        for i in range(min, max+1):
            # do not use all 255 to avoid going to black
            val = int(round(((255.0 - antiBlack)/ valueRange) * step)) + antiBlack
            # store in dictionary the accepted values, not the step
            self._pitchSpanColors[i] = self._rgbToHex(((val*.75), (val*.6), val))
            step += 1

        #environLocal.printDebug([self._pitchSpanColors])
    
    def _getPitchSpan(self, subStream):
        '''For a given subStream, return a value in half-steps of the range

        >>> from music21 import *
        >>> s = corpus.parseWork('bach/bwv66.6')
        >>> p = SadoianAmbitus()
        >>> p._getPitchSpan(s.parts[0].getElementsByClass('Measure')[3])
        (66, 71)
        >>> p._getPitchSpan(s.parts[0].getElementsByClass('Measure')[6])
        (69, 73)

        >>> s = stream.Stream()
        >>> c = chord.Chord(['a2', 'b4', 'c8'])
        >>> s.append(c)
        >>> p._getPitchSpan(s)
        (45, 108)
        '''
        
        if len(subStream.flat.notes) == 0:
            # need to handle case of no pitches
            return None

        # find the min and max pitch space value for all pitches
        psFound = []
        for n in subStream.flat.notes:
            pitches = []
            if 'Chord' in n.classes:
                pitches = n.pitches
            elif 'Note' in n.classes:
                pitches = [n.pitch]

            psFound += [p.ps for p in pitches]
        # use built-in functions
        return int(min(psFound)), int(max(psFound))

    
    def _getPitchRanges(self, subStream):
        '''For a given subStream, return the smallest difference between any two pitches and the largest difference between any two pitches. This is used to get the smallest and larges ambitus possible in a given work. 

        >>> from music21 import *
        >>> p = SadoianAmbitus()
        >>> s = stream.Stream()
        >>> c = chord.Chord(['a2', 'b4', 'c8'])
        >>> s.append(c)
        >>> p._getPitchSpan(s)
        (45, 108)
        >>> p._getPitchRanges(s)
        (26, 63)

        >>> s = corpus.parseWork('bach/bwv66.6')
        >>> p._getPitchRanges(s)
        (0, 34)
        '''
        psFound = []
        for n in subStream.flat.notes:
            pitches = []
            if 'Chord' in n.classes:
                pitches = n.pitches
            elif 'Note' in n.classes:
                pitches = [n.pitch]
            for p in pitches:
                psFound.append(p.ps)
        psFound.sort()
        psRange = []
        for i in range(len(psFound)-1):
            p1 = psFound[i]
            for j in range(i+1, len(psFound)):
                p2 = psFound[j]
                # p2 should always be equal or greater than p1
                psRange.append(p2-p1)

        return int(min(psRange)), int(max(psRange))


    def solutionLegend(self, compress=False):
        '''Return legend data. 

        >>> from music21 import *
        >>> s = corpus.parseWork('bach/bwv66.6')
        >>> p = analysis.discrete.SadoianAmbitus(s.parts[0]) #provide ref stream
        >>> len(p.solutionLegend())
        2
        >>> [len(x) for x in p.solutionLegend()]
        [2, 2]

        >>> [len(y) for y in [x for x in p.solutionLegend()]]
        [2, 2]

        >>> s = corpus.parseWork('bach/bwv66.6')
        >>> p = SadoianAmbitus()
        >>> p.solutionLegend(compress=True) # empty if nothing processed
        [['', []], ['', []]]

        >>> x = p.process(s.parts[0])
        >>> [len(y) for y in [x for x in p.solutionLegend(compress=True)]]
        [2, 2]

        >>> x = p.process(s.parts[1])
        >>> [len(y) for y in [x for x in p.solutionLegend(compress=True)]]
        [2, 2]

        '''
        if compress:
            colorsUsed = self.getColorsUsed()

        data = []

        colors = {} # a filtered dictionary
        for i in range(len(self._pitchSpanColors.keys())):
            if compress:
                if self._pitchSpanColors[i] not in colorsUsed:
                    continue
            colors[i] = self._pitchSpanColors[i]  

        # keys here are solutions, not colors
        keys = colors.keys()
        keys.sort()

        keysTopRow = keys[:(len(keys)/2)]
        keysBottomRow = keys[(len(keys)/2):]

        # split keys into two groups for two rows (optional)
        for keyGroup in [keysTopRow, keysBottomRow]:
            row = []
            row.append('') # empty row label
            pairs = []
            for i in keyGroup:
                color = colors[i] # get form colors
                pairs.append((i, color))
            row.append(pairs)
            data.append(row)

        return data


    def solutionToColor(self, result):
        '''
        >>> from music21 import *
        >>> p = SadoianAmbitus()
        >>> s = stream.Stream()
        >>> c = chord.Chord(['a2', 'b4', 'c8'])
        >>> s.append(c)
        >>> min, max = p._getPitchSpan(s)
        >>> p.solutionToColor(max-min).startswith('#')
        True
        '''    
        # a result of None may be possible
        if result == None:
            return self._rgbToHex((255, 255, 255))

        return self._pitchSpanColors[result]
    
    
    def process(self, sStream):
        post = self._getPitchSpan(sStream)
        if post != None:
            solution = post[1] - post[0] # max-min
        else:
            solution = None
        color = self.solutionToColor(solution)
        
        # store solutions for compressed legend generation
        self._solutionsFound.append((solution, color))
        return solution, color


    def getSolution(self, sStream):
        ''' procedure to only return a text solution
        >>> from music21 import *
        >>> s = corpus.parseWork('bach/bwv66.6')
        >>> p = SadoianAmbitus()
        >>> p.getSolution(s)
        34

        '''
        solution, color = self.process(sStream)
        return solution


#------------------------------------------------------------------------------
# public access function

def analyzeStream(streamObj, *args, **keywords):
    '''Public interface to discrete analysis methods to be applied to a Stream given as an argument. Methods return process-specific data format. See base-classes for details. 

    Analysis methods can be specified as a second argument or by keyword. Available plots include the following:

    :class:`~music21.analysis.discrete.SadoianAmbitus`
    :class:`~music21.analysis.discrete.KrumhanslSchmuckler`

    >>> from music21 import *
    >>> s = corpus.parseWork('bach/bwv66.6')
    >>> analysis.discrete.analyzeStream(s, 'Krumhansl')
    ('F#', 'minor', 0.81547089257624916)
    >>> analysis.discrete.analyzeStream(s, 'ambitus')
    34
    '''
    analysisClasses = [
        SadoianAmbitus,
        KrumhanslSchmuckler,
    ]

    if 'method' in keywords:
        method = keywords['method']

    if len(args) > 0:
        method = args[0]

    for analysisClassName in analysisClasses:    
        # this is a very loose matching, as there are few classes now
        if (method.lower() in analysisClassName.__name__.lower() or
            method.lower() in analysisClassName.name):
            obj = analysisClassName()
            return obj.getSolution(streamObj)
    # if no match raise error
    raise DiscreteAnalysisException('no such analysis method: %s' % method)

#------------------------------------------------------------------------------
class TestExternal(unittest.TestCase):

    def runTest(self):
        pass
    
    
class Test(unittest.TestCase):

    def runTest(self):
        pass



#------------------------------------------------------------------------------

if __name__ == "__main__":
    if len(sys.argv) == 1: # normal conditions
        music21.mainTest(Test)
    elif len(sys.argv) > 1:
        a = Test()




