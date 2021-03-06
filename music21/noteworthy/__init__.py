# -*- coding: utf-8 -*-
#-------------------------------------------------------------------------------
# Name:         noteworthy/__init__.py
# Purpose:      parses NWCTXT Notation
#
# Authors:      Jordi Bartolome
#               Michael Scott Cuthbert
#
# Copyright:    (c) 2011 The music21 Project
# License:      LGPL
#-------------------------------------------------------------------------------
__ALL__ = ['translate','binaryTranslate','base']

from music21.noteworthy.base import *
from music21.noteworthy import base
__doc__ = base.__doc__ # @ReservedAssignment @UndefinedVariable

#------------------------------------------------------------------------------
# eof

import translate
import binaryTranslate