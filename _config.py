from lredit import *


# customization of MainWindow
def configure(window):


    #----------------------------------------------
    # Generic edit config

    # tab width and indent width
    Mode.tab_width = 4

    # make TAB character visible
    Mode.show_tab = True

    # make space character visible
    Mode.show_space = False

    # make full-width space character visible
    Mode.show_wspace = True

    # make line-end visible
    Mode.show_lineend = True

    # make end-of-fileline visible
    Mode.show_fileend = True

    # cancel selection when text is copied into clipboard
    Mode.cancel_selection_on_copy = False

    # copy current line if text is not selected
    Mode.copy_line_if_not_selected = True

    # cut current line if text is not selected
    Mode.cut_line_if_not_selected = True


    #----------------------------------------------
    # Specific mode config

    # use space character instead of TAB
    PythonMode.tab_by_space = True


    #----------------------------------------------
    # key binding

    # F3 : search next
    window.keymap[ "F3" ] = window.command.SearchNext

    # Shift-F3 : search previous
    window.keymap[ "S-F3" ] = window.command.SearchPrev


    #----------------------------------------------
    # extension menu

    window.ext_menu_items = [
        ( "Another Pane",      "C-W", window.command.AnotherPane ),
        ( "Project Files",     "C-P", window.command.ProjectFileList ),
        ( "Recent Files",      "C-H", window.command.RecentFileList ),
        ( "Bookmark List",     "C-M", window.command.BookmarkList ),
        ( "Document List",     "C-D", window.command.DocumentList ),
        ( "Outline Analysis",  "C-O", window.command.Outline ),
        ( "Search Result",     "C-S", window.command.SearchResultList ),
    ]


    #----------------------------------------------
    # user defined command

    def command_MyTool1(info):
        # print to log pane
        print( "Hello World!" )

    def command_MyTool2(info):
        # insert text into active edit
        edit = window.activeEditPane().edit
        edit.modifyText( text="Hello World!" )

    window.launcher.command_list += [
        ( "MyTool1",  command_MyTool1 ),
        ( "MyTool2",  command_MyTool2 ),
    ]

    #----------------------------------------------
    # user menu

    def command_MyMenu(info):

        items = [
            ( "My Tool 1", "C-1", command_MyTool1 ),
            ( "My Tool 2", "C-2", command_MyTool2 ),
        ]

        window.menu( None, items )

    window.keymap[ "C-T" ] = command_MyMenu


    #----------------------------------------------
    # customization of menu bar

    # add [Tool] > [Extra]
    window.insertMenu( ("tool","custom_tools_end"),
        MenuNode(
            "extra", "&Extra",
            items=[
                MenuNode( "focus_left",   "Focus to &Left", window.command.FocusLeftEdit ),
                MenuNode( "focus_right",  "Focus to &Right", window.command.FocusRightEdit ),
            ]
        )
    )

    # open specified document
    class command_SwitchDocument:

        def __init__( self, doc ):
            self.doc = doc

        def __call__( self, info ):
            window.activeOpen( doc=self.doc )

    # function to display opened documents
    def menuitems_Documents():
        items = []
        i = 0
        items.append( MenuNode( separator=True ) )
        for edit in window.edit_list:
            name = edit.doc.getName()
            items.append( MenuNode( "doc_%d"%i, name, command_SwitchDocument(edit.doc) ) )
            i+=1
        items.append( MenuNode( separator=True ) )
        return items

    # add menu items of documents at the bottom of [View] menu
    window.appendMenu( ("view",), menuitems_Documents )


    #----------------------------------------------
    # misc tools

    # remove continuing overlapped lines
    def command_Unique(info):

        edit = window.activePane().edit

        previous_line = [None]
        def func( text, info ):
            if previous_line[0]==text:
                return False
            else:
                previous_line[0]=text
                return True

        edit.filterLines(func)

    # search by previous condition and bookmark the found lines
    def command_SearchAndBookmark(info):

        if not window.search_object: return

        edit = window.activePane().edit
        point = edit.pointDocumentBegin()
        count = 0
        
        while point:
            point = edit.search( search_object=window.search_object, point=point, direction=1, move_cursor=False, select=False, hitmark=False, paint=False, message=False )
            if point:
                edit.bookmark( point.line, [ 1 ], paint=False )
                point.line += 1
                point.index = 0
                count += 1
        
        msg = "found %d lines" % ( count )
        window.setStatusMessage( msg, 3000 )

        window.paint()

    window.launcher.command_list += [
        ( "Unique",             command_Unique ),
        ( "SearchAndBookmark",  command_SearchAndBookmark ),
    ]


    #----------------------------------------------
    # association between filename pattern and mode

    window.fileext_list = [
        ( "*.ini", "ini" ),
        ( "*.py *.pyw *.pys", "python" ),
        ( "*.pl", "perl" ),
        ( "*.js", "javascript" ),
        ( "*.cpp *.cc *.cxx *.hpp *.hh *.hxx *.h", "c++" ),
        ( "*.c *.h", "c" ),
        ( "*.mm *.h", "objective-c++" ),
        ( "*.m *.h", "objective-c" ),
        ( "*.cs", "c#" ),
        ( "*.java", "java" ),
        ( "*.vert *.frag *.geo", "glsl" ),
        ( "*.xml", "xml" ),
        ( "*.html *.htm", "html" ),
        ( "makefile *.mk", "makefile" ),
        ( "*.bat", "batch" ),
        ( "*.sql", "sql" ),
        ( "*", "text" ),
    ]

    #----------------------------------------------
    # add mode

    # lexer class of Ini file
    class IniLexer(RegexLexer):

        def __init__(self):

            RegexLexer.__init__(self)

            self.rule_map['root'] = [
                (r'\s+', Token_Text),
                (r'[;#].*?$', Token_Comment),
                (r'\[.*?\]$', Token_Keyword),
                (r'(.*?)([ \t]*=[ \t]*)(.*?)$', ( Token_Name, Token_Text, Token_String) ),
                (None, Token_Text)
            ]

    # mode definition of Ini file
    class IniMode(Mode):

        name = "ini"

        def __init__(self):
            Mode.__init__(self)
            self.lexer = IniLexer()
            self.completion = WordCompletion()

        @staticmethod
        def staticconfigure(window):
            Mode.staticconfigure(window)
            callConfigFunc("staticconfigure_IniMode",window)

        def configure( self, edit ):
            Mode.configure( self, edit )
            callConfigFunc("configure_IniMode",self,edit)

    # add ini file mode
    window.mode_list.append( IniMode )

    # association of ini filename pattern
    window.fileext_list.insert( 0, ( "*.ini", "ini" ) )



#----------------------------------------------
# customization of PythonMode

# configuration of PythonMode object (such as key binding)
def configure_PythonMode( mode, edit ):

    # F6 : output 'Hello' in log pane
    def command_Print( info ):
        print( "Hello" )

    edit.keymap[ "F6" ] = command_Print


# static configuration of PythonMode class (such as menu bar customization)
def staticconfigure_PythonMode(window):

    # command to insert 'Hello Python!' into active edit area
    def command_InsertHello(info):
        edit = window.activeEditPane().edit
        edit.modifyText( text="Hello Python!" )

    # function to check if the active edit area is Python mode
    def isPythonMode():
        return isinstance( window.activeEditPaneMode(), PythonMode )

    # add menu item to display only when active mode is Python mode
    window.insertMenu( ("tool","custom_tools_end"),  MenuNode( "insert_hello", "Insert &Hello", command_InsertHello, visible=isPythonMode ) )


