# -*- coding: utf-8 -*-
#!/usr/bin/python
#-------------------------------------------------------------------------------
# Name:         test.py
# Purpose:      music21 class which allows for test cases of music21 to braille translation.
# Authors:      Jose Cabal-Ugaz
#
# Copyright:    (c) 2011 The music21 Project
# License:      LGPL
#-------------------------------------------------------------------------------

import codecs
import music21
import unittest

from music21.braille import translate

from music21 import articulations
from music21 import bar
from music21 import clef
from music21 import dynamics
from music21 import key
from music21 import meter
from music21 import note
from music21 import pitch
from music21 import stream
from music21 import tempo
from music21 import tinyNotation

# Introduction to Braille Music Transcription, Second Edition
#-------------------------------------------------------------------------------
#-------------------------------------------------------------------------------
# PART ONE
# Basic Procedures and Transcribing Single-Staff Music
#
#-------------------------------------------------------------------------------
# Chapter 2: Eighth Notes, the Eighth Rest, and Other Basic Signs
#
# NOTE: Octave marks which precede the first note in a line of braille music
# are omitted in Chapters 2-6 in the transcription manual because the concept is
# not introduced until Chapter 7. They are NOT omitted in the examples below,
# however, because they are required in transcription.

def example2_1():
    '''
    >>> from music21.braille import translate
    >>> print translate.partToBraille(example2_1())
    ⠼⠁⠀⠐⠓⠭⠋⠀⠛⠭⠊⠀⠓⠭⠛⠀⠋⠭⠭⠀⠋⠭⠙⠀⠑⠭⠛⠀⠋⠭⠑⠀⠙⠭⠭⠀⠑⠭⠛⠀
    ⠀⠀⠐⠋⠭⠓⠀⠛⠓⠊⠀⠓⠭⠭⠀⠊⠭⠛⠀⠓⠭⠋⠀⠛⠋⠑⠀⠙⠭⠭⠣⠅
    '''
    bm = tinyNotation.TinyNotationStream("g8 r8 e8 f8 r8 a8 g8 r8 f8 e8 r8 r8 e8 r8 c8 d8 r8 f8 e8 r8 d8 c8 r8 r8 \
    d8 r8 f8 e8 r8 g8 f8 g8 a8 g8 r8 r8 a8 r8 f8 g8 r8 e8 f8 e8 d8 c8 r8 r8", "3/8")
    bm.makeNotation(inPlace=True, cautionaryNotImmediateRepeat=False)
    bm[0].pop(0) # remove time signature
    bm[-1].rightBarline = bar.Barline('final')
    return bm

def example2_2():
    '''
    >>> from music21.braille import translate
    >>> print translate.partToBraille(example2_2())
    ⠼⠚⠀⠐⠑⠀⠑⠙⠚⠑⠀⠙⠚⠊⠙⠀⠚⠊⠓⠚⠀⠊⠊⠑⠭⠀⠋⠋⠓⠋⠀⠑⠋⠓⠚⠀⠑⠙⠚⠊
    ⠀⠀⠸⠓⠓⠓⠭⠣⠅
    '''
    bm = tinyNotation.TinyNotationStream("r8 r8 r8 d8 d8 c8 B8 d8 c8 B8 A8 c8 B8 A8 G8 B8 A8 A8 D8 r8 E8 E8 G8 E8 \
    D8 E8 G8 B8 d8 c8 B8 A8 G8 G8 G8 r8", "4/8")
    bm.makeNotation(inPlace=True, cautionaryNotImmediateRepeat=False)
    for numRest in range(3):
        bm[0].pop(2)
    bm[0].padAsAnacrusis()
    for measure in bm:
        measure.number -= 1
    bm[0].pop(0) # remove time signature
    bm[-1].rightBarline = bar.Barline('final')
    return bm

def example2_3():
    '''
    >>> from music21.braille import translate
    >>> print translate.partToBraille(example2_3())
    ⠼⠁⠀⠐⠋⠋⠀⠓⠊⠀⠓⠛⠀⠋⠓⠀⠛⠋⠀⠑⠛⠀⠋⠙⠀⠑⠭⠀⠋⠋⠀⠛⠛⠀⠓⠊⠀⠚⠙⠀
    ⠀⠀⠐⠊⠛⠀⠋⠑⠀⠙⠚⠀⠙⠭⠣⠅
    '''
    bm = tinyNotation.TinyNotationStream("e8 e8 g8 a8 g8 f8 e8 g8 f8 e8 d8 f8 e8 c8 d8 r8 e8 e8 f8 f8 g8 a8 b8 c'8 \
    a8 f8 e8 d8 c8 B8 c8 r8", "2/8")
    bm.makeNotation(inPlace=True, cautionaryNotImmediateRepeat=False)
    bm[0].pop(0) # remove time signature
    bm[-1].rightBarline = bar.Barline('final')
    return bm

def example2_4():
    '''
    >>> from music21.braille import translate
    >>> print translate.partToBraille(example2_4())
    ⠼⠁⠀⠸⠊⠙⠋⠀⠑⠙⠚⠀⠙⠭⠚⠀⠊⠭⠭⠀⠚⠚⠙⠀⠑⠙⠚⠀⠊⠭⠊⠀⠚⠭⠭⠣⠅⠄⠀⠀
    ⠀⠀⠸⠊⠋⠊⠀⠙⠚⠊⠀⠊⠚⠙⠀⠑⠭⠭⠀⠋⠑⠙⠀⠚⠋⠚⠀⠊⠭⠊⠀⠊⠭⠭⠣⠅
    '''
    bm = tinyNotation.TinyNotationStream("A8 c8 e8 d8 c8 B8 c8 r8 B8 A8 r8 r8 B8 B8 c8 d8 c8 B8 A8 r8 A8 B8 r8 r8 \
    A8 E8 A8 c8 B8 A8 A8 B8 c8 d8 r8 r8 e8 d8 c8 B8 E8 B8 A8 r8 A8 A8 r8 r8", "3/8")
    bm.makeNotation(inPlace=True, cautionaryNotImmediateRepeat=False)
    bm[7].rightBarline = bar.Barline('double')
    bm[-1].rightBarline = bar.Barline('final')
    bm[0].pop(0) # remove time signature
    return bm

def example2_5():
    '''
    >>> from music21.braille import translate
    >>> print translate.partToBraille(example2_5())
    ⠼⠚⠀⠨⠑⠋⠀⠛⠙⠊⠙⠀⠑⠙⠊⠙⠀⠊⠙⠊⠓⠀⠋⠓⠛⠭⠀⠑⠋⠛⠑⠀⠙⠑⠋⠛⠀⠀⠀⠀
    ⠀⠀⠐⠓⠋⠙⠋⠀⠛⠭⠣⠅
    '''
    bm = tinyNotation.TinyNotationStream("r8 r8 d'8 e'8 f'8 c'8 a8 c'8 d'8 c'8 a8 c'8 a8 c'8 a8 g8 e8 g8 f8 r8 \
    d8 e8 f8 d8 c8 d8 e8 f8 g8 e8 c8 e8 f8 r8", "4/8")
    bm.makeNotation(inPlace=True, cautionaryNotImmediateRepeat=False)
    for numRest in range(2):
        bm[0].pop(2)
    bm[0].padAsAnacrusis()
    for measure in bm:
        measure.number -= 1
    bm[0].pop(0) # remove time signature
    bm[-1].rightBarline = bar.Barline('final')
    return bm

def example2_6():
    '''
    >>> from music21.braille import translate
    >>> print translate.partToBraille(example2_6())
    ⠼⠁⠀⠸⠓⠓⠓⠓⠋⠛⠀⠊⠓⠓⠓⠭⠓⠀⠊⠊⠊⠙⠚⠊⠀⠊⠓⠓⠓⠭⠭⠀⠓⠛⠛⠛⠭⠭⠀⠀
    ⠀⠀⠸⠛⠋⠋⠋⠭⠭⠀⠑⠋⠑⠓⠛⠑⠀⠙⠋⠑⠙⠭⠭⠣⠅
    '''
    bm = tinyNotation.TinyNotationStream("G8 G8 G8 G8 E8 F8 A8 G8 G8 G8 r8 G8 A8 A8 A8 c8 B8 A8 A8 G8 G8 G8 r8 r8 \
    G8 F8 F8 F8 r8 r8 F8 E8 E8 E8 r8 r8 D8 E8 D8 G8 F8 D8 C8 E8 D8 C8 r8 r8", "6/8")
    bm.makeNotation(inPlace=True, cautionaryNotImmediateRepeat=False)
    bm[-1].rightBarline = bar.Barline('final')
    bm[0].pop(0)
    return bm

def example2_7():
    '''
    >>> from music21.braille import translate
    >>> print translate.partToBraille(example2_7())
    ⠼⠁⠀⠐⠋⠭⠋⠛⠭⠛⠀⠑⠭⠑⠋⠭⠋⠀⠙⠑⠋⠓⠛⠋⠀⠋⠑⠑⠑⠭⠭⠀⠙⠭⠙⠋⠭⠋⠀⠀
    ⠀⠀⠐⠛⠭⠛⠊⠭⠊⠀⠓⠭⠓⠓⠊⠚⠀⠑⠙⠙⠙⠭⠭⠣⠅
    '''
    bm = tinyNotation.TinyNotationStream("e8 r8 e8 f8 r8 f8 d8 r8 d8 e8 r8 e8 c8 d8 e8 g8 f8 e8 e8 d8 d8 d8 r8 r8 \
    c8 r8 c8 e8 r8 e8 f8 r8 f8 a8 r8 a8 g8 r8 g8 g8 a8 b8 d'8 c'8 c'8 c'8 r8 r8", "6/8")
    bm.makeNotation(inPlace=True, cautionaryNotImmediateRepeat=False)
    bm[-1].rightBarline = bar.Barline('final')
    bm[0].pop(0)
    return bm

#-------------------------------------------------------------------------------
# Chapter 3: Quarter Notes, the Quarter Rest, and the Dot

def example3_1():
    '''
    >>> from music21.braille import translate
    >>> print translate.partToBraille(example3_1())
    ⠼⠁⠀⠨⠱⠺⠳⠺⠀⠹⠺⠪⠧⠀⠺⠳⠫⠳⠀⠱⠺⠱⠧⠀⠫⠳⠪⠳⠀⠱⠳⠺⠱⠀⠫⠱⠹⠪⠀⠀
    ⠀⠀⠐⠳⠱⠳⠧⠣⠅
    '''
    bm = tinyNotation.TinyNotationStream("d'4 b4 g4 b4 c'4 b4 a4 r4 b4 g4 e4 g4 d4 B4 d4 r4 e4 g4 a4 g4 d4 g4 b4 \
    d'4 e'4 d'4 c'4 a4 g4 d4 g4 r4", "4/4")
    bm.makeNotation(inPlace=True, cautionaryNotImmediateRepeat=False)
    bm[-1].rightBarline = bar.Barline('final')
    bm[0].pop(0)
    return bm

def example3_2():
    '''
    >>> from music21.braille import translate
    >>> print translate.partToBraille(example3_2())
    ⠼⠁⠀⠸⠪⠻⠹⠻⠀⠳⠫⠹⠫⠀⠻⠳⠪⠻⠀⠱⠫⠻⠧⠀⠳⠪⠳⠹⠀⠻⠪⠹⠱⠀⠹⠪⠳⠹⠀⠀
    ⠀⠀⠸⠱⠫⠻⠧⠣⠅
    '''
    bm = tinyNotation.TinyNotationStream("A4 F4 C4 F4 G4 E4 C4 E4 F4 G4 A4 F4 D4 E4 F4 r4 G4 A4 G4 C4 F4 A4 c4 d4 \
    c4 A4 G4 C4 D4 E4 F4 r4", "4/4")
    bm.makeNotation(inPlace=True, cautionaryNotImmediateRepeat=False)
    bm[-1].rightBarline = bar.Barline('final')
    bm[0].pop(0)
    return bm

def example3_3():
    '''
    >>> from music21.braille import translate
    >>> print translate.partToBraille(example3_3())
    ⠼⠁⠀⠐⠳⠫⠀⠪⠳⠀⠻⠧⠀⠱⠧⠀⠹⠄⠙⠀⠱⠄⠑⠀⠫⠧⠀⠹⠧⠀⠳⠳⠀⠪⠺⠀⠹⠧⠀⠀
    ⠀⠀⠐⠪⠧⠀⠳⠄⠓⠀⠻⠱⠀⠹⠫⠀⠹⠧⠣⠅
    '''
    bm = tinyNotation.TinyNotationStream("g4 e4 a4 g4 f4 r4 d4 r4 c4. c8 d4. d8 e4 r4 c4 r4 g4 g4 a4 b4 c'4 r4 a4 r4 \
    g4. g8 f4 d4 c4 e4 c4 r4", "2/4")
    bm.makeNotation(inPlace=True, cautionaryNotImmediateRepeat=False)
    bm[-1].rightBarline = bar.Barline('final')
    bm[0].pop(0)
    return bm

def example3_4():
    '''
    >>> from music21.braille import translate
    >>> print translate.partToBraille(example3_4())
    ⠼⠁⠀⠸⠫⠙⠑⠫⠧⠀⠻⠊⠛⠫⠧⠀⠱⠋⠛⠓⠋⠹⠀⠱⠱⠳⠧⠀⠻⠋⠑⠫⠧⠀⠳⠛⠋⠻⠧⠀
    ⠀⠀⠸⠪⠓⠛⠋⠛⠳⠀⠻⠱⠹⠧⠣⠅
    '''
    bm = tinyNotation.TinyNotationStream("E4 C8 D8 E4 r4 F4 A8 F8 E4 r4 D4 E8 F8 G8 E8 C4 D4 D4 G4 r4 \
    F4 E8 D8 E4 r4 G4 F8 E8 F4 r4 A4 G8 F8 E8 F8 G4 F4 D4 C4 r4", "4/4")
    bm.makeNotation(inPlace=True, cautionaryNotImmediateRepeat=False)
    bm[-1].rightBarline = bar.Barline('final')
    bm[0].pop(0)
    return bm

def example3_5():
    '''
    >>> from music21.braille import translate
    >>> print translate.partToBraille(example3_5())
    ⠼⠁⠀⠐⠻⠄⠙⠱⠫⠀⠻⠄⠓⠪⠻⠀⠪⠹⠱⠹⠀⠪⠻⠳⠧⠣⠅⠄⠀⠳⠄⠋⠹⠫⠀⠻⠄⠙⠻⠪
    ⠀⠀⠐⠳⠳⠻⠫⠀⠻⠪⠻⠧⠣⠅
    '''
    bm = tinyNotation.TinyNotationStream("f4. c8 d4 e4 f4. g8 a4 f4 a4 c'4 d'4 c'4 a4 f4 g4 r4 \
    g4. e8 c4 e4 f4. c8 f4 a4 g4 g4 f4 e4 f4 a4 f4 r4", "4/4")
    bm.makeNotation(inPlace=True, cautionaryNotImmediateRepeat=False)
    bm[3].rightBarline = bar.Barline('double')
    bm[-1].rightBarline = bar.Barline('final')
    bm[0].pop(0)
    return bm

