import os

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
            filename = line.strip()
            if not filename : continue
            fullpath = ckit.normPath( ckit.joinPath( self.dirname, filename ) )
            self.items.append( ( filename, fullpath ) )

    ## プロジェクト中のアイテムを列挙する
    def enumName(self):
        for item in self.items:
            yield item[0]

    ## プロジェクト中のアイテムをフルパスで列挙する
    def enumFullpath(self):
        for item in self.items:
            yield item[1]

    ## プロジェクトファイルが更新されているかをチェックする
    def isFileModified(self):
        if not self.filename : return False
        try:
            timestamp = os.stat(self.filename).st_mtime
        except WindowsError:
            return False
        return self.timestamp != timestamp

## @} project

