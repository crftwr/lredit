## @addtogroup commandline
## @{

## コマンドラインの履歴を管理するクラス
class History:

    ## コンストラクタ
    def __init__( self, maxnum=100 ):
        self.items = []
        self.maxnum = maxnum

    ## 履歴を追加する
    def append( self, newentry ):
    
        for i in range(len(self.items)):
            if self.items[i]==newentry:
                del self.items[i]
                break
        self.items.insert( 0, newentry )

        if len(self.items)>self.maxnum:
            self.items = self.items[:self.maxnum]

    ## 履歴を削除する
    def remove( self, entry ):
        for i in range(len(self.items)):
            if self.items[i]==entry:
                del self.items[i]
                return
        raise KeyError        

    ## 履歴を ini ファイルに保存する
    def save( self, ini, section, prefix="history" ):
        i=0
        while i<len(self.items):
            ini.set( section, "%s_%d"%(prefix,i), self.items[i] )
            i+=1

        while True:
            if not ini.remove_option( section, "%s_%d"%(prefix,i) ) : break
            i+=1

    ## 履歴を ini ファイルから読み込む
    def load( self, ini, section, prefix="history" ):
        for i in range(self.maxnum):
            try:
                self.items.append( ini.get( section, "%s_%d"%(prefix,i) ) )
            except:
                break

    ## コマンドラインの補完候補を、履歴から列挙するためのハンドラ
    def candidateHandler( self, update_info ):

        left = update_info.text[ : update_info.selection[0] ]
        left_lower = left.lower()

        candidate_list = []

        for item in self.items:
            item_lower = item.lower()
            if item_lower.startswith(left_lower) and len(item_lower)!=len(left_lower):
                candidate_list.append( item )

        return candidate_list, 0

    ## コマンドラインの補完候補から履歴から削除するためのハンドラ
    def candidateRemoveHandler( self, text ):
        try:
            self.remove( text )
            return True
        except KeyError:
            pass
        return False

## @} commandline