def example3_6():
    '''
    >>> from music21.braille import translate
    >>> print translate.partToBraille(example3_6())
    ⠼⠁⠀⠐⠳⠓⠱⠑⠀⠳⠚⠑⠚⠓⠀⠪⠊⠊⠚⠙⠀⠺⠚⠳⠭⠀⠪⠊⠱⠑⠀⠳⠚⠪⠙⠀⠀⠀⠀⠀
    ⠀⠀⠐⠚⠙⠑⠹⠊⠀⠳⠓⠳⠭⠣⠅
    '''
    bm = tinyNotation.TinyNotationStream("g4 g8 d4 d8 g4 b8 d'8 b8 g8 a4 a8 a8 b8 c'8 b4 b8 g4 r8 a4 a8 d4 d8 g4 b8 a4 c'8\
    b8 c'8 d'8 c'4 a8 g4 g8 g4 r8", "3/4")
    bm.makeNotation(inPlace=True, cautionaryNotImmediateRepeat=False)
    bm[-1].rightBarline = bar.Barline('final')
    bm[0].pop(0)
    return bm

#-------------------------------------------------------------------------------
# Chapter 4: Half Notes, the Half Rest, and the Tie

def example4_1():
    '''
    >>> from music21.braille import translate
    >>> print translate.partToBraille(example4_1())
    ⠼⠁⠀⠐⠝⠏⠀⠕⠟⠀⠏⠗⠀⠟⠎⠀⠗⠞⠀⠎⠝⠀⠞⠕⠀⠝⠥⠣⠅
    '''
    bm = tinyNotation.TinyNotationStream("c2 e2 d2 f2 e2 g2 f2 a2 g2 b2 a2 c'2 b2 d'2 c'2 r2", "4/4")
    bm.makeNotation(inPlace=True, cautionaryNotImmediateRepeat=False)
    bm[-1].rightBarline = bar.Barline('final')
    bm[0].pop(0)
    return bm

def example4_2():
    '''
    >>> from music21.braille import translate
    >>> print translate.partToBraille(example4_2())
    ⠼⠁⠀⠸⠟⠎⠀⠗⠝⠀⠱⠹⠱⠫⠀⠟⠥⠀⠕⠟⠀⠝⠟⠀⠫⠻⠳⠪⠀⠟⠥⠣⠅
    '''
    bm = tinyNotation.TinyNotationStream("F2 A2 G2 C2 D4 C4 D4 E4 F2 r2 D2 F2 C2 F2 E4 F4 G4 A4 F2 r2", "4/4")
    bm.makeNotation(inPlace=True, cautionaryNotImmediateRepeat=False)
    bm[-1].rightBarline = bar.Barline('final')
    bm[0].pop(0)
    return bm    

def example4_3():
    '''
    >>> from music21.braille import translate
    >>> print translate.partToBraille(example4_3())
    ⠼⠁⠀⠐⠝⠹⠀⠑⠙⠚⠙⠱⠀⠏⠫⠀⠛⠋⠑⠋⠻⠀⠗⠳⠀⠊⠓⠛⠓⠪⠀⠚⠊⠓⠊⠚⠑⠀⠹⠥
    ⠀⠀⠨⠏⠫⠀⠑⠙⠚⠙⠱⠀⠝⠹⠀⠚⠊⠓⠊⠺⠀⠎⠪⠀⠓⠛⠋⠛⠳⠀⠛⠋⠑⠋⠛⠑⠀⠀⠀⠀
    ⠀⠀⠐⠹⠥⠣⠅
    '''
    bm = tinyNotation.TinyNotationStream("c2 c4 d8 c8 B8 c8 d4 e2 e4 f8 e8 d8 e8 f4 g2 g4 a8 g8 f8 g8 a4 \
    b8 a8 g8 a8 b8 d'8 c'4 r2 e'2 e'4 d'8 c'8 b8 c'8 d'4 c'2 c'4 b8 a8 g8 a8 b4 a2 a4 g8 f8 e8 f8 g4 \
    f8 e8 d8 e8 f8 d8 c4 r2", "3/4")
    bm.makeNotation(inPlace=True, cautionaryNotImmediateRepeat=False)
    bm[-1].rightBarline = bar.Barline('final')
    bm[0].pop(0)
    return bm

def example4_4():
    '''
    >>> from music21.braille import translate
    >>> measure1 = example4_4()[0]
    >>> print translate.measureToBraille(measure1, showLeadingOctave = False)
    ⠟⠈⠉⠻⠄⠛
    '''
    bm = tinyNotation.TinyNotationStream("f2~ f4. f8", "4/4")
    bm.makeNotation(inPlace=True, cautionaryNotImmediateRepeat=False)
    bm[0].pop(1)
    bm[-1].rightBarline = None
    return bm

def example4_5():
    '''
    >>> from music21.braille import translate
    >>> measure1 = example4_5()[0]
    >>> print translate.measureToBraille(measure1, showLeadingOctave = False)
    ⠳⠄⠈⠉⠓⠊⠓
    '''
    bm = tinyNotation.TinyNotationStream("g4.~ g8 a8 g8", "3/4")
    bm.makeNotation(inPlace=True, cautionaryNotImmediateRepeat=False)
    bm[0].pop(1)
    bm[-1].rightBarline = None
    return bm

def example4_6():
    '''
    >>> from music21.braille import translate
    >>> bm = example4_6()
    >>> measure1 = bm[0]
    >>> measure2 = bm[1]
    >>> print translate.measureToBraille(measure1, showLeadingOctave = False)
    ⠗⠳⠈⠉
    >>> print translate.measureToBraille(measure2, showLeadingOctave = False)
    ⠗⠧
    '''
    bm = tinyNotation.TinyNotationStream("g2 g4~ g2 r4", "3/4")
    bm.makeNotation(inPlace=True, cautionaryNotImmediateRepeat=False)
    bm[0].pop(0)
    bm[-1].rightBarline = None
    return bm

def example4_7():
    '''
    >>> from music21.braille import translate
    >>> print translate.partToBraille(example4_7())
    ⠼⠁⠀⠐⠗⠄⠀⠏⠄⠀⠝⠄⠀⠏⠄⠀⠹⠱⠫⠀⠳⠻⠫⠀⠕⠄⠈⠉⠀⠕⠄⠀⠏⠫⠀⠫⠻⠳⠀⠀
    ⠀⠀⠐⠎⠪⠀⠪⠳⠻⠀⠏⠻⠀⠕⠫⠀⠝⠄⠈⠉⠀⠝⠄⠣⠅
    '''
    bm = tinyNotation.TinyNotationStream("g2. e2. c2. e2. c4 d4 e4 g4 f4 e4 d2.~ d2.\
    e2 e4 e4 f4 g4 a2 a4 a4 g4 f4 e2 f4 d2 e4 c2.~ c2.", "3/4")
    bm.makeNotation(inPlace=True, cautionaryNotImmediateRepeat=False)
    bm[-1].rightBarline = bar.Barline('final')
    bm[0].pop(0)
    return bm

#-------------------------------------------------------------------------------
# Chapter 5: Whole and Double Whole Notes and Rests, Measure Rests, and
# Transcriber-Added Signs

def example5_1():
    '''
    >>> from music21.braille import translate
    >>> print translate.partToBraille(example5_1())
    ⠼⠁⠀⠨⠽⠀⠮⠀⠿⠀⠮⠀⠽⠀⠵⠀⠽⠈⠉⠀⠽⠀⠵⠀⠯⠀⠿⠀⠵⠀⠽⠀⠷⠀⠿⠈⠉⠀⠀⠀
    ⠀⠀⠨⠿⠣⠅
    '''
    bm = tinyNotation.TinyNotationStream("c'1 a1 f1 a1 c'1 d'1 c'1~ c'1 d'1 e'1 f'1 d'1 c'1 g'1 f'1~ f'1", "4/4")
    bm.makeNotation(inPlace=True, cautionaryNotImmediateRepeat=False)
    bm[-1].rightBarline = bar.Barline('final')
    bm[0].pop(0)
    return bm

def example5_2():
    '''
    >>> from music21.braille import translate
    >>> print translate.partToBraille(example5_2())
    ⠼⠁⠀⠸⠽⠀⠯⠀⠷⠀⠮⠀⠾⠀⠮⠀⠷⠈⠉⠀⠷⠀⠮⠀⠽⠀⠮⠀⠿⠀⠷⠀⠾⠀⠷⠀⠯⠀⠿⠀
    ⠀⠀⠸⠮⠀⠿⠀⠵⠀⠾⠀⠵⠀⠽⠈⠉⠀⠽⠣⠅
    '''
    bm = tinyNotation.TinyNotationStream("C1 E1 G1 A1 B1 A1 G1~ G1 A1 c1 A1 F1 G1 B1 G1 E1 F1 A1 F1 D1 BB1 D1 C1~ C1", "4/4")
    bm.makeNotation(inPlace=True, cautionaryNotImmediateRepeat=False)
    bm[-1].rightBarline = bar.Barline('final')
    bm[0].pop(0)
    return bm

def example5_3():
    '''
    >>> from music21.braille import translate
    >>> print translate.partToBraille(example5_3())
    ⠼⠁⠀⠍⠐⠗⠀⠗⠗⠗⠀⠳⠳⠍⠣⠅
    '''
    bm = tinyNotation.TinyNotationStream("r1 g2 g2 g2 g2 g4 g4 r1", "3/2")
    bm.makeNotation(inPlace=True, cautionaryNotImmediateRepeat=False)
    bm[-1].rightBarline = bar.Barline('final')
    bm[0].pop(0)
    return bm

def example5_4():
    '''
    >>> from music21.braille import translate
    >>> print translate.partToBraille(example5_4())
    ⠼⠁⠀⠸⠏⠟⠀⠷⠀⠏⠕⠀⠽⠀⠕⠏⠀⠟⠏⠀⠵⠀⠍⠀⠝⠕⠀⠯⠀⠟⠗⠀⠮⠀⠗⠟⠀⠏⠕⠀
    ⠀⠀⠸⠽⠀⠍⠣⠅
    '''
    bm = tinyNotation.TinyNotationStream("E2 F2 G1 E2 D2 C1 D2 E2 F2 E2 D1 r1 \
    C2 D2 E1 F2 G2 A1 G2 F2 E2 D2 C1 r1", "4/4")
    bm.makeNotation(inPlace=True, cautionaryNotImmediateRepeat=False)
    bm[-1].rightBarline = bar.Barline('final')
    bm[0].pop(0)
    return bm

def example5_5():
    '''
    >>> from music21.braille import translate
    >>> print translate.partToBraille(example5_5())
    ⠼⠁⠀⠸⠟⠄⠀⠍⠀⠎⠄⠀⠍⠀⠻⠳⠪⠀⠹⠪⠻⠀⠳⠥⠀⠍⠀⠏⠄⠀⠍⠀⠗⠄⠀⠍⠀⠹⠱⠫
    ⠀⠀⠸⠳⠫⠹⠀⠻⠥⠀⠍⠣⠅
    '''
    bm = tinyNotation.TinyNotationStream("F2. r2. A2. r2. F4 G4 A4 c4 A4 F4 G4 r2 r2. \
    E2. r2. G2. r2. C4 D4 E4 G4 E4 C4 F4 r2 r2.", "3/4")
    bm.makeNotation(inPlace=True, cautionaryNotImmediateRepeat=False)
    bm[-1].rightBarline = bar.Barline('final')
    bm[0].pop(0)
    return bm

def example5_6():
    '''
    NOTE: Breve note and breve rest are transcribed using method (b) on page 24.
    
    >>> from music21.braille import translate
    >>> print translate.partToBraille(example5_6())
    ⠼⠁⠀⠐⠮⠽⠾⠀⠝⠞⠮⠞⠝⠀⠾⠍⠘⠉⠍⠀⠷⠾⠎⠗⠀⠮⠘⠉⠮⠍⠣⠅
    '''
    bm = tinyNotation.TinyNotationStream("a1 c'1 b1 c'2 b2 a1 b2 c'2 b1")
    bm.append(note.Rest(quarterLength=8.0))
    bm2 = tinyNotation.TinyNotationStream("g1 b1 a2 g2")
    bm2.append(note.Note('A4', quarterLength=8.0))
    bm2.append(note.Rest(quarterLength=4.0))
    bm.append(bm2.flat)
    bm.insert(0, meter.TimeSignature("6/2"))
    bm.makeNotation(inPlace=True, cautionaryNotImmediateRepeat=False)
    bm[-1].rightBarline = bar.Barline('final')
    bm[0].pop(0)
    return bm

# The following examples (as well as the rest of the examples in the chapter) don't work correctly yet.
#
def example5_7a():
    bm = tinyNotation.TinyNotationStream("r1 r1 r1 r1 r1", "4/4")
    bm.makeNotation(inPlace=True, cautionaryNotImmediateRepeat=False)
    bm[0].pop(0)
    return bm

def example5_7b():
    bm = tinyNotation.TinyNotationStream("r1 r1 r1 r1")
    bm.makeNotation(inPlace=True, cautionaryNotImmediateRepeat=False)
    bm[0].pop(0)
    return bm

def example5_7c():
    bm = tinyNotation.TinyNotationStream("r1 r1")
    bm.makeNotation(inPlace=True, cautionaryNotImmediateRepeat=False)
    bm[0].pop(0)
    return bm

#-------------------------------------------------------------------------------
# Chapter 6: Accidentals

def example6_1():
    '''
    >>> from music21.braille import translate
    >>> print translate.noteToBraille(note.Note('C#4', quarterLength = 2.0), showOctave = False)
    ⠩⠝
    >>> print translate.noteToBraille(note.Note('Gn4', quarterLength = 2.0), showOctave = False)
    ⠡⠗
    >>> print translate.noteToBraille(note.Note('E-4', quarterLength = 2.0), showOctave = False)
    ⠣⠏
    '''
    pass

def example6_2():
    '''
    >>> from music21.braille import translate
    >>> print translate.measureToBraille(example6_2()[0], showLeadingOctave = False)
    ⠩⠳⠩⠩⠻⠗
    '''
    bm = tinyNotation.TinyNotationStream("g#4 f##4 g#2")
    bm.makeNotation(inPlace=True, cautionaryNotImmediateRepeat=False)
    bm[0].pop(1)
    bm[-1].rightBarline = None
    return bm

def example6_3():
    '''
    >>> from music21.braille import translate
    >>> print translate.measureToBraille(example6_3()[0], showLeadingOctave = False)
    ⠝⠣⠞⠈⠉
    >>> print translate.measureToBraille(example6_3()[1], showLeadingOctave = False)
    ⠺⠹⠪⠻
    '''
    bm = tinyNotation.TinyNotationStream("c'2 b-2~ b-4 c'4 a4 f4", "4/4")
    bm.makeNotation(inPlace=True, cautionaryNotImmediateRepeat=False)
    bm[0].pop(0)
    bm[-1].rightBarline = None
    return bm

def example6_4():
    '''
    >>> from music21.braille import translate
    >>> print translate.measureToBraille(example6_4()[0], showLeadingOctave = False)
    ⠡⠫⠋⠊⠙⠡⠋
    >>> print translate.measureToBraille(example6_4()[1], showLeadingOctave = False)
    ⠟⠄
    '''
    bm = tinyNotation.TinyNotationStream("en4 en8 a8 c'8 e'n8 f'2.", "3/4")
    bm.notes[0].accidental = pitch.Accidental()
    bm.notes[4].accidental = pitch.Accidental()
    bm.makeNotation(inPlace=True, cautionaryNotImmediateRepeat=False)
    bm[0].pop(0)
    bm[-1].rightBarline = None
    return bm

