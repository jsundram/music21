#-------------------------------------------------------------------------------
# Name:         stream.py
# Purpose:      base classes for dealing with groups of positioned objects
#
# Authors:      Michael Scott Cuthbert
#               Christopher Ariza
#
# Copyright:    (c) 2009 The music21 Project
# License:      LGPL
#-------------------------------------------------------------------------------

import copy, types, random
import doctest, unittest
import sys

from copy import deepcopy
# try:
#     import cPickle as pickleMod
# except ImportError:
#     import pickle as pickleMod


import music21 ## needed to properly do isinstance checking
#from music21 import ElementWrapper
from music21 import common
from music21 import clef
from music21 import chord
from music21 import defaults
from music21 import duration
from music21 import dynamics
from music21 import instrument
from music21 import lily as lilyModule
from music21 import measure
from music21 import meter
from music21 import musicxml as musicxmlMod
from music21 import note

from music21 import environment
_MOD = "stream.py"
environLocal = environment.Environment(_MOD)

CLASS_SORT_ORDER = ["Clef", "TempoMark", "KeySignature", "TimeSignature", "Dynamic", "GeneralNote"]


#-------------------------------------------------------------------------------

class StreamException(Exception):
    pass

#-------------------------------------------------------------------------------



#-------------------------------------------------------------------------------
class StreamIterator():
    '''A simple Iterator object used to handle iteration of Streams and other 
    list-like objects. 
    '''
    def __init__(self, srcStream):
        self.srcStream = srcStream
        self.index = 0

    def __iter__(self):
        return self

    def next(self):
        if self.index >= len(self.srcStream.elements):
            del self.srcStream
            raise StopIteration
        post = self.srcStream.elements[self.index]
        # here, the parent of extracted element is being set to Stream
        # that is the source of the iteration
        post.parent = self.srcStream
        self.index += 1
        return post


#-------------------------------------------------------------------------------
class Stream(music21.Music21Object):
    '''
    This is basic container for Music21Objects that occur at certain times. 
    
    Like the base class, Music21Object, Streams have offsets, priority, id, and groups
    they also have an elements attribute which returns a list of elements; 
    
    The Stream has a duration that is usually the 
    release time of the chronologically last element in the Stream (that is,
    the highest onset plus duration of any element in the Stream).
    However, it can either explicitly set in which case we say that the
    duration is unlinked

    Streams may be embedded within other Streams.
    
    TODO: Get Stream Duration working -- should be the total length of the 
    Stream. -- see the ._getDuration() and ._setDuration() methods
    '''

    def __init__(self):
        '''
        
        '''
        music21.Music21Object.__init__(self)

        # self._elements stores ElementWrapper objects. These are not ordered.
        # this should have a public attribute/property self.elements
        self._elements = []
        self._unlinkedDuration = None

        # the .obj attributes was held over from old ElementWrapper model
        # no longer needed
        #self.obj = None

        self.isSorted = True
        self.isFlat = True  ## does it have no embedded elements

        # seems that this hsould be named with a leading lower case?
        self.flattenedRepresentationOf = None ## is this a stream returned by Stream().flat ?
        
        self._cache = common.defHash()


    #---------------------------------------------------------------------------
    # sequence like operations

    # if we want to have all the features of a mutable sequence, 
    # we should implement
    # append(), count(), index(), extend(), insert(), 
    # pop(), remove(), reverse() and sort(), like Python standard list objects.
    # But we're not there yet.


    def __len__(self):
        '''Get the total number of elements
        Does not recurse into objects

        >>> a = Stream()
        >>> for x in range(4):
        ...     n = note.Note('G#')
        ...     n.offset = x * 3
        ...     a.insert(n)
        >>> len(a)
        4

        >>> b = Stream()
        >>> for x in range(4):
        ...     b.insert(deepcopy(a) ) # append streams
        >>> len(b)
        4
        >>> len(b.flat)
        16
        '''
        return len(self._elements)

    def __iter__(self):
        '''
        A Stream can return an iterator.  Same as running x in a.elements
        '''
        return StreamIterator(self)


    def __getitem__(self, key):
        '''Get an ElementWrapper from the stream in current order; sorted if isSorted is True,
        but not necessarily.
        
        if an int is given, returns that index
        if a class is given, it runs getElementsByClass and returns that list
        if a string is given it first runs getElementById on the stream then if that
             fails, getElementsByGroup on the stream returning that list.

        ## maybe it should, but does not yet:    if a float is given, returns the element at that offset

        >>> a = Stream()
        >>> a.repeatInsert(note.Rest(), range(6))
        >>> subslice = a[2:5]
        >>> len(subslice)
        3
        >>> a[1].offset
        1.0
        >>> b = note.Note()
        >>> b.id = 'green'
        >>> b.groups.append('violin')
        >>> a.insert(b)
        >>> a[note.Note][0] == b
        True
        >>> a['violin'][0] == b
        True
        >>> a['green'] == b
        True
        '''

        if common.isNum(key):
            returnEl = self.elements[key]
            returnEl.parent = self
            return returnEl
    
        elif isinstance(key, slice): # get a slice of index values
            found = copy.copy(self) # return a stream of elements
            found.elements = self.elements[key]
            for element in found:
                pass ## sufficient to set parent properly
            return found

        elif common.isStr(key):
            # first search id, then search groups
            idMatch = self.getElementById(key)
            if idMatch != None:
                return idMatch
            else: # search groups, return first element match
                groupStream = self.getElementsByGroup(key)
                if len(groupStream) > 0:
                    return groupStream
                else:
                    raise KeyError('provided key (%s) does not match any id or group' % key)
        elif isinstance(key, type(type)):
            # assume it is a class name
            classStream = self.getElementsByClass(key)
            if len(classStream) > 0:
                return classStream
            else:
                raise KeyError('provided class (%s) does not match any contained Objects' % key)


    #---------------------------------------------------------------------------
    # adding and editing Elements and Streams -- all need to call _elementsChanged
    # most will set isSorted to False

    def _elementsChanged(self):
        '''
        Call any time _elements is changed. Called by methods that add or change
        elements.

        >>> a = Stream()
        >>> a.isFlat
        True
        >>> a._elements.append(Stream())
        >>> a._elementsChanged()
        >>> a.isFlat
        False
        '''
        self.isSorted = False
        self.isFlat = True

        for thisElement in self._elements:
            if isinstance(thisElement, Stream): 
                self.isFlat = False
                break
        self._cache = common.defHash()

    def _getElements(self):
        return self._elements
   
    def _setElements(self, value):
        '''
        >>> a = Stream()
        >>> a.repeatInsert(note.Note("C"), range(10))
        >>> b = Stream()
        >>> b.repeatInsert(note.Note("C"), range(10))
        >>> b.offset = 6
        >>> c = Stream()
        >>> c.repeatInsert(note.Note("C"), range(10))
        >>> c.offset = 12
        >>> b.insert(c)
        >>> b.isFlat
        False
        >>> a.isFlat
        True
        >>> a.elements = b.elements
        >>> a.isFlat
        False
        '''
        self._elements = value
        self._elementsChanged()
        return value
        
    elements = property(_getElements, _setElements)

    def __setitem__(self, key, value):
        '''Insert items at index positions. Index positions are based
        on position in self.elements. 

        >>> a = Stream()
        >>> a.repeatInsert(note.Note("C"), range(10))
        >>> b = Stream()
        >>> b.repeatInsert(note.Note("C"), range(10))
        >>> b.offset = 6
        >>> c = Stream()
        >>> c.repeatInsert(note.Note("C"), range(10))
        >>> c.offset = 12
        >>> b.insert(c)
        >>> a.isFlat
        True
        >>> a[3] = b
        >>> a.isFlat
        False
        '''
        self._elements[key] = value
        storedIsFlat = self.isFlat
        self._elementsChanged()

        if isinstance(value, Stream): 
            self.isFlat = False
        else:
            self.isFlat = storedIsFlat


    def __delitem__(self, key):
        '''Delete items at index positions. Index positions are based
        on position in self.elements. 

        >>> a = Stream()
        >>> a.repeatInsert(note.Note("C"), range(10))
        >>> del a[0]
        >>> len(a)
        9
        '''
        del self._elements[key]
        self._elementsChanged()


    def pop(self, index):
        '''return the matched object from the list. 

        >>> a = Stream()
        >>> a.repeatInsert(note.Note("C"), range(10))
        >>> junk = a.pop(0)
        >>> len(a)
        9
        '''
        post = self._elements.pop(index)
        self._elementsChanged()
        return post


    def index(self, obj):
        '''return the index for the specified object 

        >>> a = Stream()
        >>> fSharp = note.Note("F#")
        >>> a.repeatInsert(note.Note("A#"), range(10))
        >>> a.append(fSharp)
        >>> a.index(fSharp)
        10
        '''
        try:
            match = self._elements.index(obj)
        except ValueError: # if not found
            # access object inside of element
            match = None
            for i in range(len(self._elements)):
                if obj == self._elements[i].obj:
                    match = i
                    break
        return match


    def __deepcopy__(self, memo=None):
        '''This produces a new, independent object.
        '''
        #environLocal.printDebug(['Stream calling __deepcopy__', self])

        new = self.__class__()
        old = self
        for name in self.__dict__.keys():

            if name.startswith('__'):
                continue
           
            part = getattr(self, name)
                    
            # all subclasses of Music21Object that define their own
            # __deepcopy__ methods must be sure to not try to copy parent
            if name == '_currentParent':
                newValue = self.parent # keep a reference, not a deepcopy
                setattr(new, name, newValue)
            # attributes that require special handling
            elif name == 'flattenedRepresentationOf':
                # keep a reference, not a deepcopy
                newValue = self.flattenedRepresentationOf
                setattr(new, name, newValue)
            elif name == '_cache':
                continue # skip for now
            elif name == '_elements':
                # must manually add elements to 
                for e in self._elements: 
                    # this will work for all with __deepcopy___
                    newElement = copy.deepcopy(e)
                    # get the old offset from the parent Stream     
                    # user here to provide new offset
                    new.insert(e.getOffsetBySite(old), newElement)
                # the elements, formerly had their stream as parent     
                # they will still have that site in locations
                # need to set new stream as parent 
                
            elif isinstance(part, Stream):
                environLocal.printDebug(['found stream in dict keys', self,
                    part, name])
                raise StreamException('streams as attributes requires special handling')

            else: # use copy.deepcopy   
                #environLocal.printDebug(['forced to use copy.deepcopy:',
                #    self, name, part])
                newValue = copy.deepcopy(part)
                #setattr() will call the set method of a named property.
                setattr(new, name, newValue)

                
        return new



    def insert(self, offsetOrItemOrList, itemOrNone = None):
        '''
        Inserts an item(s) at the given offset(s)
        
        Has three forms: in the two argument form, inserts an element at the given offset:
        
        >>> st1 = Stream()
        >>> st1.insert(32, note.Note("B-"))
        >>> st1._getHighestOffset()
        32.0
        
        In the single argument form with an object, inserts the element at its stored offset:
        
        >>> n1 = note.Note("C#")
        >>> n1.offset = 30.0
        >>> st1 = Stream()
        >>> st1.insert(n1)
        >>> st2 = Stream()
        >>> st2.insert(40.0, n1)
        >>> n1.getOffsetBySite(st1)
        30.0
        
        In single argument form list a list of alternating offsets and items, inserts the items
        at the specified offsets:
        
        >>> n1 = note.Note("G")
        >>> n2 = note.Note("F#")
        >>> st3 = Stream()
        >>> st3.insert([1.0, n1, 2.0, n2])
        >>> n1.getOffsetBySite(st3)
        1.0
        >>> n2.getOffsetBySite(st3)
        2.0
        >>> len(st3)
        2
        '''
        if itemOrNone != None:
            offset = offsetOrItemOrList
            item = itemOrNone            
        elif itemOrNone == None and isinstance(offsetOrItemOrList, list):
            i = 0
            while i < len(offsetOrItemOrList):
                offset = offsetOrItemOrList[i]
                item   = offsetOrItemOrList[i+1]
                self.insert(offset, item)
                i += 2
            return
        else:
            item = offsetOrItemOrList
            offset = item.offset
        
        # if not an element, embed
        if not isinstance(item, music21.Music21Object): 
            environLocal.printDebug(['insert called with non Music21Object', item])
            element = music21.ElementWrapper(item)
        else:
            element = item

        offset = float(offset)
        element.locations.add(offset, self)
        # need to explicitly set the parent of the elment
        element.parent = self 

        if self.isSorted is True and self.highestTime <= offset:
            storeSorted = True
        else:
            storeSorted = False

        self._elements.append(element)  # could also do self.elements = self.elements + [element]
        self._elementsChanged()         # maybe much slower?
        self.isSorted = storeSorted

    def append(self, others):
        '''
        Add Music21Objects (including other Streams) to the Stream 
        (or multiple if passed a list)
        with offset equal to the highestTime (that is the latest "release" of an object), 
        that is, directly after the last element ends. 

        if the objects are not Music21Objects, they are wrapped in ElementWrappers

        runs fast for multiple addition and will preserve isSorted if True

        >>> a = Stream()
        >>> notes = []
        >>> for x in range(0,3):
        ...     n = note.Note('G#')
        ...     n.duration.quarterLength = 3
        ...     notes.append(n)
        >>> a.append(notes[0])
        >>> a.highestOffset, a.highestTime
        (0.0, 3.0)
        >>> a.append(notes[1])
        >>> a.highestOffset, a.highestTime
        (3.0, 6.0)
        >>> a.append(notes[2])
        >>> a.highestOffset, a.highestTime
        (6.0, 9.0)
        >>> notes2 = []
        >>> # since notes are not embedded in Elements here, their offset
        >>> # changes when added to a stream!
        >>> for x in range(0,3):
        ...     n = note.Note("A-")
        ...     n.duration.quarterLength = 3
        ...     n.offset = 0
        ...     notes2.append(n)                
        >>> a.append(notes2) # add em all again
        >>> a.highestOffset, a.highestTime
        (15.0, 18.0)
        >>> a.isSequence()
        True
        
        Add a note that already has an offset set -- does nothing different!
        >>> n3 = note.Note("B-")
        >>> n3.offset = 1
        >>> n3.duration.quarterLength = 3
        >>> a.append(n3)
        >>> a.highestOffset, a.highestTime
        (18.0, 21.0)
        
        '''

        highestTime = self.highestTime
        if not common.isListLike(others):
            # back into a list for list processing if single
            others = [others]

        for item in others:
            # if not an element, embed
            if not isinstance(item, music21.Music21Object): 
                element = music21.ElementWrapper(item)
            else:
                element = item

            element.locations.add(highestTime, self)
            # need to explicitly set the parent of the element
            element.parent = self 
            self._elements.append(element)  


            # this should look to the contained object duration
            if (hasattr(element, "duration") and 
                hasattr(element.duration, "quarterLength")):
                highestTime += element.duration.quarterLength

        ## does not change sorted state
        storeSorted = self.isSorted    
        self._elementsChanged()         
        self.isSorted = storeSorted



    def insertAtIndex(self, pos, item):
        '''Insert in elements by index position.

        >>> a = Stream()
        >>> a.repeatAppend(note.Note('A-'), 30)
        >>> a[0].name == 'A-'
        True
        >>> a.insertAtIndex(0, note.Note('B'))
        >>> a[0].name == 'B'
        True
        '''

        if not hasattr(item, "locations"):
            raise StreamException("Cannot insert and item that does not have a location; wrap in an ElementWrapper() first")

        # NOTE: this may have unexpected side effects, as the None location
        # may have been set much later in this objects life.
        # optionally, could use last assigned site to get the offset        
        # or, use zero
        item.locations.add(item.getOffsetBySite(None), self)
        # need to explicitly set the parent of the element
        item.parent = self 

        self._elements.insert(pos, item)
        self._elementsChanged()

    def insertAtNativeOffset(self, item):
        '''
        inserts the item at the offset that was defined before the item was inserted into a stream
        (that is item.getOffsetBySite(None); in fact, the entire code is self.insert(item.getOffsetBySite(None), item)

        >>> n1 = note.Note("F-")
        >>> n1.offset = 20.0
        >>> stream1 = Stream()
        >>> stream1.append(n1)
        >>> n1.getOffsetBySite(stream1)
        0.0
        >>> n1.offset
        0.0
        >>> stream2 = Stream()
        >>> stream2.insertAtNativeOffset(n1)
        >>> stream2[0].offset
        20.0
        >>> n1.getOffsetBySite(stream2)
        20.0
        '''
        self.insert(item.getOffsetBySite(None), item)

    def isClass(self, className):
        '''
        Returns true if the Stream or Stream Subclass is a particular class or subclasses that class.

        Used by getElementsByClass in Stream

        >>> a = Stream()
        >>> a.isClass(note.Note)
        False
        >>> a.isClass(Stream)
        True
        >>> b = Measure()
        >>> b.isClass(Measure)
        True
        >>> b.isClass(Stream)
        True
        '''
        ## same as Music21Object.isClass, not ElementWrapper.isClass
        if isinstance(self, className):
            return True
        else:
            return False


    #---------------------------------------------------------------------------

    def _recurseRepr(self, thisStream, prefixSpaces = 0):
        msg = []
        insertSpaces = 4
        for element in thisStream:    
            off = str(element.getOffsetBySite(thisStream))    
            if isinstance(element, Stream):
                msg.append((" " * prefixSpaces) + "{" + off + "} " + 
                           element.__repr__())
                msg.append(self._recurseRepr(element, 
                           prefixSpaces + insertSpaces))
            else:
                msg.append((" " * prefixSpaces) + "{" + off + "} " + 
                            element.__repr__())
        return '\n'.join(msg)


    def _reprText(self):
        '''Retrun a text representation. This methods can be overridden by
        subclasses to provide alternative text representations.
        '''
        return self._recurseRepr(self)



    #---------------------------------------------------------------------------
    # temporary storage: does not work yet!

