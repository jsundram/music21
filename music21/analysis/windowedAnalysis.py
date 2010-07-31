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

import unittest, doctest, random
import sys
import math

import music21

from music21 import meter
from music21.pitch import Pitch
from music21 import stream 


from music21 import environment
_MOD = 'windowed.py'
environLocal = environment.Environment(_MOD)


#------------------------------------------------------------------------------
class WindowedAnalysisException(Exception):
    pass


#------------------------------------------------------------------------------

class WindowedAnalysis(object):
    def __init__(self, streamObj, analysisProcessor):
        '''Create a WindowedAnalysis object.

        The provided `analysisProcessor` must provide a `process()` method that, when given a windowed Stream (a Measure) returns two element tuple containing (a) a data value (implementation dependent) and (b) a color code. 
        '''
        self.processor = analysisProcessor
        #environLocal.printDebug(self.processor)
        if 'Stream' not in streamObj.classes:
            raise WindowedAnalysisException, 'non-stream provided as argument'

        self._srcStream = streamObj
        # store a windowed Stream, partitioned into bars of 1/4
        self._windowedStream = self._getMinimumWindowStream() 

    def _getMinimumWindowStream(self):
        ''' Take the loaded stream and restructure it into measures of 1 quarter note duration.

        >>> from music21 import corpus
        >>> s = corpus.parseWork('bach/bwv324')
        >>> p = SadoianAmbitus()
        >>> # placing one part into analysis
        >>> wa = WindowedAnalysis(s.parts[0], p)

        >>> post = wa._getMinimumWindowStream()
        >>> len(post.measures)
        42
        >>> post.measures[0]
        <music21.stream.Measure 1 offset=0.0>
        >>> post.measures[0].timeSignature # set to 1/4 time signature
        <music21.meter.TimeSignature 1/4>
        >>> len(post.measures[1].notes) # one note in this measures 
        1
        '''
        # create a stream that contains just a 1/4 time signature; this is 
        # the minimum window size (and partitioning will be done by measure)
        meterStream = stream.Stream()
        meterStream.insert(0, meter.TimeSignature('1/4'))
        
        # makeTies() splits the durations into proper measure boundaries for 
        # analysis; this means that a duration that spans multiple 1/4 measures
        # will be represented in each of those measures
        return self._srcStream.makeMeasures(meterStream).makeTies(inPlace=True)


    def _analyze(self, windowSize):
        ''' Calls, for a given window size, an analysis method across all windows in the source Stream. Windows above size 1 are always overlapped, so if a window of size 2 is used, windows 1-2, then 2-3, then 3-4 are compared. If a window of size 3 is used, windows 1-3, then 2-4, then 3-5 are compared. 

        Windows are assumed to be partitioned by :class:`music21.stream.Measure` objects.

        Returns two lists for results, each equal in size to the length of minimum windows minus the window size plus one. If we have 20 1/4 windows, then the results lists will be of length 20 for window size 1, 19 for window size 2, 18 for window size 3, etc. 

        >>> from music21 import corpus
        >>> s = corpus.parseWork('bach/bwv66.6')
        >>> p = SadoianAmbitus()
        >>> wa = WindowedAnalysis(s, p)
        >>> len(wa._windowedStream)
        39
        >>> a, b = wa._analyze(1)
        >>> len(a), len(b)
        (39, 39)

        >>> a, b = wa._analyze(4)
        >>> len(a), len(b)
        (36, 36)

        '''
        max = len(self._windowedStream.getElementsByClass('Measure'))
        data = [0] * (max - windowSize + 1)
        color = [0] * (max - windowSize + 1)               
        
        for i in range(max-windowSize + 1):
            # getting a range of Measures to be used as windows
            # for getMeasureRange(), collect is set to [] so that clefs, timesignatures, and other objects are not gathered. 

            # a flat representation removes all Streams, returning only 
            # Notes, Chords, etc.
            current = self._windowedStream.getMeasureRange(i, 
                      i+windowSize, collect=[]).flat
            # current is a Stream for analysis
            data[i], color[i] = self.processor.process(current)
             
        return data, color

        
    def process(self, minWindow=1, maxWindow=1, windowStepSize=1):

        ''' Main method for windowed analysis across one or more window size.

        Calls :meth:`~music21.analysis.WindowedAnalysis._analyze` for 
        the number of different window sizes to be analyzed.

        The `minWindow` and `maxWindow` set the range of window sizes in quarter lengths. The `windowStepSize` parameter determines the the increment between these window sizes, in quarter lengths. 

        If `minWindow` or `maxWindow` is None, the largest window size available will be set. 

        >>> from music21 import corpus
        >>> s = corpus.parseWork('bach/bwv324')
        >>> p = KrumhanslSchmuckler()
        >>> # placing one part into analysis
        >>> wa = WindowedAnalysis(s[0], p)
        >>> x, y, z = wa.process(1, 1)
        >>> len(x) # we only have one series of windows
        1
        >>> x[0][0], y[0][0] # for each window, we get a solution and a color
        (('B', 'major', 0.6868258874056411), '#FF8000')

        >>> x, y, z = wa.process(1, 2)
        >>> len(x) # we have two series of windows
        2

        >>> x[0][0] # the data returned is processor dependent; here we get
        ('B', 'major', 0.6868258874056411)
        >>> y[0][0] # a color is returned for each matching data position
        '#FF8000'
        '''
        # names = [x.id for x in sStream]
                
        #max = len(sStream[0].measures)
        if maxWindow == None:
            max = len(self._windowedStream)
        else:
            max = maxWindow

        if minWindow == None:
            min = len(self._windowedStream)
        else:
            min = minWindow
        
        # need to create storage for the output of each row, or the processing
        # of all windows of a single size across the entire Stream
        solutionMatrix = [] 
        colorMatrix = [] 
        # store meta data about each row as a dictionary
        metaMatrix = [] 

        for i in range(min, max+1, windowStepSize):
            environLocal.printDebug(['processing window:', i])
            # each of these results are lists, where len is based on 
            soln, colorn = self._analyze(i) 
            # store lists of results in a list of lists
            solutionMatrix.append(soln)
            colorMatrix.append(colorn)
            meta = {'windowSize': i}
            metaMatrix.append(meta)
        
        return solutionMatrix, colorMatrix, metaMatrix





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