def example6_5():
    '''
    >>> from music21.braille import translate
    >>> print translate.measureToBraille(example6_5()[0], showLeadingOctave = False)
    ⠙⠣⠚⠊⠓⠻
    >>> print translate.measureToBraille(example6_5()[1], showLeadingOctave = False)
    ⠓⠡⠚⠹⠱
    '''
    bm = tinyNotation.TinyNotationStream("c'8 b-8 a8 g8 f4 g8 bn8 c'4 d'4", "3/4")
    bm.notes[-3].accidental = pitch.Accidental()
    bm.makeNotation(inPlace=True, cautionaryNotImmediateRepeat=False)
    bm[0].pop(0)
    bm[-1].rightBarline = None
    return bm

def example6_6():
    '''
    >>> from music21.braille import translate
    >>> print translate.partToBraille(example6_6())
    ⠼⠁⠀⠐⠹⠩⠹⠱⠩⠱⠀⠫⠻⠩⠻⠳⠀⠩⠳⠪⠣⠺⠡⠺⠀⠝⠥⠀⠏⠣⠫⠱⠀⠹⠱⠡⠫⠹⠀⠀
    ⠀⠀⠐⠺⠣⠺⠪⠡⠺⠀⠝⠥⠣⠅
    '''
    bm = tinyNotation.TinyNotationStream("c4 c#4 d4 d#4 e4 f4 f#4 g4 g#4 a4 b-4 bn4 c'2 r2\
    e'2 e'-4 d'4 c'4 d'4 e'4 c'4 b4 b-4 a4 bn4 c'2 r2")
    bm.makeNotation(inPlace=True, cautionaryNotImmediateRepeat=False)
    bm[0].pop(0)
    bm[-1].rightBarline = bar.Barline('final')
    return bm

def example6_7():
    '''
    >>> from music21.braille import translate
    >>> print translate.partToBraille(example6_7())
    ⠼⠁⠀⠨⠳⠩⠻⠡⠻⠫⠀⠣⠫⠱⠣⠱⠹⠀⠺⠣⠺⠪⠣⠪⠀⠳⠩⠻⠡⠻⠫⠀⠣⠫⠱⠣⠱⠹⠀⠀
    ⠀⠀⠸⠺⠹⠱⠫⠀⠝⠥⠀⠽⠣⠅
    '''
    bm = tinyNotation.TinyNotationStream("g'4 f'#4 f'n4 e'n4 e'-4 d'4 d'-4 c'4 b4 b-4 a4 a-4 g4 f#4 fn4 e4\
    e-4 d4 d-4 c4 B4 c4 d4 e4 c2 r2 c1")
    bm.makeNotation(inPlace=True, cautionaryNotImmediateRepeat=False)
    bm[-3][2].accidental.displayStatus = False
    bm[-3][3].accidental.displayStatus = False
    bm[0].pop(0)
    bm[-1].rightBarline = bar.Barline('final')
    return bm

def example6_8():
    '''
    >>> from music21.braille import translate
    >>> print translate.partToBraille(example6_8())
    ⠼⠁⠀⠨⠹⠙⠣⠚⠣⠊⠙⠛⠣⠊⠈⠉⠀⠊⠓⠛⠓⠝⠀⠣⠱⠛⠑⠙⠙⠣⠊⠛⠀⠓⠓⠙⠙⠟⠣⠅
    '''
    bm = tinyNotation.TinyNotationStream("c'4 c'8 b-8 a-8 c'8 f'8 a'-8~ a'-8 g'8 f'8 g'8 c'2\
    d'-4 f'8 d'-8 c'8 c'8 a-8 f8 g8 g8 c8 c8 f2", "4/4")
    bm.makeNotation(inPlace=True, cautionaryNotImmediateRepeat=False)
    bm[0].pop(0)
    bm[-1].rightBarline = bar.Barline('final')
    return bm

def example6_9():
    '''
    >>> from music21.braille import translate
    >>> print translate.partToBraille(example6_9())
    ⠼⠁⠀⠸⠫⠗⠫⠀⠩⠻⠎⠻⠀⠓⠊⠺⠳⠫⠀⠩⠑⠋⠩⠻⠱⠳⠀⠹⠏⠩⠻⠀⠳⠞⠹⠀⠀⠀⠀⠀
    ⠀⠀⠸⠚⠊⠓⠚⠊⠓⠩⠛⠩⠑⠀⠯⠣⠅
    '''
    bm = tinyNotation.TinyNotationStream("E4 G2 E4 F#4 A2 F#4 G8 A8 B4 G4 E4 D#8 E8 F#4 D#4 G4\
    C4 E2 F#4 G4 B2 c4 B8 A8 G8 B8 A8 G8 F#8 D#8 E1")
    bm.makeNotation(inPlace=True, cautionaryNotImmediateRepeat=False)
    bm[0].pop(0)
    bm[-1].rightBarline = bar.Barline('final')
    return bm

def example6_10():
    '''
    >>> from music21.braille import translate
    >>> print translate.partToBraille(example6_10())
    ⠼⠁⠀⠐⠪⠎⠪⠈⠉⠀⠪⠧⠣⠞⠀⠹⠹⠧⠹⠈⠉⠀⠹⠧⠕⠀⠋⠫⠋⠻⠧⠀⠋⠫⠋⠱⠧⠀⠀⠀
    ⠀⠀⠨⠙⠹⠙⠣⠚⠺⠚⠀⠎⠄⠧⠣⠅
    '''
    bm = tinyNotation.TinyNotationStream("a4 a2 a4~ a4 r4 b-2 c'4 c'4 r4 c'4~ c'4 r4 d'2\
    e'8 e'4 e'8 f'4 r4 e'8 e'4 e'8 d'4 r4 c'8 c'4 c'8 b-8 b-4 b-8 a2. r4")
    bm.makeNotation(inPlace=True, cautionaryNotImmediateRepeat=False)
    bm[0].pop(0)
    bm[-1].rightBarline = bar.Barline('final')
    return bm

def example6_11():
    '''
    >>> from music21.braille import translate
    >>> print translate.partToBraille(example6_11())
    ⠼⠁⠀⠸⠪⠄⠚⠹⠺⠀⠊⠙⠋⠙⠊⠙⠫⠀⠱⠄⠛⠪⠻⠀⠑⠛⠊⠛⠑⠛⠪⠀⠩⠳⠄⠋⠎⠀⠀⠀
    ⠀⠀⠐⠺⠄⠚⠝⠀⠑⠙⠚⠊⠩⠓⠋⠩⠛⠓⠀⠎⠈⠉⠊⠩⠓⠪⠣⠅
    '''
    bm = tinyNotation.TinyNotationStream("A4. B8 c4 B4 A8 c8 e8 c8 A8 c8 e4 d4. f8 a4 f4 d8 f8 a8 f8 d8 f8 a4\
    g#4. e8 a2 b4. b8 c'2 d'8 c'8 b8 a8 g#8 e8 f#8 g#8 a2~ a8 g#8 a4")
    bm.makeNotation(inPlace=True, cautionaryNotImmediateRepeat=False)
    bm[0].pop(0)
    bm[-1].rightBarline = bar.Barline('final')
    return bm

def example6_12():
    '''
    >>> from music21.braille import translate
    >>> print translate.partToBraille(example6_12())
    ⠼⠁⠀⠨⠋⠣⠋⠑⠣⠑⠙⠊⠣⠊⠓⠀⠣⠣⠚⠣⠊⠓⠣⠓⠛⠋⠑⠙⠀⠑⠚⠣⠚⠡⠚⠙⠑⠋⠛⠀
    ⠀⠀⠐⠓⠩⠓⠊⠚⠹⠧⠣⠅
    '''
    bm = tinyNotation.TinyNotationStream("e'8 e'-8 d'8 d'-8 c'8 a8 a-8 g8 b--8 a-8 g8 g-8 f8 e8 d8 c8 d8 B8 B-8 Bn8 c8 d8 e8 f8 g8 g#8 a8 b8 c'4 r4")
    bm.makeNotation(inPlace=True, cautionaryNotImmediateRepeat=False)
    bm.measure(2).notes[5].accidental.displayStatus = False
    bm.measure(2).notes[6].accidental.displayStatus = False
    bm.measure(3).notes[1].accidental.displayStatus = False
    bm[0].pop(0)
    bm[-1].rightBarline = bar.Barline('final')
    return bm

#-------------------------------------------------------------------------------
# Chapter 7: Octave Marks

def example7_1():
    '''
    >>> from music21.braille import translate
    >>> print translate.partToBraille(example7_1())
    ⠼⠁⠀⠈⠽⠀⠘⠽⠀⠸⠽⠀⠐⠽⠀⠨⠽⠀⠰⠽⠀⠠⠽
    '''
    bm = stream.Part()
    bm.append(note.Note('C1', quarterLength=4.0))
    bm.append(note.Note('C2', quarterLength=4.0))
    bm.append(note.Note('C3', quarterLength=4.0))
    bm.append(note.Note('C4', quarterLength=4.0))
    bm.append(note.Note('C5', quarterLength=4.0))
    bm.append(note.Note('C6', quarterLength=4.0))
    bm.append(note.Note('C7', quarterLength=4.0))
    bm.makeNotation(inPlace=True, cautionaryNotImmediateRepeat=False)
    bm[0].pop(0)
    bm[-1].rightBarline = None
    return bm

def example7_2():
    '''
    >>> from music21.braille import translate
    >>> print translate.partToBraille(example7_2())
    ⠼⠁⠀⠈⠈⠮⠾⠀⠠⠠⠽
    '''
    bm = stream.Part()
    bm.append(note.Note('A0', quarterLength=4.0))
    bm.append(note.Note('B0', quarterLength=4.0))
    bm.append(note.Note('C8', quarterLength=4.0))
    bm.insert(0, meter.TimeSignature('2/1'))
    bm.makeNotation(inPlace=True, cautionaryNotImmediateRepeat=False)
    bm[0].pop(0)
    bm[-1].rightBarline = None
    return bm
    
def example7_3a():
    '''
    >>> from music21.braille import translate
    >>> print translate.measureToBraille(example7_3a()[0])
    ⠐⠹⠫
    '''
    bm = tinyNotation.TinyNotationStream("c4 e4")
    bm.makeNotation(inPlace=True, cautionaryNotImmediateRepeat=False)
    bm[0].pop(1)
    bm[-1].rightBarline = None
    return bm

def example7_3b():
    '''
    >>> from music21.braille import translate
    >>> print translate.measureToBraille(example7_3b()[0])
    ⠨⠝⠄⠪
    '''
    bm = tinyNotation.TinyNotationStream("c'2. a4")
    bm.makeNotation(inPlace=True, cautionaryNotImmediateRepeat=False)
    bm[0].pop(1)
    bm[-1].rightBarline = None
    return bm

def example7_4a():
    '''
    >>> from music21.braille import translate
    >>> print translate.measureToBraille(example7_4a()[0])
    ⠐⠝⠐⠎
    '''
    bm = tinyNotation.TinyNotationStream("c2 a2", "4/4")
    bm.makeNotation(inPlace=True, cautionaryNotImmediateRepeat=False)
    bm[0].pop(1)
    bm[-1].rightBarline = None
    return bm

def example7_4b():
    '''
    >>> from music21.braille import translate
    >>> print translate.measureToBraille(example7_4b()[0])
    ⠨⠝⠐⠏
    '''
    bm = tinyNotation.TinyNotationStream("c'2 e2", "4/4")
    bm.makeNotation(inPlace=True, cautionaryNotImmediateRepeat=False)
    bm[0].pop(1)
    bm[-1].rightBarline = None
    return bm

def example7_5a():
    '''
    >>> from music21.braille import translate
    >>> print translate.measureToBraille(example7_5a()[0])
    ⠸⠝⠟
    '''
    bm = tinyNotation.TinyNotationStream("C2 F2")
    bm.makeNotation(inPlace=True, cautionaryNotImmediateRepeat=False)
    bm[0].pop(1)
    bm[-1].rightBarline = None
    return bm

def example7_5b():
    '''
    >>> from music21.braille import translate
    >>> print translate.measureToBraille(example7_5b()[0])
    ⠐⠟⠨⠝
    '''
    bm = tinyNotation.TinyNotationStream("f2 c'2")
    bm.makeNotation(inPlace=True, cautionaryNotImmediateRepeat=False)
    bm[0].pop(1)
    bm[-1].rightBarline = None
    return bm

def example7_6():
    '''
    >>> from music21.braille import translate
    >>> inPart = example7_6()
    >>> print translate.partToBraille(inPart)
    ⠼⠁⠀⠣⠨⠋⠋⠋⠋⠀⠑⠑⠣⠺⠀⠙⠙⠙⠙⠀⠣⠐⠋⠨⠙⠣⠺⠀⠛⠛⠨⠹⠀⠣⠚⠚⠨⠻⠀⠀
    ⠀⠀⠣⠨⠋⠑⠙⠣⠚⠀⠣⠨⠫⠣⠐⠫⠣⠅
    >>> inPart.measure(7).notes[3].accidental
    <accidental flat>
    >>> inPart.measure(7).notes[3].accidental.displayStatus == True
    True
    '''
    bm = tinyNotation.TinyNotationStream("e'-8 e'-8 e'-8 e'-8 d'8 d'8 b-4 c'8 c'8 c'8 c'8 e-8 c'8 b-4\
    f8 f8 c'4 b-8 b-8 f'4 e'-8 d'8 c'8 b-8 e'-4 e-4", "4/8")
    bm.makeNotation(inPlace=True, cautionaryNotImmediateRepeat=False)
    bm[0].pop(0)
    bm[-1].rightBarline = bar.Barline('final')
    return bm

def example7_7():
    '''
    "Whenever the marking “8va” occurs in print over or under certain notes, 
    these notes should be transcribed according to the octaves in which they 
    are actually to be played." page 42, Braille Transcription Manual
    
    >>> from music21.braille import translate
    >>> print translate.partToBraille(example7_7())
    ⠼⠁⠀⠐⠊⠙⠛⠙⠀⠨⠊⠙⠛⠙⠀⠰⠊⠛⠙⠑⠀⠨⠊⠛⠋⠙⠀⠟⠣⠅
    '''
    bm = tinyNotation.TinyNotationStream("a8 c'8 f'8 c'8 a8 c'8 f'8 c'8 a'8 f'8 c'8 d'8 a'8 f'8 e'8 c'8 f'2", "4/8")
    bm.makeNotation(inPlace=True, cautionaryNotImmediateRepeat=False)
    bm[0].pop(0)
    bm[1].transpose(value='P8', inPlace=True)
    bm[2].transpose(value='P8', inPlace=True)
    bm[-1].rightBarline = bar.Barline('final')
    return bm

def example7_8():
    '''
    >>> from music21.braille import translate
    >>> print translate.partToBraille(example7_8())
    ⠼⠁⠀⠸⠝⠘⠳⠸⠫⠀⠱⠄⠙⠹⠹⠀⠸⠎⠳⠫⠀⠱⠗⠳⠀⠐⠹⠄⠚⠪⠳⠀⠪⠻⠹⠪⠀⠀⠀⠀
    ⠀⠀⠘⠳⠳⠸⠱⠳⠀⠫⠝⠄⠣⠅
    '''
    bm = tinyNotation.TinyNotationStream("C2 GG4 E4 D4. C8 C4 C4 A2 G4 E4 D4 G2 G4\
    c4. B8 A4 G4 A4 F4 C4 AA4 GG4 GG4 D4 G4 E4 C2.")
    bm.makeNotation(inPlace=True, cautionaryNotImmediateRepeat=False)
    bm[0].pop(0)
    bm[-1].rightBarline = bar.Barline('final')
    return bm

