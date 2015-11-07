import os
import fnmatch

import ckit
from ckit.ckit_const import *


## @addtogroup directory
## @{

#--------------------------------------------------------------------

## ディレクトリクラス
class Directory:

    ## コンストラクタ
    def __init__( self, dirname ):
        
        self.dirname = os.path.normpath(dirname)


    ## ディレクトリ中のファイル名を列挙する
    def enumFilenames( self, filename_pattern_list ):
        for root, dirs, files in os.walk( self.dirname ):
            for filename in files:
                for filename_pattern in filename_pattern_list:
                    if fnmatch.fnmatch( filename, filename_pattern ):
                        yield ckit.joinPath( root, filename )


## ディレクトリのリスト
class DirectoryList:

    ## コンストラクタ
    def __init__(self):
        self.items = []


    ## ディレクトリをリストに追加する
    def openDirectory( self, dirname ):

        # 重複を避けるために一度閉じる
        self.closeDirectory(dirname)

        directory = Directory(dirname)
        self.items.insert( 0, directory )


    ## ディレクトリをリストから削除する
    def closeDirectory( self, dirname ):
        
        dirname = os.path.normpath(dirname)

        for i, item in enumerate(self.items):
            if dirname == item.dirname:
                del self.items[i]
                break


    ## ディレクトリを列挙する
    def enumDirectories(self):
        for item in self.items:
            yield item.dirname


    ## ディレクトリリスト中のファイル名を列挙する
    def enumFilenames( self, filename_pattern_list ):
        for item in self.items:
            for filename in item.enumFilenames(filename_pattern_list):
                yield filename


## @} directory

