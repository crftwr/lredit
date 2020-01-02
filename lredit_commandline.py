import os

import ckit
from ckit.ckit_const import *

import lredit_misc
import lredit_native
import lredit_debug


## @addtogroup commandline
## @{

#--------------------------------------------------------------------

## コマンドラインからのコマンド実行機能
class commandline_Launcher:

    def __init__( self, main_window ):
        self.main_window = main_window
        self.command_list = []

    def onCandidate( self, update_info ):

        basedir = "."

        left = update_info.text[ : update_info.selection[0] ]
        left_lower = left.lower()
        pos_arg = left.rfind(";")+1
        arg = left[ pos_arg : ]
        pos_dir = max( arg.rfind("/")+1, arg.rfind("\\")+1 )
        directory = arg[:pos_dir].strip()
        directory_lower = directory.lower()
        name_prefix = arg[pos_dir:].lower()

        dirname_list = []
        filename_list = []
        candidate_list = []
        
        if len(arg)>0:

            try:
                path = ckit.joinPath( basedir, directory )

                drive, tail = os.path.splitdrive(path)
                unc = ( drive.startswith("\\\\") or drive.startswith("//") )

                if unc:
                    lredit_misc.checkNetConnection(path)
                if unc and not tail:
                    servername = drive.replace('/','\\')
                    infolist = lredit_native.enumShare(servername)
                    for info in infolist:
                        if info[1]==0:
                            if info[0].lower().startswith(name_prefix):
                                if ckit.pathSlash():
                                    dirname_list.append( info[0] + "/" )
                                else:
                                    dirname_list.append( info[0] + "\\" )
                else:
                    infolist = lredit_native.findFile( ckit.joinPath(path,'*'), use_cache=True )
                    for info in infolist:
                        if info[0].lower().startswith(name_prefix):
                            if info[3] & ckit.FILE_ATTRIBUTE_DIRECTORY:
                                if ckit.pathSlash():
                                    dirname_list.append( info[0] + "/" )
                                else:
                                    dirname_list.append( info[0] + "\\" )
                            else:                    
                                filename_list.append( info[0] )
            except:
                pass

        for item in self.command_list:
            item_lower = item[0].lower()
            if item_lower.startswith(left_lower) and len(item_lower)!=len(left_lower):
                candidate_list.append( item[0] )

        for item in self.main_window.enumCommand():
            item_lower = item.lower()
            if item_lower.startswith(left_lower) and len(item_lower)!=len(left_lower):
                candidate_list.append( item )

        return dirname_list + filename_list + candidate_list

    def onEnter( self, commandline, text, mod ):
        
        args = text.split(';')
        
        for i in range(len(args)):
            args[i] = args[i].strip()
        
        command_name = args[0].lower()
        
        def found(command):
            
            info = ckit.CommandInfo()
            info.args = args[1:]
            info.mod = mod

            commandline.planCommand( command, info, text )
            commandline.quit()

        for command in self.command_list:
            if command[0].lower() == command_name:
                found(command[1])
                return True

        for command in self.main_window.enumCommand():
            if command.lower() == command_name:
                found( getattr(self.main_window.command, command) )
                return True

        return False
    
    def onStatusString( self, text ):
        text_lower = text.lower()
        for command in self.command_list:
            if command[0].lower() == text_lower:
                return "OK"
        return None
    

## コマンドラインからのファイルオープン機能
class commandline_Open:

    def __init__( self, main_window ):
        self.main_window = main_window

    def onCandidate( self, update_info ):
        return []

    def onEnter( self, commandline, text, mod ):
        
        args = text.split(';')
        
        for arg in args:
            if not os.path.exists(arg) or not os.path.isfile(arg):
                return False

        info = ckit.CommandInfo()
        info.args = args
        info.mod = 0

        commandline.planCommand( self.main_window.command.Open, info, text )
        commandline.quit()

        return True
    
    def onStatusString( self, text ):
        args = text.split(';')
        for arg in args:
            if not os.path.exists(arg) or not os.path.isfile(arg):
                return None
        return "OK"