def example7_9():
    '''
    >>> from music21.braille import translate
    >>> print translate.partToBraille(example7_9())
    ⠼⠁⠀⠐⠫⠄⠊⠙⠋⠀⠱⠑⠙⠺⠀⠫⠄⠩⠓⠚⠨⠋⠀⠹⠙⠚⠪⠀⠊⠩⠙⠋⠊⠨⠙⠓⠀⠀⠀⠀
    ⠀⠀⠨⠛⠑⠐⠊⠨⠋⠑⠐⠛⠀⠨⠙⠚⠐⠑⠊⠩⠓⠋⠀⠎⠄⠣⠅
    '''
    bm = tinyNotation.TinyNotationStream("e4. a8 c'8 e'8 d'4 d'8 c'8 b4 e4. g#8 b8 e'8 c'4 c'8 b8 a4\
    a8 c'#8 e'8 a'8 c'#8 g'8 f'8 d'8 a8 e'8 d'8 f8 c'8 b8 d8 a8 g#8 e8 a2.", "3/4")
    bm.makeNotation(inPlace=True, cautionaryNotImmediateRepeat=False)
    bm[0].pop(0)
    bm[-1].rightBarline = bar.Barline('final')
    return bm
    
def example7_10():
    '''
    >>> from music21.braille import translate
    >>> inPart = example7_10()
    >>> inPart.measure(2).notes[0].accidental.displayStatus == True
    True
    >>> inPart.measure(2).notes[1].accidental.displayStatus == True
    True
    >>> inPart.measure(3).notes[2].accidental.displayStatus == True
    True
    >>> inPart.measure(3).notes[4].accidental.displayStatus == True
    True
    >>> inPart.measure(3).notes[7].accidental.displayStatus == False
    True
    >>> inPart.measure(4).notes[1].accidental.displayStatus == True
    True
    >>> inPart.measure(4).notes[2].accidental.displayStatus == True
    True
    >>> inPart.measure(5).notes[2].accidental.displayStatus == True
    True
    >>> inPart.measure(7).notes[1].accidental.displayStatus == True
    True
    >>> inPart.measure(7).notes[2].accidental.displayStatus == True
    True
    >>> inPart.measure(7).notes[3].accidental.displayStatus == True
    True
    >>> inPart.measure(7).notes[6].accidental.displayStatus == False
    True
    
        
    >>> print translate.partToBraille(inPart)
    ⠼⠁⠀⠐⠪⠨⠫⠪⠫⠀⠩⠙⠩⠛⠋⠐⠊⠺⠨⠫⠀⠑⠐⠊⠩⠛⠨⠑⠩⠙⠊⠋⠨⠙⠀⠀⠀⠀⠀⠀
    ⠀⠀⠐⠚⠩⠛⠩⠓⠊⠺⠫⠀⠪⠪⠩⠨⠻⠫⠀⠱⠱⠨⠺⠪⠀⠊⠩⠨⠙⠩⠓⠩⠛⠋⠐⠋⠨⠙⠚⠀
    ⠀⠀⠐⠎⠥⠣⠅
    '''
    bm = tinyNotation.TinyNotationStream("a4 e'4 a'4 e'4 c'#8 f'#8 e'8 a8 b4 e'4 d'8 a8 f#8 d'8 c'#8 a8 e8 c'#8 b8 f#8 g#8 a8 b4 e4\
    a4 a4 f'#4 e'4 d'4 d'4 b'4 a'4 a'8 c'#8 g'#8 f'#8 e'8 e8 c'#8 b8 a2 r2", "4/4")
    bm.makeNotation(inPlace=True, cautionaryNotImmediateRepeat=False)
    bm[0].pop(0)
    bm[-1].rightBarline = bar.Barline('final')
    return bm

def example7_11():
    '''
    >>> from music21.braille import translate
    >>> inPart = example7_11()
    >>> inPart.measure(4).notes[0].accidental.displayStatus == True # A-3
    True
    >>> inPart.measure(4).notes[3].accidental.displayStatus == False # A-3
    True
    >>> inPart.measure(5).notes[1].accidental.displayStatus == True # E-3
    True
    >>> inPart.measure(5).notes[2].accidental.displayStatus == True # A-3
    True
    >>> inPart.measure(6).notes[0].accidental.displayStatus == True # E-3
    True
    >>> inPart.measure(6).notes[5].accidental.displayStatus == True # E-2
    True
    
    >>> print translate.partToBraille(inPart)
    ⠼⠚⠀⠘⠓⠀⠸⠹⠘⠓⠸⠹⠣⠋⠀⠱⠘⠓⠸⠱⠓⠀⠹⠓⠐⠹⠣⠚⠀⠣⠪⠛⠹⠸⠊⠀⠀⠀⠀⠀
    ⠀⠀⠸⠓⠣⠋⠣⠊⠓⠙⠛⠀⠣⠋⠘⠓⠸⠑⠙⠘⠓⠣⠋⠀⠛⠸⠑⠙⠡⠚⠓⠓⠀⠹⠄⠧⠣⠅
    '''
    bm = tinyNotation.TinyNotationStream("r2 r8 GG8 C4 GG8 C4 E-8 D4 GG8 D4 G8 C4 G8 c4 B-8 A-4 F8 C4 A-8\
    G8 E-8 A-8 G8 C8 F8 E-8 GG8 D8 C8 GG8 EE-8 FF8 D8 C8 BBn8 GG8 GG8 CC4. r4", "6/8")
    bm.makeNotation(inPlace=True, cautionaryNotImmediateRepeat=False)
    for numRest in range(2):
        bm[0].pop(2)
    bm[0].padAsAnacrusis()
    bm[0].pop(0)
    bm[-1].rightBarline = bar.Barline('final')
    for measure in bm:
        measure.number -= 1
    bm.measure(7).notes[3].accidental = pitch.Accidental()
    return bm

#-------------------------------------------------------------------------------
# Chapter 8: The Music Heading: Signatures, Tempo, and Mood

def example8_1a():
    '''
    Flats.
    
    >>> from music21.braille import translate
    >>> print translate.keySigToBraille(key.KeySignature(-1))
    ⠣
    >>> print translate.keySigToBraille(key.KeySignature(-2))
    ⠣⠣
    >>> print translate.keySigToBraille(key.KeySignature(-3))
    ⠣⠣⠣
    >>> print translate.keySigToBraille(key.KeySignature(-4))
    ⠼⠙⠣
    >>> print translate.keySigToBraille(key.KeySignature(-5))
    ⠼⠑⠣
    >>> print translate.keySigToBraille(key.KeySignature(-6))
    ⠼⠋⠣
    >>> print translate.keySigToBraille(key.KeySignature(-7))
    ⠼⠛⠣
    '''
    pass
    
def example8_1b():
    '''
    Sharps.
    
    >>> from music21.braille import translate
    >>> print translate.keySigToBraille(key.KeySignature(1))
    ⠩
    >>> print translate.keySigToBraille(key.KeySignature(2))
    ⠩⠩
    >>> print translate.keySigToBraille(key.KeySignature(3))
    ⠩⠩⠩
    >>> print translate.keySigToBraille(key.KeySignature(4))
    ⠼⠙⠩
    >>> print translate.keySigToBraille(key.KeySignature(5))
    ⠼⠑⠩
    >>> print translate.keySigToBraille(key.KeySignature(6))
    ⠼⠋⠩
    >>> print translate.keySigToBraille(key.KeySignature(7))
    ⠼⠛⠩
    '''
    pass
    
def example8_2():
    '''
    Time signatures with two numbers.
    
    >>> from music21.braille import translate
    >>> print translate.timeSigToBraille(meter.TimeSignature('6/8'))
    ⠼⠋⠦
    >>> print translate.timeSigToBraille(meter.TimeSignature('2/4'))
    ⠼⠃⠲
    >>> print translate.timeSigToBraille(meter.TimeSignature('12/8'))
    ⠼⠁⠃⠦
    >>> print translate.timeSigToBraille(meter.TimeSignature('2/2'))
    ⠼⠃⠆
    '''
    pass

def example8_3():
    '''
    Time signatures with one number. Not currently supported.
    '''
    pass

def example8_4():
    '''
    Combined time signatures. Not currently supported.
    '''
    pass

def example8_5():
    '''
    Common/cut time signatures.
    
    >>> from music21.braille import translate
    >>> print translate.timeSigToBraille(meter.TimeSignature('common'))
    ⠨⠉
    >>> print translate.timeSigToBraille(meter.TimeSignature('cut'))
    ⠸⠉
    '''
    pass

def example8_6():
    '''
    Combined key and time signatures.
    
    >>> from music21.braille import translate
    >>> print translate.keyAndTimeSigToBraille(sampleKeySig = key.KeySignature(1), sampleTimeSig = meter.TimeSignature('2/4'))
    ⠩⠼⠃⠲
    >>> print translate.keyAndTimeSigToBraille(sampleKeySig = key.KeySignature(-3), sampleTimeSig = meter.TimeSignature('3/4'))
    ⠣⠣⠣⠼⠉⠲
    >>> print translate.keyAndTimeSigToBraille(sampleKeySig = key.KeySignature(4), sampleTimeSig = meter.TimeSignature('3/8'))
    ⠼⠙⠩⠼⠉⠦
    >>> print translate.keyAndTimeSigToBraille(sampleKeySig = key.KeySignature(3), sampleTimeSig = meter.TimeSignature('3/8'))
    ⠩⠩⠩⠼⠉⠦
    
    
    The following two cases are identical, having no key signature is equivalent to having a key signature with no sharps or flats.
    
    
    >>> print translate.keyAndTimeSigToBraille(sampleKeySig = None, sampleTimeSig = meter.TimeSignature('4/4'))
    ⠼⠙⠲
    >>> print translate.keyAndTimeSigToBraille(sampleKeySig = key.KeySignature(0), sampleTimeSig = meter.TimeSignature('4/4'))
    ⠼⠙⠲
    
    
    >>> print translate.keyAndTimeSigToBraille(sampleKeySig = key.KeySignature(-1), sampleTimeSig = meter.TimeSignature('3/4'))
    ⠣⠼⠉⠲
    >>> print translate.keyAndTimeSigToBraille(sampleKeySig = key.KeySignature(0), sampleTimeSig = meter.TimeSignature('6/8'))
    ⠼⠋⠦
    '''
    pass

def example8_7a():
    '''
    >>> from music21.braille import translate
    >>> from music21 import key
    >>> from music21 import meter
    >>> from music21 import tempo
    >>> print translate.headingToBraille(sampleTempoText = tempo.TempoText("Andante"), sampleKeySig = key.KeySignature(-4),\
    sampleTimeSig = meter.TimeSignature("4/4"), sampleMetronomeMark = None)
    ⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠠⠁⠝⠙⠁⠝⠞⠑⠲⠀⠼⠙⠣⠼⠙⠲⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
    >>> print translate.headingToBraille(sampleTempoText = tempo.TempoText("Con moto"), sampleKeySig = key.KeySignature(3),\
    sampleTimeSig = meter.TimeSignature("3/8"), sampleMetronomeMark = None)
    ⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠠⠉⠕⠝⠀⠍⠕⠞⠕⠲⠀⠩⠩⠩⠼⠉⠦⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
    >>> print translate.headingToBraille(sampleTempoText = tempo.TempoText("Andante cantabile"), sampleKeySig = None,\
    sampleTimeSig = meter.TimeSignature("4/4"), sampleMetronomeMark = None)
    ⠀⠀⠀⠀⠀⠀⠀⠀⠠⠁⠝⠙⠁⠝⠞⠑⠀⠉⠁⠝⠞⠁⠃⠊⠇⠑⠲⠀⠼⠙⠲⠀⠀⠀⠀⠀⠀⠀⠀⠀
    >>> print translate.headingToBraille(sampleTempoText = tempo.TempoText("Very brightly"), sampleKeySig = key.KeySignature(2),\
    sampleTimeSig = meter.TimeSignature("7/8"), sampleMetronomeMark = None)
    ⠀⠀⠀⠀⠀⠀⠀⠀⠀⠠⠧⠑⠗⠽⠀⠃⠗⠊⠛⠓⠞⠇⠽⠲⠀⠩⠩⠼⠛⠦⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
    '''
    pass
    
def example8_8():
    '''
    Metronome Markings
    
    >>> print translate.metronomeMarkToBraille(sampleMetronomeMark = tempo.MetronomeMark(number = 80, referent = note.HalfNote()))
    ⠝⠶⠼⠓⠚
    '''
    pass

def example8_9():
    '''
    >>> from music21.braille import translate
    >>> from music21 import key
    >>> from music21 import meter
    >>> from music21 import tempo
    >>> print translate.headingToBraille(sampleTempoText = tempo.TempoText("Andante"), sampleKeySig = key.KeySignature(-3),\
    sampleTimeSig = meter.TimeSignature("12/8"), sampleMetronomeMark = tempo.MetronomeMark(number = 132, referent = note.EighthNote()))
    ⠀⠀⠀⠀⠀⠀⠀⠀⠠⠁⠝⠙⠁⠝⠞⠑⠲⠀⠙⠶⠼⠁⠉⠃⠀⠣⠣⠣⠼⠁⠃⠦⠀⠀⠀⠀⠀⠀⠀⠀
    >>> print translate.headingToBraille(sampleTempoText = tempo.TempoText("Lento assai, cantante e tranquillo"), sampleKeySig = key.KeySignature(-5),\
    sampleTimeSig = meter.TimeSignature("6/8"), sampleMetronomeMark = tempo.MetronomeMark(number = 52, referent = note.Note(quarterLength = 1.5)))
    ⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠠⠇⠑⠝⠞⠕⠀⠁⠎⠎⠁⠊⠂⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
    ⠀⠀⠀⠀⠀⠀⠀⠀⠀⠉⠁⠝⠞⠁⠝⠞⠑⠀⠑⠀⠞⠗⠁⠝⠟⠥⠊⠇⠇⠕⠲⠀⠀⠀⠀⠀⠀⠀⠀⠀
    ⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠹⠄⠶⠼⠑⠃⠀⠼⠑⠣⠼⠋⠦⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
    '''
    pass

def drill8_1():
    '''
    >>> from music21.braille import translate
    >>> print translate.partToBraille(drill8_1())
    ⠀⠀⠀⠀⠀⠀⠠⠁⠝⠙⠁⠝⠞⠑⠀⠍⠁⠑⠎⠞⠕⠎⠕⠲⠀⠹⠶⠼⠊⠃⠀⠨⠉⠀⠀⠀⠀⠀⠀⠀
    ⠼⠁⠀⠐⠎⠓⠛⠫⠀⠱⠫⠛⠓⠪⠀⠳⠨⠙⠚⠪⠳⠀⠻⠄⠋⠕⠀⠹⠫⠪⠨⠫⠀⠫⠱⠙⠚⠪⠀⠀
    ⠀⠀⠨⠪⠓⠛⠫⠱⠀⠹⠊⠚⠝⠣⠅
    '''
    bm = tinyNotation.TinyNotationStream("a2 g8 f8 e4 d4 e4 f8 g8 a4 g4 c'8 b8 a4 g4 f4. e8 d2\
    c4 e4 a4 e'4 e'4 d'4 c'8 b8 a4 a'4 g'8 f'8 e'4 d'4 c'4 a8 b8 c'2", "c")
    bm.insert(0, tempo.TempoText("Andante maestoso"))
    bm.insert(0, tempo.MetronomeMark(number=92, referent=note.QuarterNote()))
    bm.makeNotation(inPlace=True, cautionaryNotImmediateRepeat=False)
    bm[-1].rightBarline = bar.Barline('final')
    return bm

