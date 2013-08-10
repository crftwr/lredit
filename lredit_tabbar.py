import ckit
from ckit.ckit_const import *


## @addtogroup widget
## @{

#--------------------------------------------------------------------

## タブバーウィジェット
#
class TabBarWidget(ckit.Widget):

    MAX_ITEM_WIDTH = 30

    def __init__( self, window, x, y, width, height, selchange_handler ):

        ckit.Widget.__init__( self, window, x, y, width, height )

        self.plane0 = None
        self.createThemePlane()
        
        self.items = []
        self.selection = None
        self.scroll_pos = 0
        
        self.selchange_handler = selchange_handler

        self.paint()

    def destroy(self):
        self.destroyThemePlane()

    def show(self,visible):
        ckit.Widget.show(self,visible)
        self.plane0.show(visible)
        
    def charToTabIndex( self, char_x, char_y ):

        x = -self.scroll_pos

        if 0 <= (char_y - self.y) < self.height:
            for i, item in enumerate(self.items):
        
                name = item[0]
                item_width = min( self.window.getStringWidth(name), TabBarWidget.MAX_ITEM_WIDTH ) + 2
            
                if x <= (char_x - self.x) < x + item_width:
                    return i
                
                x += item_width
        
        return None

    def onLeftButtonDown( self, char_x, char_y, mod ):
        #print( "onLeftButtonDown", char_x, char_y, mod )
        index = self.charToTabIndex( char_x, char_y )
        if index==None : return
        self.selection = index
        if self.selchange_handler:
            self.selchange_handler( self.selection, self.items[self.selection] )

    def onLeftButtonUp( self, char_x, char_y, mod ):
        #print( "onLeftButtonUp", char_x, char_y, mod )
        pass

    def createThemePlane(self):
        if not self.plane0:
            self.plane0 = ckit.ThemePlane3x3( self.window, 'tabbar0.png' )

    def destroyThemePlane(self):
        if self.plane0:
            self.plane0.destroy()
            self.plane0 = None

    def setItems( self, items ):
        self.items = items
        self.paint()
        
    def setSelection( self, selection ):
        self.selection = selection
        self.paint()

    def makeVisible( self, index ):
    
        tabs_width = 0

        for i, item in enumerate(self.items):
        
            name = item[0]
            item_width = min( self.window.getStringWidth(name), TabBarWidget.MAX_ITEM_WIDTH ) + 2

            if i==index:
                if self.scroll_pos > tabs_width:
                    self.scroll_pos = tabs_width
            
                elif self.scroll_pos + self.width < tabs_width + item_width:
                    self.scroll_pos = tabs_width + item_width - self.width

            tabs_width += item_width

            if i==len(self.items)-1:
                if tabs_width < self.scroll_pos + self.width:
                    self.scroll_pos = max( tabs_width - self.width, 0 )

    def paint(self):
    
        if self.selection!=None:
            self.makeVisible(self.selection)
            
        client_rect = self.window.getClientRect()
        offset_x, offset_y = self.window.charToClient( 0, 0 )
        char_w, char_h = self.window.getCharSize()

        # 背景画像をウインドウの端にあわせる
        offset_x2 = 0
        if self.x==0 : offset_x2 = offset_x
        offset_x3 = 0
        if self.x+self.width==self.window.width() : offset_x3 = offset_x
        offset_y2 = 0
        if self.y==0 : offset_y2 = offset_y
        offset_y3 = 0
        if self.y+self.height==self.window.height() : offset_y3 = offset_y

        # 背景画像
        self.plane0.setPosSize( self.x*char_w+offset_x-offset_x2, self.y*char_h+offset_y-offset_y2, self.width*char_w+offset_x2+offset_x3, self.height*char_h+offset_y2+offset_y3 )

        line_color = (120,120,120)
        active_bg_color = (240,240,240)
        inactive_bg_color = None

        fg = ckit.getColor("bar_fg")
        attr = ckit.Attribute( fg=fg )
        attribute_table = {}
        attribute_table[ True, 0 ]  = ckit.Attribute( fg=fg, bg=active_bg_color,   line0=( LINE_LEFT,    line_color ) )
        attribute_table[ True, 1 ]  = ckit.Attribute( fg=fg, bg=active_bg_color,   line0=( 0,            line_color ) )
        attribute_table[ True, 2 ]  = ckit.Attribute( fg=fg, bg=active_bg_color,   line0=( LINE_RIGHT,   line_color ) )
        attribute_table[ False, 0 ] = ckit.Attribute( fg=fg, bg=inactive_bg_color, line0=( LINE_LEFT,    line_color ) )
        attribute_table[ False, 1 ] = ckit.Attribute( fg=fg, bg=inactive_bg_color, line0=( 0,            line_color ) )
        attribute_table[ False, 2 ] = ckit.Attribute( fg=fg, bg=inactive_bg_color, line0=( LINE_RIGHT,   line_color ) )

        # テキスト塗りつぶし
        self.window.putString( self.x, self.y, self.width, 1, attr, " " * self.width )

        # アイテム
        x = self.x
        y = self.y
        width = self.width
        height = self.height
        offset = -self.scroll_pos

        for i, item in enumerate(self.items):
            active = i==self.selection
            name = item[0]
            item_width = self.window.getStringWidth(name)
            if item_width>TabBarWidget.MAX_ITEM_WIDTH:
                name = ckit.adjustStringWidth( self.window, name, TabBarWidget.MAX_ITEM_WIDTH, align=ckit.ALIGN_LEFT, ellipsis=ckit.ELLIPSIS_RIGHT )
                item_width = TabBarWidget.MAX_ITEM_WIDTH
            self.window.putString( x, y, width, height, attribute_table[active,0], " ", offset=offset )
            offset += 1
            self.window.putString( x, y, width-1, height, attribute_table[active,1], name, offset=offset )
            offset += item_width
            if i<len(self.items)-1:
                self.window.putString( x, y, width, height, attribute_table[active,1], " ", offset=offset )
            else:
                self.window.putString( x, y, width, height, attribute_table[active,2], " ", offset=offset )
            offset += 1

## @} widget

