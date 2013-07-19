# -*- coding: utf-8 -*-
#-------------------------------------------------------------------------------
# Name:         convertIPythonNotebooksToReST.py
# Purpose:      music21 documentation IPython notebook to ReST converter
#
# Authors:      Josiah Wolf Oberholtzer
#
# Copyright:    Copyright © 2013 Michael Scott Cuthbert and the music21 Project
# License:      LGPL, see license.txt
#-------------------------------------------------------------------------------

import abc
import json
import os
import re
import subprocess


class ReSTWriter(object):
    '''
    Abstract base class for ReST writers.
    '''

    ### CLASS VARIABLES ###

    __metaclass__ = abc.ABCMeta

    ### SPECIAL METHODS ###

    @abc.abstractmethod
    def __call__(self):
        raise NotImplemented

    ### PUBLIC METHODS ###

    def write(self, filePath, rst): #
        '''
        Write ``lines`` to ``filePath``, only overwriting an existing file
        if the content differs.
        '''
        shouldWrite = True
        if os.path.exists(filePath):
            with open(filePath, 'r') as f:
                oldRst = f.read()
            if rst == oldRst:
                shouldWrite = False
        if shouldWrite:
            with open(filePath, 'w') as f:
                f.write(rst)
            print '\tWROTE   {0}'.format(os.path.relpath(filePath))
        else:
            print '\tSKIPPED {0}'.format(os.path.relpath(filePath))


class ModuleReferenceReSTWriter(ReSTWriter):
    '''
    Writes module reference ReST files, and their index ReST file.
    '''

    ### SPECIAL METHODS ###
    
    def __call__(self):
        from music21 import documentation
        moduleReferenceDirectoryPath = os.path.join(
            documentation.__path__[0],
            'source',
            'moduleReference',
            )
        referenceNames = []
        for module in [x for x in documentation.ModuleIterator()]:
            moduleDocumenter = documentation.ModuleDocumenter(module)
            rst = '\n'.join(moduleDocumenter())
            referenceName = moduleDocumenter.referenceName
            referenceNames.append(referenceName)
            fileName = '{0}.rst'.format(referenceName)
            filePath = os.path.join(
                moduleReferenceDirectoryPath,
                fileName,
                )
            self.write(filePath, rst)
        
        lines = []
        lines.append('.. moduleReference:')
        lines.append('')
        lines.append('Module Reference')
        lines.append('================')
        lines.append('')
        lines.append('.. toctree::')
        lines.append('   :maxdepth: 1')
        lines.append('')
        for referenceName in sorted(referenceNames):
            lines.append('   {0}'.format(referenceName))
        rst = '\n'.join(lines)
        indexFilePath = os.path.join(
            moduleReferenceDirectoryPath,
            'index.rst',
            )
        self.write(indexFilePath, rst)


class CorpusReferenceReSTWriter(ReSTWriter):
    '''
    Write the corpus reference ReST file.
    '''

    ### SPECIAL METHODS ###

    def __call__(self):
        from music21 import documentation
        systemReferenceDirectoryPath = os.path.join(
            documentation.__path__[0],
            'source',
            'systemReference',
            )
        corpusReferenceFilePath = os.path.join(
            systemReferenceDirectoryPath,
            'referenceCorpus.rst',
            )
        lines = documentation.CorpusDocumenter()()
        rst = '\n'.join(lines)
        self.write(corpusReferenceFilePath, rst)