def drill8_2():
    '''
    >>> from music21.braille import translate
    >>> print translate.partToBraille(drill8_2())
    ⠀⠀⠀⠀⠀⠀⠀⠀⠠⠊⠝⠀⠎⠞⠗⠊⠉⠞⠀⠞⠊⠍⠑⠲⠀⠣⠣⠣⠼⠉⠲⠀⠀⠀⠀⠀⠀⠀⠀⠀
    ⠼⠁⠀⠸⠋⠭⠘⠚⠭⠸⠋⠭⠀⠡⠫⠻⠩⠻⠀⠓⠭⠑⠭⠓⠭⠀⠪⠳⠻⠀⠋⠭⠙⠭⠊⠭⠀⠀⠀⠀
    ⠀⠀⠡⠘⠪⠺⠡⠺⠀⠙⠑⠭⠋⠭⠘⠚⠀⠸⠋⠡⠋⠭⠛⠭⠩⠛⠀⠓⠑⠭⠓⠭⠊⠀⠊⠓⠭⠛⠭⠋
    ⠀⠀⠸⠑⠙⠺⠈⠺⠀⠘⠏⠄⠣⠅
    '''
    bm = tinyNotation.TinyNotationStream("E-8 r8 BB-8 r8 E-8 r8 En4 F4 F#4 G8 r8 D8 r8 G8 r8 A-4 G4 F4\
    E-8 r8 C8 r8 AA-8 r8 AAn4 BB-4 BBn4 C8 D8 r8 E-8 r8 BB-8 E-8 En8 r8 F8 r8 F#8\
    G8 D8 r8 G8 r8 A-8 A-8 G8 r8 F8 r8 E-8 D8 C8 BB-4 BB-4 EE-2.", "3/4")
    bm.insert(0, key.KeySignature(-3))
    bm.insert(0, tempo.TempoText("In strict time"))
    bm.makeNotation(inPlace=True, cautionaryNotImmediateRepeat=False)
    bm[-1].rightBarline = bar.Barline('final')
    bm[-2].notes[-1].transpose('P-8', inPlace=True)
    bm.measure(7).notes[-1].accidental.displayStatus = False # flat not strictly necessary
    bm.measure(11).notes[-1].accidental.displayStatus = False # flat not necessary (never?)
    return bm

def drill8_3():
    '''
    >>> from music21.braille import translate
    >>> print translate.partToBraille(drill8_3())
    ⠀⠀⠀⠀⠀⠀⠀⠀⠠⠉⠕⠝⠀⠙⠑⠇⠊⠉⠁⠞⠑⠵⠵⠁⠲⠀⠼⠑⠩⠼⠋⠦⠀⠀⠀⠀⠀⠀⠀⠀
    ⠼⠚⠀⠨⠑⠙⠀⠺⠄⠈⠉⠚⠑⠓⠀⠳⠄⠻⠭⠀⠫⠄⠈⠉⠋⠑⠐⠓⠀⠨⠱⠙⠱⠭⠀⠀⠀⠀⠀⠀
    ⠀⠀⠐⠊⠓⠊⠚⠊⠚⠀⠙⠑⠋⠛⠓⠊⠀⠚⠛⠑⠓⠋⠐⠚⠀⠨⠻⠑⠋⠑⠙⠀⠚⠛⠨⠑⠺⠛⠀⠀
    ⠀⠀⠐⠑⠛⠚⠹⠊⠀⠞⠄⠈⠉⠀⠺⠄⠭⠣⠅
    '''
    bm = tinyNotation.TinyNotationStream("r2 d'#8 c'#8 b4.~ b8 d'#8 g'#8 g'#4. f'#4 r8 e'4.~ e'8 d'#8 g#8 d'#4 c'#8 d'#4 r8 a#8 g#8 a#8 b8 a#8 b8\
    c'#8 d'#8 e'8 f'#8 g'#8 a'#8 b'8 f'#8 d'#8 g'#8 e'8 b8 f'#4 d'#8 e'8 d'#8 c'#8 b8 f#8 d'#8 b4 f#8 d#8 f#8 b8 c'#4 a#8 b2.~ b4. r8", "6/8")
    bm.insert(0, key.KeySignature(5))
    bm.insert(0, tempo.TempoText("Con delicatezza"))
    bm.makeNotation(inPlace=True, cautionaryNotImmediateRepeat=False)
    bm[-1].rightBarline = bar.Barline('final')
    bm[0].pop(4)
    bm[0].padAsAnacrusis()
    for measure in bm:
        measure.number -= 1
    return bm

def drill8_4():
    '''
    >>> from music21.braille import translate
    >>> print translate.partToBraille(drill8_4())
    ⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠠⠛⠗⠁⠵⠊⠕⠎⠕⠲⠀⠣⠼⠙⠲⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
    ⠼⠁⠀⠸⠎⠄⠄⠓⠀⠟⠫⠱⠀⠫⠄⠛⠳⠫⠀⠩⠝⠱⠧⠀⠘⠎⠄⠄⠡⠚⠀⠩⠹⠄⠑⠫⠳⠀⠀⠀
    ⠀⠀⠸⠻⠳⠪⠻⠀⠕⠄⠄⠭⠣⠅
    '''
    bm = tinyNotation.TinyNotationStream("A2.. G8 F2 E4 D4 E4. F8 G4 E4 C#2 D4 r4 AA2.. BBn8 C#4. D8 E4 G4 F4 G4 A4 F4 D2.. r8", "4/4")
    bm.insert(0, key.KeySignature(-1))
    bm.insert(0, tempo.TempoText("Grazioso"))
    bm.makeNotation(inPlace=True, cautionaryNotImmediateRepeat=False)
    bm[-1].rightBarline = bar.Barline('final')
    return bm

def drill8_5():
    '''
    >>> from music21.braille import translate
    >>> print translate.partToBraille(drill8_5())
    ⠀⠀⠀⠀⠀⠀⠀⠠⠃⠑⠝⠀⠍⠁⠗⠉⠁⠞⠕⠲⠀⠝⠶⠼⠁⠁⠃⠀⠣⠣⠸⠉⠀⠀⠀⠀⠀⠀⠀⠀
    ⠼⠚⠀⠨⠻⠫⠀⠕⠺⠳⠀⠨⠏⠹⠐⠻⠀⠨⠟⠫⠱⠀⠝⠐⠻⠻⠀⠗⠻⠳⠀⠎⠨⠱⠹⠀⠺⠪⠺⠹
    ⠀⠀⠨⠕⠫⠻⠀⠗⠫⠹⠀⠟⠱⠺⠀⠨⠏⠹⠐⠻⠀⠨⠕⠺⠺⠀⠝⠺⠹⠀⠱⠺⠹⠱⠀⠺⠹⠺⠪⠀
    ⠀⠀⠐⠞⠣⠅
    '''
    bm = tinyNotation.TinyNotationStream("r2 f'4 e'-4 d'2 b-4 g4 e'-2 c'4 f4 f'2 e'-4 d'4 c'2 f4 f4 g2 f4 g4\
    a2 d'4 c'4 b-4 a4 b-4 c'4 d'2 e'-4 f'4 g'2 e'-4 c'4 f'2 d'4 b-4\
    e'-2 c'4 f4 d'2 b-4 b-4 c'2 b-4 c'4 d'4 b-4 c'4 d'4 b-4 c'4 b-4 a4 b-2", "cut")
    bm.insert(0, key.KeySignature(-2))
    bm.insert(0, tempo.TempoText("Ben marcato"))
    bm.insert(0, tempo.MetronomeMark(number=112, referent=note.HalfNote()))
    bm.makeNotation(inPlace=True, cautionaryNotImmediateRepeat=False)
    bm[-1].rightBarline = bar.Barline('final')
    bm[0].pop(5)
    bm[0].padAsAnacrusis()
    for measure in bm:
        measure.number -= 1
    return bm

#-------------------------------------------------------------------------------
# Chapter 9: Fingering

def example9_1():
    '''
    >>> from music21.braille import translate
    >>> print translate.partToBraille(example9_1(), measureNumberWithHeading = False, recenterHeading = True)
    ⠀⠀⠀⠀⠣⠼⠃⠲⠀⠀⠀
    ⠐⠪⠂⠳⠇⠀⠻⠄⠃⠙⠁
    '''
    bm = tinyNotation.TinyNotationStream("a4 g f. c8", "2/4")
    bm.insert(0, key.KeySignature(-1))
    bm.makeNotation(inPlace=True, cautionaryNotImmediateRepeat=False)
    bm[-1].rightBarline = None
    bm[0].notes[0].fingering = '4'
    bm[0].notes[1].fingering = '3'
    bm[1].notes[0].fingering = '2'
    bm[1].notes[1].fingering = '1'
    return bm

def example9_2():
    '''
    >>> from music21.braille import translate
    >>> print translate.partToBraille(example9_2(), measureNumberWithHeading = False, recenterHeading = True)
    ⠀⠀⠀⠀⠀⠀⠀⠣⠣⠼⠉⠲⠀⠀⠀⠀⠀⠀⠀
    ⠨⠻⠂⠋⠇⠑⠃⠙⠁⠚⠃⠈⠉⠀⠺⠭⠊⠙⠚
    '''
    bm = tinyNotation.TinyNotationStream("f'4 e'-8 d' c' b-~ b-4 r8 a c' b-", "3/4")
    bm.insert(0, key.KeySignature(-2))
    bm.makeNotation(inPlace=True, cautionaryNotImmediateRepeat=False)
    bm[-1].rightBarline = None 
    bm[0].notes[0].fingering = '4'
    bm[0].notes[1].fingering = '3'
    bm[0].notes[2].fingering = '2'
    bm[0].notes[3].fingering = '1'
    bm[0].notes[4].fingering = '2'
    return bm
    
def example9_3():
    '''
    >>> from music21.braille import translate
    >>> print translate.partToBraille(example9_3(), measureNumberWithHeading = False, recenterHeading = True)
    ⠀⠀⠀⠀⠼⠋⠦⠀⠀⠀⠀⠀
    ⠐⠝⠄⠁⠈⠉⠀⠹⠄⠻⠃⠓
    '''
    bm = tinyNotation.TinyNotationStream("c2.~ c4. f4 g8", "6/8")
    bm.makeNotation(inPlace=True, cautionaryNotImmediateRepeat=False)
    bm[-1].rightBarline = None 
    bm[0].notes[0].fingering = '1'
    bm[1].notes[1].fingering = '2'
    return bm

def example9_4a():
    '''
    >>> from music21.braille import translate
    >>> print translate.partToBraille(example9_4a(), measureNumberWithHeading = False, recenterHeading = True)
    ⠀⠩⠩⠼⠉⠲⠀
    ⠐⠕⠃⠉⠁⠸⠻
    '''
    bm = tinyNotation.TinyNotationStream("d2 F#4", "3/4")
    bm.insert(0, key.KeySignature(2))
    bm.makeNotation(inPlace=True, cautionaryNotImmediateRepeat=False)
    bm[-1].rightBarline = None 
    bm[0].notes[0].fingering = '2-1'
    return bm

def example9_4b():
    '''
    >>> from music21.braille import translate
    >>> print translate.partToBraille(example9_4b(), measureNumberWithHeading = False, recenterHeading = True)
    ⠀⠼⠉⠲⠀⠀  
    ⠐⠝⠇⠉⠁⠳
    '''
    bm = tinyNotation.TinyNotationStream("c2 g4", "3/4")
    bm.makeNotation(inPlace=True, cautionaryNotImmediateRepeat=False)
    bm[-1].rightBarline = None 
    bm[0].notes[0].fingering = '3-1'
    return bm

def example9_5a():
    '''
    >>> from music21.braille import translate
    >>> print translate.partToBraille(example9_5a(), measureNumberWithHeading = False, recenterHeading = True)
    ⠀⠀⠼⠃⠲⠀⠀⠀
    ⠐⠙⠋⠓⠨⠙⠅⠂
    '''
    bm = tinyNotation.TinyNotationStream("c8 e g c'", "2/4")
    bm.makeNotation(inPlace=True, cautionaryNotImmediateRepeat=False)
    bm[-1].rightBarline = None 
    bm[0].notes[3].fingering = '5|4'
    return bm

def example9_5b():
    '''
    >>> from music21.braille import translate
    >>> print translate.partToBraille(example9_5b(), measureNumberWithHeading = False, recenterHeading = True, upperFirstInNoteFingering = False)
    ⠀⠀⠀⠀⠀⠼⠋⠦⠀⠀⠀⠀⠀⠀
    ⠐⠑⠃⠇⠙⠁⠃⠑⠃⠇⠫⠄⠇⠂
    '''
    bm = tinyNotation.TinyNotationStream("d8 c d e4.", "6/8")
    bm.makeNotation(inPlace=True, cautionaryNotImmediateRepeat=False)
    bm[-1].rightBarline = None 
    bm[0].notes[0].fingering = '3|2'
    bm[0].notes[1].fingering = '2|1'
    bm[0].notes[2].fingering = '3|2'
    bm[0].notes[3].fingering = '4|3'
    return bm
  
def example9_6():
    '''
    >>> from music21.braille import translate
    >>> print translate.partToBraille(example9_6(), measureNumberWithHeading = False, recenterHeading = True, upperFirstInNoteFingering = True) 
    ⠀⠀⠀⠀⠀⠀⠀⠀⠩⠩⠼⠃⠲⠀⠀⠀⠀⠀⠀⠀⠀⠀
    ⠐⠻⠃⠁⠪⠁⠃⠀⠨⠱⠠⠂⠻⠂⠅⠀⠻⠂⠇⠫⠇⠃
    >>> from music21.braille import translate
    >>> print translate.partToBraille(example9_6(), measureNumberWithHeading = False, recenterHeading = True, upperFirstInNoteFingering = False)
    ⠀⠀⠀⠀⠀⠀⠀⠀⠩⠩⠼⠃⠲⠀⠀⠀⠀⠀⠀⠀⠀⠀
    ⠐⠻⠁⠃⠪⠃⠁⠀⠨⠱⠂⠠⠻⠅⠂⠀⠻⠇⠂⠫⠃⠇
    '''
    bm = tinyNotation.TinyNotationStream("f#4 a d' f'# f'# e'", "2/4")
    bm.insert(0, key.KeySignature(2))
    bm.makeNotation(inPlace=True, cautionaryNotImmediateRepeat=False)
    bm[-1].rightBarline = None 
    bm[0].notes[0].fingering = '2,1'
    bm[0].notes[1].fingering = '1,2'
    bm[1].notes[0].fingering = 'x,4'
    bm[1].notes[1].fingering = '4,5'
    bm[2].notes[0].fingering = '4,3'
    bm[2].notes[1].fingering = '3,2'
    return bm

