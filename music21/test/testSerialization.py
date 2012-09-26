# -*- coding: utf-8 -*-
#-------------------------------------------------------------------------------
# Name:         testSerialization.py
# Purpose:      tests for serializing music21 objects
#
# Authors:      Christopher Ariza
#
# Copyright:    Copyright © 2012 Michael Scott Cuthbert and the music21 Project
# License:      LGPL, see license.txt
#-------------------------------------------------------------------------------


import unittest
import music21 # needed to do fully-qualified isinstance name checking

from music21 import freezeThaw

from music21 import environment
_MOD = "testSerialization.py"
environLocal = environment.Environment(_MOD)





#-------------------------------------------------------------------------------
class Test(unittest.TestCase):

    def runTest(self):
        '''Need a comment
        '''
        pass

    def testBasicA(self):
        from music21 import note
        unused_t1 = note.Lyric('test')
        #print t1.json

        n1 = note.Note('G#3', quarterLength=3)
        n1.lyric = 'testing'
        self.assertEqual(n1.pitch.nameWithOctave, 'G#3')        
        self.assertEqual(n1.quarterLength, 3.0)        
        self.assertEqual(n1.lyric, 'testing')        
        
        n2 = note.Note()
        
        raw = freezeThaw.JSONFreezer(n1).json
        freezeThaw.JSONThawer(n2).json = raw
        
        self.assertEqual(n2.pitch.nameWithOctave, 'G#3')    
        self.assertEqual(n2.quarterLength, 3.0)        
        #self.assertEqual(n2.lyric, 'testing')        

            
    def testBasicB(self):
        from music21 import chord

        c1 = chord.Chord(['c2', 'a4', 'e5'], quarterLength=1.25)
        c2 = chord.Chord()

        raw = freezeThaw.JSONFreezer(c1).json
        freezeThaw.JSONThawer(c2).json = raw

        
        self.assertEqual(str(c1.pitches), '[<music21.pitch.Pitch C2>, <music21.pitch.Pitch A4>, <music21.pitch.Pitch E5>]')
        self.assertEqual(c1.quarterLength, 1.25)


    def testBasicC(self):
        from music21 import stream, note, converter

        s = stream.Stream()
        n1 = note.Note('d2', quarterLength=2.0)
        s.append(n1)
        s.append(note.Note('g~6', quarterLength=.25))

        temp = converter.freezeStr(s)
        post = converter.thawStr(temp)
        self.assertEqual(len(post.notes), 2)
        self.assertEqual(str(post.notes[0].pitch), 'D2')


    def testBasicD(self):
        from music21 import stream, note, converter, spanner
        import copy

        s = stream.Stream()
        n1 = note.Note('d2', quarterLength=2.0)
        n2 = note.Note('e2', quarterLength=2.0)
        sp = spanner.Slur(n1, n2)

        s.append(n1)
        s.append(n2)
        s.append(sp)

        # the deepcopy is what creates the bug in the preservation of a weakref

        #temp = converter.freezeStr(s)

        sCopy = copy.deepcopy(s)
        temp = converter.freezeStr(sCopy)

        post = converter.thawStr(temp)
        self.assertEqual(len(post.notes), 2)
        self.assertEqual(str(post.notes[0].pitch), 'D2')
        spPost = post.spanners[0]
        self.assertEqual(spPost.getComponents(), [post.notes[0], post.notes[1]])
        self.assertEqual(spPost.getComponentIds(), [id(post.notes[0]), id(post.notes[1])])


    def testBasicE(self):
        from music21 import corpus, converter
        s = corpus.parse('bwv66.6')

        temp = converter.freezeStr(s, fmt='pickle')        
        sPost = converter.thawStr(temp)
        #sPost.show()
        self.assertEqual(len(s.flat.notes), len(sPost.flat.notes))

        self.assertEqual(len(s.parts[0].notes), len(sPost.parts[0].notes))
        #print s.parts[0].notes
        #sPost.parts[0].notes


    def testBasicF(self):
        from music21 import stream, note, converter, spanner
        
        s = stream.Score()
        s.repeatAppend(note.Note('G4'), 5)
        for i, syl in enumerate(['se-', 'ri-', 'al-', 'iz-', 'ing']):
            s.notes[i].addLyric(syl)
        s.append(spanner.Slur(s.notes[0], s.notes[-1]))
        
        # file writing
        #converter.freeze(s, fmt='jsonpickle', fp='/_scratch/test.json')
        #converter.freeze(s, fmt='pickle', fp='/_scratch/test.p')
    
        data = converter.freezeStr(s, fmt='pickle')
        sPost = converter.thawStr(data)
        self.assertEqual(len(sPost.notes), 5)
        #sPost.show()

    def xtestJsonPickle(self):
        # jsonpickle doesnt work
        from music21 import stream, note, converter, spanner
        
        s = stream.Score()
        s.repeatAppend(note.Note('G4'), 5)
        for i, syl in enumerate(['se-', 'ri-', 'al-', 'iz-', 'ing']):
            s.notes[i].addLyric(syl)
        s.append(spanner.Slur(s.notes[0], s.notes[-1]))
            
        data = converter.freezeStr(s, fmt='jsonpickle')
        #print data
        sPost = converter.thawStr(data)
        self.assertEqual(len(sPost.notes), 5)
        #sPost.show()


    def xtestJsonPickle2(self):
        from music21 import corpus, converter
        s = corpus.parse('bwv66.6')

        temp = converter.freezeStr(s, fmt='jsonpickle')        
        sPost = converter.thawStr(temp)
        #sPost.show()
        self.assertEqual(len(s.flat.notes), len(sPost.flat.notes))

        self.assertEqual(len(s.parts[0].notes), len(sPost.parts[0].notes))

        #sPost.show()

    def testBasicJ(self):
        from music21 import stream, note, converter

        p1 = stream.Part()
        for m in range(3):
            m = stream.Measure()
            for i in range(4):
                m.append(note.Note('C4'))
            p1.append(m)

        p2 = stream.Part()
        for m in range(3):
            m = stream.Measure()
            for i in range(4):
                m.append(note.Note('G4'))
            p2.append(m)

        s = stream.Score()
        s.insert(0, p1)
        s.insert(0, p2)
        #s.show()

        temp = converter.freezeStr(s, fmt='pickle')        
        sPost = converter.thawStr(temp)
        self.assertEqual(len(sPost.parts), 2)
        self.assertEqual(len(sPost.parts[0].getElementsByClass('Measure')), 3)
        self.assertEqual(len(sPost.parts[1].getElementsByClass('Measure')), 3)
        self.assertEqual(len(sPost.flat.notes), 24)


    def testBasicI(self):
        from music21 import stream, note, converter

        p1 = stream.Part()
        p1.repeatAppend(note.Note('C4'), 12)
        p1.makeMeasures(inPlace = True)
        p2 = stream.Part()
        p2.repeatAppend(note.Note('G4'), 12)
        p2.makeMeasures(inPlace = True)
        s = stream.Score()
        s.insert(0, p1)
        s.insert(0, p2)
        #s.show()

        temp = converter.freezeStr(s, fmt='pickle')        
        sPost = converter.thawStr(temp)
        self.assertEqual(len(sPost.parts), 2)
        self.assertEqual(len(sPost.parts[0].getElementsByClass('Measure')), 3)
        self.assertEqual(len(sPost.parts[1].getElementsByClass('Measure')), 3)
        self.assertEqual(len(sPost.flat.notes), 24)




    def testBasicK(self):
        # fails because of weakref
        from music21 import corpus, converter
        s = corpus.parse('beethoven/opus133').parts[0]
        unused_data = converter.freezeStr(s, fmt='pickle')




#------------------------------------------------------------------------------

if __name__ == "__main__":
    music21.mainTest(Test)


#------------------------------------------------------------------------------
# eof