## コマンドラインからの文書選択機能
class commandline_Document:

    def __init__( self, main_window ):
        self.main_window = main_window

    def onCandidate( self, update_info ):

        left = update_info.text[ : update_info.selection[0] ]
        left_lower = left.lower()

        candidate_list = []
        
        for edit in self.main_window.edit_list:
            docname = edit.doc.getName()
            docname_lower = docname.lower()
            if docname_lower.startswith(left_lower) and len(docname_lower)!=len(left_lower):
                candidate_list.append( docname )

        return candidate_list

    def onEnter( self, commandline, text, mod ):

        text_lower = text.lower()

        for edit in self.main_window.edit_list:
            if edit.doc.getName().lower() == text_lower:

                info = ckit.CommandInfo()
                info.args = [ text ]
                info.mod = 0

                commandline.planCommand( self.main_window.command.Document, info, text )
                commandline.quit()

                return True
       
        return False
    
    def onStatusString( self, text ):
        text_lower = text.lower()
        for edit in self.main_window.edit_list:
            if edit.doc.getName().lower() == text_lower:
                return "OK"
        return None


## コマンドラインからのモード切替機能
class commandline_Mode:

    def __init__( self, main_window ):
        self.main_window = main_window

    def onCandidate( self, update_info ):

        left = update_info.text[ : update_info.selection[0] ]
        left_lower = left.lower()

        candidate_list = []
        
        for mode in self.main_window.mode_list:
            mode_name_lower = mode.__name__.lower()
            if mode_name_lower.startswith(left_lower) and len(mode_name_lower)!=len(left_lower):
                candidate_list.append( mode.__name__ )

        return candidate_list

    def onEnter( self, commandline, text, mod ):

        text_lower = text.lower()

        for mode in self.main_window.mode_list:
            if mode.__name__.lower() == text_lower:

                info = ckit.CommandInfo()
                info.args = [ text ]
                info.mod = 0

                commandline.planCommand( self.main_window.command.Mode, info, text )
                commandline.quit()

                return True
        
        return False
    
    def onStatusString( self, text ):
        text_lower = text.lower()
        for mode in self.main_window.mode_list:
            if mode.__name__.lower() == text_lower:
                return "OK"
        return None


## コマンドラインからのマイナーモード切替機能
class commandline_MinorMode:

    def __init__( self, main_window ):
        self.main_window = main_window

    def onCandidate( self, update_info ):

        left = update_info.text[ : update_info.selection[0] ]
        left_lower = left.lower()

        candidate_list = []
        
        for mode in self.main_window.minor_mode_list:
            mode_name_lower = mode.__name__.lower()
            if mode_name_lower.startswith(left_lower) and len(mode_name_lower)!=len(left_lower):
                candidate_list.append( mode.__name__ )

        return candidate_list

    def onEnter( self, commandline, text, mod ):

        text_lower = text.lower()

        for mode in self.main_window.minor_mode_list:
            if mode.__name__.lower() == text_lower:

                info = ckit.CommandInfo()
                info.args = [ text ]
                info.mod = 0

                commandline.planCommand( self.main_window.command.MinorMode, info, text )
                commandline.quit()

                return True
        
        return False
    
    def onStatusString( self, text ):
        text_lower = text.lower()
        for mode in self.main_window.minor_mode_list:
            if mode.__name__.lower() == text_lower:
                return "OK"
        return None


## コマンドラインでの計算機能
class commandline_Calculator:

    def __init__(self):
        pass

    def onCandidate( self, update_info ):
        return []
    
    def onEnter( self, commandline, text, mod ):
        
        from math import sin, cos, tan, acos, asin, atan
        from math import e, fabs, log, log10, pi, pow, sqrt

        try:
            result = eval(text)
        except:
            return False
        
        if isinstance(result,int):
            result_string = "%d" % result
        elif isinstance(result,float):
            result_string = "%f" % result
        else:
            return False

        commandline.appendHistory( text )
        
        if result_string!=text:

            print( "%s => %s" % ( text, result_string ) )
            commandline.setText( result_string )
            commandline.selectAll()
        
        return True

    def onStatusString( self, text ):
        return None