def drill9_1():
    '''
    >>> from music21.braille import translate
    >>> print translate.partToBraille(drill9_1())
    ⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠠⠁⠇⠇⠑⠛⠗⠑⠞⠞⠕⠲⠀⠣⠣⠣⠼⠋⠦⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
    ⠼⠚⠀⠐⠓⠃⠊⠀⠺⠄⠈⠉⠚⠓⠁⠚⠀⠱⠄⠅⠈⠉⠑⠙⠚⠀⠪⠓⠫⠃⠛⠁⠀⠳⠄⠃⠭⠊⠚⠀
    ⠀⠀⠨⠹⠄⠈⠉⠙⠊⠁⠙⠃⠀⠫⠄⠇⠈⠉⠋⠑⠃⠛⠂⠀⠋⠑⠙⠚⠂⠊⠛⠃⠁⠀⠀⠀⠀⠀⠀⠀
    ⠀⠀⠐⠫⠄⠁⠃⠈⠉⠋⠣⠅
    '''
    bm = tinyNotation.TinyNotationStream("r2 g8 a- b-4.~ b-8 g b- d'4.~ d'8 c' b- a-4 g8 e-4 f8 g4. r8 a- b-\
    c'4.~ c'8 a- c' e'-4.~ e'-8 d' f' e'- d' c' b- a- f e-4.~ e-8", "6/8")
    bm.insert(0, tempo.TempoText("Allegretto"))
    bm.insert(0, key.KeySignature(-3))
    bm.makeNotation(inPlace=True, cautionaryNotImmediateRepeat=False)
    bm[0].pop(4)
    bm[0].padAsAnacrusis()
    for m in bm:
        m.number -= 1
    bm[0].notes[0].fingering = '2'
    bm[1].notes[2].fingering = '1'
    bm[2].notes[0].fingering = '5'
    bm[3].notes[2].fingering = '2'
    bm[3].notes[3].fingering = '1'
    bm[4].notes[0].fingering = '2'
    bm[5].notes[2].fingering = '1'
    bm[5].notes[3].fingering = '2'
    bm[6].notes[0].fingering = '3'
    bm[6].notes[2].fingering = '2'
    bm[6].notes[3].fingering = '4'
    bm[7].notes[3].fingering = '4'
    bm[7].notes[5].fingering = '2|1'
    bm[8].notes[0].fingering = '1|2'
    return bm

def drill9_2():
    '''
    >>> from music21.braille import translate
    >>> print translate.partToBraille(drill9_2())
    ⠀⠀⠀⠀⠀⠀⠀⠠⠁⠙⠁⠛⠊⠕⠀⠑⠀⠍⠕⠇⠞⠕⠀⠇⠑⠛⠁⠞⠕⠲⠀⠨⠉⠀⠀⠀⠀⠀⠀⠀
    ⠼⠁⠀⠐⠎⠃⠈⠉⠊⠓⠊⠨⠑⠅⠂⠀⠙⠂⠇⠚⠇⠁⠨⠋⠅⠂⠑⠂⠇⠙⠇⠃⠛⠅⠫⠂⠈⠉⠀⠀
    ⠀⠀⠨⠋⠛⠋⠐⠚⠁⠙⠃⠑⠇⠐⠊⠁⠚⠀⠙⠐⠓⠁⠎⠃⠉⠇⠈⠉⠊⠛⠁⠀⠀⠀⠀⠀⠀⠀⠀⠀
    ⠀⠀⠐⠓⠨⠙⠂⠚⠇⠊⠃⠨⠑⠂⠙⠇⠚⠃⠨⠋⠂⠀⠕⠇⠈⠉⠑⠓⠅⠛⠙⠀⠀⠀⠀⠀⠀⠀⠀⠀
    ⠀⠀⠨⠑⠋⠐⠚⠁⠙⠃⠱⠇⠐⠊⠁⠓⠃⠀⠎⠄⠁⠈⠉⠊⠭⠣⠅
    '''
    bm = tinyNotation.TinyNotationStream("a2~ a8 g a d' c' b e' d' c' f' e'4~ e'8 f' e' b c' d' a b c' g a2~ a8 f\
    g c' b a d' c' b e' d'2~ d'8 g' f' c' d' e' b c' d'4 a8 g a2.~ a8 r", "c")
    bm.insert(0, tempo.TempoText("Adagio e molto legato"))
    bm.makeNotation(inPlace=True, cautionaryNotImmediateRepeat=False)
    bm[0].notes[0].fingering = '2'
    bm[0].notes[4].fingering = '5|4'
    bm[1].notes[0].fingering = '4|3'
    bm[1].notes[1].fingering = '3|1'
    bm[1].notes[2].fingering = '5|4'
    bm[1].notes[3].fingering = '4|3'
    bm[1].notes[4].fingering = '3|2'
    bm[1].notes[5].fingering = '5'
    bm[1].notes[6].fingering = '4'
    bm[2].notes[3].fingering = '1'
    bm[2].notes[4].fingering = '2'
    bm[2].notes[5].fingering = '3'
    bm[2].notes[6].fingering = '1'
    bm[3].notes[1].fingering = '1'
    bm[3].notes[2].fingering = '2-3'
    bm[3].notes[4].fingering = '1'
    bm[4].notes[1].fingering = '4'
    bm[4].notes[2].fingering = '3'
    bm[4].notes[3].fingering = '2'
    bm[4].notes[4].fingering = '4'
    bm[4].notes[5].fingering = '3'
    bm[4].notes[6].fingering = '2'
    bm[4].notes[7].fingering = '4'
    bm[5].notes[0].fingering = '3'
    bm[5].notes[2].fingering = '5'
    bm[6].notes[2].fingering = '1'
    bm[6].notes[3].fingering = '2'
    bm[6].notes[4].fingering = '3'
    bm[6].notes[5].fingering = '1'
    bm[6].notes[6].fingering = '2'
    bm[7].notes[0].fingering = '1'
    return bm

def drill9_3():
    '''
    >>> from music21.braille import translate
    >>> print translate.partToBraille(drill9_3())
    ⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠠⠍⠕⠙⠑⠗⠁⠞⠕⠲⠀⠩⠩⠼⠃⠲⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
    ⠼⠁⠀⠘⠺⠇⠂⠙⠃⠇⠑⠁⠃⠀⠋⠂⠁⠛⠠⠇⠓⠠⠁⠊⠁⠃⠀⠺⠇⠁⠙⠠⠇⠑⠁⠃⠀⠀⠀⠀
    ⠀⠀⠐⠋⠇⠁⠛⠠⠃⠓⠁⠁⠛⠃⠃⠀⠫⠇⠁⠑⠁⠃⠙⠠⠇⠀⠚⠠⠁⠊⠁⠃⠓⠠⠇⠛⠠⠂⠀⠀
    ⠀⠀⠸⠫⠂⠁⠑⠁⠄⠙⠃⠄⠀⠑⠁⠁⠙⠃⠃⠚⠁⠇⠩⠊⠃⠂⠀⠞⠁⠇⠣⠅
    '''
    bm = tinyNotation.TinyNotationStream("BB4 C#8 D E F# G A B4 c#8 d e f# g f# e4 d8 c#\
    B A G F# E4 D8 C# D C# BB AA# BB2", "2/4")
    bm.insert(0, key.KeySignature(2))
    bm.insert(0, tempo.TempoText("Moderato"))
    bm.makeNotation(inPlace=True, cautionaryNotImmediateRepeat=False)
    bm[2].insert(0, clef.TrebleClef())
    bm[5].insert(0, clef.BassClef())
    # measure 1 fingerings
    bm[0].notes[0].fingering = '3,4'
    bm[0].notes[1].fingering = '2,3'
    bm[0].notes[2].fingering = '1,2'
    # measure 2 fingerings
    bm[1].notes[0].fingering = '4,1'
    bm[1].notes[1].fingering = 'x,3'
    bm[1].notes[2].fingering = 'x,1'
    bm[1].notes[3].fingering = '1,2'
    # measure 3 fingerings
    bm[2].notes[0].fingering = '3,1'
    bm[2].notes[1].fingering = 'x,3'
    bm[2].notes[2].fingering = '1,2'
    # measure 4 fingerings    
    bm[3].notes[0].fingering = '3,1'
    bm[3].notes[1].fingering = 'x,2'
    bm[3].notes[2].fingering = '1,1'
    bm[3].notes[3].fingering = '2,2'
    # measure 5 fingerings
    bm[4].notes[0].fingering = '3,1'
    bm[4].notes[1].fingering = '1,2'
    bm[4].notes[2].fingering = 'x,3'
    # measure 6 fingerings
    bm[5].notes[0].fingering = 'x,1'
    bm[5].notes[1].fingering = '1,2'
    bm[5].notes[2].fingering = 'x,3'
    bm[5].notes[3].fingering = 'x,4'
    # measure 7 fingerings
    bm[6].notes[0].fingering = '4,1'
    bm[6].notes[1].fingering = '1,x'
    bm[6].notes[2].fingering = '2,x'
    # measure 8 fingerings
    bm[7].notes[0].fingering = '1,1'
    bm[7].notes[1].fingering = '2,2'
    bm[7].notes[2].fingering = '1,3'
    bm[7].notes[3].fingering = '2,4'
    # measure 9 fingerings
    bm[8].notes[0].fingering = '1,3'
    return bm
    
def drill9_4():
    '''
    >>> from music21.braille import translate
    >>> print translate.partToBraille(drill9_4())
    ⠀⠀⠀⠀⠀⠀⠀⠠⠝⠕⠞⠀⠞⠕⠕⠀⠋⠁⠎⠞⠲⠀⠹⠶⠼⠁⠚⠚⠀⠩⠼⠑⠦⠀⠀⠀⠀⠀⠀⠀
    ⠼⠁⠀⠸⠋⠩⠑⠃⠋⠛⠃⠑⠀⠺⠸⠫⠇⠓⠀⠓⠃⠛⠇⠓⠊⠚⠃⠀⠺⠁⠘⠺⠅⠚⠁⠀⠀⠀⠀⠀
    ⠀⠀⠘⠑⠓⠚⠁⠓⠅⠚⠂⠀⠸⠫⠃⠳⠁⠛⠀⠋⠘⠚⠸⠓⠋⠘⠚⠀⠸⠫⠁⠘⠫⠅⠋⠂⠀⠀⠀⠀
    ⠀⠀⠘⠫⠇⠭⠋⠃⠋⠁⠀⠑⠇⠋⠃⠋⠇⠋⠃⠋⠁⠀⠋⠇⠋⠃⠫⠇⠋⠃⠀⠫⠁⠈⠉⠋⠭⠭⠣⠅
    '''
    bm = tinyNotation.TinyNotationStream("E8 D# E F# D# BB4 E G8 G F# G A B B4 BB BB8 DD GG BB GG BB E4 G F#8\
    E BB G E BB E4 EE EE8 EE4 r8 EE8 EE DD EE EE EE EE EE EE EE4 EE8 EE4~ EE8 r8 r", "5/8")
    bm.insert(0, key.KeySignature(1))
    bm.insert(0, tempo.MetronomeMark(number = 100, referent = note.QuarterNote()))
    bm.insert(0, tempo.TempoText("Not too fast"))
    bm.makeNotation(inPlace=True, cautionaryNotImmediateRepeat=False)
    # measure 1 fingerings
    bm[0].notes[1].fingering = '2'
    bm[0].notes[3].fingering = '2'
    # measure 2 fingerings
    bm[1].notes[1].fingering = '3'
    # measure 3 fingerings
    bm[2].notes[0].fingering = '2'
    bm[2].notes[1].fingering = '3'
    bm[2].notes[4].fingering = '2'
    # measure 4 fingerings    
    bm[3].notes[0].fingering = '1'
    bm[3].notes[1].fingering = '5'
    bm[3].notes[2].fingering = '1'
    # measure 5 fingerings
    bm[4].notes[2].fingering = '1'
    bm[4].notes[3].fingering = '5'
    bm[4].notes[4].fingering = '4'
    # measure 6 fingerings
    bm[5].notes[0].fingering = '2'
    bm[5].notes[1].fingering = '1'
    # measure 8 fingerings
    bm[7].notes[0].fingering = '1'
    bm[7].notes[1].fingering = '5'
    bm[7].notes[2].fingering = '4'
    # measure 9 fingerings
    bm[8].notes[0].fingering = '3'
    bm[8].notes[1].fingering = '2'
    bm[8].notes[2].fingering = '1'
    # measure 10 fingerings
    bm[9].notes[0].fingering = '3'
    bm[9].notes[1].fingering = '2'
    bm[9].notes[2].fingering = '3'
    bm[9].notes[3].fingering = '2'
    bm[9].notes[4].fingering = '1'
    # measure 11 fingerings
    bm[10].notes[0].fingering = '3'
    bm[10].notes[1].fingering = '2'
    bm[10].notes[2].fingering = '3'
    bm[10].notes[3].fingering = '2'
    # measure 12 fingerings
    bm[11].notes[0].fingering = '1'
    return bm

def drill9_5():
    '''
    >>> from music21.braille import translate
    >>> print translate.partToBraille(drill9_5())
    ⠀⠀⠀⠀⠀⠠⠇⠊⠛⠓⠞⠇⠽⠂⠀⠁⠇⠍⠕⠎⠞⠀⠊⠝⠀⠕⠝⠑⠲⠀⠣⠼⠉⠲⠀⠀⠀⠀⠀⠀
    ⠼⠁⠀⠐⠛⠅⠸⠊⠁⠩⠓⠃⠊⠁⠙⠊⠀⠐⠓⠸⠚⠃⠊⠁⠚⠃⠑⠇⠚⠃⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
    ⠀⠀⠐⠓⠙⠡⠚⠙⠐⠊⠐⠙⠁⠀⠣⠐⠚⠐⠙⠁⠡⠚⠃⠙⠇⠣⠚⠃⠙⠇⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
    ⠀⠀⠸⠊⠁⠙⠃⠐⠊⠅⠐⠙⠁⠡⠚⠃⠑⠇⠀⠙⠁⠐⠊⠂⠩⠓⠇⠊⠂⠙⠊⠀⠀⠀⠀⠀⠀⠀⠀⠀
    ⠀⠀⠐⠙⠐⠚⠂⠊⠇⠚⠙⠚⠀⠊⠨⠑⠅⠙⠂⠊⠇⠓⠃⠙⠁⠀⠟⠄⠃⠣⠅
    '''
    bm = tinyNotation.TinyNotationStream("f8 A G# A c A g B- A B- d B- g c Bn c a c b- c Bn c B- c\
    A c a c Bn d c a g# a c' a c b- a b- c' b- a d' c' a g c f2.", "3/4")
    bm.insert(0, key.KeySignature(-1))
    bm.insert(0, tempo.TempoText("Lightly, almost in one"))
    bm.makeNotation(inPlace=True, cautionaryNotImmediateRepeat=False)
    bm[1].notes[0].accidental.displayStatus = False
    # measure 1 fingerings
    bm[0].notes[0].fingering = '5'
    bm[0].notes[1].fingering = '1'
    bm[0].notes[2].fingering = '2'
    bm[0].notes[3].fingering = '1'
    # measure 2 fingerings
    bm[1].notes[1].fingering = '2'
    bm[1].notes[2].fingering = '1'
    bm[1].notes[3].fingering = '2'
    bm[1].notes[4].fingering = '3'
    bm[1].notes[5].fingering = '2'
    # measure 3 fingerings
    bm[2].notes[5].fingering = '1'
    # measure 4 fingerings    
    bm[3].notes[1].fingering = '1'
    bm[3].notes[2].fingering = '2'
    bm[3].notes[3].fingering = '3'
    bm[3].notes[4].fingering = '2'
    bm[3].notes[5].fingering = '3'
    # measure 5 fingerings
    bm[4].notes[0].fingering = '1'
    bm[4].notes[1].fingering = '2'
    bm[4].notes[2].fingering = '5'
    bm[4].notes[3].fingering = '1'
    bm[4].notes[4].fingering = '2'
    bm[4].notes[5].fingering = '3'
    # measure 6 fingerings
    bm[5].notes[0].fingering = '1'
    bm[5].notes[1].fingering = '4'
    bm[5].notes[2].fingering = '3'
    bm[5].notes[3].fingering = '4'
    # measure 7 fingerings
    bm[6].notes[1].fingering = '4'
    bm[6].notes[2].fingering = '3'
    # measure 8 fingerings
    bm[7].notes[1].fingering = '5'
    bm[7].notes[2].fingering = '4'
    bm[7].notes[3].fingering = '3'
    bm[7].notes[4].fingering = '2'
    bm[7].notes[5].fingering = '1'
    # measure 12 fingerings
    bm[8].notes[0].fingering = '2'
    return bm