#     def writePickle(self, fp):
#         f = open(fp, 'wb') # binary
#         # a negative protocol value will get the highest protocol; 
#         # this is generally desirable 
#         pickleMod.dump(self, f, protocol=-1)
#         f.close()
# 
# 
#     def openPickle(self, fp):
#         # not sure this will work
#         f = open(fp, 'rb')
#         self = pickleMod.load(f)
#         f.close()


    #---------------------------------------------------------------------------
    # methods that act on individual elements without requiring 
    # @ _elementsChanged to fire

    def addGroupForElements(self, group, classFilter=None):
        '''
        Add the group to the groups attribute of all elements.
        if classFilter is set then only those elements whose objects
        belong to a certain class (or for Streams which are themselves of
        a certain class) are set.
         
        >>> a = Stream()
        >>> a.repeatAppend(note.Note('A-'), 30)
        >>> a.repeatAppend(note.Rest(), 30)
        >>> a.addGroupForElements('flute')
        >>> a[0].groups 
        ['flute']
        >>> a.addGroupForElements('quietTime', note.Rest)
        >>> a[0].groups 
        ['flute']
        >>> a[50].groups
        ['flute', 'quietTime']
        >>> a[1].groups.append('quietTime') # set one note to it
        >>> a[1].step = "B"
        >>> b = a.getElementsByGroup('quietTime')
        >>> len(b)
        31
        >>> c = b.getElementsByClass(note.Note)
        >>> len(c)
        1
        >>> c[0].name
        'B-'

        '''
        for myElement in self.elements:
            if classFilter is None:
                myElement.groups.append(group)
            else:
                if hasattr(myElement, "elements"): # stream type
                    if isinstance(myElement, classFilter):
                        myElement.groups.append(group)
                elif hasattr(myElement, "obj"): # element type
                    if isinstance(myElement.obj, classFilter):
                        myElement.groups.append(group)
                else: # music21 type
                    if isinstance(myElement, classFilter):
                        myElement.groups.append(group)


    #---------------------------------------------------------------------------
    # getElementsByX(self): anything that returns a collection of Elements should return a Stream

    def getElementsByClass(self, classFilterList, unpackElement=False):
        '''Return a list of all Elements that match the className.

        Note that, as this appends Elements to a new Stream, whatever former
        parent relationship the ElementWrapper had is lost. The ElementWrapper's parent
        is set to the new stream that contains it. 
        
        >>> a = Stream()
        >>> a.repeatInsert(note.Rest(), range(10))
        >>> for x in range(4):
        ...     n = note.Note('G#')
        ...     n.offset = x * 3
        ...     a.insert(n)
        >>> found = a.getElementsByClass(note.Note)
        >>> len(found)
        4
        >>> found[0].pitch.accidental.name
        'sharp'
        >>> b = Stream()
        >>> b.repeatInsert(note.Rest(), range(15))
        >>> a.insert(b)
        >>> # here, it gets elements from within a stream
        >>> # this probably should not do this, as it is one layer lower
        >>> found = a.getElementsByClass(note.Rest)
        >>> len(found)
        10
        >>> found = a.flat.getElementsByClass(note.Rest)
        >>> len(found)
        25
        '''
        if unpackElement: # a list of objects
            found = []
        else: # return a Stream     
            found = Stream()

        if not common.isListLike(classFilterList):
            classFilterList = [classFilterList]

        # appendedAlready fixes bug where if an element matches two 
        # classes it was appendedTwice
        for myEl in self:
            appendedAlready = False
            for myCl in classFilterList:
                if myEl.isClass(myCl) and appendedAlready == False:
                    appendedAlready = True
                    if unpackElement and hasattr(myEl, "obj"):
                        found.append(myEl.obj)
                    elif not isinstance(found, Stream):
                        found.append(myEl)
                    else:
                        # using append here on a non list adds elements to a 
                        # new stream without offsets in locations. thus
                        # all offset information is lost. using
                        # insert fixes the problem
                        found.insert(myEl.getOffsetBySite(self), myEl)
        return found


    def getElementsByGroup(self, groupFilterList):
        '''
        # TODO: group comparisons are not YET case insensitive.  
        
        >>> from music21 import note
        >>> n1 = note.Note("C")
        >>> n1.groups.append('trombone')
        >>> n2 = note.Note("D")
        >>> n2.groups.append('trombone')
        >>> n2.groups.append('tuba')
        >>> n3 = note.Note("E")
        >>> n3.groups.append('tuba')
        >>> s1 = Stream()
        >>> s1.append(n1)
        >>> s1.append(n2)
        >>> s1.append(n3)
        >>> tboneSubStream = s1.getElementsByGroup("trombone")
        >>> for thisNote in tboneSubStream:
        ...     print thisNote.name
        C
        D
        >>> tubaSubStream = s1.getElementsByGroup("tuba")
        >>> for thisNote in tubaSubStream:
        ...     print thisNote.name
        D
        E
        '''
        
        if not hasattr(groupFilterList, "__iter__"):
            groupFilterList = [groupFilterList]

        returnStream = Stream()
        for myEl in self:
            for myGrp in groupFilterList:
                if hasattr(myEl, "groups") and myGrp in myEl.groups:
                    returnStream.insert(myEl.getOffsetBySite(self),
                                                myEl)
                    #returnStream.append(myEl)

        return returnStream


    def getGroups(self):
        '''Get a dictionary for each groupId and the count of instances.

        >>> a = Stream()
        >>> n = note.Note()
        >>> a.repeatAppend(n, 30)
        >>> a.addGroupForElements('P1')
        >>> a.getGroups()
        {'P1': 30}
        >>> a[12].groups.append('green')
        >>> a.getGroups()
        {'P1': 30, 'green': 1}
        '''

        # TODO: and related:

        #getStreamGroups which does the same but makes the value of the hash key be a stream with all the elements that match the group?
        # this is similar to what getElementsByGroup does

        post = {}
        for element in self:
            for groupName in element.groups:
                if groupName not in post.keys():
                    post[groupName] = 0
                post[groupName] += 1
        return post


    def getElementById(self, id, classFilter=None):
        '''Returns the first encountered element for a given id. Return None
        if no match

        >>> e = 'test'
        >>> a = Stream()
        >>> a.insert(0, e)
        >>> a[0].id = 'green'
        >>> None == a.getElementById(3)
        True
        >>> a.getElementById('green').id
        'green'
        '''
        for element in self.elements:
            if element.id == id:
                if classFilter != None:
                    if element.isClass(classFilter):
                        return element
                    else:
                        continue # id may match but not proper class
                else:
                    return element
        return None

    def getElementsByOffset(self, offsetStart, offsetEnd,
                    includeCoincidentBoundaries=True, onsetOnly=True):
        '''
        Return a Stream/list of all Elements that are found within a 
        certain offset time range, specified as start and stop values, 
        and including boundaries.

        If onsetOnly is true, only the onset of an event is taken into 
        consideration; the offset is not.

        The time range is taken as the context for the flat representation.

        The includeCoincidentBoundaries option determines if an end boundary
        match is included.
        
        >>> a = Stream()
        >>> a.repeatInsert(note.Note("C"), range(10)) 
        >>> b = a.getElementsByOffset(4,6)
        >>> len(b)
        3
        >>> b = a.getElementsByOffset(4,5.5)
        >>> len(b)
        2

        >>> a = Stream()
        >>> n = note.Note('G')
        >>> n.quarterLength = .5
        >>> a.repeatInsert(n, range(8))
        >>> b = Stream()
        >>> b.repeatInsert(a, [0, 3, 6])
        >>> c = b.getElementsByOffset(2,6.9)
        >>> len(c)
        2
        
         >>> c = b.flat.getElementsByOffset(2,6.9)
        >>> len(c)
        10
        '''
        found = Stream()

        #(offset, priority, dur, element). 
        for element in self:
            match = False
            offset = element.offset
            dur = element.duration

            if dur == None or onsetOnly:          
                elementEnd = offset
            else:
                elementEnd = offset + dur

            if includeCoincidentBoundaries:
                if offset >= offsetStart and elementEnd <= offsetEnd:
                    match = True
            else: # 
                if offset >= offsetStart and elementEnd < offsetEnd:
                    match = True

            if match:
                found.insert(element)
        return found


    def getElementAtOrBefore(self, offset, unpackElement=False):
        '''Given an offset, find the element at this offset, or with the offset
        less than and nearest to.

        Return one element or None if no elements are at or preceded by this 
        offset. 

        TODO: include sort order for concurrent matches?

        >>> a = Stream()

        >>> x = music21.Music21Object()
        >>> x.id = 'x'
        >>> y = music21.Music21Object()
        >>> y.id = 'y'
        >>> z = music21.Music21Object()
        >>> z.id = 'z'

        >>> a.insert(20, x)
        >>> a.insert(10, y)
        >>> a.insert( 0, z)

        >>> b = a.getElementAtOrBefore(21)
        >>> b.offset, b.id
        (20.0, 'x')

        >>> b = a.getElementAtOrBefore(19)
        >>> b.offset, b.id
        (10.0, 'y')

        >>> b = a.getElementAtOrBefore(0)
        >>> b.offset, b.id
        (0.0, 'z')
        >>> b = a.getElementAtOrBefore(0.1)
        >>> b.offset, b.id
        (0.0, 'z')

        '''
        candidates = []
        nearestTrailSpan = offset # start with max time
        for element in self:
            span = offset - element.offset
            #environLocal.printDebug(['element span check', span])
            if span < 0: # the element is after this offset
                continue
            elif span == 0: 
                candidates.append((span, element))
                nearestTrailSpan = span
            else:
                if span <= nearestTrailSpan: # this may be better than the best
                    candidates.append((span, element))
                    nearestTrailSpan = span
                else:
                    continue
        #environLocal.printDebug(['element candidates', candidates])
        if len(candidates) > 0:
            candidates.sort()
            return candidates[0][1]
        else:
            return None


    def getElementAtOrAfter(self, offset, unpackElement=False):
        '''Given an offset, find the element at this offset, or with the offset
        greater than and nearest to.
        TODO: write this
        '''
        raise Exception("not yet implemented")




    def getElementBeforeOffset(self, offset, unpackElement=False):
        '''Get element before a provided offset
        TODO: write this
        '''
        raise Exception("not yet implemented")

    def getElementAfterOffset(self, offset, unpackElement=False):
        '''Get element after a provided offset
        TODO: write this
        '''
        raise Exception("not yet implemented")




    def getElementBeforeElement(self, element, unpackElement=False):
        '''given an element, get the element before
        TODO: write this
        '''
        raise Exception("not yet implemented")

    def getElementAfterElement(self, element, unpackElement=False):
        '''given an element, get the element next
        TODO: write this
        '''
        raise Exception("not yet implemented")



    def groupElementsByOffset(self, returnDict = False, unpackElement = False):
        '''
        returns a List of lists in which each entry in the
        main list is a list of elements occurring at the same time.
        list is ordered by offset (since we need to sort the list
        anyhow in order to group the elements), so there is
        no need to call stream.sorted before running this,
        but it can't hurt.
        
        it is DEFINITELY a feature that this method does not
        find elements within substreams that have the same
        absolute offset.  See Score.lily for how this is
        useful.  For the other behavior, call Stream.flat first.
        '''
        offsetsRepresented = common.defHash()
        for el in self.elements:
            if not offsetsRepresented[el.offset]:
                offsetsRepresented[el.offset] = []
            if unpackElement is False:
                offsetsRepresented[el.offset].append(el)
            else:
                offsetsRepresented[el.offset].append(el.obj)
        if returnDict is True:
            return offsetsRepresented
        else:
            offsetList = []
            for thisOffset in sorted(offsetsRepresented.keys()):
                offsetList.append(offsetsRepresented[thisOffset])
            return offsetList



    #--------------------------------------------------------------------------
    # routines for obtaining specific types of elements form a Stream
    # getNotes and getPitches are found with the interval routines
        

    def getMeasures(self):
        '''Return all Measure objects in a Stream()
        '''
        return self.getElementsByClass(Measure)

    measures = property(getMeasures)


    def getTimeSignatures(self):
        '''Collect all time signatures in this stream.
        If no TimeSignature objects are defined, get a default
    
        Note: this could be a method of Stream.
    
        >>> a = Stream()
        >>> b = meter.TimeSignature('3/4')
        >>> a.insert(b)
        >>> a.repeatInsert(note.Note("C#"), range(10)) 
        >>> c = a.getTimeSignatures()
        >>> len(c) == 1
        True
        '''
        post = self.getElementsByClass(meter.TimeSignature)
    
        # get a default and/or place default at zero if nothing at zero
        if len(post) == 0 or post[0].offset > 0: 
            ts = meter.TimeSignature()
            ts.load('%s/%s' % (defaults.meterNumerator, 
                               defaults.meterDenominatorBeatType))
            #ts.numerator = defaults.meterNumerator
            #ts.denominator = defaults.meterDenominatorBeatType
            post.insert(0, ts)
        return post
    


    def getInstrument(self, searchParent=True):
        '''Search this stream or parent streams for instruments, otherwise 
        return a default

        >>> a = Stream()
        >>> b = a.getInstrument()
        '''
        #environLocal.printDebug(['searching for instrument, called from:', 
        #                        self])
        #TODO: Rename: getInstruments, and return a Stream of instruments
        #for cases when there is more than one instrument

        instObj = None
        post = self.getElementsByClass(instrument.Instrument)
        if len(post) > 0:
            #environLocal.printDebug(['found local instrument:', post[0]])
            instObj = post[0] # get first
        else:
            if searchParent:
                if isinstance(self.parent, Stream) and self.parent != self:
                    #environLocal.printDebug(['searching parent Stream', 
                    #    self, self.parent])
                    instObj = self.parent.getInstrument()         

        # if still not defined, get default
        if instObj == None:
            instObj = instrument.Instrument()
            instObj.partId = defaults.partId # give a default id
            instObj.partName = defaults.partName # give a default id
        return instObj



    def bestClef(self, allowTreble8vb = False):
        '''Returns the clef that is the best fit for notes and chords found in thisStream.

        Perhaps rename 'getClef'; providing best clef if not clef is defined in this stream; otherwise, return a stream of clefs with offsets


        >>> a = Stream()
        >>> for x in range(30):
        ...    n = note.Note()
        ...    n.midi = random.choice(range(60,72))
        ...    a.insert(n)
        >>> b = a.bestClef()
        >>> b.line
        2
        >>> b.sign
        'G'

        >>> c = Stream()
        >>> for x in range(30):
        ...    n = note.Note()
        ...    n.midi = random.choice(range(35,55))
        ...    c.insert(n)
        >>> d = c.bestClef()
        >>> d.line
        4
        >>> d.sign
        'F'
        '''
        #environLocal.printDebug(['calling bestClef()'])

        totalNotes = 0
        totalHeight = 0

        notes = self.getElementsByClass(note.GeneralNote, unpackElement=True)

        def findHeight(thisPitch):
            height = thisPitch.diatonicNoteNum
            if thisPitch.diatonicNoteNum > 33: # a4
                height += 3 # bonus
            elif thisPitch.diatonicNoteNum < 24: # Bass F or lower
                height += -3 # bonus
            return height
        
        for thisNote in notes:
            if thisNote.isRest:
                pass
            elif thisNote.isNote:
                totalNotes  += 1
                totalHeight += findHeight(thisNote.pitch)
            elif thisNote.isChord:
                for thisPitch in thisNote.pitches:
                    totalNotes += 1
                    totalHeight += findHeight(thisPitch)
        if totalNotes == 0:
            averageHeight = 29
        else:
            averageHeight = (totalHeight + 0.0) / totalNotes

        if (allowTreble8vb == False):
            if averageHeight > 28:    # c4
                return clef.TrebleClef()
            else:
                return clef.BassClef()
        else:
            if averageHeight > 32:    # g4
                return clef.TrebleClef()
            elif averageHeight > 26:  # a3
                return clef.Treble8vbClef()
            else:
                return clef.BassClef()


    #--------------------------------------------------------------------------
    # offset manipulation

    def shiftElements(self, offset):
        '''Add offset value to every offset of contained Elements.

        >>> a = Stream()
        >>> a.repeatInsert(note.Note("C"), range(0,10))
        >>> a.shiftElements(30)
        >>> a.lowestOffset
        30.0
        >>> a.shiftElements(-10)
        >>> a.lowestOffset
        20.0
        '''
        for e in self:
            e.locations.setOffsetBySite(self, 
                e.locations.getOffsetBySite(self) + offset)
        self._elementsChanged() 
        
    def transferOffsetToElements(self):
        '''Transfer the offset of this stream to all internal elements; then set
        the offset of this stream to zero.

        >>> a = Stream()
        >>> a.repeatInsert(note.Note("C"), range(0,10))
        >>> a.offset = 30
        >>> a.transferOffsetToElements()
        >>> a.lowestOffset
        30.0
        >>> a.offset
        0.0
        >>> a.offset = 20
        >>> a.transferOffsetToElements()        
        >>> a.lowestOffset
        50.0
        '''
        self.shiftElements(self.offset)
        self.offset = 0.0
        self._elementsChanged()


    #--------------------------------------------------------------------------
    # utilities for creating large numbers of elements

    def repeatAppend(self, item, numberOfTimes):
        '''
        Given an object and a number, run append that many times on a deepcopy of the object.
        numberOfTimes should of course be a positive integer.
        
        >>> a = Stream()
        >>> n = note.Note()
        >>> n.duration.type = "whole"
        >>> a.repeatAppend(n, 10)
        >>> a.duration.quarterLength
        40.0
        >>> a[9].offset
        36.0
        '''
        # if not an element, embed
        if not isinstance(item, music21.Music21Object): 
            element = music21.ElementWrapper(item)
        else:
            element = item
            
        for i in range(0, numberOfTimes):
            self.append(deepcopy(element))
    
    def repeatInsert(self, item, offsets):
        '''Given an object, create many DEEPcopies at the positions specified by 
        the offset list:

        >>> a = Stream()
        >>> n = note.Note('G-')
        >>> n.quarterLength = 1
        
        >>> a.repeatInsert(n, [0, 2, 3, 4, 4.5, 5, 6, 7, 8, 9, 10, 11, 12])
        >>> len(a)
        13
        >>> a[10].offset
        10.0
        '''
        if not common.isListLike(offsets): 
            raise StreamException('must provide a lost of offsets, not %s' % offsets)

        if not isinstance(item, music21.Music21Object): 
            # if not an element, embed
            element = music21.ElementWrapper(item)
        else:
            element = item

        for offset in offsets:
            elementCopy = deepcopy(element)
            self.insert(offset, elementCopy)



    def extractContext(self, searchElement, before = 4.0, after = 4.0, 
                       maxBefore = None, maxAfter = None):
        r'''
        extracts elements around the given element within (before) quarter notes and (after) quarter notes
        (default 4)
        
        TODO: maxBefore -- maximum number of elements to return before; etc.
        
        >>> from music21 import note
        >>> qn = note.QuarterNote()
        >>> qtrStream = Stream()
        >>> qtrStream.repeatInsert(qn, [0, 1, 2, 3, 4, 5])
        >>> hn = note.HalfNote()
        >>> hn.name = "B-"
        >>> qtrStream.append(hn)
        >>> qtrStream.repeatInsert(qn, [8, 9, 10, 11])
        >>> hnStream = qtrStream.extractContext(hn, 1.0, 1.0)
        >>> hnStream._reprText()
        '{5.0} <music21.note.Note C>\n{6.0} <music21.note.Note B->\n{8.0} <music21.note.Note C>'
        '''
        
        display = Stream()
        found = None
        foundOffset = 0
        foundEnd = 0 
        for i in range(0, len(self.elements)):
            b = self.elements[i]
            if b.id is not None or searchElement.id is not None:
                if b.id == searchElement.id:
                    found = i
                    foundOffset = self.elements[i].getOffsetBySite(self)
                    foundEnd    = foundOffset + self.elements[i].duration.quarterLength                        
            else:
                if b is searchElement or (hasattr(b, "obj") and b.obj is searchElement):
                    found = i
                    foundOffset = self.elements[i].getOffsetBySite(self)
                    foundEnd    = foundOffset + self.elements[i].duration.quarterLength
        if found is None:
            raise StreamException("Could not find the element in the stream")

        for thisElement in self:
            thisElOffset = thisElement.getOffsetBySite(self)
            if (thisElOffset >= foundOffset - before and
                   thisElOffset < foundEnd + after):
                display.insert(thisElOffset, thisElement)

        return display


    #---------------------------------------------------------------------------
    # transformations of self that return a new Stream

    def splitByClass(self, objName, fx):
        '''Given a stream, get all objects specified by objName and then form
        two new streams.  Fx should be a lambda or other function on elements.
        All elements where fx returns True go in the first stream.
        All other elements are put in the second stream.
        
        >>> stream1 = Stream()
        >>> for x in range(30,81):
        ...     n = note.Note()
        ...     n.offset = x
        ...     n.midi = x
        ...     stream1.insert(n)
        >>> fx = lambda n: n.midi > 60
        >>> b, c = stream1.splitByClass(note.Note, fx)
        >>> len(b)
        20
        >>> len(c)
        31
        '''
        a = Stream()
        b = Stream()
        for element in self.getElementsByClass(objName):
            if fx(element):
                a.insert(element)
            else:
                b.insert(element)
        return a, b
            


    def makeMeasures(self, meterStream=None, refStream=None):
        '''Take a stream and partition all elements into measures based on 
        one or more TimeSignature defined within the stream. If no TimeSignatures are defined, a default is used.

        This always creates a new stream with Measures, though objects are not
        copied from self stream. 
    
        If a meterStream is provided, this is used instead of the meterStream
        found in the Stream.
    
        If a refStream is provided, this is used to provide max offset values, necessary to fill empty rests and similar.
        
        >>> a = Stream()
        >>> a.repeatAppend(note.Rest(), 3)
        >>> b = a.makeMeasures()
        >>> c = meter.TimeSignature('3/4')
        >>> a.insert(0.0, c)
        >>> x = a.makeMeasures()
        
        TODO: Test something here...
    
        >>> d = Stream()
        >>> n = note.Note()
        >>> d.repeatAppend(n, 10)
        >>> d.repeatInsert(n, [x+.5 for x in range(10)])
        >>> x = d.makeMeasures()
        '''
        #environLocal.printDebug(['calling Stream.makeMeasures()'])

        # the srcObj shold not be modified or chagned
        srcObj = self

        # may need to look in parent if no time signatures are found
        if meterStream == None:
            meterStream = srcObj.getTimeSignatures()

        # get a clef and for the entire stream
        clefObj = srcObj.bestClef()
    
        # for each element in stream, need to find max and min offset
        # assume that flat/sorted options will be set before procesing
        offsetMap = [] # list of start, start+dur, element
        for e in srcObj:
            if hasattr(e, 'duration') and e.duration != None:
                dur = e.duration.quarterLength
            else:
                dur = 0 
            # may just need to copy element offset component
            #offset = e.getOffsetBySite(srcObj)
            # NOTE: rounding here may cause secondary problems
            offset = round(e.getOffsetBySite(srcObj), 8)
            offsetMap.append([offset, offset + dur, copy.copy(e)])
    
        #environLocal.printDebug(['makesMeasures()', offsetMap])    
    
        #offsetMap.sort() not necessary; just get min and max
        oMin = min([start for start, end, e in offsetMap])
        oMax = max([end for start, end, e in offsetMap])
    
        # this should not happen, but just in case
        if not common.almostEquals(oMax, srcObj.highestTime):
            raise StreamException('mismatch between oMax and highestTime (%s, %s)' % (oMax, srcObj.highestTime))
        #environLocal.printDebug(['oMin, oMax', oMin, oMax])
    
        # if a ref stream is provided, get highst time from there
        # only if it is greater thant the highest time yet encountered
        if refStream != None:
            if refStream.highestTime > oMax:
                oMax = refStream.highestTime
    
        # create a stream of measures to contain the offsets range defined
        # create as many measures as needed to fit in oMax
        post = Stream()
        o = 0 # initial position of first measure is assumed to be zero
        measureCount = 0
        lastTimeSignature = None
        while True:    
            m = Measure()
            m.measureNumber = measureCount + 1
            # get active time signature at this offset
            # make a copy and it to the meter
            thisTimeSignature = meterStream.getElementAtOrBefore(o)
            if thisTimeSignature != lastTimeSignature:
                lastTimeSignature = meterStream.getElementAtOrBefore(o)
                m.timeSignature = deepcopy(thisTimeSignature)
                #environLocal.printDebug(['assigned time sig', m.timeSignature])

            # only add a clef for the first measure when automatically 
            # creating Measures; this clef is from bestClef, called above
            if measureCount == 0: 
                m.clef = clefObj
    
            # avoid an infinite loop
            if thisTimeSignature.barDuration.quarterLength == 0:
                raise StreamException('time signature has no duration')    
            post.insert(o, m) # insert measure
            # increment by meter length
            o += thisTimeSignature.barDuration.quarterLength 
            if o >= oMax: # may be zero
                break # if length of this measure exceedes last offset
            else:
                measureCount += 1
        
        # populate measures with elements
        for start, end, e in offsetMap:
            # iterate through all measures 
            match = False
            lastTimeSignature = None
            for i in range(len(post)):
                m = post[i]
                if m.timeSignature != None:
                    lastTimeSignature = m.timeSignature
                # get start and end offsets for each measure
                # seems like should be able to use m.duration.quarterLengths
                mStart = m.getOffsetBySite(post)
                mEnd = mStart + lastTimeSignature.barDuration.quarterLength
                # if elements start fits within this measure, break and use 
                # offset cannot start on end
                if start >= mStart and start < mEnd:
                    match = True
                    #environLocal.printDebug(['found measure match', i, mStart, mEnd, start, end, e])
                    break
            if not match:
                raise StreamException('cannot place element with start/end %s/%s within any measures' % (start, end))
            # find offset in the temporal context of this measure
            # i is the index of the measure that this element starts at
            # mStart, mEnd are correct
            oNew = start - mStart # remove measure offset from element offset
            # insert element at this offset in the measure
            # not copying elements here!
            # here, we have the correct measure from above
            #environLocal.printDebug(['measure placement', mStart, oNew, e])
            m.insert(oNew, e)

        return post # returns a new stream populated w/ new measure streams


    def makeRests(self, refStream=None, inPlace=True):
        '''Given a streamObj with an  with an offset not equal to zero, 
        fill with one Rest preeceding this offset. 
    
        If refStream is provided, use this to get min and max offsets. Rests 
        will be added to fill all time defined within refStream.
    
        TODO: rename fillRests() or something else.  CHRIS: I Don't Understand what refStream does for this method!
    
        >>> a = Stream()
        >>> a.insert(20, note.Note())
        >>> len(a)
        1
        >>> a.lowestOffset
        20.0
        >>> b = a.makeRests()
        >>> len(b)
        2
        >>> b.lowestOffset
        0.0
        '''
        #environLocal.printDebug(['calling makeRests'])
        if not inPlace: # make a copy
            returnObj = deepcopy(self)
        else:
            returnObj = self
    
        oLow = returnObj.lowestOffset
        oHigh = returnObj.highestTime
        if refStream != None:
            oLowTarget = refStream.lowestOffset
            oHighTarget = refStream.highestTime
            environLocal.printDebug(['refStream used in makeRests', oLowTarget, oHighTarget, len(refStream)])
        else:
            oLowTarget = 0
            oHighTarget = returnObj.highestTime
            
        qLen = oLow - oLowTarget
        if qLen > 0:
            r = note.Rest()
            r.duration.quarterLength = qLen
            returnObj.insert(oLowTarget, r)
    
        qLen = oHighTarget - oHigh
        if qLen > 0:
            r = note.Rest()
            r.duration.quarterLength = qLen
            returnObj.insert(oHigh, r)
    
        # do not need to sort, can concatenate without sorting
        # post = streamLead + returnObj 
        return returnObj.sorted


    def makeTies(self, meterStream=None, inPlace=True):
        '''Given a stream containing measures, examine each element in the stream 
        if the elements duration extends beyond the measures bound, create a tied  entity.
    
        Edits the current stream in-place by default.  This can be changed by setting the inPlace keyword to false
        
        TODO: take a list of clases to act as filter on what elements are tied.
    
        configure ".previous" and ".next" attributes
    
        >>> d = Stream()
        >>> n = note.Note()
        >>> n.quarterLength = 12
        >>> d.repeatAppend(n, 10)
        >>> d.repeatInsert(n, [x+.5 for x in range(10)])
        >>> #x = d.makeMeasures()
        >>> #x = x.makeTies()
    
        '''

        #environLocal.printDebug(['calling Stream.makeTies()'])

        if not inPlace: # make a copy
            returnObj = deepcopy(self)
        else:
            returnObj = self


        if len(returnObj) == 0:
            raise StreamException('cannot process an empty stream')        
    
        # get measures from this stream
        measureStream = returnObj.getMeasures()
        if len(measureStream) == 0:
            raise StreamException('cannot process a stream without measures')        
    
        # may need to look in parent if no time signatures are found
        if meterStream == None:
            meterStream = returnObj.getTimeSignatures()
    
        mCount = 0
        lastTimeSignature = None
        while True:
            # update measureStream on each iteration, 
            # as new measure may have been added to the stream 
            measureStream = returnObj.getElementsByClass(Measure)
            if mCount >= len(measureStream):
                break
            # get the current measure to look for notes that need ties
            m = measureStream[mCount]
            if m.timeSignature != None:
                lastTimeSignature = m.timeSignature

            if mCount + 1 < len(measureStream):
                mNext = measureStream[mCount+1]
                mNextAdd = False
            else: # create a new measure
                mNext = Measure()
                # set offset to last offset plus total length
                moffset = m.getOffsetBySite(measureStream)
                mNext.offset = (moffset + 
                                lastTimeSignature.barDuration.quarterLength)
                if len(meterStream) == 0: # in case no meters are defined
                    ts = meter.TimeSignature()
                    ts.load('%s/%s' % (defaults.meterNumerator, 
                                       defaults.meterDenominatorBeatType))
                else: # get the last encountered meter
                    ts = meterStream.getElementAtOrBefore(mNext.offset)
                # only copy and assign if not the same as the last
                if not lastTimeSignature.ratioEqual(ts):
                    mNext.timeSignature = deepcopy(ts)
                # increment measure number
                mNext.measureNumber = m.measureNumber + 1
                mNextAdd = True
    
            # seems like should be able to use m.duration.quarterLengths
            mStart, mEnd = 0, lastTimeSignature.barDuration.quarterLength
            for e in m:
                #environLocal.printDebug(['Stream.makeTies() iterating over elements in measure', m, e])

                if hasattr(e, 'duration') and e.duration != None:
                    # check to see if duration is within Measure
                    eoffset = e.getOffsetBySite(m)
                    eEnd = eoffset + e.duration.quarterLength
                    # assume end can be at boundary of end of measure
                    if eEnd > mEnd:
                        if eoffset >= mEnd:
                            raise StreamException('element has offset %s within a measure that ends at offset %s' % (e.offset, mEnd))  
    
                        # note: cannot use GeneralNote.splitNoteAtPoint b/c
                        # we are not assuming that these are notes, only elements
    
                        qLenBegin = mEnd - eoffset
                        #print 'e.offset, mEnd, qLenBegin', e.offset, mEnd, qLenBegin
                        qLenRemain = e.duration.quarterLength - qLenBegin
                        # modify existing duration
                        e.duration.quarterLength = qLenBegin
                        # create and place new element
                        eRemain = deepcopy(e)
                        eRemain.duration.quarterLength = qLenRemain
    
                        # set ties
                        if (e.isClass(note.Note) or 
                            e.isClass(note.Unpitched)):
                            #environLocal.printDebug(['tieing in makeTies', e])
                            e.tie = note.Tie('start')
                            # TODO: not sure if we can assume to stop remainder
                            #e.Remain.tie = note.Tie('stop')
    
                        # TODO: this does not seem the best way to do this!
                        # need to find a better way to insert this first in elements

                        # used to do this:
                        eRemain.offset = 0
                        mNext.elements = [eRemain] + mNext.elements

                        # alternative approach (same slowness)
                        #mNext.insert(0, eRemain)
                        #mNext = mNext.sorted
    
                        # we are not sure that this element fits 
                        # completely in the next measure, thus, need to continue
                        # processing each measure
                        if mNextAdd:
                            returnObj.insert(mNext.offset, mNext)
            mCount += 1

        return returnObj
    

    def makeBeams(self, inPlace=True):
        '''Return a new measure with beams applied to all notes. 

        if inPlace is false, this creates a new, independent copy of the source.

        In the process of making Beams, this method also updates tuplet types. this is destructive and thus changes an attribute of Durations in Notes.

        TODO: inPlace=False does not work in many cases

        >>> aMeasure = Measure()
        >>> aMeasure.timeSignature = meter.TimeSignature('4/4')
        >>> aNote = note.Note()
        >>> aNote.quarterLength = .25
        >>> aMeasure.repeatAppend(aNote,16)
        >>> bMeasure = aMeasure.makeBeams()
        '''

        #environLocal.printDebug(['calling Stream.makeBeams()'])

        if not inPlace: # make a copy
            returnObj = deepcopy(self)
        else:
            returnObj = self

        if self.isClass(Measure):
            mColl = [] # store a list of measures for processing
            mColl.append(returnObj)
        elif len(self.getMeasures()) > 0:
            mColl = returnObj.getMeasures() # a stream of measures
        else:
            raise StreamException('cannot process a stream that neither is a Measure nor has Measures')        

        lastTimeSignature = None
        for m in mColl:
            if m.timeSignature != None:
                lastTimeSignature = m.timeSignature
            if lastTimeSignature == None:
                raise StreamException('cannot proces beams in a Measure without a time signature')
    
            # environLocal.printDebug(['beaming with ts', ts])
            noteStream = m.getNotes()
            if len(noteStream) <= 1: 
                continue # nothing to beam
            durList = []
            for n in noteStream:
                durList.append(n.duration)
            # getBeams can take a list of Durations; however, this cannot
            # distinguish a Note from a Rest; thus, we can submit a flat 
            # stream of note or note-like entities; will return
            # the saem lost of beam objects
            beamsList = lastTimeSignature.getBeams(noteStream)
            for i in range(len(noteStream)):
                # this may try to assign a beam to a Rest
                noteStream[i].beams = beamsList[i]
            # apply tuple types in place
            duration.updateTupletType(durList)

        return returnObj


    def extendDuration(self, objName, inPlace=True):
        '''Given a stream and an object name, go through stream and find each 
        object. The time between adjacent objects is then assigned to the 
        duration of each object. The last duration of the last object is assigned
        to the end of the stream.
        
        >>> import music21.dynamics
        >>> stream1 = Stream()
        >>> n = note.QuarterNote()
        >>> n.duration.quarterLength
        1.0
        >>> stream1.repeatInsert(n, [0, 10, 20, 30, 40])
        >>> dyn = music21.dynamics.Dynamic('ff')
        >>> stream1.insert(15, dyn)
        >>> sort1 = stream1.sorted
        >>> sort1[-1].offset # offset of last element
        40.0
        >>> sort1.duration.quarterLength # total duration
        41.0
        >>> len(sort1)
        6
    
        >>> stream2 = sort1.flat.extendDuration(note.GeneralNote)
        >>> len(stream2)
        6
        >>> stream2[0].duration.quarterLength
        10.0
        >>> stream2[1].duration.quarterLength # all note durs are 10
        10.0
        >>> stream2[-1].duration.quarterLength # or extend to end of stream
        1.0
        >>> stream2.duration.quarterLength
        41.0
        >>> stream2[-1].offset
        40.0

        TODO: Chris; what file is testFiles.ALL[2]?? 
        
#        >>> from music21.musicxml import testFiles
#        >>> from music21 import converter
#        >>> mxString = testFiles.ALL[2] # has dynamics
#        >>> a = converter.parse(mxString)
#        >>> b = a.flat.extendDuration(dynamics.Dynamic)    
        '''
    
        if not inPlace: # make a copy
            returnObj = deepcopy(self)
        else:
            returnObj = self

        # Should we do this?  or just return an exception if not there.
        # this cannot work unless we use a sorted representation
        returnObj = returnObj.sorted

        qLenTotal = returnObj.duration.quarterLength
        elements = []
        for element in returnObj.getElementsByClass(objName):
            if not hasattr(element, 'duration'):
                raise StreamException('can only process objects with duration attributes')
            if element.duration == None:
                element.duration = duration.Duration()
            elements.append(element)
    
        #print elements[-1], qLenTotal, elements[-1].duration
        # print _MOD, elements
        for i in range(len(elements)-1):
            #print i, len(elements)
            span = elements[i+1].getOffsetBySite(self) - elements[i].getOffsetBySite(self)
            elements[i].duration.quarterLength = span
    
        # handle last element
        #print elements[-1], qLenTotal, elements[-1].duration
        elements[-1].duration.quarterLength = (qLenTotal -
                                                 elements[-1].getOffsetBySite(self))
        #print elements[-1], elements[-1].duration    
        return returnObj
    



    #---------------------------------------------------------------------------
    def _getSorted(self):
        '''
        returns a new Stream where all the elements are sorted according to offset time
        
        if this stream is not flat, then only the highest elements are sorted.  To sort all,
        run myStream.flat.sorted
        
        ## TODO: CLEF ORDER RULES, etc.
        
        >>> s = Stream()
        >>> s.repeatInsert(note.Note("C#"), [0, 2, 4])
        >>> s.repeatInsert(note.Note("D-"), [1, 3, 5])
        >>> s.isSorted
        False
        >>> g = ""
        >>> for myElement in s:
        ...    g += "%s: %s; " % (myElement.offset, myElement.name)
        >>> g
        '0.0: C#; 2.0: C#; 4.0: C#; 1.0: D-; 3.0: D-; 5.0: D-; '
        >>> y = s.sorted
        >>> y.isSorted
        True
        >>> g = ""
        >>> for myElement in y:
        ...    g += "%s: %s; " % (myElement.offset, myElement.name)
        >>> g
        '0.0: C#; 1.0: D-; 2.0: C#; 3.0: D-; 4.0: C#; 5.0: D-; '
        >>> farRight = note.Note("E")
        >>> farRight.priority = 5
        >>> farRight.offset = 2.0
        >>> y.insert(farRight)
        >>> g = ""
        >>> for myElement in y:
        ...    g += "%s: %s; " % (myElement.offset, myElement.name)
        >>> g
        '0.0: C#; 1.0: D-; 2.0: C#; 3.0: D-; 4.0: C#; 5.0: D-; 2.0: E; '
        >>> z = y.sorted
        >>> g = ""
        >>> for myElement in z:
        ...    g += "%s: %s; " % (myElement.offset, myElement.name)
        >>> g
        '0.0: C#; 1.0: D-; 2.0: C#; 2.0: E; 3.0: D-; 4.0: C#; 5.0: D-; '
        >>> z[2].name, z[3].name
        ('C#', 'E')
        '''
        post = self.elements ## already a copy
        post.sort(cmp=lambda x,y: cmp(x.getOffsetBySite(self), y.getOffsetBySite(self)) or cmp(x.priority, y.priority))
        newStream = copy.copy(self)
        newStream.elements = post
        for thisElement in post:
            thisElement.locations.add(thisElement.getOffsetBySite(self),
                                       newStream)
            # need to explicitly set parent
            thisElement.parent = newStream 

        newStream.isSorted = True
        return newStream
    
    sorted = property(_getSorted)        

    def _getFlat(self):
        '''
        returns a new Stream where no elements nest within other elements
        
        >>> s = Stream()
        >>> s.repeatInsert(note.Note("C#"), [0, 2, 4])
        >>> s.repeatInsert(note.Note("D-"), [1, 3, 5])
        >>> s.isSorted
        False
        >>> g = ""
        >>> for myElement in s:
        ...    g += "%s: %s; " % (myElement.offset, myElement.name)
        >>> g
        '0.0: C#; 2.0: C#; 4.0: C#; 1.0: D-; 3.0: D-; 5.0: D-; '
        >>> y = s.sorted
        >>> y.isSorted
        True
        >>> g = ""
        >>> for myElement in y:
        ...    g += "%s: %s; " % (myElement.offset, myElement.name)
        >>> g
        '0.0: C#; 1.0: D-; 2.0: C#; 3.0: D-; 4.0: C#; 5.0: D-; '

        >>> q = Stream()
        >>> for i in range(5):
        ...   p = Stream()
        ...   p.repeatInsert(music21.Music21Object(), range(5))
        ...   q.insert(i * 10, p) 
        >>> len(q)
        5
        >>> qf = q.flat
        >>> len(qf)        
        25
        >>> qf[24].offset
        44.0

        
        >>> r = Stream()
        >>> for j in range(5):
        ...   q = Stream()
        ...   for i in range(5):
        ...      p = Stream()
        ...      p.repeatInsert(music21.Music21Object(), range(5))
        ...      q.insert(i * 10, p) 
        ...   r.insert(j * 100, q)
        >>> len(r)
        5
        >>> len(r.flat)
        125
        >>> r.flat[124].offset
        444.0
        '''
        return self._getFlatOrSemiFlat(retainContainers = False)

    flat = property(_getFlat)

    def _getSemiFlat(self):
