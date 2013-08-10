import os
import json


## @addtogroup bookmark
## @{


#--------------------------------------------------------------------

# table         : [ [ filename, bookmark_list ], ... ]
# bookmark_list : [ bookmark, ... ]
# bookmark      : ( lineno, color, display_text )

#--------------------------------------------------------------------

## ブックマーク管理クラス
class BookmarkTable:

    ## コンストラクタ
    def __init__( self, maxnum=1000 ):
        
        self.table = []
        self.maxnum = maxnum

    def _shrinkText( self, text ):
        text = ' '.join(text.split())
        text = text[:80]
        return text

    ## テキストファイル全体のブックマークのリストを格納する
    def setBookmarkList( self, filename, bookmark_list ):

        filename = os.path.normpath(filename)
        
        bookmark_list2 = []
        for bookmark in bookmark_list:
            if bookmark[1]:
                bookmark = ( bookmark[0], bookmark[1], self._shrinkText(bookmark[2]) )
                bookmark_list2.append(bookmark)
        bookmark_list = bookmark_list2
        
        for i, item in enumerate(self.table):
            if item[0] == filename:
                if bookmark_list:
                    item[1] = bookmark_list
                else:
                    del self.table[i]
                break
        else:
            if bookmark_list:
                item = [ filename, bookmark_list ]
                self.table.append(item)
                self.table.sort( key = lambda item: item[0] )

    ## テキストファイルのブックマークを１つ格納する
    def setBookmark( self, filename, bookmark ):
        
        filename = os.path.normpath(filename)
        bookmark = ( bookmark[0], bookmark[1], self._shrinkText(bookmark[2]) )
        
        for item in self.table:
            if item[0] == filename:
                for i, b in enumerate(item[1]):
                    if b[0] == bookmark[0]:
                        if bookmark[1]:
                            item[1][i] = ( b[0], bookmark[1], bookmark[2] )
                        else:
                            del item[1][i]
                        break
                else:
                    if bookmark[1]:
                        item[1].append(bookmark)
                        item[1].sort()
                if len(item[1])==0:
                    self.table.remove(item)
                break
        else:
            if bookmark[1]:
                item = [ filename, [ bookmark ] ]
                self.table.append(item)
                def compare( item1, item2 ):
                    return cmp( item1[0], item2[1] )
                self.table.sort( compare )

    ## テキストファイル１つのブックマークのリストを取得する
    def getBookmarkList( self, filename ):

        filename = os.path.normpath(filename)
        
        for item in self.table:
            if item[0] == filename:
                return item[1]
        return []

    ## ブックマークの情報を ini ファイルに保存する
    def save( self, ini, section, prefix="bookmark" ):
        i=0

        for filename, bookmark_list in self.table:
            for bookmark in bookmark_list:
                assert(bookmark[1])
                value = json.dumps( ( filename, bookmark[0], bookmark[1], bookmark[2] ) )
                ini.set( section, "%s_%d"%(prefix,i), value )
                i+=1

        while True:
            if not ini.remove_option( section, "%s_%d"%(prefix,i) ) : break
            i+=1

    ## ブックマークの情報を ini ファイルから読み込む
    def load( self, ini, section, prefix="bookmark" ):
        for i in range(self.maxnum):
            try:
                value = ini.get( section, "%s_%d"%(prefix,i) )
                filename, lineno, color, display_text = json.loads(value)
                self.setBookmark( filename, (lineno, color, display_text) )
            except:
                break

## @} bookmark

