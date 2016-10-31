
# パフォーマンスのために、ここで import するのは IPCのために必要な最小限にとどめる

import sys
import os
import argparse
import json
import ctypes
import time

import importlib.abc
    
class CustomPydFinder(importlib.abc.MetaPathFinder):
    def find_module( self, fullname, path=None ):
        exe_path = os.path.split(sys.argv[0])[0]
        pyd_filename_body = fullname.split(".")[-1]
        pyd_fullpath = os.path.join( exe_path, "lib", pyd_filename_body + ".pyd" )
        if os.path.exists(pyd_fullpath):
            for importer in sys.meta_path:
                if isinstance(importer, self.__class__):
                    continue
                loader = importer.find_module( fullname, None)
                if loader:
                    return loader

sys.meta_path.append(CustomPydFinder())

import ckit
import pyauto

import lredit_resource

#--------------------------------------------------------------------

arg_parser = argparse.ArgumentParser(description=lredit_resource.startupString())
arg_parser.add_argument( "--debug", action="store_true", help="debug mode (development purpose)" )
arg_parser.add_argument( "--profile", action="store_true", help="profile mode (development purpose)" )
arg_parser.add_argument( "--multi", action="store_true", help="force multi-instance" )
arg_parser.add_argument( "--single", action="store_true", help="force single-instance" )
arg_parser.add_argument( "--readonly", dest="readonly", action="store_true", help="open files in read-only mode" )
arg_parser.add_argument( "--text", action="append", nargs='+', help="open file", metavar=("FILENAME","LINE[:INDEX]") )
arg_parser.add_argument( "--project", action="store", nargs=1, help="load project file", metavar="FILENAME" )
arg_parser.add_argument( "--compare", action="store", nargs=2, help="compare two files", metavar="FILENAME" )
arg_parser.add_argument( "file", nargs="*", help="files to open normally" )

args = arg_parser.parse_args( ckit.getArgv()[1:] )

# Jsonに格納可能な形式に変換
if 1:
    text_list = []
    if args.text:
        import re
        re_pattern = re.compile( "([0-9]+)(:([0-9]+))?" )
        for item in args.text:
            if len(item)>1:
                re_result = re_pattern.match(item[1])
                line = int(re_result.group(1))
                if re_result.group(3):
                    index = int(re_result.group(3))
                else:
                    index = 1
            else:
                line = 1
                index = 1
            text_list.append( ( os.path.abspath(item[0]), line, index ) )

    if args.project:
        args.project = [ os.path.abspath(filename) for filename in args.project ]
    if args.compare:
        args.compare = [ os.path.abspath(filename) for filename in args.compare ]
    if args.file:
        args.file = [ os.path.abspath(filename) for filename in args.file ]

    arg_data = {}
    arg_data["readonly"] = args.readonly
    arg_data["text"] = text_list
    arg_data["project"] = args.project
    arg_data["compare"] = args.compare
    arg_data["file"] = args.file

#--------------------------------------------------------------------

instance_mutex = ctypes.windll.kernel32.CreateMutexW( 0, 0, "LreditInstanceMutex" )
instance_exists = ctypes.windll.kernel32.GetLastError()==183 # ERROR_ALREADY_EXISTS

def findExistingLreditWindow( retry=50, retry_interval=0.1 ):
    found = [None]
    def callback( wnd, arg ):
        if wnd.getClassName()=="LreditWindowClass":
            while True:
                parent = wnd.getParent()
                if parent != pyauto.Window.getDesktop():
                    wnd = parent
                    continue
                owner = wnd.getOwner()
                if owner:
                    wnd = owner
                    continue
                break
            found[0] = wnd
            return False
        return True

    for i in range(retry):
        pyauto.Window.enum( callback, None )
        if found[0]: return found[0]
        time.sleep(retry_interval)

    return None

def sendIpc(wnd):

    print( "another lredit instance already exists." )
    print( "sending Ipc data." )

    ckit.TextWindow.sendIpc( wnd.getHWND(), json.dumps(arg_data) )

    print( "done." )

if instance_exists:

    if args.multi:
        ipc = False
    elif args.single:
        ipc = True
    else:
        # Ctrlキーが押されている場合は、新しいウインドウを開くか確認する
        lctrl_state = pyauto.Input.getAsyncKeyState(ckit.VK_LCONTROL)
        rctrl_state = pyauto.Input.getAsyncKeyState(ckit.VK_RCONTROL)
        if (lctrl_state & 0x8000) or (rctrl_state & 0x8000):

            MB_YESNOCANCEL = 3
            MB_YESNO = 4
            IDCANCEL = 2
            IDYES = 6
            IDNO = 7

            result = ctypes.windll.user32.MessageBoxW(
                0,
                ckit.strings["msgbox_ask_new_window"],
                ckit.strings["msgbox_title_new_window"],
                MB_YESNO )

            if result == IDYES:
                ipc = False
            elif result == IDNO:
                ipc = True
            else:
                sys.exit(0)
        else:
            ipc = True

    if ipc:
        existing_lredit_wnd = findExistingLreditWindow()
        if existing_lredit_wnd:
            sendIpc(existing_lredit_wnd)
            ctypes.windll.kernel32.CloseHandle(instance_mutex)
            sys.exit(0)

#--------------------------------------------------------------------

# IPCのために必要でないモジュールはここで import する

import shutil
import threading

import lredit_mainwindow
import lredit_debug
import lredit_misc


ckit.registerWindowClass( "Lredit" )
ckit.registerCommandInfoConstructor( ckit.CommandInfo )

# exeと同じ位置にある設定ファイルを優先する
if os.path.exists( os.path.join( ckit.getAppExePath(), 'config.py' ) ):
    ckit.setDataPath( ckit.getAppExePath() )
else:
    ckit.setDataPath( os.path.join( ckit.getAppDataPath(), lredit_resource.lredit_dirname ) )
    if not os.path.exists(ckit.dataPath()):
        os.mkdir(ckit.dataPath())

default_config_filename = os.path.join( ckit.getAppExePath(), '_config.py' )
config_filename = os.path.join( ckit.dataPath(), 'config.py' )
ini_filename = os.path.join( ckit.dataPath(), 'lredit.ini' )

# config.py がどこにもない場合は作成する
if not os.path.exists(config_filename) and os.path.exists(default_config_filename):
    shutil.copy( default_config_filename, config_filename )

_main_window = lredit_mainwindow.MainWindow(
    config_filename = config_filename,
    ini_filename = ini_filename,
    debug = args.debug,
    profile = args.profile )

_main_window.registerStdio()

ckit.initTemp("lredit_")

_main_window.configure()

_main_window.startup(arg_data)

_main_window.messageLoop( name="top" )

_main_window.saveState()

lredit_debug.enableExitTimeout()

_main_window.unregisterStdio()

ckit.JobQueue.cancelAll()
ckit.JobQueue.joinAll()

ckit.destroyTemp()

_main_window.destroy()

lredit_debug.disableExitTimeout()

ctypes.windll.kernel32.CloseHandle(instance_mutex)

# スレッドが残っていても強制終了
if not args.debug:
    os._exit(0)