## does not yet work (nor same for flat above in part because .copy() does not eliminate the cache...
#        if not self._cache['semiflat']:
#            self._cache['semiflat'] = self._getFlatOrSemiFlat(retainContainers = True)
#        return self._cache['semiflat']

        return self._getFlatOrSemiFlat(retainContainers = True)

    semiFlat = property(_getSemiFlat)
        
    def _getFlatOrSemiFlat(self, retainContainers):
        # this copy will have a shared locations object
        newStream = copy.copy(self)

        newStream._elements = []
        newStream._elementsChanged()

        for myEl in self.elements:
            # check for stream instance instead
            if hasattr(myEl, "elements"): # recurse time:
                if retainContainers == True: ## semiFlat
                    newOffset = myEl.locations.getOffsetBySite(self)
                    newStream.insert(
                        myEl.locations.getOffsetBySite(self), myEl)
                    recurseStream = myEl.semiFlat
                else:
                    recurseStream = myEl.flat
                
                recurseStreamOffset = myEl.locations.getOffsetBySite(self)
                #environLocal.printDebug("recurseStreamOffset: " + str(myEl.id) + " " + str(recurseStreamOffset))
                
                for subEl in recurseStream:
                    oldOffset = subEl.locations.getOffsetBySite(recurseStream)
                    newOffset = oldOffset + recurseStreamOffset
                    #environLocal.printDebug("newOffset: " + str(subEl.id) + " " + str(newOffset))
                    newStream.insert(newOffset, subEl)
            
            else:
                newStream.insert(
                    myEl.locations.getOffsetBySite(self), myEl)

        newStream.isFlat = True
        newStream.flattenedRepresentationOf = self #common.wrapWeakref(self)
        return newStream
    

    #---------------------------------------------------------------------------
    # duration and offset methods and properties
    
    def _getHighestOffset(self):
        '''
        >>> p = Stream()
        >>> p.repeatInsert(note.Note("C"), range(5))
        >>> p.highestOffset
        4.0
        '''
        if self._cache["HighestOffset"] is not None:
            pass # return cache unaltered
        elif len(self.elements) == 0:
            self._cache["HighestOffset"] = 0.0
        elif self.isSorted is True:
            lastEl = self.elements[-1]
            self._cache["HighestOffset"] = lastEl.offset 
        else: # iterate through all elements
            max = None
            for thisElement in self.elements:
                elEndTime = None
                elEndTime = thisElement.offset
                if max is None or elEndTime > max :
                    max = elEndTime
            self._cache["HighestOffset"] = max
        return self._cache["HighestOffset"]

    highestOffset = property(_getHighestOffset, doc='''
        Get start time of element with the highest offset in the Stream

        >>> stream1 = Stream()
        >>> for x in [3, 4]:
        ...     n = note.Note('G#')
        ...     n.offset = x * 3.0
        ...     stream1.insert(n)
        >>> stream1.highestOffset
        12.0

        ''')

    def _getHighestTime(self):
        '''The largest offset plus duration.

        >>> n = note.Note('A-')
        >>> n.quarterLength = 3
        >>> p1 = Stream()
        >>> p1.repeatInsert(n, [0, 1, 2, 3, 4])
        >>> p1.highestTime # 4 + 3
        7.0
        
        >>> q = Stream()
        >>> for i in [20, 0, 10, 30, 40]:
        ...    p = Stream()
        ...    p.repeatInsert(n, [0, 1, 2, 3, 4])
        ...    q.insert(i, p) # insert out of order
        >>> len(q.flat)
        25
        >>> q.highestTime # this works b/c the component Stream has an duration
        47.0
        >>> r = q.flat
        
        Make sure that the cache really is empty
        >>> r._cache['HighestTime']
        >>> r.highestTime # 44 + 3
        47.0
        '''

        if self._cache["HighestTime"] is not None:
            pass # return cache unaltered
        elif len(self.elements) == 0:
            self._cache["HighestTime"] = 0.0
        elif self.isSorted is True:
            lastEl = self.elements[-1]
            if hasattr(lastEl, "duration") and hasattr(lastEl.duration, "quarterLength"):
                #environLocal.printDebug([lastEl.offset,
                #         lastEl.offsetlastEl.duration.quarterLength])
                self._cache["HighestTime"] = lastEl.getOffsetBySite(self) + lastEl.duration.quarterLength
            else:
                self._cache["HighestTime"] = lastEl.getOffsetBySite(self)
        else:
            max = None
            for thisElement in self:
                elEndTime = None
                if hasattr(thisElement, "duration") and hasattr(thisElement.duration, "quarterLength"):
                    elEndTime = thisElement.getOffsetBySite(self) + thisElement.duration.quarterLength
                else:
                    elEndTime = thisElement.getOffsetBySite(self)
                if max is None or elEndTime > max :
                    max = elEndTime
            self._cache["HighestTime"] = max

        return self._cache["HighestTime"]

    
    highestTime = property(_getHighestTime, doc='''
        returns the max(el.offset + el.duration.quarterLength) over all elements,
        usually representing the last "release" in the Stream.

        The duration of a Stream is usually equal to the highestTime expressed as a Duration object, 
        but can be set separately.  See below.
        ''')




    
    def _getLowestOffset(self):
        '''
        >>> p = Stream()
        >>> p.repeatInsert(None, range(5))
        >>> q = Stream()
        >>> q.repeatInsert(p, range(0,50,10))
        >>> len(q.flat)        
        25
        >>> q.lowestOffset
        0.0
        >>> r = Stream()
        >>> r.repeatInsert(q, range(97, 500, 100))
        >>> len(r.flat)
        125
        >>> r.lowestOffset
        97.0
        '''
        if self._cache["LowestOffset"] is not None:
            pass # return cache unaltered
        elif len(self.elements) == 0:
            self._cache["LowestOffset"] = 0.0
        elif self.isSorted is True:
            firstEl = self.elements[0]
            self._cache["LowestOffset"] = firstEl.offset 
        else: # iterate through all elements
            min = None
            for thisElement in self.elements:
                elStartTime = None
                elStartTime = thisElement.offset
                if min is None or elStartTime < min :
                    min = elStartTime
            self._cache["LowestOffset"] = min
        return self._cache["LowestOffset"]

    lowestOffset = property(_getLowestOffset, doc='''
        Get start time of element with the lowest offset in the Stream

        >>> stream1 = Stream()
        >>> stream1.lowestOffset
        0.0
        >>> for x in range(3,5):
        ...     n = note.Note('G#')
        ...     n.offset = x * 3.0
        ...     stream1.insert(n)
        ...
        >>> stream1.lowestOffset
        9.0

        ''')

    def _getDuration(self):
        '''
        Gets the duration of the ElementWrapper (if separately set), but
        normal returns the duration of the component object if available, otherwise
        returns None.

        '''

        if self._unlinkedDuration is not None:
            return self._unlinkedDuration
        elif self._cache["Duration"] is not None:
            return self._cache["Duration"]
        else:
            self._cache["Duration"] = duration.Duration()
            self._cache["Duration"].quarterLength = self.highestTime
            return self._cache["Duration"]



    def _setDuration(self, durationObj):
        '''
        Set the total duration of the Stream independently of the highestTime  
        of the stream.  Useful to define the scope of the stream as independent
        of its constituted elements.
        
        If set to None, then the default behavior of computing automatically from highestTime is reestablished.
        '''
        if (isinstance(durationObj, music21.duration.DurationCommon)):
            self._unlinkedDuration = durationObj
        elif (durationObj is None):
            self._unlinkedDuration = None
        else:
            # need to permit Duration object assignment here
            raise Exception, 'this must be a Duration object, not %s' % durationObj

    duration = property(_getDuration, _setDuration, doc='''
    Returns the total duration of the Stream, from the beginning of the stream until the end of the final element.
    May be set independently by supplying a Duration object.

    >>> a = Stream()
    >>> q = note.QuarterNote()
    >>> a.repeatInsert(q, [0,1,2,3])
    >>> a.highestOffset
    3.0
    >>> a.highestTime
    4.0
    >>> a.duration.quarterLength
    4.0
    
    >>> # Advanced usage: overriding the duration
    >>> newDuration = duration.Duration("half")
    >>> newDuration.quarterLength
    2.0

    >>> a.duration = newDuration
    >>> a.duration.quarterLength
    2.0
    >>> a.highestTime # unchanged
    4.0
    ''')

    #---------------------------------------------------------------------------
    def _getLily(self):
        '''Returns the stream translated into Lilypond format.'''
        if self._overriddenLily is not None:
            return self._overriddenLily
        elif self._cache["lily"] is not None:
            return self._cache["lily"]
        
        lilyout = u" { "