#-------------------------------------------------------------------------------
# Chapter 10: Changes of Signature; the Braille Music Hyphen, Asterisk, and 
# Parenthesis; Clef Signs

def example10_1():
    '''
    >>> from music21.braille import translate
    >>> print translate.partToBraille(example10_1())
    ⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠼⠙⠣⠼⠋⠦⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
    ⠼⠁⠀⠐⠻⠨⠙⠑⠙⠚⠀⠼⠃⠲⠀⠐⠪⠳⠣⠅⠄⠀⠡⠣⠣⠣⠼⠋⠦⠀⠐⠋⠨⠋⠑⠫⠐⠓⠀⠀
    ⠀⠀⠼⠉⠲⠀⠐⠪⠳⠻⠣⠅⠄⠀⠡⠡⠡⠀⠐⠓⠛⠋⠑⠙⠚⠀⠝⠄⠣⠅
    '''
    bm = stream.Part()
    
    m1 = stream.Measure(number=1)
    m1.append(clef.TrebleClef())
    m1.append(key.KeySignature(-4))
    m1.append(meter.TimeSignature('6/8'))
    m1.append(note.Note('F4'))
    m1.append(note.Note('C5', quarterLength=0.5))
    m1.append(note.Note('D-5', quarterLength=0.5))
    m1.append(note.Note('C5', quarterLength=0.5))
    m1.append(note.Note('B-4', quarterLength=0.5))
    bm.append(m1)
    
    m2 = stream.Measure(number=2)
    m2.append(meter.TimeSignature('2/4'))
    m2.append(note.Note('A-4'))
    m2.append(note.Note('G4'))
    m2.rightBarline = bar.Barline('double')
    bm.append(m2)
    
    m3 = stream.Measure(number=3)
    m3.append(key.KeySignature(-3))
    m3.append(meter.TimeSignature('6/8'))
    m3.append(note.Note('E-4', quarterLength=0.5))
    m3.append(note.Note('E-5', quarterLength=0.5))
    m3.append(note.Note('D5', quarterLength=0.5))
    m3.append(note.Note('E-5'))
    m3.append(note.Note('G4', quarterLength=0.5))
    bm.append(m3)
    
    m4 = stream.Measure(number=4)
    m4.append(meter.TimeSignature('3/4'))
    m4.append(note.Note('A-4'))
    m4.append(note.Note('G4'))
    m4.append(note.Note('F4'))
    m4.rightBarline = bar.Barline('double')
    bm.append(m4)
    
    m5 = stream.Measure(number=5)
    m5.append(key.KeySignature(0))
    m5.append(note.Note('G4', quarterLength=0.5))
    m5.append(note.Note('F4', quarterLength=0.5))
    m5.append(note.Note('E4', quarterLength=0.5))
    m5.append(note.Note('D4', quarterLength=0.5))
    m5.append(note.Note('C4', quarterLength=0.5))
    m5.append(note.Note('B3', quarterLength=0.5))
    bm.append(m5)
    
    m6 = stream.Measure(number=6)
    m6.append(note.Note('C4', quarterLength=3.0))
    m6.rightBarline = bar.Barline('final')
    bm.append(m6)

    bm.makeNotation(inPlace=True, cautionaryNotImmediateRepeat=False)    
    return bm

def example10_5():
    '''
    >>> from music21.braille import translate
    >>> print translate.partToBraille(example10_5())
    ⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠣⠣⠣⠼⠉⠲⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
    ⠼⠁⠀⠐⠳⠄⠛⠫⠀⠸⠺⠐⠺⠳⠀⠟⠣⠅⠄⠐⠀⠐⠳⠀⠨⠫⠄⠑⠹⠀⠱⠐⠳⠡⠺⠀⠀⠀⠀⠀
    ⠀⠀⠨⠱⠹⠣⠅⠄⠐⠀⠼⠙⠣⠀⠨⠹⠀⠪⠄⠓⠻⠀⠹⠨⠹⠡⠐⠫⠀⠟⠄⠣⠅
    '''
    bm = tinyNotation.TinyNotationStream("g4. f8 e-4 B-4 b-4 g4 f2 g4 e'-4. d'8 c'4 d'4 g4 bn4\
    d'4 c'4 c'4 a-4. g8 f4 c4 c'4 en4 f2.", "3/4")
    bm.insert(0, key.KeySignature(-3))
    bm.makeNotation(inPlace=True, cautionaryNotImmediateRepeat=False)
    bm[2].insert(1, bar.Barline('double'))
    bm[5].insert(2, key.KeySignature(-4))
    bm[5].insert(2, bar.Barline('double'))
    return bm

def example10_6():
    '''
    >>> from music21.braille import translate
    >>> print translate.partToBraille(example10_6())
    ⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠩⠩⠩⠼⠙⠲⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
    ⠼⠁⠀⠐⠪⠨⠪⠈⠉⠊⠓⠛⠋⠀⠻⠫⠈⠉⠋⠑⠙⠚⠀⠱⠹⠈⠉⠙⠚⠊⠚⠀⠝⠣⠅⠄⠀⠀⠀⠀
    ⠀⠀⠭⠨⠊⠓⠛⠀⠋⠑⠙⠚⠊⠚⠙⠚⠀⠎⠄⠧⠣⠅
    '''
    bm = tinyNotation.TinyNotationStream("a4 a'~ a'8 g'# f'# e' f'#4 e'~ e'8 d' c'# b d'4 c'#~ c'#8 b a b\
    c'#2 r8 a'8 g'# f'# e' d' c'# b a b c'# b a2. r4", "4/4")
    bm.insert(0, key.KeySignature(3))
    bm.makeNotation(inPlace=True, cautionaryNotImmediateRepeat=False)
    bm[3].insert(2.0, bar.Barline('double'))
    return bm

def example10_9():
    '''
    >>> from music21.braille import translate
    >>> print translate.partToBraille(example10_9(), recenterHeading = True, showClefSigns = False)
    ⠀⠀⠀⠀⠀⠀⠀⠣⠣⠼⠙⠲⠀⠀⠀⠀⠀⠀⠀
    ⠼⠁⠀⠘⠺⠸⠻⠺⠐⠻⠀⠺⠱⠹⠪⠀⠾⠣⠅
    >>> print translate.partToBraille(example10_9(), recenterHeading = True, showClefSigns = True)
    ⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠣⠣⠼⠙⠲⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
    ⠼⠁⠀⠜⠼⠇⠘⠺⠸⠻⠺⠜⠌⠇⠐⠻⠀⠺⠱⠹⠪⠀⠾⠣⠅
    '''
    bm = tinyNotation.TinyNotationStream("BB-4 F B- f b- d' c' a b-1", "4/4")
    bm.insert(0, key.KeySignature(-2))
    bm.insert(0, clef.BassClef())
    bm.makeNotation(inPlace=True, cautionaryNotImmediateRepeat=False)
    bm[0].insert(3.0, clef.TrebleClef())
    return bm

def example10_10():
    '''
    >>> from music21.braille import translate
    >>> print translate.partToBraille(example10_10(), recenterHeading = True, showClefSigns = False)
    ⠀⠀⠀⠀⠀⠀⠩⠩⠩⠼⠋⠦⠀⠀⠀⠀⠀⠀
    ⠼⠁⠀⠐⠊⠋⠊⠚⠙⠑⠀⠋⠛⠓⠪⠄⠣⠅
    >>> print translate.partToBraille(example10_10(), recenterHeading = True, showClefSigns = True)
    ⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠩⠩⠩⠼⠋⠦⠀⠀⠀⠀⠀⠀⠀⠀⠀
    ⠼⠁⠀⠜⠬⠇⠐⠊⠋⠊⠚⠙⠑⠀⠜⠌⠇⠨⠋⠛⠓⠪⠄⠣⠅
    '''
    bm = tinyNotation.TinyNotationStream("a8 e a b c'# d' e' f'# g'# a'4.", "6/8")
    bm.insert(0, key.KeySignature(3))
    bm.insert(0, clef.AltoClef())
    bm.makeNotation(inPlace=True, cautionaryNotImmediateRepeat=False)
    bm[1].insert(0.0, clef.TrebleClef())
    return bm

#-------------------------------------------------------------------------------
# Chapter 11: Segments for Single-Line Instrumental Music, Format for the 
# Beginning of a Composition or Movement

def example11_1():
    '''
    >>> from music21.braille import translate
    >>> print translate.partToBraille(example11_1(), segmentStartMeasureNumbers = [9])
    ⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠩⠩⠼⠉⠲⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
    ⠼⠁⠀⠸⠱⠋⠛⠓⠊⠀⠺⠪⠓⠛⠀⠋⠑⠙⠑⠋⠛⠀⠳⠪⠧⠀⠺⠙⠑⠋⠛⠀⠫⠱⠙⠚⠀⠀⠀⠀
    ⠀⠀⠐⠙⠋⠑⠙⠚⠩⠊⠀⠞⠧
    ⠼⠊⠀⠐⠻⠑⠙⠺⠀⠐⠫⠙⠚⠩⠪⠀⠐⠱⠚⠡⠊⠩⠳⠀⠎⠧⠀⠪⠓⠛⠋⠑⠀⠹⠱⠋⠛⠀⠀⠀
    ⠀⠀⠸⠓⠊⠚⠊⠓⠛⠀⠫⠱⠧⠣⠅
    '''
    bm = tinyNotation.TinyNotationStream("D4 E8 F#8 G8 A8 B4 A4 G8 F#8 E8 D8 C#8 D8 E8 F#8 G4 A4 r4 B4 c#8 d8 e8 f#8 e4 d4 c#8 B8\
    c#8 e8 d8 c#8 B8 A#8 B2 r4 f#4 d8 c#8 B4 e4 c#8 B8 A#4 d4 B8 An8 G#4 A2 r4\
    A4 G8 F#8 E8 D8 C#4 D4 E8 F#8 G8 A8 B8 A8 G8 F#8 E4 D4 r4", "3/4")
    bm.insert(0, key.KeySignature(2))
    bm.makeNotation(inPlace=True, cautionaryNotImmediateRepeat=False)
    return bm

#-------------------------------------------------------------------------------
# Chapter 12: Slurs (Phrasing)

def example12_1():
    bm = tinyNotation.TinyNotationStream("g4. f8=s e4 d4 g4 f4 e4 r4 f4 g4 a4 b4 c'4 d'4 c'4 r4", "4/4")
    bm.makeNotation(inPlace=True, cautionaryNotImmediateRepeat=False)
    return bm

#-------------------------------------------------------------------------------
# Chapter 13: Words, Abbreviations, Letters, and Phrases of Expression

def example13_1():
    bm = tinyNotation.TinyNotationStream("f2 e4 e4 d4 c4 a4. b-8 a4 g4 c8 d8 e8 f8 g4 f4 e4 f2.", "3/4")
    bm.insert(0, key.KeySignature(-1))
    bm.makeNotation(inPlace=True, cautionaryNotImmediateRepeat=False)
    bm[1].insert(2.0, dynamics.Dynamic('p'))
    bm[3].insert(1.0, dynamics.Dynamic('mf'))
    return bm

def example13_2():
    bm = tinyNotation.TinyNotationStream("", "4/4")
    bm.insert(0, key.KeySignature(1))
    
def example13_3():
    bm = tinyNotation.TinyNotationStream("a1 a1 a1 a1", "c")
    bm.makeNotation(inPlace=True, cautionaryNotImmediateRepeat=False)
    bm[-1].rightBarline = None
    return bm

#-------------------------------------------------------------------------------
# Chapter 14: Smaller Values and Regular Note-Grouping, the Music Comma

def example14_1():
    '''
    >>> from music21.braille import translate
    >>> print translate.partToBraille(example14_1(), measureNumberWithHeading = False, recenterHeading = True)
    ⠀⠀⠀⠀⠀⠀⠀⠀⠣⠼⠙⠲⠀⠀⠀⠀⠀⠀⠀
    ⠨⠦⠐⠛⠊⠨⠦⠙⠊⠨⠦⠓⠨⠙⠨⠦⠐⠋⠓
    '''
    bm = tinyNotation.TinyNotationStream("f8 a c' a g c' e g", "4/4")
    bm.notes[0].articulations.append(articulations.Accent())
    bm.notes[2].articulations.append(articulations.Accent())
    bm.notes[4].articulations.append(articulations.Accent())
    bm.notes[6].articulations.append(articulations.Accent())
    bm.insert(0, key.KeySignature(-1))
    bm.makeNotation(inPlace=True, cautionaryNotImmediateRepeat=False)
    bm[-1].rightBarline = None
    return bm

#-------------------------------------------------------------------------------
# Chapter 15: Smaller Values and Regular Note-Grouping, the Music Comma

def example15_1():
    '''
    >>> from music21.braille import translate
    >>> print translate.partToBraille(example15_1())
    ⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠩⠼⠃⠲⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
    ⠼⠚⠀⠐⠑⠀⠓⠄⠿⠓⠚⠀⠊⠄⠷⠊⠚⠀⠓⠄⠷⠚⠑⠀⠫⠄⠋⠀⠑⠄⠾⠚⠓⠀⠊⠄⠷⠊⠚⠀
    ⠀⠀⠐⠓⠄⠯⠋⠑⠀⠳⠄
    '''
    bm = tinyNotation.TinyNotationStream("r4. d8 g8. f#16 g8 b8 a8. g16 a8 b8 g8. g16 b8 d'8 e'4. e'8\
    d'8. b16 b8 g8 a8. g16 a8 b8 g8. e16 e8 d8 g4.", "2/4")
    bm.insert(0, key.KeySignature(1))
    bm.makeNotation(inPlace=True, cautionaryNotImmediateRepeat=False)
    bm[0].pop(3)
    bm[0].padAsAnacrusis()
    for m in bm:
        m.number -= 1
    bm[-1].rightBarline = None
    return bm
 
def example15_2():
    '''
    >>> from music21.braille import translate
    >>> print translate.partToBraille(example15_2(), measureNumberWithHeading = False, recenterHeading = True)
    ⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠩⠼⠃⠲⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
    ⠨⠑⠍⠯⠑⠍⠩⠽⠀⠱⠚⠭⠀⠚⠍⠽⠚⠍⠩⠮⠀⠺⠓⠭
    '''
    bm = tinyNotation.TinyNotationStream("d'8 r16 e'16 d'8 r16 c'#16 d'4 b8 r8 b8 r16 c'16 b8 r16 a#16 b4 g8 r8", "2/4")
    bm.insert(0, key.KeySignature(1))
    bm.makeNotation(inPlace=True, cautionaryNotImmediateRepeat=False)
    bm[-1].rightBarline = None
    return bm

def example15_3():
    '''
    >>> from music21.braille import translate
    >>> print translate.partToBraille(example15_3())
    ⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠼⠋⠦⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
    ⠼⠁⠀⠐⠋⠄⠿⠋⠳⠓⠀⠑⠄⠯⠑⠻⠛⠀⠹⠑⠫⠛⠀⠫⠑⠱⠋⠀⠫⠛⠳⠮⠞⠝⠀⠀⠀⠀⠀⠀
    ⠀⠀⠐⠹⠯⠵⠹⠍
    '''
    bm = tinyNotation.TinyNotationStream("e8. f16 e8 g4 g8 d8. e16 d8 f4 f8 c4 d8 e4 f8\
    e4 d8 d4 e8 e4 f8 g4 a16 b32 c'32 c4 e16 d16 c4 r16", "6/8")
    bm.makeNotation(inPlace=True, cautionaryNotImmediateRepeat=False)
    bm[-1].rightBarline = None
    return bm