## コマンドラインでの 10進 <-> 16進 変換機能
class commandline_Int32Hex:

    def __init__(self):
        pass

    def onCandidate( self, update_info ):
        return []
    
    def onEnter( self, commandline, text, mod ):
    
        def base16to10(src):
            if src[:2].lower() != "0x":
                raise ValueError
            i = int( src, 16 )
            if i<0 or i>0xffffffff:
                raise ValueError
            if i>=0x80000000:
                dst = "%d" % ( -0x80000000 + ( i - 0x80000000 ) )
            else:
                dst = "%d" % i
            return dst    

        def base10to16(src):
            i = int( src, 10 )
            if i<-0x80000000 or i>=0x80000000:
                raise ValueError
            if i<0:
                dst = "0x%08x" % ( 0x80000000 + ( i + 0x80000000 ) )
            else:
                dst = "0x%08x" % i
            return dst
        
        text = text.strip()

        try:
            result_string = base10to16(text)
        except:
            try:
                result_string = base16to10(text)
            except:
                return False    

        commandline.appendHistory( text )
        
        if result_string!=text:

            print( "%s => %s" % ( text, result_string ) )
            commandline.setText( result_string )
            commandline.selectAll()
        
        return True

    def onStatusString( self, text ):
        return None

#--------------------------------------------------------------------

## コマンドライン入力にファイル名を補完候補として提供するクラス
class candidate_Filename():

    def __init__( self, basedir, fixed_items=[] ):
        
        self.basedir = basedir
        self.fixed_items = fixed_items

    def __call__( self, update_info ):
        
        left = update_info.text[ : update_info.selection[0] ]
        pos_dir = max(left.rfind("/")+1,left.rfind("\\")+1)
        directory = left[:pos_dir]
        directory_lower = directory.lower()
        name_prefix = left[pos_dir:].lower()
        
        candidate_set = set()
        candidate_list = []
        
        def appendCandidate(candidate):
            if candidate not in candidate_set:
                candidate_list.append(candidate)
                candidate_set.add(candidate)

        for item in self.fixed_items:
            item_lower = item.lower()
            if item_lower.startswith(directory_lower):
                item_lower = item_lower[ len(directory_lower) : ]
                if item_lower.startswith(name_prefix) and len(item_lower)!=len(name_prefix):
                    appendCandidate( item[ len(directory_lower) : ] )

        try:
            path = ckit.joinPath( self.basedir, directory )

            drive, tail = os.path.splitdrive(path)
            unc = ( drive.startswith("\\\\") or drive.startswith("//") )

            if unc:
                lredit_misc.checkNetConnection(path)
            if unc and not tail:
                servername = drive.replace('/','\\')
                infolist = lredit_native.enumShare(servername)
                for info in infolist:
                    if info[1]==0:
                        if info[0].lower().startswith(name_prefix):
                            if ckit.pathSlash():
                                appendCandidate( info[0] + "/" )
                            else:
                                appendCandidate( info[0] + "\\" )

            else:
                infolist = lredit_native.findFile( ckit.joinPath(path,'*'), use_cache=True )
                for info in infolist:
                    if info[0].lower().startswith(name_prefix):
                        if info[3] & ckit.FILE_ATTRIBUTE_DIRECTORY:
                            if ckit.pathSlash():
                                appendCandidate( info[0] + "/" )
                            else:
                                appendCandidate( info[0] + "\\" )
                        else:                    
                            appendCandidate( info[0] )

        except Exception as e:
            print( e )
        
        return candidate_list, len(directory)

#--------------------------------------------------------------------

## @} commandline

