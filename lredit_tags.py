import os
import re

import ckit


## @addtogroup tags
## @{


## TAGS ファイル利用するためのクラス
class Tags:

    pattern_line0 = re.compile( '(.*)\t(.*)\t/\^(.*)\$/;"\t(.*)' ) # 検索文字列形式
    pattern_line1 = re.compile( '(.*)\t(.*)\t([0-9]+);"\t(.*)' )   # 行番号形式

    ## コンストラクタ
    def __init__( self, filename ):

        self.filename = ckit.normPath(filename)
        self.mtime = None
        self.items = []
        self.cancel_requested = False

    ## TAGSファイルを読み込んで、メモリにロードする
    def parse(self):

        # タイムスタンプを覚えておく
        stat = os.stat(self.filename)
        self.mtime = stat.st_mtime

        fd = open( self.filename, "r", encoding="utf-8", errors="ignore" )
        try:
            for line in fd:
                if self.cancel_requested : break
                result = Tags.pattern_line0.match(line)
                if result:
                    symbol = result.group(1)
                    filename = result.group(2)
                    pattern = result.group(3)
                    self.items.append( ( symbol, filename, pattern ) )
                    continue

                result = Tags.pattern_line1.match(line)
                if result:
                    symbol = result.group(1)
                    filename = result.group(2)
                    lineno = int(result.group(3))
                    self.items.append( ( symbol, filename, lineno ) )
                    continue
        finally:
            fd.close()

    ## TAGSファイルの読み込みを中断する
    def cancel(self):
        self.cancel_requested = True

    ## シンボルの位置を取得する
    def find( self, symbol ):
        result = []
        for item in self.items:
            if item[0]==symbol:
                result.append(item)
        return result

    ## TAGSファイルのフルパスを取得する
    def getFullpath(self):
        return self.filename

    ## TAGSファイルが更新されているかをチェックする
    def isFileModified(self):

        try:
            stat = os.stat(self.filename)
        except WindowsError:
            return True

        return stat.st_mtime > self.mtime

    def symbols(self):
        return map( lambda item: item[0], self.items )

## @} tags

