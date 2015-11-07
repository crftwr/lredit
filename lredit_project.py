import os
import fnmatch

import ckit
from ckit.ckit_const import *


## @addtogroup project
## @{

#--------------------------------------------------------------------

## プロジェクトクラス
class Project:

    ## コンストラクタ
    def __init__( self, filename ):
        
        self.filename = ckit.normPath(filename)
        self.name = os.path.splitext(os.path.basename(filename))[0]
        self.dirname = os.path.dirname(self.filename)

        self.items = []

        self.parse()
        self.timestamp = os.stat(self.filename).st_mtime

    ## プロジェクトファイルをメモリに読み込む
    def parse(self):
        
        fd = open( self.filename, "rb" )
        data = fd.read()
        fd.close()

        encoding = ckit.detectTextEncoding( data, ascii_as="utf-8" )
        
        if encoding.bom:
            data = data[ len(encoding.bom) : ]

        if encoding.encoding:
            data = data.decode( encoding=encoding.encoding, errors='replace' )
        else:
            raise UnicodeError

        lines = data.splitlines(False)

        for line in lines:
            path = line.strip()
            if not path : continue
            dirname, filename = ckit.splitPath(path)
            
            if ("*" in filename) or ("?" in filename):
                self.items.append( ( dirname, filename.split(" ") ) )
            else:
                self.items.append( ( dirname, filename ) )

    ## プロジェクト中のアイテムを列挙する
    def enumName(self):
        for item in self.items:
            if isinstance(item[1],str):
                yield ckit.joinPath( item[0], item[1] )
            else:
                for filename in os.listdir( os.path.join( self.dirname, item[0] ) ):
                    for pattern in item[1]:
                        if fnmatch.fnmatch( filename, pattern ):
                            yield ckit.joinPath( item[0], filename )

    ## プロジェクト中のアイテムをフルパスで列挙する
    def enumFullpath(self):
        for item in self.enumName():
            yield ckit.normPath( ckit.joinPath( self.dirname, item ) )

    ## プロジェクトファイルが更新されているかをチェックする
    def isFileModified(self):
        if not self.filename : return False
        try:
            timestamp = os.stat(self.filename).st_mtime
        except WindowsError:
            return False
        return self.timestamp != timestamp

## @} project

