import ckit
from ckit.ckit_const import *

import lredit_misc


## @addtogroup textwidget
## @{

#--------------------------------------------------------------------

## TextWidget のマイナーモードのベースクラス
class MinorMode:

    name = "-"
    
    def __init__(self):
        pass

    def __str__(self):
        return self.name

    def executeCommand( self, name, info ):

        try:
            command = getattr( self, "command_" + name )
        except AttributeError:
            return False
        
        command(info)
        return True

    def enumCommand(self):
        for attr in dir(self):
            if attr.startswith("command_"):
                yield attr[ len("command_") : ]

    @staticmethod
    def staticconfigure(window):
        pass

    def configure( self, edit ):
        pass


class TestMode(MinorMode):

    name = "test"
    
    def __init__(self):
        MinorMode.__init__(self)
        
    @staticmethod
    def staticconfigure(window):
        MinorMode.staticconfigure(window)
        ckit.callConfigFunc("staticconfigure_TestMode",window)

    def configure( self, edit ):

        MinorMode.configure( self, edit )

        def command_TestMenu(info):
        
            def command_Test1(info):
                edit.modifyText( text="aaaa" )

            def command_Test2(info):
                edit.modifyText( text="bbbb" )

            def command_Test3(info):
                edit.modifyText( text="cccc" )

            items = [
                ( "test1", "C-1", command_Test1 ),
                ( "test2", "C-2", command_Test2 ),
                ( "test3", "C-3", command_Test3 ),
            ]
        
            edit.window.menu( None, items )
            
        edit.keymap[ "C-Return" ] = command_TestMenu

        ckit.callConfigFunc("configure_TestMode",self,edit)

## @} textwidget

