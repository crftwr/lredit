import StringIO
import configparser

import pyauto

#-------------------------------------------------------------------------

class IpcData:

    options = [ "compare=" ]

    def __init__( self, data=None ):

        self.ini = configparser.RawConfigParser()
        self.num_filename = 0
        
        if data:
            fd = StringIO.StringIO(data)
            self.ini.readfp(fd)
            self.num_filename = self._countOption( "FILENAME", "item" )

    def getValue(self):
        fd = StringIO.StringIO("")
        self.ini.write(fd)
        return fd.getvalue().strip()

    def trySetOption( self, option, value ):
    
        value = value.encode("utf8")

        if option=="--filename":
            self._addSection("FILENAME")
            self.ini.set( "FILENAME", "item%d" % self.num_filename, value )
            self.num_filename += 1
            return True
        
        elif option=="--compare":
            self._addSection("COMPARE")
            self.ini.set( "COMPARE", "enabled", "1" )
            return True
        
        return False
            
    def _addSection( self, section ):            
        try:
            self.ini.add_section(section)
        except configparser.DuplicateSectionError:
            pass

    def _countOption( self, section, option ):
        count = 0
        while True:
            try:
                self.ini.get( section, "%s%d" % (option, count) )
            except ( configparser.NoOptionError, configparser.NoSectionError ):
                break
            count += 1
        return count

    def _getOptionList( self, section, option ):
        items = []
        count = 0
        while True:
            try:
                items.append( self.ini.get( section, "%s%d" % (option, count) ) )
            except ( configparser.NoOptionError, configparser.NoSectionError ):
                break
            count += 1
        return items

    def getFilenameList(self):
        return self._getOptionList( "FILENAME", "item" )

    def isCompareEnabled(self):
        try:
            value = self.ini.get( "COMPARE", "enabled" )
        except ( configparser.NoOptionError, configparser.NoSectionError ):
            return False
        return int(value)!=0

#-------------------------------------------------------------------------