#        if self.showTimeSignature is not False and self.timeSignature is not None:
#            lilyout += self.timeSignature.lily
    
        for thisObject in self.elements:
            if hasattr(thisObject, "startTransparency") and thisObject.startTransparency is True:
                lilyout += lilyModule.TRANSPARENCY_START

            if hasattr(thisObject.duration, "tuplets") and thisObject.duration.tuplets:
                if thisObject.duration.tuplets[0].type == "start":
                    numerator = str(int(thisObject.duration.tuplets[0].tupletNormal[0]))
                    denominator = str(int(thisObject.duration.tuplets[0].tupletActual[0]))
                    lilyout += "\\times " + numerator + "/" + denominator + " {"
                    ### TODO-- should get the actual ratio not assume that the
                    ### type of top and bottom are the same
            if hasattr(thisObject, "lily"):
                lilyout += unicode(thisObject.lily)
                lilyout += " "
            else:
                pass
            
            if hasattr(thisObject.duration, "tuplets") and thisObject.duration.tuplets:
                if thisObject.duration.tuplets[0].type == "stop":
                    lilyout = lilyout.rstrip()
                    lilyout += "} "

            if hasattr(thisObject, "stopTransparency") and thisObject.stopTransparency == True:
                lilyout += lilyModule.TRANSPARENCY_STOP
        
        lilyout += " } "
        lilyObj = lilyModule.LilyString(lilyout)
        self._cache["lily"] = lilyObj
        return lilyObj

    def _setLily(self, value):
        '''Sets the Lilypond output for the stream. Overrides what is obtained
        from get_lily.'''
        self._overriddenLily = value
        self._cache["lily"] = None

    lily = property(_getLily, _setLily)



    def _getMXPart(self, instObj=None, meterStream=None, refStream=None):
        '''If there are Measures within this stream, use them to create and
        return an MX Part and ScorePart. 

        meterStream can be provided to provide a template within which
        these events are positioned; this is necessary for handling
        cases where one part is shorter than another. 
        '''
        #environLocal.printDebug(['calling Stream._getMXPart'])

        if instObj == None:
            # see if an instrument is defined in this or a parent stream
            instObj = self.getInstrument()

        # instruments are defined here
        mxScorePart = musicxmlMod.ScorePart()
        mxScorePart.set('partName', instObj.partName)
        mxScorePart.set('id', instObj.partId)

        mxPart = musicxmlMod.Part()
        mxPart.setDefaults()
        mxPart.set('id', instObj.partId) # need to set id

        # get a stream of measures
        # if flat is used here, the Measure is not obtained
        # may need to be semi flat?
        measureStream = self.getElementsByClass(Measure)
        if len(measureStream) == 0:
            # try to add measures if none defined
            # returns a new stream w/ new Measures but the same objects
            measureStream = self.makeMeasures(meterStream, refStream)
            #measureStream = makeTies(measureStream, meterStream)
            measureStream = measureStream.makeTies(meterStream)

            measureStream = measureStream.makeBeams()
            #measureStream = makeBeams(measureStream)

            if len(measureStream) == 0:            
                raise StreamException('no measures found in stream with %s elements' % (self.__len__()))
            environLocal.printDebug(['created measures:', len(measureStream)])
        else: # there are measures
            # this will override beams already set
            pass
            # measureStream = makeBeams(measureStream)

        # for each measure, call .mx to get the musicxml representation
        for obj in measureStream:
            mxPart.append(obj.mx)

        # mxScorePart contains mxInstrument
        return mxScorePart, mxPart


    def _getMX(self):
        '''Create and return a musicxml score.

        >>> n1 = note.Note()
        >>> measure1 = Measure()
        >>> measure1.insert(n1)
        >>> str1 = Stream()
        >>> str1.insert(measure1)
        >>> mxScore = str1.mx
        '''
        #environLocal.printDebug('calling Stream._getMX')

        mxComponents = []
        instList = []
        multiPart = False
        meterStream = self.getTimeSignatures() # get from containter first

        # we need independent sub-stream elements to shift in presentation
        highestTime = 0

        for obj in self:
            # if obj is a Part, we have mutli-parts
            if isinstance(obj, Part):
                multiPart = True
                break # only need one
            # if components are Measures, self is a part
            elif isinstance(obj, Measure):
                multiPart = False
                break # only need one
            # if components are streams of Notes or Measures, 
            # than assume this is like a part
            elif isinstance(obj, Stream) and (len(obj.measures) > 0 
                or len(obj.notes) > 0):
                multiPart = True
                break # only need one

        if multiPart:
            # need to edit streams contained within streams
            # must repack into a new stream at each step
            midStream = Stream()
            finalStream = Stream()
            partStream = copy.copy(self)

            for obj in partStream.getElementsByClass(Stream):
                # need to copy element here
                obj.transferOffsetToElements() # apply this streams offset to elements

                ts = obj.getTimeSignatures()
                # the longest meterStream is used as the meterStream for all parts
                if len(ts) > meterStream:
                    meterStream = ts
                ht = obj.highestTime
                if ht > highestTime:
                    highestTime = ht
                midStream.insert(obj)

            refStream = Stream()
            refStream.insert(0, True) # placeholder at 0
            refStream.insert(highestTime, True) 

            # would like to do something like this but cannot
            # replace object inside of the stream
            for obj in midStream.getElementsByClass(Stream):
                obj = obj.makeRests(refStream)
                finalStream.insert(obj)

            environLocal.printDebug(['handling multi-part Stream of length:',
                                    len(finalStream)])
            count = 0
            for obj in finalStream:
                count += 1
                if count > len(finalStream):
                    raise StreamException('infinite stream encountered')

                # only things that can be treated as parts are in finalStream
                inst = obj.getInstrument()
                instIdList = [x.partId for x in instList]
                if inst.partId in instIdList: # must have unique ids 
                    inst.partIdRandomize() # set new random id
                instList.append(inst)

                mxComponents.append(obj._getMXPart(inst, meterStream,
                                refStream))

        else: # assume this is the only part
            environLocal.printDebug('handling single-part Stream')
            # if no instrument is provided it will be obtained through self
            # when _getMxPart is called
            mxComponents.append(self._getMXPart(None, meterStream))


        # create score and part list
        mxPartList = musicxmlMod.PartList()
        mxIdentification = musicxmlMod.Identification()
        mxIdentification.setDefaults() # will create a composer
        mxScore = musicxmlMod.Score()
        mxScore.setDefaults()
        mxScore.set('partList', mxPartList)
        mxScore.set('identification', mxIdentification)

        for mxScorePart, mxPart in mxComponents:
            mxPartList.append(mxScorePart)
            mxScore.append(mxPart)

        return mxScore


    def _setMXPart(self, mxScore, partId):
        '''Load a part given an mxScore and a part name.
        '''
        #environLocal.printDebug(['calling Stream._setMXPart'])

        mxPart = mxScore.getPart(partId)
        mxInstrument = mxScore.getInstrument(partId)

        # create a new music21 instrument
        instrumentObj = instrument.Instrument()
        if mxInstrument != None:
            instrumentObj.mx = mxInstrument

        # add part id as group
        instrumentObj.groups.append(partId)

        streamPart = Part() # create a part instance for each part
        streamPart.insert(instrumentObj) # add instrument at zero offset

        # offset is in quarter note length
        oMeasure = 0
        lastTimeSignature = None
        for mxMeasure in mxPart:
            # create a music21 measure and then assign to mx attribute
            m = Measure()
            m.mx = mxMeasure  # assign data into music21 measure 
            if m.timeSignature != None:
                lastTimeSignature = m.timeSignature
            elif lastTimeSignature == None and m.timeSignature == None:
                # if no time sigature is defined, need to get a default
                ts = meter.TimeSignature()
                ts.load('%s/%s' % (defaults.meterNumerator, 
                                   defaults.meterDenominatorBeatType))
                lastTimeSignature = ts
            # add measure to stream at current offset for this measure
            streamPart.insert(oMeasure, m)
            # increment measure offset for next time around
            oMeasure += lastTimeSignature.barDuration.quarterLength 

        streamPart.addGroupForElements(partId) # set group for components 
        streamPart.groups.append(partId) # set group for stream itself

        # add to this stream
        # this assumes all start at the same place
        self.insert(0, streamPart)


    def _setMX(self, mxScore):
        '''Given an mxScore, build into this stream
        '''
        partNames = mxScore.getPartNames().keys()
        partNames.sort()
        for partName in partNames: # part names are part ids
            self._setMXPart(mxScore, partName)

    mx = property(_getMX, _setMX)
        


    def _getMusicXML(self):
        '''Provide a complete MusicXM: representation. 
        '''
        mxScore = self._getMX()
        return mxScore.xmlStr()

    def _setMusicXML(self, mxNote):
        '''
        '''
        pass

    musicxml = property(_getMusicXML, _setMusicXML)


    #------------ interval routines --------------------------------------------
    def getNotes(self):
        '''Return all Note, Chord, Rest, etc. objects in a Stream()

        >>> s1 = Stream()
        >>> c = chord.Chord(['a', 'b'])
        >>> s1.append(c)
        >>> s2 = s1.getNotes()
        >>> len(s2) == 1
        True
        '''
        # note: class names must be provided in one argument as a list
        return self.getElementsByClass([note.GeneralNote, chord.Chord])

    notes = property(getNotes)

    def getPitches(self):
        '''
        Return all pitches found in any element in the stream as a list

        (since Pitches have no duration, it's a list not a stream)
        '''  
        returnPitches = []
        for thisEl in self.elements:
            if hasattr(thisEl, "pitch"):
                returnPitches.append(thisEl.pitch)
            elif hasattr(thisEl, "pitches"):
                for thisPitch in thisEl.pitches:
                    returnPitches.append(thisPitch)
        return returnPitches
    
    pitches = property(getPitches)

    
    def findConsecutiveNotes(self, skipRests = False, skipChords = False, skipUnisons = False, 
                               skipGaps = False, getOverlaps = False, noNone = False, **keywords):
        '''
        Returns a list of consecutive *pitched* Notes in a Stream.  A single "None" is placed in the list 
        at any point there is a discontinuity (such as if there is a rest between two pitches).
        The method is used by melodicIntervals.
        
        How to determine consecutive pitches is a little tricky and there are many options.  

        skipUnison uses the midi-note value (.ps) to determine unisons, so enharmonic transitions (F# -> Gb) are
        also skipped if skipUnisons is true.  We believe that this is the most common usage.  However, because
        of this, you cannot completely be sure that the x.findConsecutiveNotes() - x.findConsecutiveNotes(skipUnisons = True)
        will give you the number of P1s in the piece, because there could be d2's in there as well.
        
        N.B. for chords, currently, only the first pitch is tested for unison.  this is a bug TODO: FIX
        
        See Test.testFindConsecutiveNotes() for usage details.
        
        (**keywords is there so that other methods that pass along dicts to findConsecutiveNotes don't have to remove 
        their own args)
        '''
        sortedSelf = self.sorted
        returnList = []
        lastStart = 0.0
        lastEnd = 0.0
        lastWasNone = False
        lastPitch = None
        for el in sortedSelf.elements:
            if lastWasNone is False and skipGaps is False and el.offset > lastEnd:
                if not noNone:
                    returnList.append(None)
                    lastWasNone = True
            if hasattr(el, "pitch"):
                if skipUnisons is False or isinstance(lastPitch, list) or lastPitch is None or el.pitch.ps != lastPitch.ps:
                    if getOverlaps is True or el.offset >= lastEnd:
                        if el.offset >= lastEnd:  # is not an overlap...
                            lastStart = el.offset
                            if hasattr(el, "duration"):
                                lastEnd = lastStart + el.duration.quarterLength
                            else:
                                lastEnd = lastStart
                            lastWasNone = False
                            lastPitch = el.pitch
                        else:  # do not update anything for overlaps
                            pass 

                        returnList.append(el)

            elif hasattr(el, "pitches"):
                if skipChords is True:
                    if lastWasNone is False:
                        if not noNone:
                            returnList.append(None)
                            lastWasNone = True
                            lastPitch = None
                else:
                    if (skipUnisons is True and isinstance(lastPitch, list) and
                        el.pitches[0].ps == lastPitch[0].ps):
                        pass
                    else:
                        if getOverlaps is True or el.offset >= lastEnd:
                            if el.offset >= lastEnd:  # is not an overlap...
                                lastStart = el.offset
                                if hasattr(el, "duration"):
                                    lastEnd = lastStart + el.duration.quarterLength
                                else:
                                    lastEnd = lastStart
            
                                lastPitch = el.pitches
                                lastWasNone = False 

                            else:  # do not update anything for overlaps
                                pass 
                            returnList.append(el)

            elif skipRests is False and isinstance(el, note.Rest) and lastWasNone is False:
                if noNone is False:
                    returnList.append(None)
                    lastWasNone = True
                    lastPitch = None
            elif skipRests is True and isinstance(el, note.Rest):
                lastEnd = el.offset + el.duration.quarterLength
        
        if lastWasNone is True:
            returnList.pop()
        return returnList
    
    def melodicIntervals(self, *skipArgs, **skipKeywords):
        '''
        returns a Stream of intervals between Notes (and by default, Chords) that follow each other in a stream.
        the offset of the Interval is the offset of the beginning of the interval (if two notes are adjacent, 
        then it is equal to the offset of the second note)
        
        see Stream.findConsecutiveNotes for a discussion of what consecutive notes mean, and which keywords 
        are allowed.
        
        The interval between a Note and a Chord (or between two chords) is the interval between pitches[0].
        For more complex interval calculations, run findConsecutiveNotes and then use generateInterval
        '''
        returnList = self.findConsecutiveNotes(**skipKeywords)
        returnStream = self.__class__()


    #---------------------------------------------------------------------------
    def _getDurSpan(self, flatStream):
        '''Given elementsSorted, create a list of parallel
        values that represent dur spans, or start and end times.

        >>> a = Stream()
        >>> a.repeatInsert(note.HalfNote(), range(5))
        >>> a._getDurSpan(a.flat)
        [(0.0, 2.0), (1.0, 3.0), (2.0, 4.0), (3.0, 5.0), (4.0, 6.0)]
        '''
        post = []        
        for i in range(len(flatStream)):
            element = flatStream[i]
            if element.duration == None:
                durSpan = (element.offset, element.offset)
            else:
                dur = element.duration.quarterLength
                durSpan = (element.offset, element.offset+dur)
            post.append(durSpan)
        # assume this is already sorted 
        # index found here will be the same as elementsSorted
        return post


    def _durSpanOverlap(self, a, b, includeCoincidentBoundaries=False):
        '''
        Compare two durSpans and find overlaps; optionally, 
        include coincident boundaries. a and b are sorted to permit any ordering.

        If an element ends at 3.0 and another starts at 3.0, this may or may not
        be considered an overlap. The includeCoincidentEnds parameter determines
        this behaviour, where ending and starting 3.0 being a type of overlap
        is set by the includeCoincidentBoundaries being True. 

        >>> a = Stream()
        >>> a._durSpanOverlap([0, 10], [11, 12], False)
        False
        >>> a._durSpanOverlap([11, 12], [0, 10], False)
        False
        >>> a._durSpanOverlap([0, 3], [3, 6], False)
        False
        >>> a._durSpanOverlap([0, 3], [3, 6], True)
        True
        '''

        durSpans = [a, b]
        # sorting will ensure that leading numbers are ordered from low to high
        durSpans.sort() 
        found = False

        if includeCoincidentBoundaries:
            # if the start of b is before the end of a
            if durSpans[1][0] <= durSpans[0][1]:   
                found = True
        else: # do not include coincident boundaries
            if durSpans[1][0] < durSpans[0][1]:   
                found = True
        return found



    def _findLayering(self, flatStream, includeDurationless=True,
                   includeCoincidentBoundaries=False):
        '''Find any elements in an elementsSorted list that have simultaneities 
        or durations that cause overlaps.
        
        Returns two lists. Each list contains a list for each element in 
        elementsSorted. If that elements has overlaps or simultaneities, 
        all index values that match are included in that list. 
        
        See testOverlaps, in unit tests, for examples. 
        
        
        '''
        flatStream = flatStream.sorted
        # these may not be sorted
        durSpanSorted = self._getDurSpan(flatStream)

        # create a list with an entry for each element
        # in each entry, provide indices of all other elements that overalap
        overlapMap = [[] for i in range(len(durSpanSorted))]
        # create a list of keys for events that start at the same time
        simultaneityMap = [[] for i in range(len(durSpanSorted))]
        
        for i in range(len(durSpanSorted)):
            src = durSpanSorted[i]
            # second entry is duration
            if not includeDurationless and flatStream[i].duration == None: 
                continue
            # compare to all past and following durations
            for j in range(len(durSpanSorted)):
                if j == i: continue # do not compare to self
                dst = durSpanSorted[j]
                # print src, dst, self._durSpanOverlap(src, dst, includeCoincidentBoundaries)
        
                if src[0] == dst[0]: # if start times are the same
                    simultaneityMap[i].append(j)
        
                if self._durSpanOverlap(src, dst, includeCoincidentBoundaries):
                    overlapMap[i].append(j)
        
        return simultaneityMap, overlapMap



    def _consolidateLayering(self, flatStream, map):
        '''
        Given elementsSorted and a map of equal length with lists of 
        index values that meet a given condition (overlap or simultaneities),
        organize into a dictionary by the relevant or first offset
        '''
        flatStream = flatStream.sorted

        if len(map) != len(flatStream):
            raise StreamException('map must be the same length as flatStream')

        post = {}
        for i in range(len(map)):
            # print 'examining i:', i
            indices = map[i]
            if len(indices) > 0: 
                srcOffset = flatStream[i].offset
                srcElementObj = flatStream[i]
                dstOffset = None
                # print 'found indices', indices
                # check indices
                for j in indices: # indices of other elements tt overlap
                    elementObj = flatStream[j]

                    # check if this object has been stored anywhere yet
                    # if so, use the offset of where it was stored to 
                    # to store the src element below
                    store = True
                    for key in post.keys():
                        if elementObj in post[key]:
                            store = False
                            dstOffset = key
                            break
                    if dstOffset == None:
                        dstOffset = srcOffset
                    if store:
                        # print 'storing offset', dstOffset
                        if dstOffset not in post.keys():
                            post[dstOffset] = [] # create dictionary entry
                        post[dstOffset].append(elementObj)

                # check if this object has been stored anywhere yet
                store = True
                for key in post.keys():
                    if srcElementObj in post[key]:
                        store = False
                        break
                # dst offset may have been set when looking at indices
                if store:
                    if dstOffset == None:
                        dstOffset = srcOffset
                    if dstOffset not in post.keys():
                        post[dstOffset] = [] # create dictionary entry
                    # print 'storing offset', dstOffset
                    post[dstOffset].append(srcElementObj)
                    # print post
        return post



    def findGaps(self):
        '''
        returns either (1) a Stream containing Elements (that wrap the None object)
        whose offsets and durations are the length of gaps in the Stream
        or (2) None if there are no gaps.
        
        N.B. there may be gaps in the flattened representation of the stream
        but not in the unflattened.  Hence why "isSequence" calls self.flat.isGapless
        '''
        if self.cache["GapStream"]:
            return self.cache["GapStream"]
        
        sortedElements = self.sorted.elements
        gapStream = Stream()
        highestCurrentEndTime = 0
        for thisElement in sortedElements:
            if thisElement.offset > highestCurrentEndTime:
                gapElement = music21.ElementWrapper(obj = None, offset = highestCurrentEndTime)
                gapElement.duration = duration.Duration()
                gapElement.duration.quarterLength = thisElement.offset - highestCurrentEndTime
                gapStream.insert(gapElement)
            highestCurrentEndTime = max(highestCurrentEndTime, thisElement.offset + thisElement.duration.quarterLength)

        if len(gapStream) == 0:
            return None
        else:
            self.cache["GapStream"] = gapStream
            return gapStream

    def _getIsGapless(self):
        if self._cache["isGapless"] is not None:
            return self._cache["isGapless"]
        else:
            if self.findGaps() is None:
                self._cache["Gapless"] = True
                return True
            else:
                self._cache["Gapless"] = False
                return False
            
    isGapless = property(_getIsGapless)
            
    def getSimultaneous(self, includeDurationless=True):
        '''Find and return any elements that start at the same time. 
        >>> stream1 = Stream()
        >>> for x in range(4):
        ...     n = note.Note('G#')
        ...     n.offset = x * 0
        ...     stream1.insert(n)
        ...
        >>> b = stream1.getSimultaneous()
        >>> len(b[0]) == 4
        True
        >>> stream2 = Stream()
        >>> for x in range(4):
        ...     n = note.Note('G#')
        ...     n.offset = x * 3
        ...     stream2.insert(n)
        ...
        >>> d = stream2.getSimultaneous()
        >>> len(d) == 0
        True
        '''