class IPythonNotebookReSTWriter(ReSTWriter):
    '''
    Converts IPython notebooks into ReST, and handles their associated image
    files.

    This class wraps the 3rd-party ``nbconvert`` Python script.
    '''

    ### SPECIAL METHODS ###

    def __call__(self):
        from music21 import documentation
        ipythonNotebookFilePaths = [x for x in
            documentation.IPythonNotebookIterator()()]
        for ipythonNotebookFilePath in ipythonNotebookFilePaths:
            self._convertOneNotebook(ipythonNotebookFilePath)
            self._cleanupNotebookAssets(ipythonNotebookFilePath)
            print '\tWROTE   {0}'.format(os.path.relpath(
                ipythonNotebookFilePath))

    ### PRIVATE METHODS ###

    def _cleanupNotebookAssets(self, ipythonNotebookFilePath):
        notebookFileNameWithoutExtension = os.path.splitext(
            os.path.basename(ipythonNotebookFilePath))[0]
        notebookParentDirectoryPath = os.path.abspath(
            os.path.dirname(ipythonNotebookFilePath),
            )
        imageFileDirectoryName = notebookFileNameWithoutExtension + '_files' 
        imageFileDirectoryPath = os.path.join(
            notebookParentDirectoryPath,
            imageFileDirectoryName,
            )
        for fileName in os.listdir(imageFileDirectoryPath):
            if fileName.endswith('.text'):
                filePath = os.path.join(
                    imageFileDirectoryPath,
                    fileName,
                    )
                os.remove(filePath)

    def _convertOneNotebook(self, ipythonNotebookFilePath):
        assert os.path.exists(ipythonNotebookFilePath)
        self._runNBConvert(ipythonNotebookFilePath)
        notebookFileNameWithoutExtension = os.path.splitext(
            os.path.basename(ipythonNotebookFilePath))[0]
        notebookParentDirectoryPath = os.path.abspath(
            os.path.dirname(ipythonNotebookFilePath),
            )
        imageFileDirectoryName = notebookFileNameWithoutExtension + '_files'
        rstFileName = notebookFileNameWithoutExtension + '.rst'
        rstFilePath = os.path.join(
            notebookParentDirectoryPath,
            rstFileName,
            )
        with open(rstFilePath, 'r') as f:
            oldLines = f.read().splitlines()
        ipythonPromptPattern = re.compile('^In\[\d+\]:')
        mangledInternalReference = re.compile(
            r'\:(class|ref|func|meth)\:\`\`(.*?)\`\`')
        newLines = []
        currentLineNumber = 0
        while currentLineNumber < len(oldLines):
            currentLine = oldLines[currentLineNumber]
            # Remove all IPython prompts and the blank line that follows:
            if ipythonPromptPattern.match(currentLine) is not None:
                currentLineNumber += 2
                continue
            # Correct the image path in each ReST image directive:
            elif currentLine.startswith('.. image:: '):
                imageFileName = currentLine.partition('.. image:: ')[2]
                if '/' not in currentLine:
                    newImageDirective = '.. image:: {0}/{1}'.format(
                        imageFileDirectoryName,
                        imageFileName,
                        )
                    newLines.append(newImageDirective)
                else:
                    newLines.append(currentLine)
                currentLineNumber += 1
            # Otherwise, nothing special to do, just add the line to our results:
            else:
                # fix cases of inline :class:`~music21.stream.Stream` being
                # converted by markdown to :class:``~music21.stream.Stream``
                newCurrentLine = mangledInternalReference.sub(
                    r':\1:`\2`', 
                    currentLine
                    )
                newLines.append(newCurrentLine)
                currentLineNumber += 1
        
        # Guarantee a blank line after literal blocks.
        lines = [newLines[0]]
        for i, pair in enumerate(self._iterateSequencePairwise(newLines)):
            first, second = pair
            if len(first.strip()) \
                and first[0].isspace() \
                and len(second.strip()) \
                and not second[0].isspace():
                lines.append('')
            lines.append(second)

        with open(rstFilePath, 'w') as f:
            f.write('\n'.join(lines))

    def _iterateSequencePairwise(self, sequence):
        prev = None
        for x in sequence:
            cur = x
            if prev is not None:
                yield prev, cur
            prev = cur
            
    def _runNBConvert(self, ipythonNotebookFilePath):
        import music21
        from music21 import common
        #runDirectoryPath = common.getBuildDocFilePath()
        pathParts = music21.__path__ + [
            'ext',
            'nbconvert',
            'nbconvert.py',
            ]
        nbconvertPath = os.path.join(*pathParts)
        nbconvertCommand = '{executable} rst {notebook}'.format(
            #executable=os.path.relpath(nbconvertPath, runDirectoryPath),
            #notebook=os.path.relpath(ipythonNotebookFilePath, runDirectoryPath),
            executable=os.path.relpath(nbconvertPath),
            notebook=os.path.relpath(ipythonNotebookFilePath),
            )
        #print nbconvertCommand
        #subprocess.call(nbconvertCommand, shell=True, cwd=runDirectoryPath)
        subprocess.call(nbconvertCommand, shell=True)

    def _processNotebook(self, ipythonNotebookFilePath):
        with open(ipythonNotebookFilePath, 'r') as f:
            contents = f.read()
            contentsAsJson = json.loads(contents)
        directoryPath, sep, baseName = ipythonNotebookFilePath.rpartition(
            os.path.sep)
        baseNameWithoutExtension = os.path.splitext(baseName)[0]
        imageFilesDirectoryPath = os.path.join(
            directoryPath,
            '{0}_files'.format(baseNameWithoutExtension),
            )
        rstFilePath = os.path.join(
            directoryPath,
            '{0}.rst'.format(baseNameWithoutExtension),
            )
        lines, imageData = documentation.IPythonNotebookDocumenter(
            contentsAsJson)()
        rst = '\n'.join(lines)
        self.write(rstFilePath, rst)
        if not imageData:
            return
        if not os.path.exists(imageFilesDirectoryPath):
            os.mkdir(imageFilesDirectoryPath)
        for imageFileName, imageFileData in imageData.iteritems():
            imageFilePath = os.path.join(
                imageFilesDirectoryPath,
                imageFileName,
                )
            shouldOverwriteImage = True
            with open(imageFilePath, 'rb') as f:
                oldImageFileData = f.read()
                if oldImageFileData == imageFileData:
                    shouldOverwriteImage = False
            if shouldOverwriteImage:
                with open(imageFilePath, 'wb') as f:
                    f.write(imageFileData)
        

if __name__ == '__main__':
    import music21
    music21.mainTest()

