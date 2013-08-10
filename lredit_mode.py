import ckit
from ckit.ckit_const import *

import lredit_lexer
import lredit_misc

Mode = ckit.Mode


## @addtogroup textwidget
## @{

#--------------------------------------------------------------------

## Pythonモード
class PythonMode(Mode):

    name = "python"
    tab_by_space = True

    def __init__(self):
        Mode.__init__(self)
        self.lexer = lredit_lexer.PythonLexer()
        self.completion = ckit.WordCompletion()

    @staticmethod
    def staticconfigure(window):
        Mode.staticconfigure(window)
        ckit.callConfigFunc("staticconfigure_PythonMode",window)

    def configure( self, edit ):
        Mode.configure( self, edit )
        ckit.callConfigFunc("configure_PythonMode",self,edit)


## JavaScriptモード
class JavaScriptMode(Mode):

    name = "javascript"

    def __init__(self):
        Mode.__init__(self)
        self.lexer = lredit_lexer.JavaScriptLexer()
        self.completion = ckit.WordCompletion()

    @staticmethod
    def staticconfigure(window):
        Mode.staticconfigure(window)
        ckit.callConfigFunc("staticconfigure_JavaScriptMode",window)

    def configure( self, edit ):
        Mode.configure( self, edit )
        ckit.callConfigFunc("configure_JavaScriptMode",self,edit)


## C言語モード
class CMode(Mode):

    name = "c"

    def __init__(self):
        Mode.__init__(self)
        self.lexer = lredit_lexer.CLexer()
        self.completion = ckit.WordCompletion()

    @staticmethod
    def staticconfigure(window):
        Mode.staticconfigure(window)
        ckit.callConfigFunc("staticconfigure_CMode",window)

    def configure( self, edit ):
        Mode.configure( self, edit )
        ckit.callConfigFunc("configure_CMode",self,edit)


## C++モード
class CppMode(Mode):

    name = "c++"

    def __init__(self):
        Mode.__init__(self)
        self.lexer = lredit_lexer.CppLexer()
        self.completion = ckit.WordCompletion()

    @staticmethod
    def staticconfigure(window):
        Mode.staticconfigure(window)
        ckit.callConfigFunc("staticconfigure_CppMode",window)

    def configure( self, edit ):
        Mode.configure( self, edit )
        ckit.callConfigFunc("configure_CppMode",self,edit)


## C#モード
class CsharpMode(Mode):

    name = "c#"

    def __init__(self):
        Mode.__init__(self)
        self.lexer = lredit_lexer.CsharpLexer()
        self.completion = ckit.WordCompletion()

    @staticmethod
    def staticconfigure(window):
        Mode.staticconfigure(window)
        ckit.callConfigFunc("staticconfigure_CsharpMode",window)

    def configure( self, edit ):
        Mode.configure( self, edit )
        ckit.callConfigFunc("configure_CsharpMode",self,edit)


## Javaモード
class JavaMode(Mode):

    name = "java"

    def __init__(self):
        Mode.__init__(self)
        self.lexer = lredit_lexer.JavaLexer()
        self.completion = ckit.WordCompletion()

    @staticmethod
    def staticconfigure(window):
        Mode.staticconfigure(window)
        ckit.callConfigFunc("staticconfigure_JavaMode",window)

    def configure( self, edit ):
        Mode.configure( self, edit )
        ckit.callConfigFunc("configure_JavaMode",self,edit)


## GLSLモード
class GlslMode(Mode):

    name = "glsl"

    def __init__(self):
        Mode.__init__(self)
        self.lexer = lredit_lexer.GlslLexer()
        self.completion = ckit.WordCompletion()

    @staticmethod
    def staticconfigure(window):
        Mode.staticconfigure(window)
        ckit.callConfigFunc("staticconfigure_GlslMode",window)

    def configure( self, edit ):
        Mode.configure( self, edit )
        ckit.callConfigFunc("configure_GlslMode",self,edit)


## XMLモード
class XmlMode(Mode):

    name = "xml"

    def __init__(self):
        Mode.__init__(self)
        self.lexer = lredit_lexer.XmlLexer()
        self.completion = ckit.WordCompletion()

    @staticmethod
    def staticconfigure(window):
        Mode.staticconfigure(window)
        ckit.callConfigFunc("staticconfigure_XmlMode",window)

    def configure( self, edit ):
        Mode.configure( self, edit )
        ckit.callConfigFunc("configure_XmlMode",self,edit)


## HTMLモード
class HtmlMode(Mode):

    name = "html"

    def __init__(self):
        Mode.__init__(self)
        self.lexer = lredit_lexer.HtmlLexer()
        self.completion = ckit.WordCompletion()

    @staticmethod
    def staticconfigure(window):
        Mode.staticconfigure(window)
        ckit.callConfigFunc("staticconfigure_HtmlMode",window)

    def configure( self, edit ):
        Mode.configure( self, edit )
        ckit.callConfigFunc("configure_HtmlMode",self,edit)


## Makefileモード
class MakefileMode(Mode):

    name = "makefile"

    def __init__(self):
        Mode.__init__(self)
        self.lexer = lredit_lexer.MakefileLexer()
        self.completion = ckit.WordCompletion()

    @staticmethod
    def staticconfigure(window):
        Mode.staticconfigure(window)
        ckit.callConfigFunc("staticconfigure_MakefileMode",window)

    def configure( self, edit ):
        Mode.configure( self, edit )
        ckit.callConfigFunc("configure_MakefileMode",self,edit)


## Batchモード
class BatchMode(Mode):

    name = "batch"

    def __init__(self):
        Mode.__init__(self)
        self.lexer = lredit_lexer.BatchLexer()
        self.completion = ckit.WordCompletion()

    @staticmethod
    def staticconfigure(window):
        Mode.staticconfigure(window)
        ckit.callConfigFunc("staticconfigure_BatchMode",window)

    def configure( self, edit ):
        Mode.configure( self, edit )
        ckit.callConfigFunc("configure_BatchMode",self,edit)

## @} textwidget