#        checkOverlap = False
        elementsSorted = self.flat.sorted
        simultaneityMap, overlapMap = self._findLayering(elementsSorted, 
                                                    includeDurationless)
        
        return self._consolidateLayering(elementsSorted, simultaneityMap)


    def getOverlaps(self, includeDurationless=True,
                     includeCoincidentBoundaries=False):
        '''
        Find any elements that overlap. Overlaping might include elements
        that have no duration but that are simultaneous. 
        Whether elements with None durations are included is determined by includeDurationless.
        
        CHRIS: What does this return? and how can someone use this?
        
        This example demonstrates end-joing overlaps: there are four quarter notes each
        following each other. Whether or not these count as overlaps
        is determined by the includeCoincidentBoundaries parameter. 

        >>> a = Stream()
        >>> for x in range(4):
        ...     n = note.Note('G#')
        ...     n.duration = duration.Duration('quarter')
        ...     n.offset = x * 1
        ...     a.insert(n)
        ...
        >>> d = a.getOverlaps(True, False) 
        >>> len(d)
        0
        >>> d = a.getOverlaps(True, True) # including coincident boundaries
        >>> len(d)
        1
        >>> len(d[0])
        4
        >>> a = Stream()
        >>> for x in [0,0,0,0,13,13,13]:
        ...     n = note.Note('G#')
        ...     n.duration = duration.Duration('half')
        ...     n.offset = x
        ...     a.insert(n)
        ...
        >>> d = a.getOverlaps() 
        >>> len(d[0])
        4
        >>> len(d[13])
        3
        >>> a = Stream()
        >>> for x in [0,0,0,0,3,3,3]:
        ...     n = note.Note('G#')
        ...     n.duration = duration.Duration('whole')
        ...     n.offset = x
        ...     a.insert(n)
        ...
        >>> # default is to not include coincident boundaries
        >>> d = a.getOverlaps() 
        >>> len(d[0])
        7
        '''
        checkSimultaneity = False
        checkOverlap = True
        elementsSorted = self.flat.sorted
        simultaneityMap, overlapMap = self._findLayering(elementsSorted, 
                                includeDurationless, includeCoincidentBoundaries)
        return self._consolidateLayering(elementsSorted, overlapMap)



    def isSequence(self, includeDurationless=True, 
                        includeCoincidentBoundaries=False):
        '''A stream is a sequence if it has no overlaps.

        TODO: check that co-incident boundaries are properly handled
        >>> a = Stream()
        >>> for x in [0,0,0,0,3,3,3]:
        ...     n = note.Note('G#')
        ...     n.duration = duration.Duration('whole')
        ...     n.offset = x * 1
        ...     a.insert(n)
        ...
        >>> a.isSequence()
        False
        '''
        elementsSorted = self.flat.sorted
        simultaneityMap, overlapMap = self._findLayering(elementsSorted, 
                                includeDurationless, includeCoincidentBoundaries)
        post = True
        for indexList in overlapMap:
            if len(indexList) > 0:
                post = False
                break       
        return post