def example15_4():
    '''
    >>> from music21.braille import translate
    >>> print translate.partToBraille(example15_4(), measureNumberWithHeading = False, recenterHeading = True)
    ⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠼⠉⠲⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
    ⠨⠫⠈⠉⠋⠄⠿⠑⠄⠯⠀⠹⠰⠹⠹⠀⠩⠨⠷⠮⠭⠯⠿⠭⠵⠾⠭⠀⠹⠧⠧
    '''
    bm = tinyNotation.TinyNotationStream("e'4~ e'8. f'16 d'8. e'16 c'4 c''4 c''4 g'#16 a'16 r8 e'16 f'16 r8 d'16 b16 r8 c'4 r4 r4", "3/4")
    bm.makeNotation(inPlace=True, cautionaryNotImmediateRepeat=False)
    bm[-1].rightBarline = None
    return bm

def example15_5():
    '''
    >>> from music21.braille import translate
    >>> print translate.partToBraille(example15_5())
    ⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠩⠩⠩⠼⠉⠦⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
    ⠼⠚⠀⠐⠯⠄⠞⠀⠚⠊⠚⠀⠩⠚⠽⠍⠐⠯⠄⠨⠝⠀⠙⠚⠙⠀⠙⠵⠍⠑⠀⠱⠯⠿⠀⠿⠐⠚⠄⠙
    ⠀⠀⠨⠋⠄⠵⠽⠾⠀⠪⠣⠅⠄
    '''
    bm = tinyNotation.TinyNotationStream("r4 e16. b32 b8 a8 b8 b#8 c'#16 r16 e16. c'#32 c'#8 b8 c'#8 c'#8 d'16 r16 d'8\
    d'4 e'16 f'#16 f'#16 b8. c'#8 e'8. d'16 c'#16 b16 a4", "3/8")
    bm.insert(0, key.KeySignature(3))
    bm.makeNotation(inPlace=True, cautionaryNotImmediateRepeat=False)
    bm[0].pop(3)
    bm[0].padAsAnacrusis()
    bm[3][1].accidental.displayStatus = False # remove cautionary accidental display
    for m in bm:
        m.number -= 1
    bm[-1].rightBarline = bar.Barline('double')
    return bm

def example15_6a(): # beamed 16th notes
    '''
    >>> from music21.braille import translate
    >>> print translate.partToBraille(example15_6a(), measureNumberWithHeading = False, recenterHeading = True)
    ⠀⠀⠀⠀⠀⠀⠀⠼⠙⠲⠀⠀⠀⠀⠀⠀⠀
    ⠐⠽⠚⠙⠑⠯⠑⠋⠛⠷⠓⠊⠚⠽⠑⠋⠋
    '''
    bm = tinyNotation.TinyNotationStream("c16 B c d e d e f g g a b c' d' e' e'", "4/4")
    bm.makeNotation(inPlace=True, cautionaryNotImmediateRepeat=False)
    bm[-1].rightBarline = None
    return bm

def example15_6b(): # unbeamed 16th notes
    '''
    >>> from music21.braille import translate
    >>> print translate.partToBraille(example15_6b(), measureNumberWithHeading = False, recenterHeading = True)
    ⠀⠀⠀⠀⠀⠀⠀⠼⠙⠲⠀⠀⠀⠀⠀⠀⠀
    ⠐⠽⠾⠽⠵⠯⠵⠯⠿⠷⠷⠮⠾⠽⠵⠯⠯
    '''
    bm = tinyNotation.TinyNotationStream("c16 B c d e d e f g g a b c' d' e' e'", "4/4")
    # not calling makeNotation because it calls makeBeams
    bm.makeMeasures(inPlace=True)
    bm.makeAccidentals(cautionaryNotImmediateRepeat=False)
    bm[-1].rightBarline = None
    return bm

def example15_7():
    '''
    >>> from music21.braille import translate
    >>> print translate.partToBraille(example15_7(), measureNumberWithHeading = False, recenterHeading = True) 
    ⠀⠀⠀⠀⠀⠀⠼⠃⠲⠀⠀⠀⠀⠀⠀
    ⠐⠷⠨⠑⠙⠚⠹⠀⠐⠷⠄⠟⠯⠵⠫
    '''
    bm = tinyNotation.TinyNotationStream("g16 d' c' b c'4 g16. f32 e16 d e4", "2/4")
    bm.makeNotation(inPlace=True, cautionaryNotImmediateRepeat=False)
    bm[-1].rightBarline = None
    return bm

def example15_8():
    '''
    >>> from music21.braille import translate
    >>> print translate.partToBraille(example15_8(), measureNumberWithHeading = False, recenterHeading = True) 
    ⠀⠀⠀⠀⠀⠀⠼⠃⠲⠀⠀⠀⠀⠀⠀⠀
    ⠸⠷⠋⠛⠋⠷⠿⠭⠀⠿⠑⠋⠑⠿⠯⠍
    '''
    bm = tinyNotation.TinyNotationStream("G16 E F E G F r8 F16 D E D F E r", "2/4")
    bm.makeNotation(inPlace=True, cautionaryNotImmediateRepeat=False)
    bm[-1].rightBarline = None
    return bm

def example15_9():
    bm = tinyNotation.TinyNotationStream("r16 d' c' b c' d' e' c' b c' b a g f# g r g' f'# e' d' c' r b a g2", "2/4")
    bm.insert(0, key.KeySignature(1))
    bm.makeNotation(inPlace=True, cautionaryNotImmediateRepeat=False)
    bm[-1].rightBarline = None
    return bm



#-------------------------------------------------------------------------------
# Chapter 16: Irregular Note-Grouping

# Triplets
# --------
def example16_1():
    '''
    >>> from music21.braille import translate
    >>> print translate.partToBraille(example16_1(), measureNumberWithHeading = False, recenterHeading = True) 
    ⠀⠀⠀⠀⠀⠀⠀⠼⠃⠲⠀⠀⠀⠀⠀⠀⠀
    ⠆⠨⠦⠐⠙⠋⠊⠳⠀⠆⠨⠦⠸⠚⠑⠊⠳
    '''
    bm = tinyNotation.TinyNotationStream("trip{c8 e a} g4 trip{B8 d a} g4", "2/4")
    bm.makeNotation(inPlace=True, cautionaryNotImmediateRepeat=False)
    bm[-1].rightBarline = None
    bm[0].notes[0].articulations.append(articulations.Accent())
    bm[1].notes[0].articulations.append(articulations.Accent())
    return bm

def example16_2():
    '''
    >>> from music21.braille import translate
    >>> print translate.partToBraille(example16_2(), measureNumberWithHeading = False, recenterHeading = True) 
    ⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠣⠣⠼⠉⠲⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
    ⠐⠺⠈⠉⠆⠚⠙⠐⠛⠆⠚⠑⠐⠛⠀⠺⠈⠉⠆⠚⠙⠑⠆⠑⠙⠚
    '''
    bm = tinyNotation.TinyNotationStream("b-4~ trip{b-8 c' f} trip{b- d' f} b-4~ trip{b-8 c' d'} trip{d' c' b-}", "3/4")
    bm.insert(0, key.KeySignature(-2))
    bm.makeNotation(inPlace=True, cautionaryNotImmediateRepeat=False)
    bm[-1].rightBarline = None
    return bm

def example16_6():
    bm = tinyNotation.TinyNotationStream("trip{b'-8 f' d'} trip{b- d' e'-} trip{f' d' b-} trip{f b- d'}", "2/4")
    bm.insert(0, key.KeySignature(-2))
    bm.makeNotation(inPlace=True, cautionaryNotImmediateRepeat=False)
    bm[-1].rightBarline = None
    return bm

#-------------------------------------------------------------------------------
#-------------------------------------------------------------------------------
# PART TWO
# Transcribing Two- and Three-Staff Music
#
#-------------------------------------------------------------------------------
# Chapter 24: Bar-over-Bar Format

def example24_1a():
    '''
    >>> from music21.braille import translate
    >>> #print translate.keyboardPartsToBraille(example24_1a()).splitlines()[1]
    '''
    rightHand = tinyNotation.TinyNotationStream("c2 e2", "4/4")
    leftHand = tinyNotation.TinyNotationStream("r1", "4/4")
    rightHand.makeNotation(inPlace=True, cautionaryNotImmediateRepeat=False)
    leftHand.makeNotation(inPlace=True, cautionaryNotImmediateRepeat=False)
    rightHand[-1].rightBarline = None
    leftHand[-1].rightBarline = None
    rightHand[-1].insert(0.0, dynamics.Dynamic('f'))
    keyboardPart = stream.Part()
    keyboardPart.append(rightHand)
    keyboardPart.append(leftHand)
    return keyboardPart

def example24_1b():
    '''
    >>> from music21.braille import translate
    >>> #print translate.keyboardPartsToBraille(example24_1b())
    '''
    rightHand = tinyNotation.TinyNotationStream("r2", "2/4")
    leftHand = tinyNotation.TinyNotationStream("C8 r8 E8 r8", "2/4")
    rightHand.makeNotation(inPlace=True, cautionaryNotImmediateRepeat=False)
    leftHand.makeNotation(inPlace=True, cautionaryNotImmediateRepeat=False)
    rightHand[-1].rightBarline = None
    leftHand[-1].rightBarline = None
    rightHand[-1].insert(0.0, dynamics.Dynamic('f'))
    keyboardPart = stream.Part()
    keyboardPart.append(rightHand)
    keyboardPart.append(leftHand)
    return keyboardPart

def example24_2():
    '''
    >>> from music21.braille import translate
    >>> print translate.keyboardPartsToBraille(example24_2())
    ⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠼⠃⠲⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
    ⠁⠀⠅⠜⠨⠙⠐⠓⠋⠓⠀⠐⠛⠓⠋⠊⠀⠐⠓⠛⠋⠑⠀⠐⠋⠋⠑⠭⠀⠐⠋⠑⠋⠓⠀⠐⠛⠓⠊⠛
    ⠀⠀⠇⠜⠸⠙⠓⠐⠙⠚⠀⠸⠊⠚⠙⠙⠀⠸⠚⠊⠓⠚⠀⠐⠙⠙⠚⠓⠀⠐⠙⠭⠣⠺⠀⠸⠊⠭⠙⠭
    ⠛⠀⠅⠜⠐⠋⠓⠓⠛⠀⠐⠏⠣⠅
    ⠀⠀⠇⠜⠐⠙⠭⠚⠓⠀⠐⠝⠣⠅
    '''
    rightHand = tinyNotation.TinyNotationStream("c'8 g8 e8 g8 f8 g8 e8 a8 g8 f8 e8 d8 e8 e8 d8 r8 e8 d8 e8 g8 f8 g8 a8 f8 e8 g8 g8 f8 e2", "2/4")
    leftHand = tinyNotation.TinyNotationStream("C8 G8 c8 B8 A8 B8 c8 c8 B8 A8 G8 B8 c8 c8 B8 G8 c8 r8 B-4 A8 r8 c8 r8 c8 r8 B8 G8 c2", "2/4")
    rightHand.makeNotation(inPlace=True, cautionaryNotImmediateRepeat=False)
    leftHand.makeNotation(inPlace=True, cautionaryNotImmediateRepeat=False)
    keyboardPart = stream.Part()
    keyboardPart.append(rightHand)
    keyboardPart.append(leftHand)
    return keyboardPart

def example24_3():
    rightHand = tinyNotation.TinyNotationStream("r2 d'4 d'8 e'-8 d'8 c'8 b-8 a8 g2~ b-4", "3/4")
    leftHand = tinyNotation.TinyNotationStream("r2 B-8 A8 G8 r8 B-8 r8 d8 r8 G8 A8 B-8 c8 d4", "3/4")
    rightHand.insert(0, key.KeySignature(-2))
    leftHand.insert(0, key.KeySignature(-2))
    rightHand.makeNotation(inPlace=True, cautionaryNotImmediateRepeat=False)
    leftHand.makeNotation(inPlace=True, cautionaryNotImmediateRepeat=False)
    rightHand[0].pop(3)
    rightHand[0].padAsAnacrusis()
    leftHand[0].pop(3)
    leftHand[0].padAsAnacrusis()
    for m in rightHand:
        m.number -= 1
    for m in leftHand:
        m.number -= 1
    rightHand[-1].rightBarline = None
    leftHand[-1].rightBarline = None
    keyboardPart = stream.Part()
    keyboardPart.append(rightHand)
    keyboardPart.append(leftHand)
    return keyboardPart

def example24_4():
    '''
    >>> from music21.braille import translate
    >>> print translate.keyboardPartsToBraille(example24_4())
    ⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠩⠩⠼⠙⠲⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
    ⠀⠊⠀⠅⠜⠰⠵⠚⠊⠛⠫⠈⠉⠯⠑⠐⠊⠨⠑⠫⠀⠨⠽⠚⠙⠑⠯⠓⠛⠋⠿⠋⠛⠓⠮⠚⠙⠑⠀⠀
    ⠀⠀⠀⠇⠜⠨⠱⠈⠉⠵⠙⠚⠓⠻⠈⠉⠿⠓⠚⠓⠀⠐⠪⠹⠑⠵⠯⠿⠓⠋⠛⠀⠀⠀⠀⠀⠀⠀⠀⠀
    ⠁⠁⠀⠅⠜⠰⠯⠑⠙⠚⠮⠓⠛⠋⠕⠣⠅
    ⠀⠀⠀⠇⠜⠨⠳⠹⠍⠊⠛⠋⠱⠣⠅⠀⠀
    '''
    rightHand = tinyNotation.TinyNotationStream("d'16 b16 a16 f#16 e4~ e16 d16 A16 d16 e4 c#16 B16 c#16 d16 e16 g16 f#16 e16 f#16 e16 f#16 g16 a16 b16 c'#16 d'16\
    e'16 d'16 c'#16 b16 a16 g16 f#16 e16 d2", "4/4")
    leftHand = tinyNotation.TinyNotationStream("d'4~ d'16 c'#16 b16 g16 f#4~ f#16 g16 b16 g16 a4 c'#4 d'8 d'16 e'16 f'#16 g'16 e'16 f'#16\
    g'4 c'#4 r16 a16 f#16 e16 d4", "4/4")
    rightHand.transpose('P8', inPlace=True)
    rightHand.insert(0, key.KeySignature(2))
    leftHand.insert(0, key.KeySignature(2))
    rightHand.makeNotation(inPlace=True, cautionaryNotImmediateRepeat=False)
    leftHand.makeNotation(inPlace=True, cautionaryNotImmediateRepeat=False)
    for m in rightHand:
        m.number += 8
    for m in leftHand:
        m.number += 8
    keyboardPart = stream.Part()
    keyboardPart.append(rightHand)
    keyboardPart.append(leftHand)
    return keyboardPart
 

#-------------------------------------------------------------------------------
class Test(unittest.TestCase):

    def runTest(self):
        pass

if __name__ == "__main__":
    #ex = example10_10()
    #ex.show()
    #print translate.partToBraille(ex, recenterHeading = True, showClefSigns = True)
    music21.mainTest(Test)

#------------------------------------------------------------------------------
# eof