#-------------------------------------------------------------------------------
class Measure(Stream):
    '''A representation of a Measure organized as a Stream. 

    All properties of a Measure that are Music21 objects are found as part of 
    the Stream's elements. 
    '''
    def __init__(self, *args, **keywords):
        Stream.__init__(self, *args, **keywords)

        # clef and timeSignature is defined as a property below

        self.timeSignatureIsNew = False
        self.clefIsNew = False

        self.filled = False
        self.measureNumber = 0   # 0 means undefined or pickup
        self.measureNumberSuffix = None # for measure 14a would be "a"


        # inherits from prev measure or is default for group
        # inherits from next measure or is default for group

        # these attrbute will, ultimate, be obtained form .elements
        self.leftbarline = None  
        self.rightbarline = None 

        # for display is overridden by next measure\'s leftbarline if that is not None and
        # the two measures are on the same system


        # TODO: it does not seem that Stream objects should be stored
        # as attributes in another stream: these elements will not be obtained
        # when this stream is flattend or other stream operations
        # are performed. it seems that all Streams, base music21 objects, and
        # Elements should be stored on the Stream's _elements list. 

        #self.internalbarlines = Stream()
        # "measure expressions" that are attached to nowhere in particular
        #self.timeIndependentDirections = Stream() 
        # list of times at which Directions take place.
        #self.timeDependentDirectionsTime = Stream() 
        # should be sorted always.
        # list of Directions that happen at a certain time, 
        # keep indices together
        #self.timeDependentDirections = Stream() 


    def addRepeat(self):
        # TODO: write
        pass

    def addTimeDependentDirection(self, time, direction):
        # TODO: write
        pass

    def addRightBarline(self, blStyle = None):
        self.rightbarline = measure.Barline(blStyle)
        return self.rightbarline
    
    def addLeftBarline(self, blStyle = None):
        self.leftbarline = measure.Barline(blStyle)
        return self.leftbarline
    
    def measureNumberWithSuffix(self):
        if self.measureNumberSuffix:
            return str(self.measureNumber) + self.measureNumberSuffix
        else:
            return str(self.measureNumber)
    
    def __repr__(self):
        return "<music21.stream.%s %s offset=%s>" % \
            (self.__class__.__name__, self.measureNumberWithSuffix(), self.offset)
        

    #---------------------------------------------------------------------------
    # Music21Objects are stored in the Stream's elements list 
    # properties are provided to store and access these attribute

    def _getClef(self):
        '''
        >>> a = Measure()
        >>> a.clef = clef.TrebleClef()
        >>> a.clef.sign    # clef is an element
        'G'
        '''
        # TODO: perhaps sort by priority?
        clefList = self.getElementsByClass(clef.Clef)
        # only return cleff that has a zero offset
        clefList = clefList.getElementsByOffset(0,0)
        if len(clefList) == 0:
            return None
        else:
            return clefList[0]    
    
    def _setClef(self, clefObj):
        '''
        >>> a = Measure()
        >>> a.clef = clef.TrebleClef()
        >>> a.clef.sign    # clef is an element
        'G'
        >>> a.clef = clef.BassClef()
        >>> a.clef.sign
        'F'
        '''
        oldClef = self._getClef()
        if oldClef != None:
            environLocal.printDebug(['removing clef', oldClef])
            junk = self.pop(self.index(oldClef))
        self.insert(0, clefObj)

    clef = property(_getClef, _setClef)    


    def _getTimeSignature(self):
        '''
        >>> a = Measure()
        >>> a.timeSignature = meter.TimeSignature('2/4')
        >>> a.timeSignature.numerator, a.timeSignature.denominator 
        (2, 4)
        '''
        # there could be more than one
        tsList = self.getElementsByClass(meter.TimeSignature)
        # only return ts that has a zero offset
        tsList = tsList.getElementsByOffset(0,0)
        if len(tsList) == 0:
            return None
        else:
            return tsList[0]    
    
    def _setTimeSignature(self, tsObj):
        '''
        >>> a = Measure()
        >>> a.timeSignature = meter.TimeSignature('5/4')
        >>> a.timeSignature.numerator, a.timeSignature.denominator 
        (5, 4)
        >>> a.timeSignature = meter.TimeSignature('2/8')
        >>> a.timeSignature.numerator, a.timeSignature.denominator 
        (2, 8)
        '''
        oldTimeSignature = self._getTimeSignature()
        if oldTimeSignature != None:
            environLocal.printDebug(['removing ts', oldTimeSignature])
            junk = self.pop(self.index(oldTimeSignature))
        self.insert(0, tsObj)

    timeSignature = property(_getTimeSignature, _setTimeSignature)   

    #---------------------------------------------------------------------------
    def _getMX(self):
        '''Return a musicxml Measure, populated with notes, chords, rests
        and a musixcml Attributes, populated with time, meter, key, etc

        >>> a = note.Note()
        >>> a.quarterLength = 4
        >>> b = Measure()
        >>> b.insert(0, a)
        >>> len(b) 
        1
        >>> mxMeasure = b.mx
        >>> len(mxMeasure) 
        1
        '''

        mxMeasure = musicxmlMod.Measure()
        mxMeasure.set('number', self.measureNumber)

        # get an empty mxAttributes object
        mxAttributes = musicxmlMod.Attributes()
        # best to only set dvisions here, as clef, time sig, meter are not
        # required for each measure
        mxAttributes.setDefaultDivisions() 

        # may need to look here at the parent, and try to find
        # the clef in the clef last defined in the parent
        if self.clef != None:
            mxAttributes.clefList = [self.clef.mx]
        
        if self.timeSignature != None:
            mxAttributes.timeList = self.timeSignature.mx 

        #mxAttributes.keyList = []
        mxMeasure.set('attributes', mxAttributes)

        #need to handle objects in order when creating musicxml 
        for obj in self.flat:
            if obj.isClass(note.GeneralNote):
                # .mx here returns a lost of notes
                mxMeasure.componentList += obj.mx
            elif obj.isClass(dynamics.Dynamic):
                # returns an mxDirection object
                mxMeasure.append(obj.mx)
        return mxMeasure


    def _setMX(self, mxMeasure):
        '''Given an mxMeasure, create a music21 measure
        '''
        # measure number may be a string and not a number (always?)
        self.measureNumber = mxMeasure.get('number')
        junk = mxMeasure.get('implicit')
        # may not be available; may need to be obtained from 

        mxAttributes = mxMeasure.get('attributes')
        mxAttributesInternal = True
        if mxAttributes == None:    
            # need to keep track of where mxattributessrc is coming from
            mxAttributesInternal = False
            # not all measures have attributes definitions; this
            # gets the last-encountered measure attributes
            mxAttributes = mxMeasure.external['attributes']
            if mxAttributes == None:
                raise StreamException(
                    'no mxAttribues available for this measure')

        # if no time is defined, get the last defined value from external
#         if len(mxAttributes.timeList) == 0:
#             if mxMeasure.external['time'] != None:
#                 mxTimeList = [mxMeasure.external['time']]
#             else:
#                 mxTime = musicxmlMod.Time()
#                 mxTime.setDefaults()
#                 mxTimeList = [mxTime]
#         else:
#             mxTimeList = mxAttributes.timeList

        if mxAttributesInternal and len(mxAttributes.timeList) != 0:
            self.timeSignature = meter.TimeSignature()
            self.timeSignature.mx = mxAttributes.timeList

        # only set clef if it is defined 
        # we must check that attributes are derived from the measure proper
        #environLocal.printDebug(['mxAttriutes clefList', mxAttributes.clefList, 
        #                        mxAttributesInternal])
        if mxAttributesInternal == True and len(mxAttributes.clefList) != 0:
            self.clef = clef.Clef()
            self.clef.mx = mxAttributes.clefList

        # set to zero for each measure
        offsetMeasureNote = 0 # offset of note w/n measure        
        mxNoteList = [] # for chords
        for i in range(len(mxMeasure)):
            mxObj = mxMeasure[i]
            if i < len(mxMeasure)-1:
                mxObjNext = mxMeasure[i+1]
            else:
                mxObjNext = None

            if isinstance(mxObj, musicxmlMod.Note):
                mxNote = mxObj
                if isinstance(mxObjNext, musicxmlMod.Note):
                    mxNoteNext = mxObjNext
                else:
                    mxNoteNext = None
                # the first note of a chord is not identified; only
                # by looking at the next note can we tell if we have a 
                # chord
                if mxNoteNext != None and mxNoteNext.get('chord') == True:
                    if mxNote.get('chord') != True:
                        mxNote.set('chord', True) # set the first as a chord

                if mxNote.get('rest') in [None, False]: # its a note

                    if mxNote.get('chord') == True:
                        mxNoteList.append(mxNote)
                        offsetIncrement = 0
                    else:
                        n = note.Note()
                        n.mx = mxNote
                        self.insert(offsetMeasureNote, n)
                        offsetIncrement = n.quarterLength
                    for mxLyric in mxNote.lyricList:
                        lyricObj = note.Lyric()
                        lyricObj.mx = mxLyric
                        n.lyrics.append(lyricObj)
                    if mxNote.get('notations') != None:
                        for mxObjSub in mxNote.get('notations'):
                            # deal with ornaments, strill, etc
                            pass
                else: # its a rest
                    n = note.Rest()
                    n.mx = mxNote # assign mxNote to rest obj
                    self.insert(offsetMeasureNote, n)            
                    offsetIncrement = n.quarterLength

                # if we we have notes in the note list and the next
                # not either does not exist or is not a chord, we 
                # have a complete chord
                if len(mxNoteList) > 0 and (mxNoteNext == None 
                    or mxNoteNext.get('chord') == False):
                    c = chord.Chord()
                    c.mx = mxNoteList
                    mxNoteList = [] # clear for next chord
                    self.insert(offsetMeasureNote, c)
                    offsetIncrement = c.quarterLength

                # do not need to increment for musicxml chords
                offsetMeasureNote += offsetIncrement

            # load dynamics into measure
            elif isinstance(mxObj, musicxmlMod.Direction):
#                 mxDynamicsFound, mxWedgeFound = self._getMxDynamics(mxObj)
#                 for mxDirection in mxDynamicsFound:
                if mxObj.getDynamicMark() != None:
                    d = dynamics.Dynamic()
                    d.mx = mxObj
                    self.insert(offsetMeasureNote, d)  
                if mxObj.getWedge() != None:
                    w = dynamics.Wedge()
                    w.mx = mxObj     
                    self.insert(offsetMeasureNote, w)  

    mx = property(_getMX, _setMX)    



    def _getMusicXML(self):
        '''Provide a complete MusicXML: representation. 
        '''

        mxMeasure = self._getMX()

        mxPart = musicxmlMod.Part()
        mxPart.setDefaults()
        mxPart.append(mxMeasure) # append measure here


        # see if an instrument is defined in this or a prent stream
        instObj = self.getInstrument()
        mxScorePart = musicxmlMod.ScorePart()
        mxScorePart.set('partName', instObj.partName)
        mxScorePart.set('id', instObj.partId)
        # must set this part to the same id
        mxPart.set('id', instObj.partId)

        mxPartList = musicxmlMod.PartList()
        mxPartList.append(mxScorePart)

        mxIdentification = musicxmlMod.Identification()
        mxIdentification.setDefaults() # will create a composer
        mxScore = musicxmlMod.Score()
        mxScore.setDefaults()
        mxScore.set('partList', mxPartList)
        mxScore.set('identification', mxIdentification)
        mxScore.append(mxPart)

        return mxScore.xmlStr()

    def _setMusicXML(self, mxScore):
        '''
        '''
        pass

    musicxml = property(_getMusicXML, _setMusicXML)

#-------------------------------------------------------------------------------
class Voice(Stream):
    '''
    A Stream subclass for declaring that all the music in the
    stream belongs to a certain "voice" for analysis or display
    purposes.
    
    Note that both Finale's Layers and Voices as concepts are
    considered Voices here.
    '''
    pass

class Part(Stream):
    '''A Stream subclass for designating music that is
    considered a single part.
    
    May be enclosed in a staff (for instance, 2nd and 3rd trombone
    on a single staff), may enclose staves (piano treble and piano bass),
    or may not enclose or be enclosed by a staff (in which case, it
    assumes that this part fits on one staff and shares it with no other
    part
    '''

    def _getLily(self):
        lv = Stream._getLily(self)
        lv2 = lilyModule.LilyString(" \\new Staff " + lv.value)
        return lv2
    
    lily = property(_getLily)

class Staff(Stream):
    '''
    A Stream subclass for designating music on a single staff
    '''
    
    staffLines = 5

class Performer(Stream):
    '''
    A Stream subclass for designating music to be performed by a
    single Performer.  Should only be used when a single performer
    performs on multiple parts.  E.g. Bass Drum and Triangle on separate
    staves performed by one player.

    a Part + changes of Instrument is fine for designating most cases
    where a player changes instrument in a piece.  A part plus staves
    with individual instrument changes could also be a way of designating
    music that is performed by a single performer (see, for instance
    the Piano doubling Celesta part in Lukas Foss's Time Cycle).  The
    Performer Stream-subclass could be useful for analyses of, for instance,
    how 5 percussionists chose to play a piece originally designated for 4
    (or 6) percussionists in the score.
    '''
    pass


class System(Stream):
    '''Totally optional: designation that all the music in this Stream
    belongs in a single system.
    '''
    systemNumber = 0
    systemNumbering = "Score" # or Page; when do system numbers reset?

class Page(Stream):
    '''
    Totally optional: designation that all the music in this Stream
    belongs on a single notated page
    '''
    pageNumber = 0
    
class Score(Stream):
    """A Stream subclass for handling multi-part music.
    
    Absolutely optional (the largest containing Stream in a piece could be
    a generic Stream, or a Part, or a Staff).  And Scores can be
    embedded in other Scores (in fact, our original thought was to call
    this class a Fragment because of this possibility of continuous
    embedding), but we figure that many people will like calling the largest
    container a Score and that this will become a standard.
    """

    def __init__(self, *args, **keywords):
        Stream.__init__(self, *args, **keywords)


    def _getLily(self):
        '''
        returns the lily code for a score.
        '''
        ret = lilyModule.LilyString()
        for thisOffsetPosition in self.groupElementsByOffset():
            if len(thisOffsetPosition) > 1:
                ret += " << "
                for thisSubElement in thisOffsetPosition:
                    if hasattr(thisSubElement, "lily"):
                        ret += thisSubElement.lily
                    else:
                        # TODO: write out debug code here
                        pass
                ret += " >> "
            else:
                if hasattr(thisOffsetPosition[0], "lily"):
                    ret += thisOffsetPosition[0].lily
                else:
                    # TODO: write out debug code here
                    pass
        return ret
        
    lily = property(_getLily)



#-------------------------------------------------------------------------------

class TestExternal(unittest.TestCase):
    def runTest(self):
        pass
    
    def testLilySimple(self):
        a = Stream()
        ts = meter.TimeSignature("3/4")
        
        b = Stream()
        q = note.QuarterNote()
        q.octave = 5
        b.repeatInsert(q, [0,1,2,3])
        
        bestC = b.bestClef(allowTreble8vb = True)
        a.insert(0, bestC)
        a.insert(0, ts)
        a.insert(0, b)
        a.lily.showPNG()

    def testLilySemiComplex(self):
        a = Stream()
        ts = meter.TimeSignature("3/8")
        
        b = Stream()
        q = note.EighthNote()

        dur1 = duration.Duration()
        dur1.type = "eighth"
        
        tup1 = duration.Tuplet()
        tup1.tupletActual = [5, dur1]
        tup1.tupletNormal = [3, dur1]

        q.octave = 2
        q.duration.tuplets.append(tup1)
        
        
        for i in range(0,5):
            b.append(deepcopy(q))
            b.elements[i].accidental = note.Accidental(i - 2)
        
        b.elements[0].duration.tuplets[0].type = "start"
        b.elements[-1].duration.tuplets[0].type = "stop"
        b.elements[2].editorial.comment.text = "a real C"
         
        bestC = b.bestClef(allowTreble8vb = True)
        a.insert(0, bestC)
        a.insert(0, ts)
        a.insert(0, b)
        a.lily.showPNG()

        
    def testScoreLily(self):
        '''
        Test the lilypond output of various score operations.
        '''

        import meter
        c = note.Note("C4")
        d = note.Note("D4")
        ts = meter.TimeSignature("2/4")
        s1 = Part()
        s1.append(deepcopy(c))
        s1.append(deepcopy(d))
        s2 = Part()
        s2.append(deepcopy(d))
        s2.append(deepcopy(c))
        score1 = Score()
        score1.insert(ts)
        score1.insert(s1)
        score1.insert(s2)
        score1.lily.showPNG()
        

    def testMXOutput(self):
        '''A simple test of adding notes to measures in a stream. 
        '''
        c = Stream()
        for m in range(4):
            b = Measure()
            for pitch in ['a', 'g', 'c#', 'a#']:
                a = note.Note(pitch)
                b.append(a)
            c.append(b)
        c.show()

    def testMxMeasures(self):
        '''A test of the automatic partitioning of notes in a measure and the creation of ties.
        '''

        n = note.Note()        
        n.quarterLength = 3
        a = Stream()
        a.repeatInsert(n, range(0,120,3))
        #a.show() # default time signature used
        
        a.insert( 0, meter.TimeSignature("5/4")  )
        a.insert(10, meter.TimeSignature("2/4")  )
        a.insert( 3, meter.TimeSignature("3/16") )
        a.insert(20, meter.TimeSignature("9/8")  )
        a.insert(40, meter.TimeSignature("10/4") )
        a.show()


    def testMultipartStreams(self):
        '''Test the creation of multi-part streams by simply having streams within streams.

        '''
        q = Stream()
        r = Stream()
        for x in ['c3','a3','g#4','d2'] * 10:
            n = note.Note(x)
            n.quarterLength = .25
            q.append(n)

            m = note.Note(x)
            m.quarterLength = 1.125
            r.append(m)

        s = Stream() # container
        s.insert(q)
        s.insert(r)
        s.insert(0, meter.TimeSignature("3/4") )
        s.insert(3, meter.TimeSignature("5/4") )
        s.insert(8, meter.TimeSignature("3/4") )

        s.show()
            


    def testMultipartMeasures(self):
        '''This demonstrates obtaining slices from a stream and layering
        them into individual parts.

        TODO: this should show instruments
        this is presently not showing instruments 
        probably b/c when appending to s Stream parent is set to that stream
        '''
        from music21 import corpus, converter
        a = converter.parse(corpus.getWork(['mozart', 'k155','movement2.xml']))
        b = a[3][10:20]
        c = a[3][20:30]
        d = a[3][30:40]

        s = Stream()
        s.insert(b)
        s.insert(c)
        s.insert(d)
        s.show()


    def testCanons(self):
        '''A test of creating a canon with shifted presentations of a source melody. This also demonstrates 
        the addition of rests to parts that start late or end early.

        The addition of rests happens with makeRests(), which is called in 
        musicxml generation of a Stream.
        '''
        
        a = ['c', 'g#', 'd-', 'f#', 'e', 'f' ] * 4

        s = Stream()
        partOffsetShift = 1.25
        partOffset = 0
        for part in range(6):  
            p = Stream()
            for pitchName in a:
                n = note.Note(pitchName)
                n.quarterLength = 1.5
                p.append(n)
            p.offset = partOffset
            s.insert(p)
            partOffset += partOffsetShift

        s.show()



    def testBeamsPartial(self):
        '''This demonstrates a partial beam; a beam that is not connected between more than one note. 
        '''
        q = Stream()
        for x in [.125, .25, .25, .125, .125, .125] * 30:
            n = note.Note('c')
            n.quarterLength = x
            q.append(n)

        s = Stream() # container
        s.insert(q)

        s.insert(0, meter.TimeSignature("3/4") )
        s.insert(3, meter.TimeSignature("5/4") )
        s.insert(8, meter.TimeSignature("4/4") )

        s.show()


    def testBeamsStream(self):
        '''A test of beams applied to different time signatures. 
        '''
        q = Stream()
        r = Stream()
        p = Stream()

        for x in ['c3','a3','c#4','d3'] * 30:
            n = note.Note(x)
            #n.quarterLength = random.choice([.25, .125, .5])
            n.quarterLength = random.choice([.25])
            q.append(n)

            m = note.Note(x)
            m.quarterLength = .5
            r.append(m)

            o = note.Note(x)
            o.quarterLength = .125
            p.append(o)

        s = Stream() # container
        s.append(q)
        s.append(r)
        s.append(p)

        s.insert(0, meter.TimeSignature("3/4") )
        s.insert(3, meter.TimeSignature("5/4") )
        s.insert(8, meter.TimeSignature("4/4") )
        self.assertEqual(len(s.flat.notes), 360)

        s.show()


    def testBeamsMeasure(self):
        aMeasure = Measure()
        aMeasure.timeSignature = meter.TimeSignature('4/4')
        aNote = note.Note()
        aNote.quarterLength = .25
        aMeasure.repeatAppend(aNote,16)
        bMeasure = aMeasure.makeBeams()
        bMeasure.show()


#-------------------------------------------------------------------------------
class Test(unittest.TestCase):

    def runTest(self):
        pass

    def testCopyAndDeepcopy(self):
        '''Test copyinng all objects defined in this module
        '''
        for part in sys.modules[self.__module__].__dict__.keys():
            if part.startswith('_') or part.startswith('__'):
                continue
            elif part in ['Test', 'TestExternal']:
                continue
            elif callable(part):
                environLocal.printDebug(['testing copying on', part])
                obj = getattr(module, part)()
                a = copy.copy(obj)
                b = copy.deepcopy(obj)
                self.assertNotEqual(a, obj)
                self.assertNotEqual(b, obj)
            
    
    def testAdd(self):
        a = Stream()
        for i in range(5):
            a.insert(0, music21.Music21Object())
        self.assertTrue(a.isFlat)
        a[2] = note.Note("C#")
        self.assertTrue(a.isFlat)
        a[3] = Stream()
        self.assertFalse(a.isFlat)

    def testSort(self):
        s = Stream()
        s.repeatInsert(note.Note("C#"), [0.0, 2.0, 4.0])
        s.repeatInsert(note.Note("D-"), [1.0, 3.0, 5.0])
        self.assertFalse(s.isSorted)
        y = s.sorted
        self.assertTrue(y.isSorted)
        g = ""
        for myElement in y:
            g += "%s: %s; " % (myElement.offset, myElement.name)
        self.assertEqual(g, '0.0: C#; 1.0: D-; 2.0: C#; 3.0: D-; 4.0: C#; 5.0: D-; ')

    def testFlatSimple(self):
        s1 = Score()
        s1.id = "s1"
        
        p1 = Part()
        p1.id = "p1"
        
        p2 = Part()
        p2.id = "p2"

        n1 = note.HalfNote("C")
        n2 = note.QuarterNote("D")
        n3 = note.QuarterNote("E")
        n4 = note.HalfNote("F")
        n1.id = "n1"
        n2.id = "n2"
        n3.id = "n3"
        n4.id = "n4"

        p1.append(n1)
        p1.append(n2)

                
        p2.append(n3)
        p2.append(n4)

        p2.offset = 20.0

        s1.insert(p1)
        s1.insert(p2)

        
        sf1 = s1.flat
        sf1.id = "flat s1"
        
#        for site in n4.locations.getSites():
#            print site.id,
#            print n4.locations.getOffsetBySite(site)
        
        self.assertEqual(len(sf1), 4)
        assert(sf1[1] is n2)
        

    def testParentCopiedStreams(self):
        srcStream = Stream()
        srcStream.insert(3, note.Note())
        # the note's parent is srcStream now
        self.assertEqual(srcStream[0].parent, srcStream)

        midStream = Stream()
        for x in range(2):
            srcNew = deepcopy(srcStream)
#             for n in srcNew:
#                 offset = n.getOffsetBySite(srcStream)

            #got = srcNew[0].getOffsetBySite(srcStream)

            #for n in srcNew: pass

            srcNew.offset = x * 10 
            midStream.insert(srcNew)
            self.assertEqual(srcNew.offset, x * 10)

        # no offset is set yet
        self.assertEqual(midStream.offset, 0)

        # component streams have offsets
        self.assertEqual(midStream[0].getOffsetBySite(midStream), 0)
        self.assertEqual(midStream[1].getOffsetBySite(midStream), 10.0)

        # component notes still have a location set to srcStream
        self.assertEqual(midStream[1][0].getOffsetBySite(srcStream), 3.0)

        # component notes still have a location set to midStream[1]
        self.assertEqual(midStream[1][0].getOffsetBySite(midStream[1]), 3.0)        

        # one location in midstream
        self.assertEqual(len(midStream.locations), 1)
        
        #environLocal.printDebug(['srcStream', srcStream])
        #environLocal.printDebug(['midStream', midStream])
        x = midStream.flat

        
    def testStreamRecursion(self):
        srcStream = Stream()
        for x in range(6):
            n = note.Note('G#')
            n.duration = duration.Duration('quarter')
            n.offset = x * 1
            srcStream.insert(n)

        self.assertEqual(len(srcStream), 6)
        self.assertEqual(len(srcStream.flat), 6)

#        self.assertEqual(len(srcStream.getOverlaps()), 0)

        midStream = Stream()
        for x in range(4):
            srcNew = deepcopy(srcStream)
            srcNew.offset = x * 10 
            midStream.insert(srcNew)

        self.assertEqual(len(midStream), 4)
        environLocal.printDebug(['pre flat of mid stream'])
        self.assertEqual(len(midStream.flat), 24)
#        self.assertEqual(len(midStream.getOverlaps()), 0)

        farStream = Stream()
        for x in range(7):
            midNew = deepcopy(midStream)
            midNew.offset = x * 100 
            farStream.insert(midNew)

        self.assertEqual(len(farStream), 7)
        self.assertEqual(len(farStream.flat), 168)
#        self.assertEqual(len(farStream.getOverlaps()), 0)
#
        # get just offset times
        # elementsSorted returns offset, dur, element
        offsets = [a.offset for a in farStream.flat]

        # create what we epxect to be the offsets
        offsetsMatch = range(0, 6)
        offsetsMatch += [x + 10 for x in range(0, 6)]
        offsetsMatch += [x + 20 for x in range(0, 6)]
        offsetsMatch += [x + 30 for x in range(0, 6)]
        offsetsMatch += [x + 100 for x in range(0, 6)]
        offsetsMatch += [x + 110 for x in range(0, 6)]

        self.assertEqual(offsets[:len(offsetsMatch)], offsetsMatch)

    def testStreamSortRecursion(self):
        farStream = Stream()
        for x in range(4):
            midStream = Stream()
            for y in range(4):
                nearStream = Stream()
                for z in range(4):
                    n = note.Note("G#")
                    n.duration = duration.Duration('quarter')
                    nearStream.insert(z * 2, n)     # 0, 2, 4, 6
                midStream.insert(y * 5, nearStream) # 0, 5, 10, 15
            farStream.insert(x * 13, midStream)     # 0, 13, 26, 39
        
        # get just offset times
        # elementsSorted returns offset, dur, element
        fsfs = farStream.flat.sorted
        offsets = [a.offset for a in fsfs]  # safer is a.getOffsetBySite(fsfs)
        offsetsBrief = offsets[:20]
        self.assertEquals(offsetsBrief, [0, 2, 4, 5, 6, 7, 9, 10, 11, 12, 13, 14, 15, 15, 16, 17, 17, 18, 19, 19])





    def testOverlaps(self):
        a = Stream()
        # here, the thir item overlaps with the first
        for offset, dur in [(0,12), (3,2), (11,3)]:
            n = note.Note('G#')
            n.duration = duration.Duration()
            n.duration.quarterLength = dur
            n.offset = offset
            a.insert(n)

        includeDurationless = True
        includeCoincidentBoundaries = False

        simultaneityMap, overlapMap = a._findLayering(a.flat, 
                                  includeDurationless, includeCoincidentBoundaries)
        self.assertEqual(simultaneityMap, [[], [], []])
        self.assertEqual(overlapMap, [[1,2], [0], [0]])


        post = a._consolidateLayering(a.flat, overlapMap)
        # print post

        #found = a.getOverlaps(includeDurationless, includeCoincidentBoundaries)
        # there should be one overlap group
        #self.assertEqual(len(found.keys()), 1)
        # there should be three items in this overlap group
        #self.assertEqual(len(found[0]), 3)

        a = Stream()
        # here, the thir item overlaps with the first
        for offset, dur in [(0,1), (1,2), (2,3)]:
            n = note.Note('G#')
            n.duration = duration.Duration()
            n.duration.quarterLength = dur
            n.offset = offset
            a.insert(n)

        includeDurationless = True
        includeCoincidentBoundaries = True

        simultaneityMap, overlapMap = a._findLayering(a.flat, 
                                  includeDurationless, includeCoincidentBoundaries)
        self.assertEqual(simultaneityMap, [[], [], []])
        self.assertEqual(overlapMap, [[1], [0,2], [1]])

        post = a._consolidateLayering(a.flat, overlapMap)



    def testStreamDuration(self):
        a = Stream()
        q = note.QuarterNote()
        a.repeatInsert(q, [0,1,2,3])
        self.assertEqual(a.highestOffset, 3)
        self.assertEqual(a.highestTime, 4)
        self.assertEqual(a.duration.quarterLength, 4.0)
         
        newDuration = duration.Duration("half")
        self.assertEqual(newDuration.quarterLength, 2.0)

        a.duration = newDuration
        self.assertEqual(a.duration.quarterLength, 2.0)
        self.assertEqual(a.highestTime, 4)

    def testLilySimple(self):
        a = Stream()
        ts = meter.TimeSignature("3/4")
        
        b = Stream()
        q = note.QuarterNote()
        q.octave = 5
        b.repeatInsert(q, [0,1,2,3])
        
        bestC = b.bestClef(allowTreble8vb = True)
        a.insert(bestC)
        a.insert(ts)
        a.insert(b)
        self.assertEqual(a.lily.value, u' { \\clef "treble"  \\time 3/4   { c\'\'4 c\'\'4 c\'\'4 c\'\'4  }   } ')

    def testLilySemiComplex(self):
        a = Stream()
        ts = meter.TimeSignature("3/8")
        
        b = Stream()
        q = note.EighthNote()

        dur1 = duration.Duration()
        dur1.type = "eighth"
        
        tup1 = duration.Tuplet()
        tup1.tupletActual = [5, dur1]
        tup1.tupletNormal = [3, dur1]

        q.octave = 2
        q.duration.appendTuplet(tup1)
        
        
        for i in range(0,5):
            b.append(deepcopy(q))
            b.elements[i].accidental = note.Accidental(i - 2)
        
        b.elements[0].duration.tuplets[0].type = "start"
        b.elements[-1].duration.tuplets[0].type = "stop"
        b2temp = b.elements[2]
        c = b2temp.editorial
        c.comment.text = "a real C"
        
        bestC = b.bestClef(allowTreble8vb = True)
        a.insert(bestC)
        a.insert(ts)
        a.insert(b)
        self.assertEqual(a.lily.value,  u' { \\clef "bass"  \\time 3/8   { \\times 3/5 {ceses,8 ces,8 c,8_"a real C" cis,8 cisis,8}  }   } ')

    def testScoreLily(self):
        c = note.Note("C4")
        d = note.Note("D4")
        ts = meter.TimeSignature("2/4")
        s1 = Part()
        s1.append(deepcopy(c))
        s1.append(deepcopy(d))
        s2 = Part()
        s2.append(deepcopy(d))
        s2.append(deepcopy(c))
        score1 = Score()
        score1.insert(ts)
        score1.insert(s1)
        score1.insert(s2)
        self.assertEqual(u" << \\time 2/4  \\new Staff  { c'4 d'4  }  \\new Staff  { d'4 c'4  }  >> ", score1.lily.value)



    def testMeasureStream(self):
        '''An approach to setting TimeSignature measures in offsets and durations
        '''
        a = meter.TimeSignature('3/4')
        b = meter.TimeSignature('5/4')
        c = meter.TimeSignature('2/4')


        a.duration = duration.Duration()
        b.duration = duration.Duration()
        c.duration = duration.Duration()

        # 20 measures of 3/4
        a.duration.quarterLength = 20 * a.barDuration.quarterLength
        # 10 measures of 5/4
        b.duration.quarterLength = 10 * b.barDuration.quarterLength
        # 5 measures of 2/4
        c.duration.quarterLength = 5 * c.barDuration.quarterLength


        m = Stream()
        m.append(a)
        m.append(b)
        m.append(c)
    
        self.assertEqual(m[1].offset, (20 * a.barDuration.quarterLength))    
        self.assertEqual(m[2].offset, ((20 * a.barDuration.quarterLength) + 
                                      (10 * b.barDuration.quarterLength)))    



    def testMultipartStream(self):
        '''Test the creation of streams with multiple parts. See versions
        of this tests in TestExternal for more details
        '''
        q = Stream()
        r = Stream()
        for x in ['c3','a3','g#4','d2'] * 10:
            n = note.Note(x)
            n.quarterLength = .25
            q.append(n)

            m = note.Note(x)
            m.quarterLength = 1
            r.append(m)

        s = Stream() # container
        s.insert(q)
        s.insert(r)
        s.insert(0, meter.TimeSignature("3/4") )
        s.insert(3, meter.TimeSignature("5/4") )
        s.insert(8, meter.TimeSignature("3/4") )
        self.assertEqual(len(s.flat.notes), 80)

        from music21 import corpus, converter
        thisWork = corpus.getWork('haydn/opus74no2/movement4.xml')
        a = converter.parse(thisWork)
        b = a[3][10:20]
        c = a[3][20:30]
        d = a[3][30:40]

        s = Stream()
        s.insert(b)
        s.insert(c)
        s.insert(d)




    def testParents(self):
        '''Test parent relationships.

        Note that here we see why sometimes qualified class names are needed.
        This test passes fine with class names Part and Measure when run interactively, 
        creating a Test instance. When run from the command line
        Part and Measure do not match, and instead music21.stream.Part has to be 
        employed instead. 
        '''

        from music21 import corpus, converter
        a = converter.parse(corpus.getWork('haydn/opus74no2/movement4.xml'))

        # test basic parent relationships
        b = a[3]
        self.assertEqual(isinstance(b, music21.stream.Part), True)
        self.assertEqual(b.parent, a)

        # this, if called, actively destroys the parent relationship!
        # on the measures (as new Elements are not created)
        #m = b.getMeasures()[5]
        #self.assertEqual(isinstance(m, Measure), True)

        # this false b/c, when getting the measures, parents are lost
        #self.assertEqual(m.parent, b) #measures parent should be part

        self.assertEqual(isinstance(b[8], music21.stream.Measure), True)
        self.assertEqual(b[8].parent, b) #measures parent should be part


        # a different test derived from a TestExternal
        q = Stream()
        r = Stream()
        for x in ['c3','a3','c#4','d3'] * 30:
            n = note.Note(x)
            n.quarterLength = random.choice([.25])
            q.append(n)
            m = note.Note(x)
            m.quarterLength = .5
            r.append(m)
        s = Stream() # container
        s.insert(q)
        s.insert(r)

        self.assertEqual(q.parent, s)
        self.assertEqual(r.parent, s)

    def testParentsMultiple(self):
        '''Test an object having multiple parents.
        '''
        a = Stream()
        b = Stream()
        n = note.Note("G#")
        n.offset = 10
        a.insert(n)
        b.insert(n)
        # the objects elements has been transfered to each parent
        # stream in the same way
        self.assertEqual(n.getOffsetBySite(a), n.getOffsetBySite(b))
        self.assertEqual(n.getOffsetBySite(a), 10)



    def testExtractedNoteAssignLyric(self):
        from music21 import converter, corpus, text
        a = converter.parse(corpus.getWork('opus74no1', 3))
        b = a[1] 
        c = b.flat
        for thisNote in c.getElementsByClass(note.Note):
            thisNote.lyric = thisNote.name
        textStr = text.assembleLyrics(b)
        self.assertEqual(textStr.startswith('C D E A F E'), 
                         True)



    def testGetInstrumentFromMxl(self):
        '''Test getting an instrument from an mxl file
        '''
        from music21 import corpus, converter

        # manuall set parent to associate 
        a = converter.parse(corpus.getWork(['haydn', 'opus74no2', 
                                            'movement4.xml']))

        b = a[3][10:20]
        # TODO: manually setting the parent is still necessary
        b.parent = a[3] # manually set the parent
        instObj = b.getInstrument()
        self.assertEqual(instObj.partName, 'Cello')

        p = a[3] # get part
        # a mesausre within this part has as its parent the part
        self.assertEqual(p[10].parent, a[3])
        instObj = p.getInstrument()
        self.assertEqual(instObj.partName, 'Cello')

        instObj = p[10].getInstrument()
        self.assertEqual(instObj.partName, 'Cello')




    def testGetInstrumentManual(self):
        from music21 import corpus, converter


        #import pdb; pdb.set_trace()
        # search parent from a measure within

        # a different test derived from a TestExternal
        q = Stream()
        r = Stream()
        for x in ['c3','a3','c#4','d3'] * 30:
            n = note.Note(x)
            n.quarterLength = random.choice([.25])
            q.append(n)
            m = note.Note(x)
            m.quarterLength = .5
            r.append(m)
        s = Stream() # container

        s.insert(q)
        s.insert(r)

        instObj = q.getInstrument()
        self.assertEqual(instObj.partName, defaults.partName)

        instObj = r.getInstrument()
        self.assertEqual(instObj.partName, defaults.partName)

        instObj = s.getInstrument()
        self.assertEqual(instObj.partName, defaults.partName)

        # test mx generation of parts
        mx = q.mx
        mx = r.mx

        # test mx generation of score
        mx = s.mx

    def testMeasureAndTieCreation(self):
        '''A test of the automatic partitioning of notes in a measure and the creation of ties.
        '''

        n = note.Note()        
        n.quarterLength = 3
        a = Stream()
        a.repeatInsert(n, range(0,120,3))        
        a.insert( 0, meter.TimeSignature("5/4")  )
        a.insert(10, meter.TimeSignature("2/4")  )
        a.insert( 3, meter.TimeSignature("3/16") )
        a.insert(20, meter.TimeSignature("9/8")  )
        a.insert(40, meter.TimeSignature("10/4") )

        mx = a.mx

    def testStreamCopy(self):
        '''Test copying a stream
        '''
        from music21 import corpus, converter


        #import pdb; pdb.set_trace()
        # search parent from a measure within

        # a different test derived from a TestExternal
        q = Stream()
        r = Stream()
        for x in ['c3','a3','c#4','d3'] * 30:
            n = note.Note(x)
            n.quarterLength = random.choice([.25])
            q.append(n)
            m = note.Note(x)
            m.quarterLength = .5
            r.append(m)
        s = Stream() # container

        s.insert(q)
        s.insert(r)

        # copying the whole: this works
        w = deepcopy(s)

        post = Stream()
        # copying while looping: this gets increasingly slow
        for aElement in s:
            environLocal.printDebug(['copying and inserting an element',
                                     aElement, len(aElement.locations)])
            bElement = deepcopy(aElement)
            post.insert(aElement.offset, bElement)
            

    def testIteration(self):
        '''This test was designed to illustrate a past problem with stream
        Iterations.
        '''
        q = Stream()
        r = Stream()
        for x in ['c3','a3','c#4','d3'] * 5:
            n = note.Note(x)
            n.quarterLength = random.choice([.25])
            q.append(n)
            m = note.Note(x)
            m.quarterLength = .5
            r.append(m)
        src = Stream() # container
        src.insert(q)
        src.insert(r)

        a = Stream()

        for obj in src.getElementsByClass(Stream):
            a.insert(obj)

        environLocal.printDebug(['expected length', len(a)])
        counter = 0
        for x in a:
            if counter >= 4:
                environLocal.printDebug(['infinite loop', counter])
                break
            environLocal.printDebug([x])
            junk = x.getInstrument(searchParent=True)
            del junk
            counter += 1


    def testGetTimeSignatures(self):
        #getTimeSignatures

        n = note.Note()        
        n.quarterLength = 3
        a = Stream()
        a.insert( 0, meter.TimeSignature("5/4")  )
        a.insert(10, meter.TimeSignature("2/4")  )
        a.insert( 3, meter.TimeSignature("3/16") )
        a.insert(20, meter.TimeSignature("9/8")  )
        a.insert(40, meter.TimeSignature("10/4") )

        offsets = [x.offset for x in a]
        self.assertEqual(offsets, [0.0, 10.0, 3.0, 20.0, 40.0])

        a.repeatInsert(n, range(0,120,3))        

        b = a.getTimeSignatures()
        self.assertEqual(len(b), 5)
        self.assertEqual(b[0].numerator, 5)
        self.assertEqual(b[4].numerator, 10)

        self.assertEqual(b[4].parent, b)

        # none of the offsets are being copied 
        offsets = [x.offset for x in b]
        self.assertEqual(offsets, [0.0, 10.0, 3.0, 20.0, 40.0])


  
    def testElements(self):
        '''Test basic Elements wrapping non music21 objects
        '''
        a = Stream()
        a.insert(50, True)
        self.assertEqual(len(a), 1)

        # there are two locations, default and the one just added
        self.assertEqual(len(a[0].locations), 2)
        # this works
        self.assertEqual(a[0].locations.getOffsetByIndex(-1), 50.0)

        self.assertEqual(a[0].locations.getSiteByIndex(-1), a)
        self.assertEqual(a[0].getOffsetBySite(a), 50.0)
        self.assertEqual(a[0].offset, 50.0)

    def testClefs(self):
        s = Stream()
        for x in ['c3','a3','c#4','d3'] * 5:
            n = note.Note(x)
            s.append(n)
        clefObj = s.bestClef()
        self.assertEqual(clefObj.sign, 'F')
        measureStream = s.makeMeasures()
        clefObj = measureStream[0].clef
        self.assertEqual(clefObj.sign, 'F')

    def testFindConsecutiveNotes(self):
        s = Stream()
        n1 = note.Note("c3")
        n1.quarterLength = 1
        n2 = chord.Chord(["c4", "e4", "g4"])
        n2.quarterLength = 4
        s.insert(0, n1)
        s.insert(1, n2)
        l1 = s.findConsecutiveNotes()
        self.assertTrue(l1[0] is n1)
        self.assertTrue(l1[1] is n2)
        l2 = s.findConsecutiveNotes(skipChords = True)
        self.assertTrue(len(l2) == 1)
        self.assertTrue(l2[0] is n1)
        
        r1 = note.Rest()
        s2 = Stream()
        s2.insert([0.0, n1,
                   1.0, r1, 
                   2.0, n2])
        l3 = s2.findConsecutiveNotes()
        self.assertTrue(l3[1] is None)
        l4 = s2.findConsecutiveNotes(skipRests = True)
        self.assertTrue(len(l4) == 2)
        s3 = Stream()
        s3.insert([0.0, n1,
                   1.0, r1,
                   10.0, n2])
        l5 = s3.findConsecutiveNotes(skipRests = False)
        self.assertTrue(len(l5) == 3)  # not 4 because two Nones allowed in a row!
        l6 = s3.findConsecutiveNotes(skipRests = True, skipGaps = True)
        self.assertTrue(len(l6) == 2)
        
        n1.quarterLength = 10
        n3 = note.Note("B-")
        s4 = Stream()
        s4.insert([0.0, n1,
                   1.0, n2,
                   10.0, n3])
        l7 = s4.findConsecutiveNotes()
        self.assertTrue(len(l7) == 2) # n2 is hidden because it is in an overlap
        l8 = s4.findConsecutiveNotes(getOverlaps = True)
        self.assertTrue(len(l8) == 3)
        self.assertTrue(l8[1] is n2)
        l9 = s4.findConsecutiveNotes(getOverlaps = True, skipChords = True)
        self.assertTrue(len(l9) == 3)
        self.assertTrue(l9[1] is None)
        
        n4 = note.Note("A#")
        n1.quarterLength = 1
        n2.quarterLength = 1
        
        s5 = Stream()
        s5.insert([0.0, n1,
                   1.0, n2,
                   2.0, n3,
                   3.0, n4])
        l10 = s5.findConsecutiveNotes()
        self.assertTrue(len(l10) == 4)
        l11 = s5.findConsecutiveNotes(skipUnisons = True)
        self.assertTrue(len(l11) == 3)
        self.assertTrue(l11[2] is n3)

if __name__ == "__main__":    
    music21.mainTest(Test)
