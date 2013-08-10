import os
import sys
import time
import gc
import re
import cProfile
import threading
import fnmatch
import difflib
import configparser
import json
import traceback
import ctypes
import msvcrt
import locale

import pyauto
import ckit
from ckit.ckit_const import *

import lredit_mode
import lredit_minormode
import lredit_project
import lredit_bookmark
import lredit_isearch
import lredit_grep
import lredit_tags
import lredit_zenhan
import lredit_statusbar
import lredit_tabbar
import lredit_msgbox
import lredit_listwindow
import lredit_configmenu
import lredit_commandline
import lredit_history
import lredit_wallpaper
import lredit_misc
import lredit_native
import lredit_resource
import lredit_debug

CommandSequence = ckit.CommandSequence


## @addtogroup mainwindow
## @{


#--------------------------------------------------------------------

class MouseInfo:
    def __init__( self, mode, **args ):
        self.mode = mode
        self.__dict__.update(args)

#--------------------------------------------------------------------

## ペインのベースクラス
class Pane:

    def __init__(self):
        pass

    def widget(self):
        return None

## 編集ペインクラス
class EditPane(Pane):

    def __init__(self):
        Pane.__init__(self)
        self.tab = None
        self.edit = None
        self.footer_paint_hook = None
        self.edit_list = []

    def widget(self):
        return self.edit

## ログペインクラス
class LogPane(Pane):

    def __init__(self):
        Pane.__init__(self)
        self.edit = None

    def widget(self):
        return self.edit

#--------------------------------------------------------------------

class JumpItem:

    def __init__(self,text):
        self.text = text

    def shiftLineNo( self, filename, left, old_right, new_right ):
        pass

    def __call__(self):
        pass

class GrepJumpItem(JumpItem):

    def __init__( self, main_window, filename, lineno, search_object, text ):

        JumpItem.__init__(self,text)

        self.main_window = main_window
        self.filename = filename
        self.lineno = lineno
        self.search_object = search_object

    def shiftLineNo( self, filename, left, old_right, new_right ):
        if self.filename==filename and self.lineno>left:
            if self.lineno>=old_right:
                self.lineno += new_right-old_right
                return True
            elif self.lineno<new_right:
                self.lineno = new_right
                return True
        return False

    def __call__(self):

        self.main_window.activeOpen( filename=self.filename, lineno=self.lineno )
        self.main_window.activeEditPane().edit.search( search_object=self.search_object, direction=1, oneline=True, message=False )
        self.main_window.command.FocusEdit()

        for i, item in enumerate(self.main_window.jump_list):
            if item == self:
                self.main_window.jump_selection = i
                break

        msg = "[%d/%d] %s:%d" % ( self.main_window.jump_selection+1, len(self.main_window.jump_list), self.filename, self.lineno+1 )
        self.main_window.setStatusMessage( msg, 3000 )


class CompareJumpItem(JumpItem):

    def __init__( self, main_window, filename1, lineno1, filename2, lineno2, text ):

        JumpItem.__init__(self,text)

        self.main_window = main_window
        self.filename1 = filename1
        self.lineno1 = lineno1
        self.filename2 = filename2
        self.lineno2 = lineno2

    def shiftLineNo( self, filename, left, old_right, new_right ):
        if self.filename1==filename and self.lineno1>left:
            if self.lineno1>=old_right:
                self.lineno1 += new_right-old_right
                return True
            elif self.lineno1<new_right:
                self.lineno1 = new_right
                return True
        if self.filename2==filename and self.lineno2>left:
            if self.lineno2>=old_right:
                self.lineno2 += new_right-old_right
                return True
            elif self.lineno2<new_right:
                self.lineno2 = new_right
                return True
        return False

    def __call__(self):

        self.main_window.leftOpen( filename=self.filename1, lineno=self.lineno1 )
        self.main_window.rightOpen( filename=self.filename2, lineno=self.lineno2 )
        self.main_window.command.FocusEdit()

        for i, item in enumerate(self.main_window.jump_list):
            if item == self:
                self.main_window.jump_selection = i
                break


#--------------------------------------------------------------------

REGION_LEFT_TAB             = 1<<1
REGION_LEFT_EDIT            = 1<<2
REGION_LEFT_FOOTER          = 1<<3

REGION_RIGHT_TAB            = 1<<4
REGION_RIGHT_EDIT           = 1<<5
REGION_RIGHT_FOOTER         = 1<<6

REGION_EDIT_SEPARATOR       = 1<<7

REGION_LOG                  = 1<<9
REGION_STATUS_BAR           = 1<<10

REGION_EDIT                 = REGION_LEFT_TAB | REGION_LEFT_EDIT | REGION_LEFT_FOOTER | REGION_RIGHT_TAB | REGION_RIGHT_EDIT | REGION_RIGHT_FOOTER | REGION_EDIT_SEPARATOR
REGION_ALL                  = 0xffffffff

## メインウインドウ
#
#  テキストエディタの主な機能を実現しているクラスです。\n\n
#  設定ファイル config.py の configure に渡される window 引数は、MainWindow クラスのオブジェクトです。
#
class MainWindow( ckit.Window ):

    FOCUS_EDIT = 0
    FOCUS_LOG = 1

    FOCUS_EDIT_LEFT  = 10
    FOCUS_EDIT_RIGHT = 11

    def __init__( self, config_filename, ini_filename, debug=False, profile=False ):

        self.initialized = False

        self.config_filename = config_filename

        self.debug = debug
        self.profile = profile

        self.ini = configparser.RawConfigParser()
        self.ini_filename = ini_filename

        self.loadState()

        self.loadTheme()

        self.title = ""

        ckit.Window.__init__(
            self,
            x=self.ini.getint( "GEOMETRY", "x" ),
            y=self.ini.getint( "GEOMETRY", "y" ),
            width=self.ini.getint( "GEOMETRY", "width" ),
            height=self.ini.getint( "GEOMETRY", "height" ),
            font_name = self.ini.get( "FONT", "name" ),
            font_size = self.ini.getint( "FONT", "size" ),
            bg_color = ckit.getColor("bg"),
            cursor0_color = ckit.getColor("cursor0"),
            cursor1_color = ckit.getColor("cursor1"),
            border_size = 2,
            title_bar = True,
            title = "",
            cursor = True,
            sysmenu=True,
            show=False,
            activate_handler = self._onActivate,
            close_handler = self._onClose,
            move_handler = self._onMove,
            size_handler = self._onSize,
            keydown_handler = self._onKeyDown,
            keyup_handler = self._onKeyUp,
            char_handler = self._onChar,
            lbuttondown_handler = self._onLeftButtonDownOutside,
            lbuttonup_handler = self._onLeftButtonUpOutside,
            mbuttondown_handler = self._onMiddleButtonDownOutside,
            mbuttonup_handler = self._onMiddleButtonUpOutside,
            rbuttondown_handler = self._onRightButtonDownOutside,
            rbuttonup_handler = self._onRightButtonUpOutside,
            lbuttondoubleclick_handler = self._onLeftButtonDoubleClickOutside,
            mousemove_handler = self._onMouseMoveOutside,
            mousewheel_handler= self._onMouseWheelOutside,
            dropfiles_handler = self._onDropFiles,
            ipc_handler = self._onIpc,
            )

        self.messageloop_list = []
        self.quit_request_list = []

        self.updateColor()

        if self.ini.getint( "DEBUG", "detect_block" ):
            lredit_debug.enableBlockDetector()

        if self.ini.getint( "DEBUG", "print_errorinfo" ):
            lredit_debug.enablePrintErrorInfo()

        self.setCursorPos( -1, -1 )

        self.focus_top = MainWindow.FOCUS_EDIT
        self.focus_edit = MainWindow.FOCUS_EDIT_LEFT
        self.left_edit_pane_width = self.ini.getint( "GEOMETRY", "left_edit_pane_width" )
        self.log_pane_height = self.ini.getint( "GEOMETRY", "log_pane_height" )

        self.command = ckit.CommandMap(self)

        self.status_bar = lredit_statusbar.StatusBar()
        self.status_bar_layer = lredit_statusbar.SimpleStatusBarLayer()
        self.status_bar_resistered = False
        self.status_bar_paint_hook = None
        self.commandline_edit = None
        self.progress_bar = None

        self.project = None
        self.bookmarks = lredit_bookmark.BookmarkTable()
        self.bookmarks.load( self.ini, "BOOKMARK" )
        self.edit_list = []
        self.jump_list = []
        self.jump_selection = None
        self.document_next_pivot = None

        self.keymap = ckit.Keymap()
        self.mode_list = []
        self.minor_mode_list = []
        self.fileext_list = []
        self.commandline_list = []

        self.filename_history = lredit_history.History(1000)
        self.filename_history.load( self.ini, "FILENAME" )
        self.commandline_history = lredit_history.History(1000)
        self.commandline_history.load( self.ini, "COMMANDLINE" )
        self.search_history = lredit_history.History(100)
        self.search_history.load( self.ini, "SEARCH" )
        self.replace_history = lredit_history.History(100)
        self.replace_history.load( self.ini, "REPLACE" )
        self.grep_location_history = lredit_history.History(100)
        self.grep_location_history.load( self.ini, "GREP", "location" )
        self.grep_filename_pattern_history = lredit_history.History(100)
        self.grep_filename_pattern_history.load( self.ini, "GREP", "filename_pattern" )
        if not self.grep_filename_pattern_history.items : self.grep_filename_pattern_history.append("*")
        self.grep_dirname_exclude_pattern_history = lredit_history.History(100)
        self.grep_dirname_exclude_pattern_history.load( self.ini, "GREP", "dirname_exclude_pattern" )
        if not self.grep_dirname_exclude_pattern_history.items : self.grep_dirname_exclude_pattern_history.append(".svn CVS RCS")

        self.launcher = lredit_commandline.commandline_Launcher(self)

        self.keydown_hook = None
        self.char_hook = None
        self.mouse_event_mask = False
        self.mouse_click_info = None

        self.mod_hooks = []
        self.mod = 0

        self.search_object = None
        self.migemo = None
        self.tags_list = []
        self.tags_jump_history = []

        self.task_queue_stack = []
        self.synccall = ckit.SyncCall()
        self.idle_count = 0

        self.user_input_ownership = threading.Lock()

        self.left_edit_pane = EditPane()
        self.left_edit_pane.tab = lredit_tabbar.TabBarWidget( self, 0, 0, self.leftEditPaneWidth(), 1, self._onTabSelectionChanged )

        self.right_edit_pane = EditPane()
        self.right_edit_pane.tab = lredit_tabbar.TabBarWidget( self, self.leftEditPaneWidth() + self.editSeparatorWidth(), 0, self.rightEditPaneWidth(), 1, self._onTabSelectionChanged )

        self.log_pane = LogPane()
        self.log_pane.edit = ckit.TextWidget( self, 0, 0, 0, 0, message_handler=self.setStatusMessage )
        doc = ckit.Document( filename=None, mode=self.createModeFromName("text") )
        doc.setReadOnly(True)
        doc.setBGColor(None)
        self.log_pane.edit.setDocument(doc)
        self.log_pane.edit.scroll_margin_v = 0
        self.log_pane.edit.scroll_bottom_adjust = True
        self.log_pane.edit.show_lineno = False
        self.log_pane.edit.doc.mode.show_tab = False
        self.log_pane.edit.doc.mode.show_space = False
        self.log_pane.edit.doc.mode.show_wspace = False
        self.log_pane.edit.doc.mode.show_lineend = False
        self.log_pane.edit.doc.mode.show_fileend = False

        self.setTimer( self.onTimerJob, 10 )
        self.setTimer( self.onTimerSyncCall, 10 )
        self.setTimer( self.onTimerIdle, 10 )

        lredit_misc.registerNetConnectionHandler( self._onCheckNetConnection )

        try:
            self.createThemePlane()
        except:
            traceback.print_exc()
            #lredit_debug.printErrorInfo()

        try:
            self.wallpaper = None
            self.updateWallpaper()
        except:
            self.wallpaper = None

        self.updateCursor()

        self.initialized = True

        self.paint()

        self.show(True)

    ## 破棄する
    def destroy(self):
        lredit_debug.disableBlockDetector()
        ckit.Window.destroy(self)

    ## メッセージループを処理する
    def messageLoop( self, continue_cond_func=None, name=None ):
        self.messageloop_list.append(name)
        if not continue_cond_func:
            def defaultLoopCond():
                if name in self.quit_request_list:
                    self.quit_request_list.remove(name)
                    return False
                return True
            continue_cond_func = defaultLoopCond
        ckit.Window.messageLoop( self, continue_cond_func )
        self.messageloop_list.remove(name)

    ## メッセージループを抜ける
    def quit( self, name=None ):
        if name not in self.messageloop_list:
            raise ValueError

        # 最上位のメッセージループを抜けるときは、タスクを全てキャンセルする
        if name=="top":
            self.enable(False)
            for task_queue in self.task_queue_stack:
                task_queue.cancel()

        self.quit_request_list.append(name)

    ## トップレベルのメッセージループが終了中であるかをチェックする
    def isQuitting(self):
        return ( "top" in self.quit_request_list )


    ## ユーザ入力権を獲得する
    #
    #  @param self      -
    #  @param blocking  ユーザ入力権を獲得するまでブロックするか
    #
    #  LREdit をマウスやキーボードで操作させる権利を獲得するための関数です。\n\n
    #
    #  バックグラウンド処理の途中や最後でユーザの操作を受け付ける場合には、
    #  releaseUserInputOwnership と releaseUserInputOwnership を使って、
    #  入力権を所有する必要があります。
    #  さもないと、フォアグラウンドのユーザ操作と衝突してしまい、ユーザが混乱したり、
    #  LREdit が正しく動作しなくなります。\n\n
    #
    #  @sa releaseUserInputOwnership
    #
    def acquireUserInputOwnership( self, blocking=1 ):
        return self.user_input_ownership.acquire(blocking)

    ## ユーザ入力権を解放する
    #
    #  @sa acquireUserInputOwnership
    #
    def releaseUserInputOwnership(self):
        self.user_input_ownership.release()

    def onTimerJob(self):

        # タスクキューが空っぽだったら破棄する
        if len(self.task_queue_stack)>0:
            if self.task_queue_stack[-1].numItems()==0:
                self.task_queue_stack[-1].cancel()
                self.task_queue_stack[-1].join()
                self.task_queue_stack[-1].destroy()
                del self.task_queue_stack[-1]

                # 新しくアクティブになったタスクキューを再開する
                if len(self.task_queue_stack)>0:
                    self.task_queue_stack[-1].restart()

        if not self.acquireUserInputOwnership(False) : return
        try:
            ckit.JobQueue.checkAll()
        finally:
            self.releaseUserInputOwnership()

    def onTimerSyncCall(self):
        self.synccall.check()

    def resetIdleCount(self):
        self.idle_count = 30

    def onTimerIdle(self):
        if self.idle_count > 0:
             self.idle_count -= 1
        else:
            for edit in self.edit_list:
                if edit.doc.isSyntaxDirty():
                    edit.doc.updateSyntaxTimer()
                    break

    ## サブスレッドで処理を実行する
    #
    #  @param self              -
    #  @param func              サブスレッドで実行する呼び出し可能オブジェクト
    #  @param arg               引数 func に渡す引数
    #  @param cancel_func       ESCキーが押されたときのキャンセル処理
    #  @param cancel_func_arg   引数 cancel_func に渡す引数
    #  @param raise_error       引数 func のなかで例外が発生したときに、それを raise するか
    #
    #  メインスレッドのユーザインタフェイスの更新を止めずに、サブスレッドの中で任意の処理を行うための関数です。\n\n
    #
    #  この関数のなかでは、引数 func をサブスレッドで呼び出しながら、メインスレッドでメッセージループを回します。
    #  返値には、引数 func の返値がそのまま返ります。\n\n
    #
    #  ファイルのコピーや画像のデコードなどの、比較的時間のかかる処理は、メインスレッドではなくサブスレッドの中で処理するように心がけるべきです。
    #  さもないと、メインスレッドがブロックし、ウインドウの再描画などが長時間されないままになるといった弊害が発生します。
    #
    def subThreadCall( self, func, arg, cancel_func=None, cancel_func_arg=(), raise_error=False ):

        class SubThread(threading.Thread):

            def __init__(subthread_self):
                threading.Thread.__init__(subthread_self)
                subthread_self.result = None
                subthread_self.error = None

            def run(subthread_self):
                lredit_native.setBlockDetector()
                try:
                    subthread_self.result = func(*arg)
                except Exception as e:
                    lredit_debug.printErrorInfo()
                    subthread_self.error = e

        def onKeyDown( vk, mod ):
            if vk==VK_ESCAPE:
                if cancel_func:
                    cancel_func(*cancel_func_arg)
            return True

        def onChar( ch, mod ):
            return True

        keydown_hook_old = self.keydown_hook
        char_hook_old = self.char_hook
        mouse_event_mask_old = self.mouse_event_mask

        sub_thread = SubThread()
        sub_thread.start()

        self.keydown_hook = onKeyDown
        self.char_hook = onChar
        self.mouse_event_mask = True
        self.mouse_click_info = None

        self.removeKeyMessage()
        self.messageLoop( sub_thread.isAlive )

        sub_thread.join()
        result = sub_thread.result
        error = sub_thread.error
        del sub_thread

        self.keydown_hook = keydown_hook_old
        self.char_hook = char_hook_old
        self.mouse_event_mask = mouse_event_mask_old

        if error:
            if raise_error:
                raise error
            else:
                print( error )

        return result

    ## コンソールプログラムをサブプロセスとして実行する
    #
    #  @param self              -
    #  @param cmd               コマンドと引数のシーケンス
    #  @param cwd               サブプロセスのカレントディレクトリ
    #  @param env               サブプロセスの環境変数
    #  @param enable_cancel     True:ESCキーでキャンセルする  False:ESCキーでキャンセルしない
    #
    #  任意のコンソールプログラムを、ファイラのサブプロセスとして実行し、そのプログラムの出力を、ログペインにリダイレクトします。\n\n
    #
    #  引数 cmd には、サブプロセスとして実行するプログラムと引数をリスト形式で渡します。\n
    #  例:  [ "subst", "R:", "//remote-machine/public/" ]
    #
    def subProcessCall( self, cmd, cwd=None, env=None, enable_cancel=False ):

        p = ckit.SubProcess(cmd,cwd,env)

        if enable_cancel:
            cancel_handler = p.cancel
        else:
            cancel_handler = None

        return self.subThreadCall( p, (), cancel_handler )

    ## バックグラウンドタスクのキューに、タスクを投入する
    #
    #  @param self              -
    #  @param job_item          バックグラウンドタスクとして実行する JobItem オブジェクト
    #  @param comment           ユーザに説明する際のタスクの名前
    #  @param create_new_queue  新しいタスクキューを作成し、優先的に処理するか。( True:作成する  False:作成しない  None:問い合わせる )
    #
    #  LREdit はバックグランド処理をサポートしており、ファイルのコピーや検索などの時間のかかる処理をバックグラウンドで実行しながら、
    #  ほかのディレクトリを閲覧したり、次に実行するバックグランド処理を予約したりすることが出来ます。\n\n
    #
    #  バックグランド処理は、複数予約することが出来ますが、同時に実行することが出来るのは１つだけで、キュー(待ち行列)に投入されて、
    #  順番に処理されます。
    #
    def taskEnqueue( self, job_item, comment="", create_new_queue=None ):

        if len(self.task_queue_stack)>0:
            if create_new_queue==None:
                result = lredit_msgbox.popMessageBox(
                    self,
                    lredit_msgbox.MSGBOX_TYPE_YESNO,
                    ckit.strings["msgbox_title_insert_task"],
                    ckit.strings["msgbox_ask_insert_task"] )
                if result==lredit_msgbox.MSGBOX_RESULT_YES:
                    create_new_queue = True
                elif result==lredit_msgbox.MSGBOX_RESULT_NO:
                    create_new_queue = False
                else:
                    return
        else:
            create_new_queue = True

        if create_new_queue:

            new_task_queue = ckit.JobQueue()

            # まず前のタスクキューをポーズする処理を投入する
            if len(self.task_queue_stack)>0:

                prev_task_queue = self.task_queue_stack[-1]
                def jobPause( job_item ):
                    prev_task_queue.pause()
                pause_job_item = ckit.JobItem( jobPause, None )
                new_task_queue.enqueue(pause_job_item)

            self.task_queue_stack.append(new_task_queue)

        else:
            if comment and self.task_queue_stack[-1].numItems()>0:
                self.setStatusMessage( ckit.strings["statusbar_task_reserved"] % comment, 3000 )

        self.task_queue_stack[-1].enqueue(job_item)

    ## コマンドラインで文字列を入力する
    #
    #  @param self                      -
    #  @param title                     コマンド入力欄の左側に表示されるタイトル文字列
    #  @param text                      コマンド入力欄の初期文字列
    #  @param selection                 コマンド入力欄の初期選択範囲
    #  @param auto_complete             自動補完を有効にするか
    #  @param autofix_list              入力確定をする文字のリスト
    #  @param return_modkey             入力欄が閉じたときに押されていたモディファイアキーを取得するか
    #  @param update_handler            コマンド入力欄の変更があったときに通知を受けるためのハンドラ
    #  @param candidate_handler         補完候補を列挙するためのハンドラ
    #  @param candidate_remove_handler  補完候補を削除するためのハンドラ
    #  @param status_handler            コマンド入力欄の右側に表示されるステータス文字列を返すためのハンドラ
    #  @param enter_handler             コマンド入力欄でEnterキーが押されたときのハンドラ
    #  @param keydown_handler           コマンド入力欄でのキー入力を処理するためのハンドラ
    #  @return                          入力された文字列
    #
    #  LREdit のメインウインドウの下端のステータスバーの領域をつかって、任意の文字列の入力を受け付けるための関数です。\n\n
    #
    def commandLine( self, title, text="", selection=None, auto_complete=False, autofix_list=None, return_modkey=False, update_handler=None, candidate_handler=None, candidate_remove_handler=None, status_handler=None, enter_handler=None, keydown_handler=None ):

        title = " " + title + " "
        title_width = self.getStringWidth(title)
        status_string = [ "" ]
        result = [ None ]
        result_mod = [ 0 ]

        class CommandLine:

            def __init__(commandline_self):
                commandline_self.planned_command_list = []

            def _onKeyDown( commandline_self, vk, mod ):

                result_mod[0] = mod

                if keydown_handler:
                    if keydown_handler( vk, mod ):
                        if status_handler:
                            text = self.commandline_edit.getText()
                            selection = self.commandline_edit.getSelection()
                            update_info = ckit.EditWidget.UpdateInfo( text, selection )
                            status_string[0] = status_handler(update_info)
                            self.paint(REGION_STATUS_BAR)
                        return True

                if self.commandline_edit.onKeyDown( vk, mod ):
                    return True

                if vk==VK_RETURN:
                    text = self.commandline_edit.getText()
                    if enter_handler:
                        commandline_self.closeList()
                        if enter_handler( commandline_self, text, mod ):
                            return True
                    result[0] = text
                    commandline_self.quit()
                elif vk==VK_ESCAPE:
                    if self.commandline_edit.getText():
                        self.commandline_edit.clear()
                    else:
                        commandline_self.quit()
                return True

            def _onChar( commandline_self, ch, mod ):
                result_mod[0] = mod
                self.commandline_edit.onChar( ch, mod )
                return True

            def _onUpdate( commandline_self, update_info ):
                if update_handler:
                    if not update_handler(update_info):
                        return False
                if status_handler:
                    status_string[0] = status_handler(update_info)
                    self.paint(REGION_STATUS_BAR)

            def _onPaint( commandline_self, x, y, width, height ):

                status_string_for_paint = " " + status_string[0] + " "
                status_width = self.getStringWidth(status_string_for_paint)

                attr = ckit.Attribute( fg=ckit.getColor("bar_fg") )

                self.putString( x, y, title_width, height, attr, title )
                self.putString( x+width-status_width, y, status_width, height, attr, status_string_for_paint )

                if self.theme_enabled:

                    client_rect = self.getClientRect()
                    offset_x, offset_y = self.charToClient( 0, 0 )
                    char_w, char_h = self.getCharSize()
                    frame_width = 2

                    self.plane_statusbar.setPosSize( 0, (self.height()-1)*char_h+offset_y-frame_width, client_rect[2], client_rect[3]-((self.height()-1)*char_h+offset_y-frame_width) )
                    self.plane_commandline.setPosSize( title_width*char_w+offset_x, (self.height()-1)*char_h+offset_y-frame_width, client_rect[2]-((title_width+status_width)*char_w+offset_x), char_h+frame_width*2 )

                self.commandline_edit.setPosSize( x+title_width, y, width-title_width-status_width, height )
                self.commandline_edit.paint()

            def getText(commandline_self):
                return self.commandline_edit.getText()

            def setText( commandline_self, text ):
                self.commandline_edit.setText(text)

            def getSelection(commandline_self):
                return self.commandline_edit.getSelection()

            def setSelection(commandline_self,selection):
                self.commandline_edit.setSelection(selection)

            def selectAll(commandline_self):
                self.commandline_edit.selectAll()

            def closeList(commandline_self):
                self.commandline_edit.closeList()

            def planCommand( commandline_self, command, info, history ):
                commandline_self.planned_command_list.append( ( command, info, history ) )

            def appendHistory(commandline_self,newentry):
                self.commandline_history.append(newentry)

            def quit(commandline_self):
                self.quit( name="commandline" )

        commandline_edit_old = self.commandline_edit
        keydown_hook_old = self.keydown_hook
        char_hook_old = self.char_hook
        mouse_event_mask_old = self.mouse_event_mask
        status_bar_paint_hook_old = self.status_bar_paint_hook

        commandline = CommandLine()

        self.commandline_edit = ckit.EditWidget( self, title_width, self.height()-1, self.width()-title_width, 1, text, selection, auto_complete=auto_complete, no_bg=True, autofix_list=autofix_list, update_handler=commandline._onUpdate, candidate_handler=candidate_handler, candidate_remove_handler=candidate_remove_handler )
        self.commandline_edit.vk_complete = []
        self.keydown_hook = commandline._onKeyDown
        self.char_hook = commandline._onChar
        self.mouse_event_mask = True
        self.mouse_click_info = None
        self.status_bar_paint_hook = commandline._onPaint

        if status_handler:
            status_string[0] = status_handler(ckit.EditWidget.UpdateInfo(text,selection))

        if self.theme_enabled:
            self.plane_commandline.show(True)

        self.updateCursor()

        self.paint()

        self.removeKeyMessage()
        self.messageLoop( name="commandline" )

        self.commandline_edit.destroy()

        self.commandline_edit = commandline_edit_old
        self.keydown_hook = keydown_hook_old
        self.char_hook = char_hook_old
        self.mouse_event_mask = mouse_event_mask_old
        self.status_bar_paint_hook = status_bar_paint_hook_old

        if self.theme_enabled:
            self.plane_commandline.show(False)

        self.setCursorPos( -1, -1 )
        self.updateCursor()
        self.updatePaneRect()

        self.paint()

        for command, info, history in commandline.planned_command_list:
            try:
                command(info)
                if history:
                    self.commandline_history.append(history)
            except Exception as e:
                print( e )
                lredit_debug.printErrorInfo()

        if return_modkey:
            return result[0], result_mod[0]
        else:
            return result[0]

    ## コマンドラインでファイル名を入力する
    #
    #  @param self                      -
    #  @param title                     コマンド入力欄の左側に表示されるタイトル文字列
    #  @param filename                  コマンド入力欄の初期文字列
    #  @param ensure_exists             ファイルが実在することを保証するか
    #  @param return_modkey             入力欄が閉じたときに押されていたモディファイアキーを取得するか
    #  @return                          入力された文字列
    #
    def inputFilename( self, title, filename, ensure_exists=False, return_modkey=False ):

        def check(filename):
            if ensure_exists:
                return ( os.path.exists(filename) and os.path.isfile(filename) )
            else:
                if os.path.exists(filename):
                    return os.path.isfile(filename)
                else:
                    return bool(os.path.basename(filename))

        def statusString( update_info ):
            if check(update_info.text):
                return "OK"
            else:
                return "  "

        def onEnter( commandline, text, mod ):
            if not check(text):
                return True
            return False

        if not filename:
            if len(self.filename_history.items)>0:
                filename = self.filename_history.items[0]
                filename = os.path.dirname(filename)
                filename = ckit.joinPath(filename,"")

        if not filename:
            filename = os.getcwd()
            filename = ckit.joinPath(filename,"")

        # ファイル名部分だけを選択する
        basename = os.path.basename(filename)
        selection = [ len(filename)-len(basename), len(filename) ]
        
        base = "."

        filename, mod = self.commandLine( title, filename, selection, auto_complete=False, autofix_list=["\\/","."], return_modkey=True, candidate_handler=lredit_commandline.candidate_Filename( base, self.filename_history.items ), status_handler=statusString, enter_handler=onEnter )
        if filename==None : return None
        self.filename_history.append(filename)
        filename = ckit.joinPath( base, filename )

        if return_modkey:
            return filename, mod
        else:
            return filename

    ## コマンドラインでディレクトリ名を入力する
    #
    #  @param self                      -
    #  @param title                     コマンド入力欄の左側に表示されるタイトル文字列
    #  @param dirname                   コマンド入力欄の初期文字列
    #  @param recursive                 再帰の有無を入力するかどうか ( None:無効, True/False:有効 )
    #  @param history                   補完入力のためのHistoryオブジェクト
    #  @param return_modkey             入力欄が閉じたときに押されていたモディファイアキーを取得するか
    #  @return                          入力された文字列
    #
    def inputDirname( self, title, dirname, recursive=None, history=None, return_modkey=False ):

        recursive = [recursive]

        if recursive[0]==None:

            onKeyDown = None

            def statusString( update_info ):
                if os.path.isdir(update_info.text):
                    return "OK"
                else:
                    return "  "
        else:

            def onKeyDown( vk, mod ):
                if mod==MODKEY_CTRL:
                    if vk==VK_R:
                        recursive[0] = not recursive[0]
                        return True

            def statusString( update_info ):
                s = ""
                if recursive[0]:
                    s += "[Recursive] "
                else:
                    s += "[---------] "
                if os.path.isdir(update_info.text):
                    s += "OK"
                else:
                    s += "  "
                return s

        if not dirname:
            if len(self.filename_history.items)>0:
                dirname = os.path.dirname( self.filename_history.items[0] )
                dirname = ckit.joinPath( dirname, "" )

        if not dirname:
            dirname = os.getcwd()
            dirname = ckit.joinPath( dirname, "" )

        selection = [ len(dirname), len(dirname) ]
        base = "."

        history_items = None
        history_remove_func = None
        if history:
            history_items = history.items
            history_remove_func = history.candidateRemoveHandler

        dirname, mod = self.commandLine( title, dirname, selection, auto_complete=False, autofix_list=["\\/","."], return_modkey=True, candidate_handler=lredit_commandline.candidate_Filename( base, history_items ), candidate_remove_handler=history_remove_func, status_handler=statusString, keydown_handler=onKeyDown )
        if dirname==None:
            if return_modkey:
                return None, recursive[0], 0
            else:
                return None, recursive[0]

        dirname = ckit.joinPath( base, dirname )
        if history : history.append(dirname)

        if return_modkey:
            return dirname, recursive[0], mod
        else:
            return dirname, recursive[0]

    ## コマンドラインでドキュメント名を入力する
    #
    #  @param self                      -
    #  @param title                     コマンド入力欄の左側に表示されるタイトル文字列
    #  @param default_docname           コマンド入力欄の初期文字列
    #  @param return_modkey             入力欄が閉じたときに押されていたモディファイアキーを取得するか
    #  @return                          入力された文字列
    #
    def inputDocument( self, title, default_docname, return_modkey=False ):

        def statusString( update_info ):

            for edit in self.edit_list:
                doc = edit.doc
                if update_info.text==doc.getName():
                    return "OK"
            else:
                return "  "

        def candidate_DocumentName( update_info ):

            candidates = []

            for edit in self.edit_list:
                doc = edit.doc
                if doc.getName().lower().startswith( update_info.text.lower() ):
                    candidates.append( doc.getName() )

            return candidates, 0

        if default_docname:
            text = default_docname
            selection = [ 0, len(text) ]
        else:
            text = ""
            selection = [0,0]

        docname, mod = self.commandLine( title, text, selection, auto_complete=False, autofix_list=[], return_modkey=True, candidate_handler=candidate_DocumentName, status_handler=statusString )

        if return_modkey:
            return docname, mod
        else:
            return docname

    ## コマンドラインで検索条件を入力する
    #
    #  @param self                      -
    #  @param title                     コマンド入力欄の左側に表示されるタイトル文字列
    #  @param return_modkey             入力欄が閉じたときに押されていたモディファイアキーを取得するか
    #  @param keydown_handler           キー入力時ハンドラ
    #  @param update_handler            文字列変更時ハンドラ
    #  @return                          入力された文字列
    #
    def inputSearch( self, title, return_modkey=False, keydown_handler=None, update_handler=None ):

        text = [""]

        def callUpdateHandler( word=None, case=None, regex=None ):
            if update_handler:
                if word==None : word = bool(self.ini.getint( "SEARCH", "word" ))
                if case==None : case = bool(self.ini.getint( "SEARCH", "case" ))
                if regex==None : regex = bool(self.ini.getint( "SEARCH", "regex" ))
                return update_handler( text[0], word, case, regex )
            return True

        def onKeyDown( vk, mod ):

            if keydown_handler:
                if keydown_handler(vk,mod):
                    return True

            if mod==MODKEY_CTRL:
                if vk==VK_W:
                    word = self.ini.getint( "SEARCH", "word" )
                    if callUpdateHandler( word = not word ):
                        word = not word
                        self.ini.set( "SEARCH", "word", str(int(word)) )
                    return True
                if vk==VK_E:
                    case = self.ini.getint( "SEARCH", "case" )
                    if callUpdateHandler( case = not case ):
                        case = not case
                        self.ini.set( "SEARCH", "case", str(int(case)) )
                    return True
                if vk==VK_R:
                    regex = self.ini.getint( "SEARCH", "regex" )
                    if callUpdateHandler( regex = not regex ):
                        regex = not regex
                        self.ini.set( "SEARCH", "regex", str(int(regex)) )
                    return True

        def onUpdate( update_info ):
            text[0] = update_info.text
            return callUpdateHandler()

        def statusString( update_info ):
            s = ""
            if self.ini.getint( "SEARCH", "word" ):
                s += "[Word] "
            else:
                s += "[----] "
            if self.ini.getint( "SEARCH", "case" ):
                s += "[Case] "
            else:
                s += "[----] "
            if self.ini.getint( "SEARCH", "regex" ):
                s += "[Regex]"
            else:
                s += "[-----]"
            s = s.rstrip()
            return s

        if self.search_history.items:
            text[0] = self.search_history.items[0]
        selection = [ 0, len(text[0]) ]

        s, mod = self.commandLine( title, text[0], selection, auto_complete=False, autofix_list=[], return_modkey=True, candidate_handler=self.search_history.candidateHandler, candidate_remove_handler=self.search_history.candidateRemoveHandler, status_handler=statusString, keydown_handler=onKeyDown, update_handler=onUpdate )
        if s==None:
            if return_modkey:
                return None, mod
            else:
                return None

        self.search_history.append(s)

        if return_modkey:
            return s, mod
        else:
            return s

    ## コマンドラインで文字列を入力する
    #
    #  @param self                      -
    #  @param title                     コマンド入力欄の左側に表示されるタイトル文字列
    #  @param default_string            コマンド入力欄の初期文字列
    #  @param string_list               補完候補文字列のリスト
    #  @param return_modkey             入力欄が閉じたときに押されていたモディファイアキーを取得するか
    #  @return                          入力された文字列
    #
    def inputString( self, title, default_string, string_list=[], return_modkey=False ):

        def statusString( update_info ):

            for s in string_list:
                if update_info.text==s:
                    return "OK"
            else:
                return "  "

        def candidate_String( update_info ):

            candidates = []

            for s in string_list:
                if s.lower().startswith( update_info.text.lower() ):
                    candidates.append( s )

            return candidates, 0

        text = default_string
        selection = [ 0, len(text) ]

        s, mod = self.commandLine( title, text, selection, auto_complete=False, autofix_list=[], return_modkey=True, candidate_handler=candidate_String, status_handler=statusString )

        if return_modkey:
            return s, mod
        else:
            return s

    ## コマンドラインで数値を入力する
    #
    #  @param self                      -
    #  @param title                     コマンド入力欄の左側に表示されるタイトル文字列
    #  @param default_string            コマンド入力欄の初期文字列
    #  @param return_modkey             入力欄が閉じたときに押されていたモディファイアキーを取得するか
    #  @return                          入力された文字列
    #
    def inputNumber( self, title, default_string="", return_modkey=False ):

        def check(text):
            try:
                n = int(text)
            except ValueError:
                return False
            return True

        def statusString( update_info ):
            if check(update_info.text):
                return "OK"
            else:
                return "  "

        def onEnter( commandline, text, mod ):
            if not check(text):
                return True
            return False

        selection = [ 0, len(default_string) ]

        number, mod = self.commandLine( title, default_string, selection, auto_complete=False, return_modkey=True, status_handler=statusString, enter_handler=onEnter )
        if number==None : return None

        if return_modkey:
            return number, mod
        else:
            return number

    ## コマンドラインでオプション設定を入力する
    #
    #  @param self                      -
    #  @param title                     コマンド入力欄の左側に表示されるタイトル文字列
    #  @param default_options           コマンド入力欄の初期文字列
    #  @param option_list               入力可能なオプションのリスト
    #  @param return_modkey             入力欄が閉じたときに押されていたモディファイアキーを取得するか
    #  @return                          入力された文字列
    #
    def inputOptions( self, title, default_options, option_list=[], return_modkey=False ):

        option_lower_set = set()
        for option in option_list:
            option_lower_set.add(option.lower())

        def splitOptions(s):
            options = []
            for option in s.split(','):
                options.append(option.strip())
            return options

        def checkOptions(s):
            for option in splitOptions(s):
                if option.lower() not in option_lower_set:
                    return False
            return True

        def statusOptions( update_info ):
            if checkOptions(update_info.text):
                return "OK"
            else:
                return "  "

        def candidate_Options( update_info ):

            left = update_info.text[ : update_info.selection[0] ]
            pos_hint = left.rfind(",")+1
            hint = left[pos_hint:]
            pos_hint += len(hint) - len(hint.lstrip())
            hint = left[pos_hint:].lower()

            used_options_list = splitOptions(left.lower())
            used_options_set = set( used_options_list )

            candidate_list = []

            for option in option_list:
                option_lower = option.lower()
                if option_lower.startswith(hint):
                    if option_lower not in used_options_set:
                        candidate_list.append(option)

            return candidate_list, pos_hint

        text = default_options
        selection = [ 0, len(text) ]

        s, mod = self.commandLine( title, text, selection, auto_complete=True, autofix_list=[","], return_modkey=True, candidate_handler=candidate_Options, status_handler=statusOptions )

        if s and not checkOptions(s):
            print( ckit.strings["error_unknown_parameter"] % s )
            s = None

        if return_modkey:
            return s, mod
        else:
            return s


    ## リストウインドウでドキュメントを選択する
    #
    #  @param self                      -
    #  @param title                     リストウインドウのタイトル文字列
    #  @param filter_func               表示するドキュメントをフィルタする関数
    #  @return                          入力された文字列
    #
    def listDocument( self, title, filter_func=None ):
    
        loop = [False]
        fullpath_mode = [False]
        select = 0

        def onKeyDown( vk, mod ):
            if vk==VK_SPACE and mod==0:
                fullpath_mode[0] = not fullpath_mode[0]
                loop[0] = True
                list_window.quit()
                return True

        def onStatusMessage( width, select ):
            return ""

        while True:

            loop[0] = False

            items = []
            for edit in self.edit_list:
                if filter_func and not filter_func(edit):
                    continue
                if fullpath_mode[0]:
                    s = edit.doc.getFullpath()
                    if not s:
                        s = edit.doc.getName()
                else:
                    s = edit.doc.getName()
                if edit.doc.isModified():
                    s += " *"
                items.append( ( s, edit ) )

            pos = self.centerOfWindowInPixel()
            list_window = lredit_listwindow.ListWindow( pos[0], pos[1], 20, 2, self.width()-5, self.height()-3, self, self.ini, True, title, items, initial_select=select, onekey_search=False, keydown_hook=onKeyDown, statusbar_handler=onStatusMessage )
            self.enable(False)
            list_window.messageLoop()

            # チラつき防止の遅延削除
            class DelayedCall:
                def __call__(self):
                    self.list_window.destroy()
            delay = DelayedCall()
            delay.list_window = list_window
            self.delayedCall( delay, 10 )

            if not loop[0]:
                break

            select = list_window.getResult()

        result = list_window.getResult()
        self.enable(True)
        self.activate()

        if not items or result<0:
            return None

        edit = items[result][1]
        return edit


    def _onTimerActivate(self):

        if not self.acquireUserInputOwnership(False) : return
        try:
            self.checkProjectFileModified()
            self.checkFileModifiedAll()
        finally:
            self.releaseUserInputOwnership()

        self.killTimer( self._onTimerActivate )

    def _onActivate( self, active ):
        if self.initialized:
            self.paint()
            if active:
                self.killTimer( self._onTimerActivate )
                self.setTimer( self._onTimerActivate, 10 )
            else:
                self._cancelMouse()

    def _onClose( self ):
        self.command.Quit()

    def _onMove( self, x, y ):

        if not self.initialized : return

        if self.commandline_edit:
            self.commandline_edit.onWindowMove()

        for edit in self.edit_list:
            edit.onWindowMove()

    def _onSize( self, width, height ):

        if not self.initialized : return

        w = width

        if self.left_edit_pane_width>w-1 : self.left_edit_pane_width=w-1
        w -= self.left_edit_pane_width

        if self.log_pane_height>height-4 : self.log_pane_height=height-4
        if self.log_pane_height<0 : self.log_pane_height=0

        self.updatePaneRect()

        for edit in self.edit_list:
            edit.onWindowMove()

        if self.wallpaper:
            self.wallpaper.adjust()

        self.paint()

    def _onKeyDown( self, vk, mod ):

        #print( "_onKeyDown", vk, mod )

        self.resetIdleCount()

        pane = self.activePane()

        if self.mod!=mod:
            for hook in self.mod_hooks:
                hook( mod, self.mod )
            self.mod=mod

        if self.keydown_hook:
            if self.keydown_hook( vk, mod ):
                return True

        if not self.acquireUserInputOwnership(False) : return
        try:

            # アクティブなTextEditWidgetのキー処理
            if pane.widget():
                result = [None]
                if self.profile:
                    cProfile.runctx( "result[0] = pane.widget().onKeyDown( vk, mod )", globals(), locals() )
                else:
                    result[0] = pane.widget().onKeyDown( vk, mod )
                if result[0]:
                    return result[0]

            # メインウインドウのキー処理
            try:
                func = self.keymap.table[ ckit.KeyEvent(vk,mod) ]
                if self.profile:
                    cProfile.runctx( "func( ckit.CommandInfo() )", globals(), locals() )
                else:
                    func( ckit.CommandInfo() )
                return True
            except KeyError:
                pass

        finally:
            self.releaseUserInputOwnership()

    def _onKeyUp( self, vk, mod ):

        #print( "_onKeyUp", vk, mod )

        if self.mod!=mod:
            for hook in self.mod_hooks:
                hook( mod, self.mod )
            self.mod=mod

    def _onChar( self, ch, mod ):

        #print( "_onChar", ch, mod )

        self.resetIdleCount()

        pane = self.activePane()

        if self.char_hook:
            if self.char_hook( ch, mod ):
                return

        if not self.acquireUserInputOwnership(False) : return
        try:

            # アクティブなTextEditWidgetの文字入力処理
            if pane.widget():
                result = [None]
                if self.profile:
                    cProfile.runctx( "result[0] = pane.widget().onChar( ch, mod )", globals(), locals() )
                else:
                    result[0] = pane.widget().onChar( ch, mod )
                if result[0]:
                    return result[0]

        finally:
            self.releaseUserInputOwnership()

    def _onLeftButtonDownOutside( self, x, y, mod ):
        if not self.acquireUserInputOwnership(False) : return
        try:
            self._onLeftButtonDown(x, y, mod)
        finally:
            self.releaseUserInputOwnership()

    def _onLeftButtonUpOutside( self, x, y, mod ):
        if not self.acquireUserInputOwnership(False) : return
        try:
            self._onLeftButtonUp(x, y, mod)
        finally:
            self.releaseUserInputOwnership()

    def _onMiddleButtonDownOutside( self, x, y, mod ):
        if not self.acquireUserInputOwnership(False) : return
        try:
            self._onMiddleButtonDown(x, y, mod)
        finally:
            self.releaseUserInputOwnership()

    def _onMiddleButtonUpOutside( self, x, y, mod ):
        if not self.acquireUserInputOwnership(False) : return
        try:
            self._onMiddleButtonUp(x, y, mod)
        finally:
            self.releaseUserInputOwnership()

    def _onRightButtonDownOutside( self, x, y, mod ):
        if not self.acquireUserInputOwnership(False) : return
        try:
            self._onRightButtonDown(x, y, mod)
        finally:
            self.releaseUserInputOwnership()

    def _onRightButtonUpOutside( self, x, y, mod ):
        if not self.acquireUserInputOwnership(False) : return
        try:
            self._onRightButtonUp(x, y, mod)
        finally:
            self.releaseUserInputOwnership()

    def _onLeftButtonDoubleClickOutside( self, x, y, mod ):
        if not self.acquireUserInputOwnership(False) : return
        try:
            self._onLeftButtonDoubleClick(x, y, mod)
        finally:
            self.releaseUserInputOwnership()

    def _onMouseMoveOutside( self, x, y, mod ):
        if not self.acquireUserInputOwnership(False) : return
        try:
            self._onMouseMove(x, y, mod)
        finally:
            self.releaseUserInputOwnership()

    def _onMouseWheelOutside( self, x, y, wheel, mod ):
        if not self.acquireUserInputOwnership(False) : return
        try:
            self._onMouseWheel(x, y, wheel, mod)
        finally:
            self.releaseUserInputOwnership()

    def _mouseCommon( self, x, y, focus=True ):

        client_rect = self.getClientRect()
        offset_x, offset_y = self.charToClient( 0, 0 )
        char_w, char_h = self.getCharSize()

        char_x = (x-offset_x) // char_w
        char_y = (y-offset_y) // char_h
        sub_x = float( (x-offset_x) - char_x * char_w ) // char_w
        sub_y = float( (y-offset_y) - char_y * char_h ) // char_h

        left_edit_pane_rect = list( self.leftEditPaneRect() )
        right_edit_pane_rect = list( self.rightEditPaneRect() )
        edit_separator_rect = list( self.editSeparatorRect() )
        log_pane_rect = list( self.logPaneRect() )

        region = None
        pane = None
        pane_rect = None

        if self.left_edit_pane.edit and left_edit_pane_rect[0]<=char_x<left_edit_pane_rect[2] and right_edit_pane_rect[1]<=char_y<right_edit_pane_rect[3]:

            if focus : self.command.FocusLeftEdit()

            if char_y==left_edit_pane_rect[1]:
                region = REGION_LEFT_TAB
                pane = self.left_edit_pane

            elif left_edit_pane_rect[1]+1<=char_y<left_edit_pane_rect[3]-1:
                region = REGION_LEFT_EDIT
                pane = self.left_edit_pane

            elif char_y==left_edit_pane_rect[3]-1:
                region = REGION_LEFT_FOOTER
                pane = self.left_edit_pane

        elif self.right_edit_pane.edit and right_edit_pane_rect[0]<=char_x<right_edit_pane_rect[2] and right_edit_pane_rect[1]<=char_y<right_edit_pane_rect[3]:

            if focus : self.command.FocusRightEdit()

            if char_y==right_edit_pane_rect[1]:
                region = REGION_RIGHT_TAB
                pane = self.right_edit_pane

            elif right_edit_pane_rect[1]+1<=char_y<right_edit_pane_rect[3]-1:
                region = REGION_RIGHT_EDIT
                pane = self.right_edit_pane

            elif char_y==right_edit_pane_rect[3]-1:
                region = REGION_RIGHT_FOOTER
                pane = self.right_edit_pane

        elif edit_separator_rect[0]<=char_x<edit_separator_rect[2] and edit_separator_rect[1]<=char_y<edit_separator_rect[3]:

            region = REGION_EDIT_SEPARATOR
            pane = None

        elif log_pane_rect[0]<=char_x<log_pane_rect[2] and log_pane_rect[1]<=char_y<log_pane_rect[3]:

            if focus : self.command.FocusLog()

            region = REGION_LOG
            pane = self.log_pane

        return [ char_x, char_y, sub_x, sub_y, region, pane ]

    def _onDropFiles( self, x, y, filename_list ):

        #print( "_onDropFiles", x, y )

        char_x, char_y, sub_x, sub_y, region, pane = self._mouseCommon( x, y, True )

        # プロジェクトファイルがDropされたらそれを開く
        textfile_list = []
        for filename in filename_list:
            if fnmatch.fnmatch( filename, "*.lre" ):
                info = ckit.CommandInfo()
                info.args = [ filename ]
                self.command.OpenProject(info)
            else:
                textfile_list.append(filename)

        if region==REGION_LEFT_EDIT:
            for filename in textfile_list:
                self.leftOpen( filename=filename )
        elif region==REGION_RIGHT_EDIT:
            for filename in textfile_list:
                self.rightOpen( filename=filename )
        else:
            for filename in textfile_list:
                self.activeOpen( filename=filename )

    def _onIpc( self, data ):

        args = json.loads(data)
        self.processArgument(args)

        # アクティブ化
        wnd = pyauto.Window.fromHWND(self.getHWND())
        if wnd.isMinimized():
            wnd.restore()
        last_active_wnd = wnd.getLastActivePopup()
        last_active_wnd.setForeground(True)
        if last_active_wnd.isEnabled():
            last_active_wnd.setActive()

    def _setClipboard_LogSelected(self):

        joint_text = ""

        selection_left, selection_right = self.log_pane.selection
        if selection_left > selection_right:
            selection_left, selection_right = selection_right, selection_left

        i = selection_left[0]
        while i<=selection_right[0] and i<self.log_pane.log.numLines():

            s = self.log_pane.log.getLine(i)

            if i==selection_left[0]:
                left = selection_left[1]
            else:
                left = 0

            if i==selection_right[0]:
                right = selection_right[1]
            else:
                right = len(s)

            joint_text += s[left:right]

            if i!=selection_right[0]:
                joint_text += "\r\n"

            i += 1

        if joint_text:
            ckit.setClipboardText(joint_text)

    def _onLeftButtonDown( self, x, y, mod ):
        #print( "_onLeftButtonDown", x, y )

        if self.mouse_event_mask : return

        self.mouse_click_info=None

        char_x, char_y, sub_x, sub_y, region, pane = self._mouseCommon( x, y, True )

        if region==REGION_LEFT_EDIT or region==REGION_RIGHT_EDIT or region==REGION_LOG:
            pane.edit.onLeftButtonDown( char_x, char_y, sub_x, sub_y, mod )
            self.setCapture()
            self.mouse_click_info = MouseInfo( "edit", x=x, y=y, mod=mod, pane=pane )

        elif region==REGION_LEFT_FOOTER or region==REGION_RIGHT_FOOTER:
            self.setCapture()
            self.mouse_click_info = MouseInfo( "footer", x=x, y=y, mod=mod, pane=pane )

        elif region==REGION_EDIT_SEPARATOR:
            self.setCapture()
            self.mouse_click_info = MouseInfo( "edit_separator", x=x, y=y, mod=mod, pane=pane )

        elif region==REGION_LEFT_TAB or region==REGION_RIGHT_TAB:
            pane.tab.onLeftButtonDown( char_x, char_y, mod )
            self.setCapture()
            self.mouse_click_info = MouseInfo( "tab", x=x, y=y, mod=mod, pane=pane )

    def _onLeftButtonUp( self, x, y, mod ):
        #print( "_onLeftButtonUp", x, y )

        if self.mouse_event_mask : return

        if self.mouse_click_info==None : return

        if self.mouse_click_info.mode=="edit":
            char_x, char_y, sub_x, sub_y, region, pane = self._mouseCommon( x, y, False )
            self.mouse_click_info.pane.edit.onLeftButtonUp( char_x, char_y, sub_x, sub_y, mod )
            self.releaseCapture()
            self.mouse_click_info = None

        elif self.mouse_click_info.mode=="footer":
            self.releaseCapture()
            self.mouse_click_info = None

        elif self.mouse_click_info.mode=="edit_separator":
            self.releaseCapture()
            self.mouse_click_info = None

        elif self.mouse_click_info.mode=="tab":
            self.releaseCapture()
            self.mouse_click_info = None

    def _onLeftButtonDoubleClick( self, x, y, mod ):
        #print( "_onLeftButtonDoubleClick", x, y )

        if self.mouse_event_mask : return

        self.mouse_click_info=None

        char_x, char_y, sub_x, sub_y, region, pane = self._mouseCommon( x, y, True )

        if region==REGION_LEFT_EDIT or region==REGION_RIGHT_EDIT or region==REGION_LOG:
            pane.edit.onLeftButtonDoubleClick( char_x, char_y, sub_x, sub_y, mod )
            self.setCapture()
            self.mouse_click_info = MouseInfo( "edit", x=x, y=y, mod=mod, pane=pane )

    def _onMiddleButtonDown( self, x, y, mod ):
        #print( "_onMiddleButtonDown", x, y )

        if self.mouse_event_mask : return

        self.mouse_click_info=None

        char_x, char_y, sub_x, sub_y, region, pane = self._mouseCommon( x, y, True )

    def _onMiddleButtonUp( self, x, y, mod ):
        #print( "_onMiddleButtonUp", x, y )

        if self.mouse_event_mask : return

        self.mouse_click_info = None

    def _onRightButtonDown( self, x, y, mod ):
        #print( "_onRightButtonDown", x, y )

        if self.mouse_event_mask : return

        self.mouse_click_info=None

        char_x, char_y, sub_x, sub_y, region, pane = self._mouseCommon( x, y, True )

        if region==REGION_LEFT_EDIT or region==REGION_RIGHT_EDIT:
            pane.edit.onRightButtonDown( char_x, char_y, sub_x, sub_y, mod )
            self.mouse_click_info = MouseInfo( "edit", x=x, y=y, mod=mod, pane=pane )


    def _onRightButtonUp( self, x, y, mod ):
        #print( "_onRightButtonUp", x, y )

        if self.mouse_event_mask : return

        if self.mouse_click_info==None : return

        if self.mouse_click_info.mode!="edit":
            char_x, char_y, sub_x, sub_y, region, pane = self._mouseCommon( x, y, False )
            self.mouse_click_info.pane.edit.onRightButtonUp( char_x, char_y, sub_x, sub_y, mod )
            self.mouse_click_info=None


    def _onMouseMove( self, x, y, mod ):
        #print( "_onMouseMove", x, y )

        if self.mouse_event_mask : return

        char_x, char_y, sub_x, sub_y, region, pane = self._mouseCommon( x, y, False )

        if self.mouse_click_info==None:
            if region==REGION_LEFT_FOOTER or region==REGION_RIGHT_FOOTER:
                self.setMouseCursor(MOUSE_CURSOR_SIZENS)
            elif region==REGION_EDIT_SEPARATOR:
                self.setMouseCursor(MOUSE_CURSOR_SIZEWE)

        elif self.mouse_click_info.mode=="edit":
            self.mouse_click_info.pane.edit.onMouseMove( char_x, char_y, sub_x, sub_y, mod )

        elif self.mouse_click_info.mode=="footer":
            self.setMouseCursor(MOUSE_CURSOR_SIZENS)
            self.log_pane_height = self.height()-char_y-2
            if self.log_pane_height>self.height()-2-self.tabBarHeight() : self.log_pane_height=self.height()-2-self.tabBarHeight()
            if self.log_pane_height<0 : self.log_pane_height=0
            self.updatePaneRect()
            cursor = self.log_pane.edit.selection.cursor()
            self.log_pane.edit.makeVisible(cursor)
            self.paint()

        elif self.mouse_click_info.mode=="edit_separator":
            self.setMouseCursor(MOUSE_CURSOR_SIZEWE)
            rect = self.editPaneRect()
            self.left_edit_pane_width = char_x - rect[0]
            self.left_edit_pane_width = max( self.left_edit_pane_width, 0 )
            self.left_edit_pane_width = min( self.left_edit_pane_width, self.editPaneWidth()-self.editSeparatorWidth() )
            self.updatePaneRect()
            self.paint( REGION_EDIT )

    def _onMouseWheel( self, x, y, wheel, mod ):
        #print( "_onMouseWheel", x, y, wheel )

        if self.mouse_event_mask : return

        x, y = self.screenToClient( x, y )
        char_x, char_y, sub_x, sub_y, region, pane = self._mouseCommon( x, y, True )

        if region==REGION_LEFT_EDIT or region==REGION_RIGHT_EDIT or region==REGION_LOG:
            pane.edit.onMouseWheel( char_x, char_y, sub_x, sub_y, wheel, mod )
            self.mouse_click_info=None

    def _cancelMouse(self):
        self.releaseCapture()
        self.mouse_click_info = None

    def _onCheckNetConnection( self, remote_resource_name ):

        def addConnection( hwnd, remote_resource_name ):
            try:
                lredit_native.addConnection( hwnd, remote_resource_name )
            except Exception as e:
                print( ckit.strings["error_connection_failed"] % remote_resource_name )
                print( e, "\n" )

        self.synccall( addConnection, (self.getHWND(), remote_resource_name) )

    def tabBarHeight(self):
        return 1

    def leftEditPaneWidth(self):
        return self.left_edit_pane_width

    def rightEditPaneWidth(self):
        return self.editPaneWidth() - self.editSeparatorWidth() - self.left_edit_pane_width

    def editSeparatorWidth(self):
        if self.left_edit_pane.edit and self.right_edit_pane.edit:
            return 1
        else:
            return 0

    def editPaneWidth(self):
        return self.width()

    def editPaneHeight(self):
        return self.height() - self.log_pane_height - 1

    def lowerPaneHeight(self):
        return self.log_pane_height + 1

    def logPaneHeight(self):
        return self.log_pane_height

    def editPaneRect(self):
        return ( 0, 0, self.width(), self.height() - self.log_pane_height - 1 )

    def leftTabBarRect(self):
        return ( 0, 0, self.leftEditPaneWidth(), self.tabBarHeight() )

    def rightTabBarRect(self):
        return ( self.leftEditPaneWidth() + self.editSeparatorWidth(), 0, self.width(), self.tabBarHeight() )

    def leftEditPaneRect(self):
        return ( 0, 0, self.leftEditPaneWidth(), self.height() - self.log_pane_height - 1 )

    def rightEditPaneRect(self):
        return ( self.leftEditPaneWidth() + self.editSeparatorWidth(), 0, self.width(), self.height() - self.log_pane_height - 1 )

    def editSeparatorRect(self):
        return ( self.leftEditPaneWidth(), 0, self.leftEditPaneWidth() + self.editSeparatorWidth(), self.height() - self.log_pane_height - 1 )

    def logPaneRect(self):
        return ( 0, self.height() - self.log_pane_height - 1, self.width(), self.height()-1 )

    def activePaneRect(self):
        if self.focus_top==MainWindow.FOCUS_EDIT:
            return self.activeEditPaneRect()
        elif self.focus_top==MainWindow.FOCUS_LOG:
            return self.logPaneRect()
        else:
            assert(False)

    def activeEditPaneRect(self):
        if self.focus_edit==MainWindow.FOCUS_EDIT_LEFT:
            return self.leftEditPaneRect()
        elif self.focus_edit==MainWindow.FOCUS_EDIT_RIGHT:
            return self.rightEditPaneRect()
        else:
            assert(False)

    def inactiveEditPaneRect(self):
        if self.focus_edit==MainWindow.FOCUS_EDIT_LEFT:
            return self.rightEditPaneRect()
        elif self.focus_edit==MainWindow.FOCUS_EDIT_RIGHT:
            return self.leftEditPaneRect()
        else:
            assert(False)

    def ratioToScreen( self, ratio ):
        rect = self.getWindowRect()
        return ( int(rect[0] * (1-ratio[0]) + rect[2] * ratio[0]), int(rect[1] * (1-ratio[1]) + rect[3] * ratio[1]) )

    ## メインウインドウの中心位置を、スクリーン座標系で返す
    #
    #  @return  ( X軸座標, Y軸座標 )
    #
    def centerOfWindowInPixel(self):
        rect = self.getWindowRect()
        return ( (rect[0]+rect[2])//2, (rect[1]+rect[3])//2 )

    def centerOfFocusedPaneInPixel(self):
        window_rect = self.getWindowRect()

        pane_rect = self.activeEditPaneRect()

        if self.width()>0:
            x_ratio = float(pane_rect[0]+pane_rect[2])/2/self.width()
        else:
            x_ratio = 0.5
        if self.height()>0:
            y_ratio = float(pane_rect[1]+pane_rect[3])/2/self.height()
        else:
            y_ratio = 0.5

        return ( int(window_rect[0] * (1-x_ratio) + window_rect[2] * (x_ratio)), int(window_rect[1] * (1-y_ratio) + window_rect[3] * (y_ratio)) )

    ## 左の編集ペインを取得する
    def leftPane(self):
        return self.left_edit_pane

    ## 右の編集ペインを取得する
    def rightPane(self):
        return self.right_edit_pane

    ## アクティブなペインを取得する
    def activePane(self):
        if self.focus_top==MainWindow.FOCUS_EDIT:
            return self.activeEditPane()
        elif self.focus_top==MainWindow.FOCUS_LOG:
            return self.log_pane
        else:
            assert(False)

    ## アクティブな編集ペインを取得する
    def activeEditPane(self):
        if self.focus_edit==MainWindow.FOCUS_EDIT_LEFT:
            return self.left_edit_pane
        elif self.focus_edit==MainWindow.FOCUS_EDIT_RIGHT:
            return self.right_edit_pane
        else:
            assert(False)

    ## 非アクティブな編集ペインを取得する
    def inactiveEditPane(self):
        if self.focus_edit==MainWindow.FOCUS_EDIT_LEFT:
            return self.right_edit_pane
        elif self.focus_edit==MainWindow.FOCUS_EDIT_RIGHT:
            return self.left_edit_pane
        else:
            assert(False)

    def updateCursor(self):
        if self.commandline_edit:
            if self.left_edit_pane.edit : self.left_edit_pane.edit.enableCursor(False)
            if self.right_edit_pane.edit : self.right_edit_pane.edit.enableCursor(False)
            self.log_pane.edit.enableCursor(False)
            self.commandline_edit.enableCursor(True)
        else:
            active_pane = self.activePane()
            if self.left_edit_pane.edit : self.left_edit_pane.edit.enableCursor( active_pane==self.left_edit_pane )
            if self.right_edit_pane.edit : self.right_edit_pane.edit.enableCursor( active_pane==self.right_edit_pane )
            self.log_pane.edit.enableCursor( active_pane==self.log_pane )
        self.updateTitleBar()
        self.updateTabBar()

    ## １画面モードであるか
    def isLayoutOne(self):
        return not (self.left_edit_pane.edit and self.right_edit_pane.edit)

    ## ２画面モードであるか
    def isLayoutTwo(self):
        return (self.left_edit_pane.edit and self.right_edit_pane.edit)

    def executeCommand( self, name, info ):

        #print( "executeCommand", name )

        if self.activePane().widget():
            if self.activePane().widget().executeCommand( name, info ):
                return True

        try:
            command = getattr( self, "command_" + name )
        except AttributeError:
            return False

        command(info)
        return True

    def enumCommand(self):
        if self.activePane().widget():
            for item in self.activePane().widget().enumCommand():
                yield item
        for attr in dir(self):
            if attr.startswith("command_"):
                yield attr[ len("command_") : ]

    def prepareMenuBar(self):

        def isWholeMenuEnabled():
            if not self.acquireUserInputOwnership(False) : return False
            try:
                return True
            finally:
                self.releaseUserInputOwnership()

        def isEncoding(encoding):
            def func():
                edit = self.activeEditPane().edit
                if not edit : return False
                if encoding in ("utf-8", "utf-8n"):
                    if edit.doc.encoding.encoding=="utf-8":
                        if edit.doc.encoding.bom and encoding=="utf-8" : return True
                        if not edit.doc.encoding.bom and encoding=="utf-8n" : return True
                    return False
                return edit.doc.encoding.encoding==encoding
            return func

        def isLineEnd(lineend):
            def func():
                edit = self.activeEditPane().edit
                if not edit : return False
                return edit.doc.lineend==lineend
            return func

        def isSelected():
            edit = self.activeEditPane().edit
            if not edit : return False
            return edit.selection.direction!=0

        def isProjectOpened():
            return (self.project!=None)

        # [開き直す]のサブメニュー項目
        def menuitems_ReopenEncoding():

            def command_ReopenSpecificEncoding( encoding ):
                def func(info):
                    info = ckit.CommandInfo()
                    info.args = [encoding]
                    self.command.ReopenEncoding(info)
                return func

            encoding_list = [
                "utf-8",
                "utf-8n",
                "shift-jis",
                "euc-jp",
                "iso-2022-jp",
                "utf-16-le",
                "utf-16-be",
            ]

            menuitems = []

            for encoding in encoding_list:
                menuitems.append( ckit.MenuNode( encoding, encoding, command_ReopenSpecificEncoding(encoding), checked=isEncoding(encoding) ) )

            return menuitems

        # [エンコーディング]のサブメニュー項目
        def menuitems_Encoding():

            def command_SpecificEncoding( encoding ):
                def func(info):
                    info = ckit.CommandInfo()
                    info.args = [encoding]
                    self.command.Encoding(info)
                return func

            encoding_list = [
                "utf-8",
                "utf-8n",
                "shift-jis",
                "euc-jp",
                "iso-2022-jp",
                "utf-16-le",
                "utf-16-be",
            ]

            menuitems = []

            for encoding in encoding_list:
                menuitems.append( ckit.MenuNode( encoding, encoding, command_SpecificEncoding(encoding), checked=isEncoding(encoding) ) )

            return menuitems

        # 改行コード
        def menuitems_LineEnd():

            def command_SpecificLineEnd( lineend ):
                def func(info):
                    info = ckit.CommandInfo()
                    info.args = [lineend]
                    self.command.LineEnd(info)
                return func

            lineend_list = [
                ( "crlf", "\r\n" ),
                ( "lf",   "\n" ),
                ( "cr",   "\r" ),
            ]

            menuitems = []

            for lineend_name, lineend in lineend_list:
                menuitems.append( ckit.MenuNode( lineend, lineend_name, command_SpecificLineEnd(lineend_name), checked=isLineEnd(lineend) ) )

            return menuitems

        # [最近のファイル]のサブメニュー項目
        def menuitems_RecentFiles():

            class command_OpenSpecificFile:

                def __init__( command_self, filename ):
                    command_self.filename = filename

                def __call__( command_self, info ):
                    self.activeOpen( filename=command_self.filename )

            menu_items = []
            i = 0
            for filename in self.filename_history.items:
                if not fnmatch.fnmatch( filename, "*.lre" ):
                    menu_items.append( ckit.MenuNode( "recent_file%d"%i, "&%d %s" % ( (i+1)%10, filename ), command_OpenSpecificFile(filename) ) )
                    i += 1
                    if i>=10: break
            return menu_items

        # [最近のプロジェクト]のサブメニュー項目
        def menuitems_RecentProjects():

            class command_OpenSpecificProject:

                def __init__( command_self, filename ):
                    command_self.filename = filename

                def __call__( command_self, info ):
                    info = ckit.CommandInfo()
                    info.args = [ command_self.filename ]
                    self.command.OpenProject(info)

            menu_items = []
            i = 0
            for filename in self.filename_history.items:
                if fnmatch.fnmatch( filename, "*.lre" ):
                    menu_items.append( ckit.MenuNode( "recent_project%d"%i, "&%d %s" % ( (i+1)%10, filename ), command_OpenSpecificProject(filename) ) )
                    i += 1
                    if i>=10: break
            return menu_items

        # メニュー全体の定義
        self.menu_bar = ckit.MenuNode(

            enabled = isWholeMenuEnabled,

            items=[
                ckit.MenuNode(
                    "file", ckit.strings["menu_file"],
                    items=[
                        ckit.MenuNode( "new",      ckit.strings["menu_new"],               self.command.New ),
                        ckit.MenuNode( "open",     ckit.strings["menu_open"],              self.command.Open ),
                        ckit.MenuNode( "reopen",   ckit.strings["menu_reopen"],
                            items=[
                                menuitems_ReopenEncoding
                            ]
                        ),
                        ckit.MenuNode( "close",    ckit.strings["menu_close"],             self.command.Close ),
                        ckit.MenuNode( separator=True ),
                        ckit.MenuNode( "project",  ckit.strings["menu_project"],
                            items = [
                                ckit.MenuNode( "open_project",         ckit.strings["menu_open_project"],      self.command.OpenProject ),
                                ckit.MenuNode( "close_project",        ckit.strings["menu_close_project"],     self.command.CloseProject,      enabled=isProjectOpened ),
                                ckit.MenuNode( "edit_project",         ckit.strings["menu_edit_project"],      self.command.EditProject,       enabled=isProjectOpened ),
                            ]
                        ),
                        ckit.MenuNode( "project_file_list",    ckit.strings["menu_project_file_list"],     self.command.ProjectFileList,   enabled=isProjectOpened ),
                        ckit.MenuNode( separator=True ),
                        ckit.MenuNode( "save",     ckit.strings["menu_save"],              self.command.Save ),
                        ckit.MenuNode( "save_as",  ckit.strings["menu_save_as"],           self.command.SaveAs ),
                        ckit.MenuNode( "save_all", ckit.strings["menu_save_all"],          self.command.SaveAll ),
                        ckit.MenuNode( separator=True ),
                        ckit.MenuNode( "encoding", ckit.strings["menu_encoding"],
                            items=[
                                menuitems_Encoding,
                                ckit.MenuNode( separator=True ),
                                menuitems_LineEnd,
                            ]
                        ),
                        ckit.MenuNode( separator=True ),
                        ckit.MenuNode(
                            "recent_files",         ckit.strings["menu_recent_files"],
                            items=[
                                menuitems_RecentFiles,
                            ]
                        ),
                        ckit.MenuNode(
                            "recent_projects",      ckit.strings["menu_recent_projects"],
                            items=[
                                menuitems_RecentProjects,
                            ]
                        ),
                        ckit.MenuNode( separator=True ),
                        ckit.MenuNode( "quit",     ckit.strings["menu_quit"],              self.command.Quit ),
                    ]
                ),

                ckit.MenuNode(
                    "edit", ckit.strings["menu_edit"],
                    items=[
                        ckit.MenuNode( "undo",         ckit.strings["menu_undo"],          self.command.Undo ),
                        ckit.MenuNode( "redo",         ckit.strings["menu_redo"],          self.command.Redo ),
                        ckit.MenuNode( separator=True ),
                        ckit.MenuNode( "cut",          ckit.strings["menu_cut"],           self.command.Cut,   enabled=isSelected ),
                        ckit.MenuNode( "copy",         ckit.strings["menu_copy"],          self.command.Copy,  enabled=isSelected ),
                        ckit.MenuNode( "paste",        ckit.strings["menu_paste"],         self.command.Paste ),
                        ckit.MenuNode( "delete",       ckit.strings["menu_delete"],        self.command.Delete ),
                        ckit.MenuNode( "select_all",   ckit.strings["menu_select_all"],    self.command.SelectDocument ),
                        ckit.MenuNode( separator=True ),
                        ckit.MenuNode( "convert_char", ckit.strings["menu_convert_char"],
                            items = [
                                ckit.MenuNode( "to_upper",   ckit.strings["menu_to_upper"],    self.command.ToUpper,   enabled=isSelected ),
                                ckit.MenuNode( "to_lower",   ckit.strings["menu_to_lower"],    self.command.ToLower,   enabled=isSelected ),
                                ckit.MenuNode( "to_zenkaku", ckit.strings["menu_to_zenkaku"],  self.command.ToZenkaku, enabled=isSelected ),
                                ckit.MenuNode( "to_hankaku", ckit.strings["menu_to_hankaku"],  self.command.ToHankaku, enabled=isSelected ),
                            ]
                        ),
                        ckit.MenuNode( separator=True ),
                        ckit.MenuNode( "complete",     ckit.strings["menu_complete"],      self.command.CompleteAbbrev ),
                        ckit.MenuNode( separator=True ),
                        ckit.MenuNode( "jump_lineno",  ckit.strings["menu_jump_lineno"],   self.command.JumpLineNo ),
                    ]
                ),

                ckit.MenuNode(
                    "search", ckit.strings["menu_search"],
                    items=[
                        ckit.MenuNode( "search",       ckit.strings["menu_search"],        self.command.Search ),
                        ckit.MenuNode( "search_next",  ckit.strings["menu_search_next"],   self.command.SearchNext ),
                        ckit.MenuNode( "search_prev",  ckit.strings["menu_search_prev"],   self.command.SearchPrev ),
                        ckit.MenuNode( separator=True ),
                        ckit.MenuNode( "grep",         ckit.strings["menu_grep"],          self.command.Grep ),
                        ckit.MenuNode( separator=True ),
                        ckit.MenuNode( "tags",         ckit.strings["menu_tags"],
                            items = [
                                ckit.MenuNode( "tags_jump",        ckit.strings["menu_tags_jump"],     self.command.TagsJump,      enabled=isProjectOpened ),
                                ckit.MenuNode( "tags_back",        ckit.strings["menu_tags_back"],     self.command.TagsBack,      enabled=isProjectOpened ),
                                ckit.MenuNode( "load_tags",        ckit.strings["menu_load_tags"],     self.command.LoadTags,      enabled=isProjectOpened ),
                                ckit.MenuNode( "generate_tags",    ckit.strings["menu_generate_tags"], self.command.GenerateTags,  enabled=isProjectOpened ),
                            ]
                        ),
                        ckit.MenuNode( separator=True ),
                        ckit.MenuNode( "replace",      ckit.strings["menu_replace"],       self.command.Replace ),
                        ckit.MenuNode( "compare",      ckit.strings["menu_compare"],       self.command.Compare ),
                    ]
                ),

                ckit.MenuNode(
                    "view", ckit.strings["menu_view"],
                    items=[
                        ckit.MenuNode( "another_pane", ckit.strings["menu_another_pane"],  self.command.AnotherPane ),
                        ckit.MenuNode( separator=True ),
                        ckit.MenuNode( "doclist",      ckit.strings["menu_doclist"],       self.command.DocumentList ),
                    ]
                ),

                ckit.MenuNode(
                    "tool", ckit.strings["menu_tool"],
                    items=[
                        ckit.MenuNode( "bookmark_list",    ckit.strings["menu_bookmark_list"], self.command.BookmarkList ),
                        ckit.MenuNode( "bookmark1",        ckit.strings["menu_bookmark1"],     self.command.Bookmark1 ),
                        ckit.MenuNode( "bookmark2",        ckit.strings["menu_bookmark2"],     self.command.Bookmark2 ),
                        ckit.MenuNode( "bookmark3",        ckit.strings["menu_bookmark3"],     self.command.Bookmark3 ),
                        ckit.MenuNode( "bookmark_next",    ckit.strings["menu_bookmark_next"], self.command.SeekBookmarkNext ),
                        ckit.MenuNode( "bookmark_prev",    ckit.strings["menu_bookmark_prev"], self.command.SeekBookmarkPrev ),
                        ckit.MenuNode( separator=True ),
                        ckit.MenuNode( "outline",          ckit.strings["menu_outline"],       self.command.Outline ),
                        ckit.MenuNode( separator=True ),
                        ckit.MenuNode( "expand_tab",               ckit.strings["menu_expand_tab"],            self.command.ExpandTab,             enabled=isSelected ),
                        ckit.MenuNode( "remove_trailing_space",    ckit.strings["menu_remove_trailing_space"], self.command.RemoveTrailingSpace,   enabled=isSelected ),
                        ckit.MenuNode( "remove_empty_lines",       ckit.strings["menu_remove_empty_lines"],    self.command.RemoveEmptyLines,      enabled=isSelected ),
                        ckit.MenuNode( "remove_marked_lines",      ckit.strings["menu_remove_marked_lines"],   self.command.RemoveMarkedLines,     enabled=isSelected ),
                        ckit.MenuNode( "remove_unmarked_lines",    ckit.strings["menu_remove_unmarked_lines"], self.command.RemoveUnmarkedLines,   enabled=isSelected ),
                        ckit.MenuNode( separator=True,      name="custom_tools_begin" ),
                        ckit.MenuNode( separator=True,      name="custom_tools_end" ),
                        ckit.MenuNode( "config_menu",      ckit.strings["menu_config_menu"],   self.command.ConfigMenu ),
                        ckit.MenuNode( "config_edit",      ckit.strings["menu_config_edit"],   self.command.EditConfig ),
                        ckit.MenuNode( "config_reload",    ckit.strings["menu_config_reload"], self.command.ReloadConfig ),
                    ]
                ),

                ckit.MenuNode(
                    "help", ckit.strings["menu_help"],
                    items=[
                        ckit.MenuNode( "help",             ckit.strings["menu_help"],          self.command.Help ),
                        ckit.MenuNode( separator=True ),
                        ckit.MenuNode( "about",            ckit.strings["menu_about"],         self.command.About ),
                    ]
                ),
            ]
        )

    def applyMenuBar(self):

        visible = self.ini.getint( "MENUBAR", "visible" )

        if visible:
            self.setMenu(self.menu_bar)
        else:
            self.setMenu(None)

        window_rect = self.getWindowRect()
        self.setPosSize( window_rect[0], window_rect[1], self.width(), self.height(), 0 )

    # メニューの検索
    def findMenu( self, node, route ):
        pos = 0
        for item in node.items:
            if isinstance(item,ckit.MenuNode):
                if item.name == route[0]:
                    if len(route)==1:
                        return node, pos
                    return self.findMenu( item, route[1:] )
            pos += 1
        return None, -1

    ## メニュー項目の挿入
    def insertMenu( self, route, item ):
        menu, pos = self.findMenu( self.menu_bar, route )
        if menu and pos>=0:
            menu.items.insert( pos, item )
        else:
            print( "ERROR : insertMenu : not found : ", route )

    ## メニュー項目の追加
    def appendMenu( self, route, item ):
        menu, pos = self.findMenu( self.menu_bar, route )
        if menu and pos>=0:
            menu.items[pos].items.append(item)
        else:
            print( "ERROR : appendMenu : not found : ", route )

    def statusBar(self):
        return self.status_bar

    def _onStatusMessageTimedout(self):
        self.clearStatusMessage()

    ## ステータスバーにメッセージを表示する
    #
    #  @param self      -
    #  @param message   表示するメッセージ文字列
    #  @param timeout   表示時間 (ミリ秒単位)
    #  @param error     エラー形式(赤文字)で表示するか
    #  @param log       メッセージを標準出力にも出力するか
    #
    #  LREdit のメインウインドウの下端にあるステータスバーに、任意の文字列を表示するための関数です。\n\n
    #
    #  引数 timeout に整数を指定すると、時間制限付の表示となり、自動的に消えます。\n
    #  引数 timeout に None を渡すと、時間制限のない表示となり、clearStatusMessage() が呼ばれるまで表示されたままになります。
    #
    #  @sa clearStatusMessage
    #
    def setStatusMessage( self, message, timeout=None, error=False, log=False ):

        if log:
            if error:
                print( ckit.strings["error_prefix"] + message )
            else:
                print( message )

        self.status_bar_layer.setMessage(message,error)

        if not self.status_bar_resistered:
            self.status_bar.registerLayer(self.status_bar_layer)
            self.status_bar_resistered = True

        if timeout!=None:
            self.killTimer( self._onStatusMessageTimedout )
            self.setTimer( self._onStatusMessageTimedout, timeout )

        self.paint( REGION_STATUS_BAR )

        if error:
            ckit.messageBeep()

    ## ステータスバーのメッセージを消す
    #
    #  LREdit のステータスバーに表示されたメッセージを消します。
    #
    #  @sa setStatusMessage
    #
    def clearStatusMessage( self ):

        self.status_bar_layer.setMessage("")

        if self.status_bar_resistered:
            self.status_bar.unregisterLayer(self.status_bar_layer)
            self.status_bar_resistered = False

        self.killTimer(self._onStatusMessageTimedout)

        self.paint( REGION_STATUS_BAR )

    def _onProgressTimedout(self):
        self.clearProgress()

    ## プログレスバーを表示する
    #
    #  @param self      -
    #  @param value     プログレス値 ( 0.0 ～ 1.0、または、[ 0.0 ～ 1.0, ... ] )
    #  @param timeout   表示時間 (ミリ秒単位)
    #
    #  LREdit のメインウインドウの右下の端にある領域に、プログレスバーを表示するか、すでに表示されているプログレスバーの進捗度を変更するための関数です。\n\n
    #
    #  引数 value には、進捗度合いを 0 から 1 までの浮動少数で渡します。\n
    #  通常は、引数 value には単一の浮動少数を渡しますが、二つ以上の進捗度を格納した配列を渡すことも可能で、その場合は複数のプログレスバーが縦に並んで表示されます。\n
    #  引数 value に None を渡したときは、[ビジーインジケータ] としての動作となり、プログレスバーが左右にアニメーションします。\n
    #
    #  引数 timeout に整数を指定すると、時間制限付の表示となり、自動的に消えます。\n
    #  引数 timeout に None を渡すと、時間制限のない表示となり、clearProgress() が呼ばれるまで表示されたままになります。
    #
    #  @sa clearProgress
    #
    def setProgressValue( self, value, timeout=None ):
        if self.progress_bar==None:
            self.progress_bar = ckit.ProgressBarWidget( self, self.width(), self.height()-1, 0, 0 )
        self.progress_bar.setValue(value)

        if timeout!=None:
            self.killTimer( self._onProgressTimedout )
            self.setTimer( self._onProgressTimedout, timeout )

        self.paint( REGION_STATUS_BAR )

    ## プログレスバーを消す
    #
    #  LREdit のプログレスバーを消します。
    #
    #  @sa setProgressValue
    #
    def clearProgress( self ):
        if self.progress_bar:
            self.progress_bar.destroy()
            self.progress_bar = None
        self.paint( REGION_STATUS_BAR )
        self.killTimer( self._onProgressTimedout )

    #--------------------------------------------------------------------------

    ## タイトルバーの表示を更新する
    def updateTitleBar(self):

        title = "%s" % lredit_resource.lredit_appname

        if self.project:
            title += " - %s" % self.project.name

        edit = self.activeEditPane().edit
        if edit:
            filename = edit.doc.getFullpath()
            if not filename:
                filename = edit.doc.getName()
            title += " - [%s]" % filename

            if edit.doc.isModified():
                title += " *"

        if self.title != title:
            self.setTitle(title)
            self.title = title

    def _onTabSelectionChanged( self, selection, item ):
        edit = item[1]
        self.activeOpen( edit=edit )

    ## タブバーの状態を更新する
    def updateTabBar(self):

        for pane in ( self.left_edit_pane, self.right_edit_pane ):

            tab_items = []
            selection = None
            for i, edit in enumerate( pane.edit_list ):
                tab_items.append( ( edit.doc.getName(), edit ) )
                if edit==pane.edit:
                    selection = i

            pane.tab.setItems( tab_items )
            pane.tab.setSelection(selection)

    ## フッタとタイトルバー表示を更新する
    def updateInformation( self, doc=None, edit=None ):
        if ((edit and edit==self.left_edit_pane.edit) or
            (doc and self.left_edit_pane.edit and doc==self.left_edit_pane.edit.doc)):
            self.paint( REGION_LEFT_FOOTER )
        if ((edit and edit==self.right_edit_pane.edit) or
            (doc and self.right_edit_pane.edit and doc==self.right_edit_pane.edit.doc)):
            self.paint( REGION_RIGHT_FOOTER )
        self.updateTitleBar()

    def _onDocumentTextModified( self, edit, left, old_right, new_right ):

        # 編集内容にジャンプリストの行番号を追従させる
        if old_right.line != new_right.line:
            for jump in self.jump_list:
                jump.shiftLineNo( edit.doc.getFullpath(), left.line, old_right.line, new_right.line )

        self.updateInformation(doc=edit.doc)

    def _onEditSelectionChanged( self, edit, anchor, cursor ):
        self.updateInformation(edit=edit)

    # BookmarkTable から TextEditWidget にブックマーク情報を反映させる
    def loadBookmarkList( self, edit ):
        fullpath = edit.doc.getFullpath()
        if fullpath:
            bookmark_list = self.bookmarks.getBookmarkList(fullpath)
            edit.setBookmarkList(bookmark_list)

    # TextEditWidget から BookmarkTable にブックマーク情報を反映させる
    def storeBookmarkList( self, edit ):
        fullpath = edit.doc.getFullpath()
        if fullpath:
            bookmark_list = edit.getBookmarkList()
            self.bookmarks.setBookmarkList( fullpath, bookmark_list )

    def _createEditWidget( self, doc ):

        edit = ckit.TextWidget( self, 0, 0, 0, 0, message_handler=self.setStatusMessage )

        edit.setDocument(doc)
        self.loadBookmarkList(edit)

        edit.doc.text_modified_handler_list.append( self._onDocumentTextModified )
        edit.selection_changed_handler_list.append( self._onEditSelectionChanged )

        edit.configure()

        return edit


    def _findEditFromDocument( self, doc ):
        for edit in self.edit_list:
            if edit.doc==doc:
                return edit
        return None


    def _findEditFromFilename( self, filename ):

        filename = os.path.abspath(filename)
        filename = os.path.normpath(filename)
        filename = filename.lower()

        for edit in self.edit_list:
            doc_filename = edit.doc.getFullpath()
            if doc_filename:
                doc_filename = os.path.normpath(doc_filename)
                doc_filename = doc_filename.lower()
                if doc_filename==filename:
                    return edit
        return None


    def _open( self, pane, another_pane, doc=None, edit=None, filename=None, lineno=None, sort=True, duplicate=False, focus=False, pane_stable=False ):

        layout2_old = (self.inactiveEditPane().edit!=None)

        # ファイル名を履歴に残す
        if filename!=None:
            filename = os.path.abspath(filename)
            filename = os.path.normpath(filename)
            if not filename.lower().startswith(ckit.getTempPath().lower()):
                self.filename_history.append( ckit.normPath(filename) )

        # Documentかファイル名からEditを導く
        if not edit:
            if doc:
                edit = self._findEditFromDocument(doc)
            else:
                edit = self._findEditFromFilename(filename)

        if edit:

            # 既存のEditである場合、すでに所属しているPaneで開く
            if pane_stable:
                if edit in another_pane.edit_list:
                    tmp = another_pane
                    another_pane = pane
                    pane = tmp

            # Editを複製する
            if duplicate:
                edit = self._createEditWidget(edit.doc)
                pane.edit_list.append(edit)

            # 反対側のPaneのリストから削除する
            if edit in another_pane.edit_list:
                another_pane.edit_list.remove(edit)
                if another_pane.edit == edit:
                    for edit2 in self.edit_list:
                        if edit2 in another_pane.edit_list:
                            another_pane.edit = edit2
                            another_pane.edit.show(True)
                            break
                    else:
                        another_pane.edit = None
                        if pane==self.left_edit_pane:
                            self.focus_edit = MainWindow.FOCUS_EDIT_LEFT
                        else:
                            self.focus_edit = MainWindow.FOCUS_EDIT_RIGHT

                pane.edit_list.append(edit)

            # Editのリストの先頭にする
            if sort:
                try:
                    self.edit_list.remove(edit)
                except ValueError:
                    pass
                self.edit_list.insert(0,edit)

        else:
            # ファイル名からDocumentを作る
            try:
                if doc==None:
                    doc = ckit.Document( filename=filename, mode=self.createModeFromFilename(filename) )
            except IOError as e:
                print( ckit.strings["error_open_failed"] % filename )
                self.setStatusMessage( ckit.strings["statusbar_open_failed"] % filename, 3000, error=True )
                self.filename_history.remove( ckit.normPath(filename) )
                return
            except UnicodeError as e:
                print( ckit.strings["error_load_failed"] % filename )
                print( "      : " + ckit.strings["not_textfile"] )
                self.setStatusMessage( ckit.strings["statusbar_open_failed"] % filename, 3000, error=True )
                self.filename_history.remove( ckit.normPath(filename) )
                return

            # DocumentからEditを作る
            edit = self._createEditWidget(doc)
            pane.edit_list.append(edit)
            self.edit_list.insert(0,edit)

        if pane.edit:
            pane.edit.show(False)
        pane.edit = edit
        pane.edit.show(True)

        if focus:
            if pane==self.left_edit_pane:
                self.focus_edit = MainWindow.FOCUS_EDIT_LEFT
            else:
                self.focus_edit = MainWindow.FOCUS_EDIT_RIGHT

        self.updateCursor()

        # 1画面/2画面を切り替える
        layout2_new = (self.inactiveEditPane().edit!=None)
        if layout2_new and not layout2_old:
            self.command.MoveSeparatorCenter()
        elif not layout2_new and layout2_old:
            self.command.MoveSeparatorMaximizeH()

        self.updatePaneRect()

        if lineno!=None:
            pane.edit.jumpLineNo(lineno)

    ## 左の編集ペインでオープンする
    def leftOpen( self, doc=None, edit=None, filename=None, lineno=None, sort=True, duplicate=False ):
        self._open( self.left_edit_pane, self.right_edit_pane, doc, edit, filename, lineno, sort, duplicate, focus=False, pane_stable=False )
        self.paint( REGION_EDIT )

    ## 右の編集ペインでオープンする
    def rightOpen( self, doc=None, edit=None, filename=None, lineno=None, sort=True, duplicate=False ):
        self._open( self.right_edit_pane, self.left_edit_pane, doc, edit, filename, lineno, sort, duplicate, focus=False, pane_stable=False )
        self.paint( REGION_EDIT )

    ## アクティブな編集ペインでオープンする
    def activeOpen( self, doc=None, edit=None, filename=None, lineno=None, sort=True, duplicate=False ):
        self._open( self.activeEditPane(), self.inactiveEditPane(), doc, edit, filename, lineno, sort, duplicate, focus=True, pane_stable=True )
        self.paint( REGION_EDIT )

    ## 非アクティブな編集ペインでオープンする
    def inactiveOpen( self, doc=None, edit=None, filename=None, lineno=None, sort=True, duplicate=False ):
        self._open( self.inactiveEditPane(), self.activeEditPane(), doc, edit, filename, lineno, sort, duplicate, focus=False, pane_stable=False )
        self.paint( REGION_EDIT )

    def _close( self, edit ):

        if edit in self.left_edit_pane.edit_list:
            pane = self.left_edit_pane
            another_pane = self.right_edit_pane
        else:
            pane = self.right_edit_pane
            another_pane = self.left_edit_pane

        # Compare の片方を閉じるときは両方の色をクリアする
        if edit.isDiffColorMode():
            for edit2 in self.edit_list:
                edit2.clearDiffColor()
            self.jump_list = []

        # 変更済みのEditに関しては保存確認する
        if edit.doc.isModified():
            self.activeOpen( edit=edit )
            result = self.saveDocument( edit.doc, confirm=True )
            if result==None:
                return None

        self.storeBookmarkList(edit)

        pane.edit.show(False)
        pane.edit = None
        self.edit_list.remove(edit)
        pane.edit_list.remove(edit)
        edit.destroy()

        # Closeしたあと、次のEditを表示する
        for edit in self.edit_list:
            if edit in pane.edit_list:
                self.activeOpen( edit=edit )
                break
        else:

            # Paneに所属しているEditがなくなったら、2 Paneモードを解除
            if another_pane.edit!=None:
                if another_pane==self.left_edit_pane:
                    self.focus_edit = MainWindow.FOCUS_EDIT_LEFT
                else:
                    self.focus_edit = MainWindow.FOCUS_EDIT_RIGHT
                self.updateCursor()
                self.command.MoveSeparatorMaximizeH()
            else:
                # １つもEditがなくなったら、[undefined] を新規作成
                self.command.New()

        return True


    ## ドキュメントを保存する
    #
    def saveDocument( self, doc, filename=None, confirm=False, input_name=False ):

        if confirm:
            result = lredit_msgbox.popMessageBox(
                self,
                lredit_msgbox.MSGBOX_TYPE_YESNO,
                ckit.strings["msgbox_title_save"],
                ckit.strings["msgbox_ask_save_document"] % doc.getName() )
            if result==lredit_msgbox.MSGBOX_RESULT_YES:
                pass
            elif result==lredit_msgbox.MSGBOX_RESULT_NO:
                return False
            else:
                return None

        if not filename:
            filename = doc.filename

        if not filename or input_name:
            filename = self.inputFilename( "Save", filename )
            if not filename : return None
            filename = os.path.abspath(filename)
            filename = ckit.normPath(filename)

        fd = open( filename, "wb" )
        doc.writeFile(fd)
        fd.close()

        doc.filename = filename

        doc.clearModified()
        doc.clearFileModified()

        self.checkProjectFileModified()

        self.paint( REGION_EDIT )
        self.updateTitleBar()

        return True


    ## ドキュメントを全て保存する
    def saveDocumentAll( self, confirm=False, untitled=False ):

        result = True

        for edit in self.edit_list:
            if untitled or edit.doc.getFullpath():
                if edit.doc.isModified():
                    result = self.saveDocument( edit.doc, confirm=confirm )
                    if result==None:
                        break
                self.storeBookmarkList(edit)

        return result


    def checkFileModifiedAll(self):

        cancel = False

        for edit in self.edit_list:
            doc = edit.doc
            if doc.getFullpath():
                if doc.isFileModified():

                    if not cancel:
                        result = lredit_msgbox.popMessageBox(
                            self,
                            lredit_msgbox.MSGBOX_TYPE_YESNO,
                            ckit.strings["msgbox_title_modified_reload"],
                            ckit.strings["msgbox_ask_modified_reload"] % doc.getName() )
                    else:
                        result = lredit_msgbox.MSGBOX_RESULT_NO

                    if result==None:
                        cancel = True

                    if result==lredit_msgbox.MSGBOX_RESULT_YES:
                        filename = doc.getFullpath()
                        doc = ckit.Document( filename=filename, mode=self.createModeFromFilename(filename) )
                        edit.setDocument(doc)
                    else:
                        doc.clearFileModified()

    def checkProjectFileModified(self):
        if self.project and self.project.isFileModified():
            self.project = lredit_project.Project(self.project.filename)
            print( ckit.strings["project_reloaded"] + "\n" )


    #--------------------------------------------------------------------------

    def createModeFromName( self, name ):
        for mode in self.mode_list:
            if mode.name==name:
                return mode()
        return ckit.TextMode()

    def createModeFromFilename( self, filename ):
        filename = os.path.basename(filename)
        for item in self.fileext_list:
            for pattern in item[0].split():
                if fnmatch.fnmatch( filename, pattern ):
                    return self.createModeFromName(item[1])
        return ckit.TextMode()

    ## 左の編集ペインのモードを取得する
    def leftPaneMode(self):
        try:
            return self.left_edit_pane.edit.doc.mode
        except AttributeError:
            return None

    ## 右の編集ペインのモードを取得する
    def rightPaneMode(self):
        try:
            return self.right_edit_pane.edit.doc.mode
        except AttributeError:
            return None

    ## アクティブな編集ペインのモードを取得する
    def activeEditPaneMode(self):
        if self.focus_edit==MainWindow.FOCUS_EDIT_LEFT:
            return self.leftPaneMode()
        elif self.focus_edit==MainWindow.FOCUS_EDIT_RIGHT:
            return self.rightPaneMode()
        else:
            assert(False)

    ## 非アクティブな編集ペインのモードを取得する
    def inactiveEditPaneMode(self):
        if self.focus_edit==MainWindow.FOCUS_EDIT_LEFT:
            return self.rightPaneMode()
        elif self.focus_edit==MainWindow.FOCUS_EDIT_RIGHT:
            return self.rightPaneMode()
        else:
            assert(False)

    #--------------------------------------------------------------------------

    def loadTheme(self):
        name = self.ini.get( "THEME", "name" )
        default_color = {
            "line_cursor" : (255,128,128),
            "diff_bg1"    : (100,50,50),
            "diff_bg2"    : (50,100,50),
            "diff_bg3"    : (50,50,100),
        }
        ckit.setTheme( name, default_color )
        self.theme_enabled = False

    def reloadTheme(self):
        self.loadTheme()
        self.destroyThemePlane()
        self.createThemePlane()
        self.updateColor()
        self.updateWallpaper()

    def createThemePlane(self):

        self.plane_edit_separator = ckit.ThemePlane3x3( self, 'vseparator.png' )
        self.plane_footer = ckit.ThemePlane3x3( self, 'footer.png' )
        self.plane_isearch = ckit.ThemePlane3x3( self, 'isearch.png', 1 )
        self.plane_statusbar = ckit.ThemePlane3x3( self, 'statusbar.png', 1.5 )
        self.plane_commandline = ckit.ThemePlane3x3( self, 'commandline.png', 1 )

        self.plane_isearch.show(False)
        self.plane_commandline.show(False)

        self.left_edit_pane.tab.createThemePlane()
        self.right_edit_pane.tab.createThemePlane()

        for edit in self.edit_list:
            edit.createThemePlane()

        self.log_pane.edit.createThemePlane()

        self.theme_enabled = True

        self.updatePaneRect()

    def destroyThemePlane(self):

        self.plane_edit_separator.destroy()
        self.plane_footer.destroy()
        self.plane_isearch.destroy()
        self.plane_statusbar.destroy()
        self.plane_commandline.destroy()

        self.left_edit_pane.tab.destroyThemePlane()
        self.right_edit_pane.tab.destroyThemePlane()

        for edit in self.edit_list:
            edit.destroyThemePlane()

        self.log_pane.edit.destroyThemePlane()

        self.theme_enabled = False

    def updatePaneRect(self):

        if self.left_edit_pane.edit==None and self.right_edit_pane.edit:
            self.left_edit_pane_width = 0
        elif self.left_edit_pane.edit and self.right_edit_pane.edit==None:
            self.left_edit_pane_width = self.editPaneWidth()

        if self.left_edit_pane.tab:

            rect = self.leftTabBarRect()

            x = rect[0]
            y = rect[1]
            width = rect[2]-rect[0]
            height = rect[3]-rect[1]

            self.left_edit_pane.tab.setPosSize( x, y, width, height )

        if self.right_edit_pane.tab:

            rect = self.rightTabBarRect()

            x = rect[0]
            y = rect[1]
            width = rect[2]-rect[0]
            height = rect[3]-rect[1]

            self.right_edit_pane.tab.setPosSize( x, y, width, height )

        if self.left_edit_pane.edit:

            rect = self.leftEditPaneRect()

            x = rect[0]
            y = rect[1]
            width = rect[2]-rect[0]
            height = rect[3]-rect[1]

            if self.left_edit_pane.edit : self.left_edit_pane.edit.setPosSize( x, y+1, width, height-2 )

        if self.right_edit_pane.edit:

            rect = self.rightEditPaneRect()

            x = rect[0]
            y = rect[1]
            width = rect[2]-rect[0]
            height = rect[3]-rect[1]

            if self.right_edit_pane.edit : self.right_edit_pane.edit.setPosSize( x, y+1, width, height-2 )

        if self.log_pane.edit:

            rect = self.logPaneRect()

            x = rect[0]
            y = rect[1]
            width = rect[2]-rect[0]
            height = rect[3]-rect[1]

            self.log_pane.edit.setPosSize( x, y, width, height )

        if self.theme_enabled:

            client_rect = self.getClientRect()
            offset_x, offset_y = self.charToClient( 0, 0 )
            char_w, char_h = self.getCharSize()

            if self.left_edit_pane.edit and self.right_edit_pane.edit:
                rect = self.editSeparatorRect()
                x = rect[0]
                y = rect[1]
                width = rect[2]-rect[0]
                height = rect[3]-rect[1]
                self.plane_edit_separator.setPosSizeByChar( self, x, y, 1, height )
                self.plane_edit_separator.show(True)
            else:
                self.plane_edit_separator.show(False)

            rect = self.editPaneRect()
            x = rect[0]
            y = rect[3]-1
            width = rect[2]-rect[0]
            height = 1
            self.plane_footer.setPosSizeByChar( self, x, y, width, height )

            self.plane_statusbar.setPosSize( 0, (self.height()-1)*char_h+offset_y, client_rect[2], client_rect[3]-((self.height()-1)*char_h+offset_y) )

    #--------------------------------------------------------------------------

    def updateColor(self):
        ckit.TextWidget.updateColor()
        self.setBGColor( ckit.getColor("bg") )
        self.setCursorColor( ckit.getColor("cursor0"), ckit.getColor("cursor1") )
        self.paint()

    #--------------------------------------------------------------------------

    def updateWallpaper(self):

        visible = self.ini.getint( "WALLPAPER", "visible" )
        strength = self.ini.getint( "WALLPAPER", "strength" )
        filename = self.ini.get( "WALLPAPER", "filename" )

        def destroyWallpaper():
            if self.wallpaper:
                self.wallpaper.destroy()
                self.wallpaper = None

        if visible:

            if filename=="":
                lredit_msgbox.popMessageBox(
                    self,
                    lredit_msgbox.MSGBOX_TYPE_OK,
                    ckit.strings["msgbox_title_wallpaper_error"],
                    ckit.strings["msgbox_wallpaper_filename_empty"] )
                destroyWallpaper()
                self.ini.set( "WALLPAPER", "visible", "0" )
                return

            destroyWallpaper()
            self.wallpaper = lredit_wallpaper.Wallpaper(self)
            try:
                self.wallpaper.load(filename,strength)
            except:
                print( ckit.strings["error_invalid_wallpaper"] % filename )
                destroyWallpaper()
                self.ini.set( "WALLPAPER", "visible", "0" )
                self.ini.set( "WALLPAPER", "filename", "" )
                return

            self.wallpaper.adjust()

        else:
            destroyWallpaper()

    #--------------------------------------------------------------------------

    ## ウインドウの内容を描画する
    def paint( self, option=REGION_ALL ):

        if not self.initialized : return

        """
        if option & REGION_FOCUSED:
            if option & REGION_FOCUSED_EDIT:
                option |= [ REGION_LEFT_EDIT, REGION_RIGHT_EDIT ][self.focus_edit]
            if option & REGION_FOCUSED_FOOTER:
                option |= [ REGION_LEFT_FOOTER, REGION_RIGHT_FOOTER ][self.focus_edit]
        """

        if option & (REGION_LEFT_TAB|REGION_LEFT_EDIT|REGION_LEFT_FOOTER) and self.left_edit_pane.widget():

            rect = self.leftEditPaneRect()

            x = rect[0]
            y = rect[1]
            width = rect[2]-rect[0]
            height = rect[3]-rect[1]

            if option & REGION_LEFT_TAB and height>=1 :
                self.left_edit_pane.tab.paint()
            if option & REGION_LEFT_EDIT and height>=1 :
                self.left_edit_pane.widget().paint()
            if option & REGION_LEFT_FOOTER and height>=1 :
                if self.left_edit_pane.footer_paint_hook:
                    self.left_edit_pane.footer_paint_hook( x, y+height-1, width, 1, self.left_edit_pane )
                else:
                    self._paintFooterInfo( x, y+height-1, width, 1, self.left_edit_pane )

        if option & (REGION_RIGHT_TAB|REGION_RIGHT_EDIT|REGION_RIGHT_FOOTER) and self.right_edit_pane.widget():

            rect = self.rightEditPaneRect()

            x = rect[0]
            y = rect[1]
            width = rect[2]-rect[0]
            height = rect[3]-rect[1]

            if option & REGION_RIGHT_TAB and height>=1 :
                self.right_edit_pane.tab.paint()
            if option & REGION_RIGHT_EDIT and height>=1 :
                self.right_edit_pane.widget().paint()
            if option & REGION_RIGHT_FOOTER and height>=1 :
                if self.right_edit_pane.footer_paint_hook:
                    self.right_edit_pane.footer_paint_hook( x, y+height-1, width, 1, self.right_edit_pane )
                else:
                    self._paintFooterInfo( x, y+height-1, width, 1, self.right_edit_pane )

        if option & REGION_EDIT_SEPARATOR:

            rect = self.editSeparatorRect()

            x = rect[0]
            y = rect[1]
            width = rect[2]-rect[0]
            height = rect[3]-rect[1]

            attr = ckit.Attribute( fg=ckit.getColor("bar_fg") )
            str_whitespace = " " * width

            for i in range( y, y+height ):
                self.putString( x, i, width, 1, attr, str_whitespace )

        if option & REGION_LOG:
            self.log_pane.widget().paint()

        if option & REGION_STATUS_BAR:
            if self.status_bar_paint_hook:
                if self.progress_bar:
                    self.progress_bar.show(False)
                self.status_bar_paint_hook( 0, self.height()-1, self.width(), 1 )
            else:
                if self.progress_bar:
                    progress_width = min( self.width() // 2, 20 )
                    self.progress_bar.setPosSize( self.width()-progress_width, self.height()-1, progress_width, 1 )
                    self.progress_bar.show(True)
                    self.progress_bar.paint()
                else:
                    progress_width = 0
                self.status_bar.paint( self, 0, self.height()-1, self.width()-progress_width, 1 )

        if not self.isActive():
            self.setCursorPos( -1, -1 )

    def _paintFooterInfo( self, x, y, width, height, pane ):
        attr = ckit.Attribute( fg=ckit.getColor("bar_fg") )
        self.putString( x, y, width, height, attr, " " * width )
        str_info = pane.edit.doc.getName()
        if pane.edit.doc.isModified() : str_info += " *"
        if pane.edit.doc.minor_mode_list:
            str_info += " (%s:%s)" % ( pane.edit.doc.mode.name, " ".join( map(lambda mode:mode.name, pane.edit.doc.minor_mode_list) ) )
        else:
            str_info += " (%s)" % pane.edit.doc.mode.name
        def lineendName(lineend):
            if lineend=="\r\n":
                return "crlf"
            elif lineend=="\r":
                return "cr"
            elif lineend=="\n":
                return "lf"
            else:
                return ""
        str_info += " [%s:%s]" % ( pane.edit.doc.encoding, lineendName(pane.edit.doc.lineend) )
        cursor = pane.edit.selection.cursor()
        str_cursor = "%d:%d" % (cursor.line+1, cursor.index+1)
        str_info += " %8s" % str_cursor
        margin = max((width-len(str_info))//2,0)
        self.putString( x+margin, y, width-margin, height, attr, str_info )
        # チラつきの原因になるのでコメントアウト
        #self.flushPaint()

    #--------------------------------------------------------------------------

    def registerStdio( self ):

        class Stdout:
            def write( writer_self, s ):
                edit = self.log_pane.edit
                end = edit.pointDocumentEnd()
                edit.modifyText( end, end, s, append_undo=False, ignore_readonly=True )

        class Stderr:
            def write( writer_self, s ):
                edit = self.log_pane.edit
                end = edit.pointDocumentEnd()
                edit.modifyText( end, end, s, append_undo=False, ignore_readonly=True )

        if not self.debug:
            sys.stdout = Stdout()
            sys.stderr = Stderr()

    def unregisterStdio( self ):
        sys.stdout = sys.__stdout__
        sys.stderr = sys.__stderr__

    ## 設定を読み込む
    #
    #  キーマップや モードリスト などをリセットした上で、config,py を再読み込みします。
    #
    def configure( self ):

        # キーボードの種別によってキー定義文字列を割り当てる
        ckit.Keymap.init()

        ## メインウインドウのキー割り当て
        self.keymap = ckit.Keymap()

        self.keymap[ "C-A-Left" ] = self.command.MoveSeparatorLeft
        self.keymap[ "C-A-Right" ] = self.command.MoveSeparatorRight
        self.keymap[ "C-A-Up" ] = self.command.MoveSeparatorUp
        self.keymap[ "C-A-Down" ] = self.command.MoveSeparatorDown
        self.keymap[ "S-Escape" ] = self.command.CancelTask
        self.keymap[ "C-Minus" ] = self.command.MoveSeparatorCenter
        self.keymap[ "C-S-Minus" ] = self.command.MoveSeparatorMaximizeH
        self.keymap[ "C-F4" ] = self.command.Close
        self.keymap[ "C-Q" ] = self.command.Close
        self.keymap[ "A-F4" ] = self.command.Quit
        self.keymap[ "C-Tab" ] = self.command.DocumentNext
        self.keymap[ "A-X" ] = self.command.CommandLine
        self.keymap[ "C-O" ] = self.command.Open
        self.keymap[ "C-S" ] = self.command.Save
        self.keymap[ "C-J" ] = self.command.Jump
        self.keymap[ "C-F" ] = self.command.Search
        self.keymap[ "C-R" ] = self.command.Replace
        self.keymap[ "C-S-F" ] = self.command.Grep
        self.keymap[ "F11" ] = self.command.SearchResultNext
        self.keymap[ "S-F11" ] = self.command.SearchResultPrev
        self.keymap[ "F4" ] = self.command.TagsJump
        self.keymap[ "S-F4" ] = self.command.TagsBack

        self.keymap[ "Left" ] = self.command.CursorLeft
        self.keymap[ "Right" ] = self.command.CursorRight
        self.keymap[ "C-Left" ] = self.command.CursorWordLeft
        self.keymap[ "C-Right" ] = self.command.CursorWordRight
        self.keymap[ "Home" ] = CommandSequence( self.command.CursorLineFirstGraph, self.command.CursorLineBegin )
        self.keymap[ "End" ] = self.command.CursorLineEnd
        self.keymap[ "Up" ] = self.command.CursorUp
        self.keymap[ "Down" ] = self.command.CursorDown
        self.keymap[ "PageUp" ] = self.command.CursorPageUp
        self.keymap[ "PageDown" ] = self.command.CursorPageDown
        self.keymap[ "A-Up" ] = self.command.SeekModifiedOrBookmarkPrev
        self.keymap[ "A-Down" ] = self.command.SeekModifiedOrBookmarkNext
        self.keymap[ "C-Home" ] = self.command.CursorDocumentBegin
        self.keymap[ "C-End" ] = self.command.CursorDocumentEnd
        self.keymap[ "C-B" ] = self.command.CursorCorrespondingBracket

        self.keymap[ "C-Up" ] = self.command.ScrollUp
        self.keymap[ "C-Down" ] = self.command.ScrollDown
        self.keymap[ "C-L" ] = self.command.ScrollCursorCenter

        self.keymap[ "S-Left" ] = self.command.SelectLeft
        self.keymap[ "S-Right" ] = self.command.SelectRight
        self.keymap[ "C-S-Left" ] = self.command.SelectWordLeft
        self.keymap[ "C-S-Right" ] = self.command.SelectWordRight
        self.keymap[ "S-Home" ] = self.command.SelectLineBegin
        self.keymap[ "S-End" ] = self.command.SelectLineEnd
        self.keymap[ "S-Up" ] = self.command.SelectUp
        self.keymap[ "S-Down" ] = self.command.SelectDown
        self.keymap[ "S-PageUp" ] = self.command.SelectPageUp
        self.keymap[ "S-PageDown" ] = self.command.SelectPageDown
        self.keymap[ "C-S-B" ] = self.command.SelectCorrespondingBracket
        self.keymap[ "C-S-Home" ] = self.command.SelectDocumentBegin
        self.keymap[ "C-S-End" ] = self.command.SelectDocumentEnd
        self.keymap[ "C-A" ] = self.command.SelectDocument

        self.keymap[ "C-S-Up" ] = self.command.SelectScrollUp
        self.keymap[ "C-S-Down" ] = self.command.SelectScrollDown

        self.keymap[ "Return" ] = CommandSequence( self.command.Enter, self.command.InsertReturnAutoIndent )
        self.keymap[ "Tab" ] = CommandSequence( self.command.IndentSelection, self.command.InsertTab )
        self.keymap[ "S-Tab" ] = CommandSequence( self.command.UnindentSelection, self.command.CursorTabLeft )
        self.keymap[ "Delete" ] = self.command.Delete
        self.keymap[ "Back" ] = self.command.DeleteCharLeft
        self.keymap[ "C-Delete" ] = self.command.DeleteWordRight
        self.keymap[ "C-Back" ] = self.command.DeleteWordLeft
        self.keymap[ "C-D" ] = self.command.DeleteCharRight
        self.keymap[ "C-H" ] = self.command.DeleteCharLeft
        self.keymap[ "C-K" ] = self.command.DeleteLineRight
        self.keymap[ "C-C" ] = self.command.Copy
        self.keymap[ "C-X" ] = self.command.Cut
        self.keymap[ "C-V" ] = self.command.Paste
        self.keymap[ "C-Z" ] = self.command.Undo
        self.keymap[ "C-Y" ] = self.command.Redo
        self.keymap[ "C-N" ] = self.command.SearchNext
        self.keymap[ "C-S-N" ] = self.command.SearchPrev
        self.keymap[ "C-Space" ] = self.command.CompleteAbbrev

        self.keymap[ "C-E" ] = self.command.ExtensionMenu
        self.keymap[ "C-M" ] = self.command.Bookmark1
        self.keymap[ "Escape" ] = CommandSequence( self.command.CloseList, self.command.FocusEdit, self.command.SelectCancel )

        ## エディットメニューの項目
        self.ext_menu_items = [
            ( "Another Pane",      "C-W", self.command.AnotherPane ),
            ( "Project Files",     "C-P", self.command.ProjectFileList ),
            ( "Recent Files",      "C-H", self.command.RecentFileList ),
            ( "Bookmark List",     "C-M", self.command.BookmarkList ),
            ( "Document List",     "C-D", self.command.DocumentList ),
            ( "Outline Analysis",  "C-O", self.command.Outline ),
            ( "Search Result",     "C-S", self.command.SearchResultList ),
        ]

        ## モードのリスト
        self.mode_list = [
            lredit_mode.PythonMode,
            lredit_mode.JavaScriptMode,
            lredit_mode.CMode,
            lredit_mode.CppMode,
            lredit_mode.CsharpMode,
            lredit_mode.JavaMode,
            lredit_mode.GlslMode,
            lredit_mode.XmlMode,
            lredit_mode.HtmlMode,
            lredit_mode.MakefileMode,
            lredit_mode.BatchMode,
            ckit.TextMode,
        ]

        ## マイナーモードのリスト
        self.minor_mode_list = [
            lredit_minormode.TestMode,
        ]

        ## ファイル名とモードの関連付け
        self.fileext_list = [
            ( "*.py *.pyw *.pys", "python" ),
            ( "*.js", "javascript" ),
            ( "*.cpp *.cc *.cxx *.hpp *.hh *.hxx *.h", "c++" ),
            ( "*.c *.h", "c" ),
            ( "*.cs", "c#" ),
            ( "*.java", "java" ),
            ( "*.vert *.frag *.geo", "glsl" ),
            ( "*.xml", "xml" ),
            ( "*.html *.htm", "html" ),
            ( "makefile *.mk", "makefile" ),
            ( "*.bat", "batch" ),
            ( "*", "text" ),
        ]

        ## コマンドラインの機能リスト
        self.commandline_list = [
            self.launcher,
            lredit_commandline.commandline_Open(self),
            lredit_commandline.commandline_Document(self),
            lredit_commandline.commandline_Mode(self),
            lredit_commandline.commandline_MinorMode(self),
            lredit_commandline.commandline_Int32Hex(),
            lredit_commandline.commandline_Calculator(),
        ]

        ## コマンドラインから実行可能な追加のコマンド
        self.launcher.command_list = [
        ]

        self.prepareMenuBar()

        ckit.reloadConfigScript( self.config_filename )
        ckit.callConfigFunc("configure",self)

        for mode in self.mode_list:
            try:
                mode.staticconfigure(self)
            except:
                traceback.print_exc()

        for mode in self.minor_mode_list:
            try:
                mode.staticconfigure(self)
            except:
                traceback.print_exc()

        for edit in self.edit_list:
            try:
                edit.configure()
            except:
                traceback.print_exc()

        try:
            self.log_pane.edit.configure()
        except:
            traceback.print_exc()

        self.applyMenuBar()


    def loadState(self):

        if os.path.exists(self.ini_filename):
            try:
                fd = open( self.ini_filename, "r", encoding="utf-8" )
                msvcrt.locking( fd.fileno(), msvcrt.LK_LOCK, 1 )
                self.ini.readfp(fd)
                fd.close()
            except Exception as e:

                MB_OK = 0
                ctypes.windll.user32.MessageBoxW(
                    0,
                    ckit.strings["error_ini_file_load_failed"] + "\n\n" + traceback.format_exc(),
                    ckit.strings["msgbox_title_generic_error"],
                    MB_OK )

                # ini ファイルの読み込みに失敗したので保存しない
                self.ini_filename = None

        ini_version = "0.00"
        try:
            ini_version = self.ini.get("GLOBAL","version")
        except:
            pass

        try:
            self.ini.add_section("GLOBAL")
        except configparser.DuplicateSectionError:
            pass

        try:
            self.ini.add_section("GEOMETRY")
        except configparser.DuplicateSectionError:
            pass

        try:
            self.ini.add_section("FONT")
        except configparser.DuplicateSectionError:
            pass

        try:
            self.ini.add_section("THEME")
        except configparser.DuplicateSectionError:
            pass

        try:
            self.ini.add_section("MENUBAR")
        except configparser.DuplicateSectionError:
            pass

        try:
            self.ini.add_section("WALLPAPER")
        except configparser.DuplicateSectionError:
            pass

        try:
            self.ini.add_section("FILENAME")
        except configparser.DuplicateSectionError:
            pass

        try:
            self.ini.add_section("SEARCH")
        except configparser.DuplicateSectionError:
            pass

        try:
            self.ini.add_section("REPLACE")
        except configparser.DuplicateSectionError:
            pass

        try:
            self.ini.add_section("GREP")
        except configparser.DuplicateSectionError:
            pass

        try:
            self.ini.add_section("COMPARE")
        except configparser.DuplicateSectionError:
            pass

        try:
            self.ini.add_section("ZENHAN")
        except configparser.DuplicateSectionError:
            pass

        try:
            self.ini.add_section("COMMANDLINE")
        except configparser.DuplicateSectionError:
            pass

        try:
            self.ini.add_section("BOOKMARK")
        except configparser.DuplicateSectionError:
            pass

        try:
            self.ini.add_section("MISC")
        except configparser.DuplicateSectionError:
            pass

        try:
            self.ini.add_section("DEBUG")
        except configparser.DuplicateSectionError:
            pass

        self.ini.set( "GLOBAL", "version", lredit_resource.lredit_version )

        if not self.ini.has_option( "GEOMETRY", "x" ):
            self.ini.set( "GEOMETRY", "x", str(0) )
        if not self.ini.has_option( "GEOMETRY", "y" ):
            self.ini.set( "GEOMETRY", "y", str(0) )
        if not self.ini.has_option( "GEOMETRY", "width" ):
            self.ini.set( "GEOMETRY", "width", str(80) )
        if not self.ini.has_option( "GEOMETRY", "height" ):
            self.ini.set( "GEOMETRY", "height", str(32) )
        if not self.ini.has_option( "GEOMETRY", "log_pane_height" ):
            self.ini.set( "GEOMETRY", "log_pane_height", str(10) )
        if not self.ini.has_option( "GEOMETRY", "left_edit_pane_width" ):
            self.ini.set( "GEOMETRY", "left_edit_pane_width", str( (self.ini.getint( "GEOMETRY", "width" )-1)//2 ) )

        if not self.ini.has_option( "FONT", "name" ):
            self.ini.set( "FONT", "name", "" )
        if not self.ini.has_option( "FONT", "size" ):
            self.ini.set( "FONT", "size", "12" )

        if not self.ini.has_option( "THEME", "name" ):
            self.ini.set( "THEME", "name", "black" )

        if not self.ini.has_option( "MENUBAR", "visible" ):
            self.ini.set( "MENUBAR", "visible", "1" )

        if not self.ini.has_option( "WALLPAPER", "visible" ):
            self.ini.set( "WALLPAPER", "visible", "0" )
        if not self.ini.has_option( "WALLPAPER", "strength" ):
            self.ini.set( "WALLPAPER", "strength", "30" )
        if not self.ini.has_option( "WALLPAPER", "filename" ):
            self.ini.set( "WALLPAPER", "filename", "" )

        if not self.ini.has_option( "SEARCH", "word" ):
            self.ini.set( "SEARCH", "word", "0" )
        if not self.ini.has_option( "SEARCH", "case" ):
            self.ini.set( "SEARCH", "case", "0" )
        if not self.ini.has_option( "SEARCH", "regex" ):
            self.ini.set( "SEARCH", "regex", "0" )

        if not self.ini.has_option( "GREP", "target" ):
            self.ini.set( "GREP", "target", "" )
        if not self.ini.has_option( "GREP", "recursive" ):
            self.ini.set( "GREP", "recursive", str(1) )

        if not self.ini.has_option( "COMPARE", "options" ):
            self.ini.set( "COMPARE", "options", "Strict" )

        if not self.ini.has_option( "ZENHAN", "options" ):
            self.ini.set( "ZENHAN", "options", "Ascii,Digit" )

        if not self.ini.has_option( "MISC", "locale" ):
            self.ini.set( "MISC", "locale", locale.getdefaultlocale()[0] )
        if not self.ini.has_option( "MISC", "isearch_type" ):
            self.ini.set( "MISC", "isearch_type", "strict" )
        if not self.ini.has_option( "MISC", "beep_type" ):
            self.ini.set( "MISC", "beep_type", "enabled" )
        if not self.ini.has_option( "MISC", "directory_separator" ):
            self.ini.set( "MISC", "directory_separator", "backslash" )
        if not self.ini.has_option( "MISC", "drive_case" ):
            self.ini.set( "MISC", "drive_case", "nocare" )
        if not self.ini.has_option( "MISC", "app_name" ):
            self.ini.set( "MISC", "app_name", "LREdit" )
        if not self.ini.has_option( "MISC", "walkaround_kb436093" ):
            self.ini.set( "MISC", "walkaround_kb436093", "0" )

        if not self.ini.has_option( "DEBUG", "detect_block" ):
            self.ini.set( "DEBUG", "detect_block", "0" )
        if not self.ini.has_option( "DEBUG", "print_errorinfo" ):
            self.ini.set( "DEBUG", "print_errorinfo", "0" )

        if self.ini.get( "MISC", "beep_type" )=="enabled":
            ckit.enableBeep(True)
        else:
            ckit.enableBeep(False)

        if self.ini.get( "MISC", "directory_separator" )=="slash":
            ckit.setPathSlash(True)
        else:
            ckit.setPathSlash(False)

        if self.ini.get( "MISC", "drive_case" )=="upper":
            ckit.setPathDriveUpper(True)
        elif self.ini.get( "MISC", "drive_case" )=="lower":
            ckit.setPathDriveUpper(False)
        else:
            ckit.setPathDriveUpper(None)

        ckit.setGlobalOption( GLOBAL_OPTION_WALKAROUND_KB436093, int(self.ini.get( "MISC", "walkaround_kb436093" )) )

        lredit_resource.lredit_appname = self.ini.get( "MISC", "app_name" )
        lredit_resource.setLocale( self.ini.get( "MISC", "locale" ) )

    def saveState(self):

        # 何らかの理由で ini ファイルを保存しない
        if self.ini_filename==None:
            return

        print( ckit.strings["saving"] )
        try:
            normal_rect = self.getNormalWindowRect()
            normal_size = self.getNormalSize()
            self.ini.set( "GEOMETRY", "x", str(normal_rect[0]) )
            self.ini.set( "GEOMETRY", "y", str(normal_rect[1]) )
            self.ini.set( "GEOMETRY", "width", str(normal_size[0]) )
            self.ini.set( "GEOMETRY", "height", str(normal_size[1]) )
            self.ini.set( "GEOMETRY", "log_pane_height", str(self.log_pane_height) )
            self.ini.set( "GEOMETRY", "left_edit_pane_width", str(self.left_edit_pane_width) )

            self.filename_history.save( self.ini, "FILENAME" )
            self.commandline_history.save( self.ini, "COMMANDLINE" )
            self.search_history.save( self.ini, "SEARCH" )
            self.replace_history.save( self.ini, "REPLACE" )
            self.grep_location_history.save( self.ini, "GREP", "location" )
            self.grep_filename_pattern_history.save( self.ini, "GREP", "filename_pattern" )
            self.grep_dirname_exclude_pattern_history.save( self.ini, "GREP", "dirname_exclude_pattern" )
            self.bookmarks.save( self.ini, "BOOKMARK" )

            tmp_ini_filename = self.ini_filename + ".tmp"

            fd = open( tmp_ini_filename, "w", encoding="utf-8" )

            msvcrt.locking( fd.fileno(), msvcrt.LK_LOCK, 1 )
            self.ini.write(fd)
            fd.close()

            try:
                os.unlink( self.ini_filename )
            except OSError:
                pass
            os.rename( tmp_ini_filename, self.ini_filename )

        except Exception as e:
            print( ckit.strings["common_failed"] )
            print( "  %s" % str(e) )
        else:
            print( ckit.strings["common_done"] )

    #--------------------------------------------------------------------------

    # コマンドラインの引数を処理する
    def processArgument( self, args ):

        arg_readonly = args["readonly"]
        arg_text = args["text"]
        arg_project = args["project"]
        arg_compare = args["compare"]
        arg_file = args["file"]

        text_list = []
        project = None

        for filename in arg_file:
            if fnmatch.fnmatch( filename, "*.lre" ):
                project = filename
            else:
                text_list.append( ( filename, 1, 1 ) )

        for item in arg_text:
            text_list.append(item)

        if arg_project:
            project = arg_project[0]

        # プロジェクトファイルを開く
        if project:
            info = ckit.CommandInfo()
            info.args = [ project ]
            self.command.OpenProject(info)

        # テキストファイルを開く
        for filename, line, index in text_list:

            self.activeOpen(filename=filename)

            edit = self.activeEditPane().edit

            # オープンに失敗しているなら続きを処理しない
            if edit==None or edit.doc.getFullpath() != ckit.normPath(filename):
                continue
            
            if arg_readonly:
                edit.doc.setReadOnly(True)

            point = edit.point(line-1,index-1)
            point = max( point, edit.pointDocumentBegin() )
            point = min( point, edit.pointDocumentEnd() )
            point = max( point, point.lineBegin() )
            point = min( point, point.lineEnd() )

            edit.setCursor(point)
            self.command.ScrollCursorCenter()

        # ファイルが渡されなかったか、渡されたファイルが開けなかった場合は、untitled を開く
        if not self.edit_list:
            doc = ckit.Document( filename=None, mode=self.createModeFromName("text") )
            self.activeOpen(doc=doc)

        # 起動引数で比較が要求されたら Compare を呼び出す
        if arg_compare:
            self.leftOpen( filename=arg_compare[0] )
            self.rightOpen( filename=arg_compare[1] )
            self.command.Compare()

    def startup( self, args ):
        print( lredit_resource.startupString() )
        self.processArgument(args)

    #--------------------------------------------------------
    # ここから下のメソッドはキーに割り当てることができる
    #--------------------------------------------------------

    ## 編集ペインにフォーカスする
    def command_FocusEdit( self, info ):
        if self.focus_top==MainWindow.FOCUS_EDIT:
            info.result = False
            return
        self.focus_top = MainWindow.FOCUS_EDIT
        self.updateCursor()
        self.paint()

    ## ログペインにフォーカスする
    def command_FocusLog( self, info ):
        if self.focus_top==MainWindow.FOCUS_LOG:
            info.result = False
            return
        self.focus_top = MainWindow.FOCUS_LOG
        self.updateCursor()
        self.paint()

    ## アクティブではないほうの編集ペインにフォーカスする
    def command_FocusInactiveEdit( self, info ):
        if self.focus_edit==MainWindow.FOCUS_EDIT_LEFT:
            self.command_FocusRightEdit(info)
        else:
            self.command_FocusLeftEdit(info)

    ## 左編集ペインにフォーカスする
    def command_FocusLeftEdit( self, info ):

        if self.focus_top==MainWindow.FOCUS_EDIT and self.focus_edit==MainWindow.FOCUS_EDIT_LEFT:
            info.result = False
            return

        self.focus_top = MainWindow.FOCUS_EDIT
        if self.left_edit_pane.edit:
            self.focus_edit = MainWindow.FOCUS_EDIT_LEFT
        else:
            info.result=False
        self.updateCursor()
        self.paint()

    ## 右編集ペインにフォーカスする
    def command_FocusRightEdit( self, info ):

        if self.focus_top==MainWindow.FOCUS_EDIT and self.focus_edit==MainWindow.FOCUS_EDIT_RIGHT:
            info.result = False
            return

        self.focus_top = MainWindow.FOCUS_EDIT
        if self.right_edit_pane.edit:
            self.focus_edit = MainWindow.FOCUS_EDIT_RIGHT
        else:
            info.result=False
        self.updateCursor()
        self.paint()

    ## 左右のペインを分離するセパレータを左方向に動かす
    def command_MoveSeparatorLeft( self, info ):

        if self.focus_top==MainWindow.FOCUS_EDIT:
            self.left_edit_pane_width = max( self.left_edit_pane_width-3, 0 )
            self.updatePaneRect()
            self.paint( REGION_EDIT )

        else:
            info.result = False
            return


    ## 左右のペインを分離するセパレータを右方向に動かす
    def command_MoveSeparatorRight( self, info ):

        if self.focus_top==MainWindow.FOCUS_EDIT:
            self.left_edit_pane_width = min( self.left_edit_pane_width+3, self.editPaneWidth()-self.editSeparatorWidth() )
            self.updatePaneRect()
            self.paint( REGION_EDIT )

        else:
            info.result = False
            return

    ## 上下のペインを分離するセパレータを上方向に動かす
    def command_MoveSeparatorUp( self, info ):

        self.log_pane_height += 3
        if self.log_pane_height>self.height()-2-self.tabBarHeight() : self.log_pane_height=self.height()-2-self.tabBarHeight()
        self.updatePaneRect()

        cursor = self.log_pane.edit.selection.cursor()
        self.log_pane.edit.makeVisible(cursor)

        self.paint()

    ## 上下のペインを分離するセパレータを下方向に動かす
    def command_MoveSeparatorDown( self, info ):

        self.log_pane_height -= 3
        if self.log_pane_height<0 : self.log_pane_height=0
        self.updatePaneRect()

        cursor = self.log_pane.edit.selection.cursor()
        self.log_pane.edit.makeVisible(cursor)

        self.paint()

    ## 左右のペインを分離するセパレータを左方向に高速に動かす
    #
    #  中央か端に達するまで、セパレータを左方向に動かします。
    #
    def command_MoveSeparatorLeftQuick( self, info ):
        center = (self.width()-self.editSeparatorWidth()) // 2
        if self.left_edit_pane_width > center :
            self.left_edit_pane_width = center
        else:
            self.left_edit_pane_width = 0
        self.updatePaneRect()
        self.paint( REGION_EDIT )

    ## 左右のペインを分離するセパレータを右方向に高速に動かす
    #
    #  中央か端に達するまで、セパレータを右方向に動かします。
    #
    def command_MoveSeparatorRightQuick( self, info ):
        center = (self.width()-self.editSeparatorWidth()) // 2
        if self.left_edit_pane_width < center :
            self.left_edit_pane_width = center
        else:
            self.left_edit_pane_width = self.width()
        self.updatePaneRect()
        self.paint( REGION_EDIT )

    ## 上下のペインを分離するセパレータを上方向に高速に動かす
    #
    #  縦3分割した位置に達するまで、セパレータを上方向に動かします。
    #
    def command_MoveSeparatorUpQuick( self, info ):

        pos_list = [
            (self.height()-2) * 1 // 3,
            (self.height()-2) * 2 // 3,
            (self.height()-2) * 3 // 3,
            ]

        for pos in pos_list:
            if pos > self.log_pane_height : break

        self.log_pane_height = pos
        self.updatePaneRect()

        cursor = self.log_pane.edit.selection.cursor()
        self.log_pane.edit.makeVisible(cursor)

        self.paint()

    ## 上下のペインを分離するセパレータを下方向に高速に動かす
    #
    #  縦3分割した位置に達するまで、セパレータを下方向に動かします。
    #
    def command_MoveSeparatorDownQuick( self, info ):

        pos_list = [
            (self.height()-2) * 3 // 3,
            (self.height()-2) * 2 // 3,
            (self.height()-2) * 1 // 3,
            0,
            ]

        for pos in pos_list:
            if pos < self.log_pane_height : break

        self.log_pane_height = pos
        self.updatePaneRect()

        cursor = self.log_pane.edit.selection.cursor()
        self.log_pane.edit.makeVisible(cursor)

        self.paint()

    ## 左右のペインを分離するセパレータを中央にリセットする
    def command_MoveSeparatorCenter( self, info ):
        self.left_edit_pane_width = (self.editPaneWidth()-self.editSeparatorWidth()) // 2
        self.updatePaneRect()
        self.paint()

    ## 左右のペインを分離するセパレータを、アクティブなペインが最大化するように、片方に寄せる
    def command_MoveSeparatorMaximizeH( self, info ):
        if self.focus_edit==MainWindow.FOCUS_EDIT_LEFT:
            self.left_edit_pane_width=self.width()-self.editSeparatorWidth()
        elif self.focus_edit==MainWindow.FOCUS_EDIT_RIGHT:
            self.left_edit_pane_width=0
        self.updatePaneRect()
        self.paint( REGION_EDIT )

    ## バックグラウンドタスクを全てキャンセルする
    def command_CancelTask( self, info ):
        for task_queue in self.task_queue_stack:
            task_queue.cancel()

    ## ログペインを1行上方向にスクロールする
    def command_LogUp( self, info ):
        self.log_pane.edit.scrollV(-1)

    ## ログペインを1行下方向にスクロールする
    def command_LogDown( self, info ):
        self.log_pane.edit.scrollV(+1)

    ## ログペインを1ページ上方向にスクロールする
    def command_LogPageUp( self, info ):
        self.log_pane.edit.scrollV(-self.logPaneHeight())

    ## ログペインを1ページ下方向にスクロールする
    def command_LogPageDown( self, info ):
        self.log_pane.edit.scrollV(+self.logPaneHeight())

    ## 終了する
    def command_Quit( self, info ):

        result = self.saveDocumentAll(confirm=True)
        if result==None:
            return

        try:
            self.quit( name="commandline" )
        except ValueError:
            pass
        self.quit( name="top" )

    ## 次のLREditに切り替える
    def command_ActivateNext( self, info ):

        desktop = pyauto.Window.getDesktop()
        wnd = desktop.getFirstChild()
        last_found = None
        while wnd:
            if wnd.getClassName()=="CkitWindowClass":
                last_found = wnd
            wnd = wnd.getNext()
        if last_found:
            wnd = last_found.getLastActivePopup()
            wnd.setForeground()

    ## ログペインの内容をクリップボードにコピーする
    def command_SetClipboard_Log( self, info ):
        lines = []
        for i in range(self.log_pane.log.numLines()):
            lines.append( self.log_pane.log.getLine(i) )
        lredit_misc.setClipboardText( '\r\n'.join(lines) )

    ## Pythonインタプリタのメモリの統計情報を出力する(デバッグ目的)
    def command_MemoryStat( self, info ):

        print( ckit.strings["memory_statistics"] + ' :' )

        gc.collect()
        objs = gc.get_objects()
        stat = {}

        for obj in objs:

            str_type = str(type(obj))
            if str_type.find("'instance'")>=0:
                str_type += " " + str(obj.__class__)

            try:
                stat[str_type] += 1
            except KeyError:
                stat[str_type] = 1

        keys = stat.keys()
        keys.sort()

        # 最長の名前を調べる
        max_len = 10
        for k in keys:
            k_len = self.getStringWidth(k)
            if max_len < k_len:
                max_len = k_len

        for k in keys:
            print( "  %s%s : %d" % ( k, ' '*(max_len-self.getStringWidth(k)), stat[k] ) )
        print( '' )

        print( ckit.strings["common_done"] + '\n' )


    ## ファイルがオープンされっぱなしになっているバグを調査するためのコマンド(デバッグ目的)
    #
    #  引数には、( クラス名, 探索の最大の深さ ) を渡します。
    #
    #  ex) RefererTree;ZipInfo;5
    #
    def command_RefererTree( self, info ):

        kwd = info.args[0]

        max_depth = 5
        if len(info.args)>1:
            max_depth = int(info.args[1])

        known_id_table = {}

        gc.collect()
        objs = gc.get_objects()

        def isRelatedObject(obj):
            if type(obj).__name__ == kwd:
                return True
            if type(obj).__name__ == 'instance':
                if obj.__class__.__name__ == kwd:
                    return True
            return False


        def dumpReferer(obj,depth):

            if known_id_table.has_key(id(obj)):
                return
            known_id_table[id(obj)] = True

            str_type = str(type(obj))

            if str_type.find("'instance'")>=0:
                str_type += " " + str(obj.__class__)
            print( "   " * depth, str_type )

            if depth==max_depth: return

            referers = gc.get_referrers(obj)
            for referer in tuple(referers):
                dumpReferer(referer,depth+1)


        print( "---- referer --------" )

        for obj in tuple(objs):
            if isRelatedObject(obj):
                dumpReferer(obj,0)

        print( "-----------------------------" )

    ## コマンドラインにコマンドを入力する
    def command_CommandLine( self, info ):

        def _getHint( update_info ):

            left = update_info.text[ : update_info.selection[0] ]
            left_lower = left.lower()
            pos_arg = left.rfind(";")+1
            arg = left[ pos_arg : ]
            pos_dir = max( arg.rfind("/")+1, arg.rfind("\\")+1 )

            return left_lower, pos_arg, pos_dir

        def onCandidate( update_info ):

            left_lower, pos_arg, pos_dir = _getHint(update_info)

            candidate_list = []
            candidate_set = set()

            for item in self.commandline_history.items:
                item_lower = item.lower()
                if item_lower.startswith(left_lower) and len(item_lower)!=len(left_lower):
                    right = item[ pos_arg + pos_dir: ]
                    candidate_list.append(right)
                    candidate_set.add(right)

            for commandline_function in self.commandline_list:
                for candidate in commandline_function.onCandidate( update_info ):
                    if candidate not in candidate_set:
                        candidate_list.append(candidate)
                        candidate_set.add(candidate)

            return candidate_list, pos_arg + pos_dir

        def onCandidateRemove(text):
            try:
                self.commandline_history.remove(text)
                return True
            except KeyError:
                pass
            return False

        def statusString( update_info ):
            if update_info.text:
                for commandline_function in self.commandline_list:
                    s = commandline_function.onStatusString(update_info.text)
                    if s!=None:
                        return s
            return "  "

        def onEnter( commandline, text, mod ):
            for commandline_function in self.commandline_list:
                if commandline_function.onEnter( commandline, text, mod ):
                    break
            return True

        self.commandLine( "Command", auto_complete=False, autofix_list=["\\/",".",";"], candidate_handler=onCandidate, candidate_remove_handler=onCandidateRemove, status_handler=statusString, enter_handler=onEnter )

        # カーソル位置の再設定
        self.activePane().widget().paint()

    ## 引数に渡された画像ファイルを壁紙にする
    def command_Wallpaper( self, info ):

        if len(info.args)>=1:
            filename = info.args[0]
        else:
            filename = self.inputFilename( "Wallpaper", None, ensure_exists=True )
            if not filename : return

        self.ini.set( "WALLPAPER", "visible", "1" )
        self.ini.set( "WALLPAPER", "filename", filename.encode("utf8") )
        self.updateWallpaper()

    ## 設定メニューをポップアップする
    def command_ConfigMenu( self, info ):
        lredit_configmenu.doConfigMenu( self )

    ## 設定スクリプトを編集する
    def command_EditConfig( self, info ):
        self.activeOpen( filename = self.config_filename )

    ## 設定スクリプトをリロードする
    def command_ReloadConfig( self, info ):
        self.configure()
        print( ckit.strings["config_reloaded"] + "\n" )

    ## ヘルプを表示する
    def command_Help( self, info ):
        print( ckit.strings["help_opening"] + " :" )
        help_path = os.path.join( ckit.getAppExePath(), 'doc\\index.html' )
        pyauto.shellExecute( None, help_path, "", "" )
        print( ckit.strings["common_done"] + '\n' )

    ## バージョン情報を出力する
    def command_About( self, info ):
        print( lredit_resource.startupString() )
        self.setStatusMessage( "%s version %s" % (lredit_resource.lredit_appname, lredit_resource.lredit_version), 3000 )

    ## 新規文書を開く
    def command_New( self, info ):
        doc = ckit.Document( filename=None, mode=self.createModeFromName("text") )
        self.activeOpen(doc=doc)

    ## ファイルを開く
    def command_Open( self, info ):

        if len(info.args)>=1:
            filename_list = info.args
        else:
            filename = self.activeEditPane().edit.doc.getFullpath()
            filename = self.inputFilename( "Open", filename, ensure_exists=True )
            if not filename : return
            filename_list = [ filename ]

        for filename in filename_list:
            self.activeOpen(filename=filename)

    ## エンコーディングを特定してファイルを開きなおす
    def command_ReopenEncoding( self, info ):

        encoding_list = [
            ( "utf-8",         ckit.TextEncoding("utf-8",b"\xEF\xBB\xBF") ),
            ( "utf-8n",        ckit.TextEncoding("utf-8") ),
            ( "shift-jis",     ckit.TextEncoding("cp932") ),
            ( "euc-jp",        ckit.TextEncoding("euc-jp") ),
            ( "iso-2022-jp",   ckit.TextEncoding("iso-2022-jp") ),
            ( "utf-16-le",     ckit.TextEncoding("utf-16-le",b"\xFF\xFE") ),
            ( "utf-16-be",     ckit.TextEncoding("utf-16-be",b"\xFE\xFF") ),
        ]

        pane = self.activeEditPane()
        edit = pane.edit
        doc = edit.doc
        filename = doc.getFullpath()
        if not filename:
            return

        if len(info.args)>=1:
            encoding_name = info.args[0]
        else:
            candidate_list = []
            for encoding in encoding_list:
                candidate_list.append(encoding[0])
            encoding_name = self.inputString( "Reopen Encoding", edit.doc.encoding.encoding, candidate_list )
            if not encoding_name : return

        for encoding in encoding_list:
            if encoding[0] == encoding_name:
                break
        else:
            print( ckit.strings["error_unknown_encoding"] % encoding_name )
            return

        if edit.doc.isModified():
            result = lredit_msgbox.popMessageBox(
                self,
                lredit_msgbox.MSGBOX_TYPE_YESNO,
                ckit.strings["msgbox_title_modified_reopen"],
                ckit.strings["msgbox_ask_modified_reopen"] % edit.doc.getName() )
            if result==lredit_msgbox.MSGBOX_RESULT_YES:
                pass
            else:
                return

        fd = open( filename, "rb" )
        doc.readFile( fd, encoding[1] )
        fd.close()

        self.paint()


    ## エンコーディングを変更する
    def command_Encoding( self, info ):

        encoding_list = [
            ( "utf-8",         ckit.TextEncoding("utf-8",b"\xEF\xBB\xBF") ),
            ( "utf-8n",        ckit.TextEncoding("utf-8") ),
            ( "shift-jis",     ckit.TextEncoding("cp932") ),
            ( "euc-jp",        ckit.TextEncoding("euc-jp") ),
            ( "iso-2022-jp",   ckit.TextEncoding("iso-2022-jp") ),
            ( "utf-16-le",     ckit.TextEncoding("utf-16-le",b"\xFF\xFE") ),
            ( "utf-16-be",     ckit.TextEncoding("utf-16-be",b"\xFE\xFF") ),
        ]

        if len(info.args)>=1:
            encoding_name = info.args[0]
        else:

            encoding = self.activeEditPane().edit.doc.encoding

            if encoding.encoding=="utf-8" and encoding.bom==None:
                encoding_name = "utf-8n"
            else:
                encoding_name = encoding.encoding

            candidate_list = []
            for e in encoding_list:
                candidate_list.append(e[0])
            encoding_name = self.inputString( "Encoding", encoding_name, candidate_list )
            if not encoding_name : return

        for encoding in encoding_list:
            if encoding[0] == encoding_name:
                self.activeEditPane().edit.setEncoding( encoding[1] )
                break
        else:
            print( ckit.strings["error_unknown_encoding"] % encoding_name )
            return

        self.paint()


    ## 改行コードを変更する
    def command_LineEnd( self, info ):

        lineend_list = [
            ( "crlf", "\r\n" ),
            ( "lf",   "\n" ),
            ( "cr",   "\r" ),
        ]

        if len(info.args)>=1:
            lineend_name = info.args[0]
        else:

            lineend = self.activeEditPane().edit.doc.lineend

            lineend_name = ""
            for item in lineend_list:
                if item[1]==lineend:
                    lineend_name = item[0]
                    break

            candidate_list = []
            for item in lineend_list:
                candidate_list.append(item[0])
            lineend_name = self.inputString( "LineEnd", lineend_name, candidate_list )
            if not lineend_name : return

        for item in lineend_list:
            if item[0] == lineend_name:
                self.activeEditPane().edit.setLineEnd( item[1] )
                break
        else:
            print( ckit.strings["error_unknown_lineend"] % lineend_name )
            return

        self.paint()


    ## アクティブな文書をもうひとつのEditで開く
    def command_Duplicate( self, info ):
        edit = self.activeEditPane().edit
        self.inactiveOpen( doc=edit.doc, duplicate=True )
        self.command.MoveSeparatorCenter()

    ## ファイルを保存する
    def command_Save( self, info ):
        edit = self.activeEditPane().edit
        self.saveDocument(edit.doc)
        self.storeBookmarkList(edit)

    ## ファイルを名前を付けて保存する
    def command_SaveAs( self, info ):

        edit = self.activeEditPane().edit

        if len(info.args)>=1:
            self.saveDocument( edit.doc, filename=info.args[0] )
        else:
            self.saveDocument( edit.doc, input_name=True )

        self.storeBookmarkList(edit)

    ## すべてのファイルを保存する
    def command_SaveAll( self, info ):
        self.saveDocumentAll()

    ## ファイルを閉じる
    def command_Close( self, info ):
        self._close( self.activeEditPane().edit )


    def _documentNextModkey( self, mod, mod_old ):
        pane = self.activeEditPane()
        self.activeOpen( edit=pane.edit, sort=True )
        self.mod_hooks.remove(self._documentNextModkey)
        self.document_next_pivot = None

    ## 次のドキュメントに切り替える
    def command_DocumentNext( self, info ):

        pane = self.activeEditPane()
        another_pane = self.inactiveEditPane()

        edit = None

        if self.document_next_pivot==None:
            # 一発目は反対のPaneに
            self.document_next_pivot = pane.edit
            if another_pane.edit:
                edit = another_pane.edit
        elif self.document_next_pivot in another_pane.edit_list:
            # 反対のPaneからPivotのPaneに戻る
            i = another_pane.edit_list.index(self.document_next_pivot) + 1
            if i>=len(another_pane.edit_list) : i=0
            edit = another_pane.edit_list[i]

        if not edit:
            if len(pane.edit_list)==1 and another_pane.edit:
                # タブが１つしかないときはPaneの切り替え
                edit = another_pane.edit
            else:
                # 次のタブへ
                i = pane.edit_list.index(pane.edit) + 1
                if i>=len(pane.edit_list) : i=0
                edit = pane.edit_list[i]

        self.activeOpen( edit=edit, sort=False )

        # モディファイアキーが離されたときにソートを確定する
        if self.mod:
            try:
                self.mod_hooks.remove(self._documentNextModkey)
            except ValueError:
                pass
            self.mod_hooks.append(self._documentNextModkey)
        else:
            self._documentNextModkey()


    ## 文書の名前を入力し切り替える
    def command_Document( self, info ):

        if len(info.args)>=1:
            docname = info.args[0]
        else:
            docname = self.inputDocument( "Document", "" )
            if docname==None : return

        for edit in self.edit_list:
            if edit.doc.getName().lower()==docname.lower():
                self.activeOpen( edit=edit )
                return
        else:
            self.setStatusMessage( ckit.strings["statusbar_switch_doc_failed"] % docname, 3000, error=True )


    ## 文書を一覧表示し切り替える
    def command_DocumentList( self, info ):
        edit = self.listDocument( "Documents" )
        if edit:
            self.activeOpen( edit=edit )


    ## ブックマークを一覧表示し切り替える
    def command_BookmarkList( self, info ):

        if not self.bookmarks.table:
            self.setStatusMessage( ckit.strings["bookmark_not_found"], 3000, error=True )
            return

        for edit in self.edit_list:
            self.storeBookmarkList(edit)

        edit = self.activeEditPane().edit
        active_edit_filename = edit.doc.getFullpath()
        active_edit_lineno = edit.selection.cursor().line

        loop = [False]
        fullpath_mode = [False]
        local_mode = [True]
        select = [None]

        def onKeyDown( vk, mod ):

            if vk==VK_SPACE and mod==0:
                fullpath_mode[0] = not fullpath_mode[0]
                select[0] = list_window.getResult()
                loop[0] = True
                list_window.quit()
                return True

            elif vk==VK_LEFT and mod==0:
                if not local_mode[0]:
                    local_mode[0] = True
                    select[0] = 0
                    loop[0] = True
                    list_window.quit()
                return True

            elif vk==VK_RIGHT and mod==0:
                if local_mode[0]:
                    local_mode[0] = False
                    select[0] = 0
                    loop[0] = True
                    list_window.quit()
                return True

            elif vk==VK_DELETE and mod==0:
                select[0] = list_window.getResult()
                s = items[select[0]][0]
                filename, bookmark = items[select[0]][1]
                bookmark = list(bookmark)
                bookmark[1] = 0
                self.bookmarks.setBookmark( filename, bookmark )
                list_window.remove(select[0])
                return True

        def onStatusMessage( width, select ):
            return ""

        while True:

            loop[0] = False

            if local_mode[0] and self.project:
                project_filenames = set( self.project.enumFullpath() )

            items = []
            for filename, bookmark_list in self.bookmarks.table:
                filename = ckit.normPath(filename)

                if local_mode[0]:
                    found = False
                    for edit in self.edit_list:
                        if filename==edit.doc.getFullpath():
                            found = True
                            break
                    if not found and self.project:
                        if filename in project_filenames:
                            found = True
                    if not found:
                        continue

                for bookmark in bookmark_list:

                    if fullpath_mode[0]:
                        s = "%s:%d: %s" % ( filename, bookmark[0]+1, bookmark[2] )
                    else:
                        s = "%s:%d: %s" % ( os.path.basename(filename), bookmark[0]+1, bookmark[2] )
                    items.append( ( s, (filename,bookmark) ) )

                    if select[0]==None and active_edit_filename==filename and active_edit_lineno==bookmark[0]:
                        select[0] = len(items)-1

            if select[0]==None:
                select[0] = 0

            if local_mode[0]:
                title = "Bookmarks (Local)"
            else:
                title = "Bookmarks (Global)"

            pos = self.centerOfWindowInPixel()
            list_window = lredit_listwindow.ListWindow( pos[0], pos[1], 20, 2, self.width()-5, self.height()-3, self, self.ini, True, title, items, initial_select=select[0], onekey_search=False, keydown_hook=onKeyDown, statusbar_handler=onStatusMessage )
            self.enable(False)
            list_window.messageLoop()

            # チラつき防止の遅延削除
            class DelayedCall:
                def __call__(self):
                    self.list_window.destroy()
            delay = DelayedCall()
            delay.list_window = list_window
            self.delayedCall( delay, 10 )

            if not loop[0]:
                break

        result = list_window.getResult()
        self.enable(True)
        self.activate()

        for edit in self.edit_list:
            self.loadBookmarkList(edit)

        self.paint( REGION_EDIT )

        if result<0 : return
        if not items : return

        filename, bookmark = items[result][1]

        self.activeOpen( filename=filename, lineno=bookmark[0] )


    ## 文字列を下に向けて検索する
    def command_Search( self, info ):

        edit = self.activePane().edit
        original_cursor = edit.selection.cursor()
        search_cursor = [ edit.selection.cursor() ]
        text = [""]
        search_object = [None]
        regex_error = [False]

        if len(info.args)>=1:
            text[0] = info.args[0]

        def onKeyDown( vk, mod ):

            if vk==VK_DOWN and mod==MODKEY_CTRL:
                if regex_error[0]:
                    self.setStatusMessage( ckit.strings["statusbar_regex_wrong"] % text[0], 3000, error=True )
                    return True
                edit.search( search_object=search_object[0], direction=1 )
                search_cursor[0] = edit.selection.cursor()
                return True

            elif vk==VK_UP and mod==MODKEY_CTRL:
                if regex_error[0]:
                    self.setStatusMessage( ckit.strings["statusbar_regex_wrong"] % text[0], 3000, error=True )
                    return True
                edit.search( search_object=search_object[0], direction=-1 )
                search_cursor[0] = edit.selection.cursor()
                return True

        def onUpdate( new_text, word, case, regex ):

            if len(text[0])>0 and len(new_text)==0:
                search_cursor[0] = edit.selection.cursor()
            elif len(text[0])==0 and len(new_text)>0:
                search_cursor[0] = original_cursor.copy()

            text[0] = new_text

            try:
                search_object[0] = ckit.Search( text[0], word, case, regex )
                regex_error[0] = False
            except re.error:
                regex_error[0] = True
                return True

            edit.search( search_object=search_object[0], point=search_cursor[0], direction=1, paint=False, message=False )
            edit.paint()

            return True

        s = self.inputSearch( "Search", keydown_handler=onKeyDown, update_handler=onUpdate )
        if s==None : return

        word = self.ini.getint( "SEARCH", "word" )
        case = self.ini.getint( "SEARCH", "case" )
        regex = self.ini.getint( "SEARCH", "regex" )

        try:
            search_object[0] = ckit.Search( s, word, case, regex )
        except re.error:
            self.setStatusMessage( ckit.strings["statusbar_regex_wrong"] % s, 3000, error=True )
            return

        edit.search( search_object=search_object[0], point=search_cursor[0], direction=1 )

        self.search_object = search_object[0]


    ## 前回検索した条件で次を検索する
    def command_SearchNext( self, info ):
        if self.search_object:
            self.activePane().edit.search( search_object=self.search_object, direction=1 )

    ## 前回検索した条件で前を検索する
    def command_SearchPrev( self, info ):
        if self.search_object:
            self.activePane().edit.search( search_object=self.search_object, direction=-1 )

    ## 文字列を検索し置換する
    def command_Replace( self, info ):

        before = self.inputSearch( "Replace(Before)" )
        if before==None : return

        word = self.ini.getint( "SEARCH", "word" )
        case = self.ini.getint( "SEARCH", "case" )
        regex = self.ini.getint( "SEARCH", "regex" )

        try:
            search_object = ckit.Search( before, word, case, regex )
        except re.error:
            self.setStatusMessage( ckit.strings["statusbar_regex_wrong"] % before, 3000, error=True )
            return

        edit = self.activePane().edit

        edit.search( search_object=search_object, direction=1 )

        def replace( after, paint=True, message=True ):

            left = edit.selection.left()
            right = edit.selection.right()

            # 選択位置が検索条件にヒットする場合だけ置換する
            selected_text = edit.getText(left,right)
            search_result = search_object.search(selected_text)
            if search_result==None or search_result[0]!=0 or search_result[1]!=len(selected_text):
                return False

            # 置換する
            if regex:
                after2 = ""
                pos = 0
                while pos<len(after):
                    if after[pos]=='\\':
                        pos += 1
                        if pos<len(after):
                            second_char = after[pos]
                            if second_char=='\\':
                                after2 += second_char
                            elif second_char=='t':
                                after2 += '\t'
                            elif second_char=='n':
                                after2 += '\n'
                            elif '0'<=second_char<='9':
                                after2 += edit.search_re_result.group(int(second_char))
                        else:
                            after2 += '\\'
                    else:
                        after2 += after[pos]
                    pos += 1
                edit.modifyText( left, right, after2, paint=paint )
            else:
                edit.modifyText( left, right, after, paint=paint )

            edit.search( search_object=search_object, direction=1, paint=paint, message=message )

            return True

        def statusString( update_info ):
            return ""

        def onKeyDown( vk, mod ):

            if vk==VK_DOWN and mod==MODKEY_CTRL:
                edit.search( search_object=search_object, direction=1 )
                return True
            elif vk==VK_UP and mod==MODKEY_CTRL:
                edit.search( search_object=search_object, direction=-1 )
                return True

        def onEnter( commandline, text, mod ):

            after = text
            self.replace_history.append(after)

            if mod==0:
                replace(after)
                return True

            elif mod==MODKEY_SHIFT:

                edit.atomicUndoBegin( True, edit.pointDocumentBegin(), edit.pointDocumentEnd() )
                try:
                    count = 0
                    while True:
                        if replace( after, paint=False, message=False ):
                            count += 1
                            continue
                        break

                finally:
                    edit.atomicUndoEnd( edit.pointDocumentBegin(), edit.pointDocumentEnd() )

                self.paint(REGION_EDIT)
                self.setStatusMessage( ckit.strings["statusbar_replace_finished"] % count, 3000 )
                return False

            return True

        self.commandLine( "Replace(After)", text="", auto_complete=False, autofix_list=[], candidate_handler=self.replace_history.candidateHandler, candidate_remove_handler=self.replace_history.candidateRemoveHandler, status_handler=statusString, enter_handler=onEnter, keydown_handler=onKeyDown )


    ## 選択範囲の行末の空白文字を削除する
    def command_RemoveTrailingSpace( self, info ):

        edit = self.activePane().edit

        def func(line):
            return line.rstrip(" \t")

        edit.replaceLines(func)

    ## 選択範囲のTABを空白文字に展開する
    def command_ExpandTab( self, info ):

        edit = self.activePane().edit
        tab_width = edit.doc.mode.tab_width

        def func(line):
            return ckit.expandTab( self, line, tab_width )

        edit.replaceLines(func)

    ## 選択範囲の空行を削除する
    def command_RemoveEmptyLines( self, info ):

        edit = self.activePane().edit

        def func( text, info ):
            return len(text)>0

        edit.filterLines(func)

    ## ブックマークされた行を削除する
    def command_RemoveMarkedLines( self, info ):

        edit = self.activePane().edit

        def func( text, info ):
            return info.bookmark==0

        edit.filterLines(func)

    ## ブックマークされてない行を削除する
    def command_RemoveUnmarkedLines( self, info ):

        edit = self.activePane().edit

        def func( text, info ):
            return info.bookmark!=0

        edit.filterLines(func)

    ## 選択範囲を大文字に変換する
    def command_ToUpper( self, info ):
        edit = self.activePane().edit
        left = edit.selection.left()
        right = edit.selection.right()
        text = edit.getText( left, right )
        text = text.upper()
        edit.modifyText( text=text )

    ## 選択範囲を小文字に変換する
    def command_ToLower( self, info ):
        edit = self.activePane().edit
        left = edit.selection.left()
        right = edit.selection.right()
        text = edit.getText( left, right )
        text = text.lower()
        edit.modifyText( text=text )

    def _zenhanCommon( self, info, func ):

        option_list = [
            "Ascii",
            "Digit",
            "Kana",
            "Space",
            "All",
        ]

        if len(info.args)>=1:
            options = info.args[0]
        else:
            options = self.ini.get( "ZENHAN", "options" )
            options = self.inputOptions( "Charactor Types", options, option_list )
            if options==None : return
            self.ini.set( "ZENHAN", "options", options )

        edit = self.activePane().edit
        left = edit.selection.left()
        right = edit.selection.right()
        text = edit.getText( left, right )

        z2h_option = 0
        for option in options.split(","):
            option = option.strip()
            if option.lower() == "All".lower():
                z2h_option |= lredit_zenhan.ALL
            elif option.lower() == "Ascii".lower():
                z2h_option |= lredit_zenhan.ASCII
            elif option.lower() == "Digit".lower():
                z2h_option |= lredit_zenhan.DIGIT
            elif option.lower() == "Kana".lower():
                z2h_option |= lredit_zenhan.KANA
            elif option.lower() == "Space".lower():
                z2h_option |= lredit_zenhan.SPACE

        text = func( text, z2h_option )

        edit.modifyText( text=text )

    ## 選択範囲を半角に変換する
    def command_ToHankaku( self, info ):
        self._zenhanCommon( info, lredit_zenhan.z2h )

    ## 選択範囲を全角に変換する
    def command_ToZenkaku( self, info ):
        self._zenhanCommon( info, lredit_zenhan.h2z )

    ## 左右の文書を比較する
    def command_Compare( self, info ):

        active_edit = self.activeEditPane().edit

        # 保存されていない文書は比較できない
        if not active_edit.doc.getFullpath():
            self.setStatusMessage( ckit.strings["statusbar_not_saved"], 3000, error=True )
            return

        # 1画面モードの場合は比較対象の文書をリスト選択する
        if self.inactiveEditPane().edit==None:
            def func(edit):
                return ( edit!=active_edit and edit.doc.getFullpath() )
            edit = self.listDocument( "Compare With", filter_func=func )
            if not edit: return
            self.inactiveOpen(edit=edit)
            self.command.MoveSeparatorCenter()

        for edit in self.edit_list:
            edit.clearDiffColor()

        jump_list = []
        self.jump_list = jump_list
        self.jump_selection = None

        left_lines = []
        right_lines = []
        
        ignore_case = False
        ignore_whitespace = False

        options = self.ini.get( "COMPARE", "options" )
        for option in options.split(","):
            option = option.strip()
            if option.lower() == "Strict".lower():
                ignore_case = False
                ignore_whitespace = False
            elif option.lower() == "Ignore.Case".lower():
                ignore_case = True
            elif option.lower() == "Ignore.WhiteSpace".lower():
                ignore_whitespace = True

        if ignore_whitespace:
            for line in self.left_edit_pane.edit.doc.lines:
                s = re.sub( "[ \t]+", "", line.s )
                left_lines.append(s)

            for line in self.right_edit_pane.edit.doc.lines:
                s = re.sub( "[ \t]+", "", line.s )
                right_lines.append(s)
        else:
            for line in self.left_edit_pane.edit.doc.lines:
                left_lines.append(line.s)

            for line in self.right_edit_pane.edit.doc.lines:
                right_lines.append(line.s)

        if ignore_case:
            left_lines = map( lambda s : s.lower(), left_lines )
            right_lines = map( lambda s : s.lower(), right_lines )


        diff_object = difflib.unified_diff( left_lines, right_lines, self.left_edit_pane.edit.doc.getName(), self.right_edit_pane.edit.doc.getName(), n=0 )

        color = 1

        self.left_edit_pane.edit.setDiffColorMode()
        self.right_edit_pane.edit.setDiffColorMode()

        # 差分に背景色をつける
        re_pattern = re.compile( "@@ -([0-9]+)(,([0-9]+))? \+([0-9]+)(,([0-9]+))? @@" )
        for line in diff_object:
            if line.startswith("@@"):

                re_result = re_pattern.match(line)
                begin1 = int(re_result.group(1))-1
                if not re_result.group(3):
                    end1 = begin1 + 1
                elif re_result.group(3)=='0':
                    begin1 += 1
                    end1 = begin1
                else:
                    end1 = begin1 + int(re_result.group(3))

                for i in range( begin1, end1 ):
                    self.left_edit_pane.edit.doc.lines[i].bg = color

                begin2 = int(re_result.group(4))-1
                if not re_result.group(6):
                    end2 = begin2 + 1
                elif re_result.group(6)=='0':
                    begin2 += 1
                    end2 = begin2
                else:
                    end2 = begin2 + int(re_result.group(6))

                for i in range( begin2, end2 ):
                    self.right_edit_pane.edit.doc.lines[i].bg = color

                color +=  1
                if color>=4:
                    color=1

                left_fullpath = self.left_edit_pane.edit.doc.getFullpath()
                right_fullpath = self.right_edit_pane.edit.doc.getFullpath()

                left_lineno = ckit.adjustStringWidth( self, "%s" % (begin1+1), self.left_edit_pane.edit.lineNoWidth()-2 )
                right_lineno = ckit.adjustStringWidth( self, "%s" % (begin2+1), self.left_edit_pane.edit.lineNoWidth()-2 )

                text = "%s:%s - %s:%s" % ( os.path.basename(left_fullpath), left_lineno, os.path.basename(right_fullpath), right_lineno )

                jump_list.append(
                    CompareJumpItem(
                        self,
                        left_fullpath,
                        begin1,
                        right_fullpath,
                        begin2,
                        text
                    )
                )

        self.command.SearchResultNext()
        self.paint()


    ## ファイル比較時のアルファベット大小の扱いを設定する
    def command_CompareOptions( self, info ):

        option_list = [
            "Strict",
            "Ignore.Case",
            "Ignore.WhiteSpace",
        ]

        if len(info.args)>=1:
            options = info.args[0]
        else:
            options = self.ini.get( "COMPARE", "options" )
            options = self.inputOptions( "Compare Options", options, option_list )
            if options==None : return
            self.ini.set( "COMPARE", "options", options )

        active_edit = self.activeEditPane().edit
        inactive_edit = self.inactiveEditPane().edit

        if active_edit and inactive_edit and active_edit.isDiffColorMode() and inactive_edit.isDiffColorMode():
            self.command.Compare()


    ## 複数のファイルから文字列を検索する
    def command_Grep( self, info ):

        target_list = [
            "Directory",
            "Directory.Recursive",
            "Project",
        ]

        def candidate_GrepTarget( update_info ):

            candidates = []

            for target in target_list:
                if target.lower().startswith( update_info.text.lower() ):
                    candidates.append( target )

            return candidates, 0

        mod = 0

        # デフォルトのファイル名パターン
        filename_pattern = ""
        if self.grep_filename_pattern_history.items : filename_pattern = self.grep_filename_pattern_history.items[0]

        # デフォルトのディレクトリ
        location = self.activeEditPane().edit.doc.getFullpath()
        if self.grep_location_history.items : location = self.grep_location_history.items[0]

        # デフォルトの検索対象 (プロジェクト、ディレクトリ)
        target = self.ini.get( "GREP", "target" )
        if not target : target = "Directory.Recursive"

        # デフォルトの無視するディレクトリ名パターン
        dirname_exclude_pattern = ""
        if self.grep_dirname_exclude_pattern_history.items : dirname_exclude_pattern = self.grep_dirname_exclude_pattern_history.items[0]

        # 検索文字列の入力
        s, mod = self.inputSearch( "Grep Keyword", return_modkey=True )
        if s==None : return

        # ファイル名パターンの入力
        if mod != MODKEY_CTRL:
            filename_pattern, mod = self.commandLine( "Grep Filename", text=filename_pattern, auto_complete=False, autofix_list=[";"," ","."], return_modkey=True, candidate_handler=self.grep_filename_pattern_history.candidateHandler, candidate_remove_handler=self.grep_filename_pattern_history.candidateRemoveHandler )
            if not filename_pattern : return
            self.grep_filename_pattern_history.append(filename_pattern)

        # 検索対象の入力
        if mod != MODKEY_CTRL:
            target, mod = self.commandLine( "Grep Target", text=target, auto_complete=True, autofix_list=["."], return_modkey=True, candidate_handler=candidate_GrepTarget )
            if not target : return
            if target not in target_list:
                print( ckit.strings["error_unknown_parameter"] % target )
                return
            self.ini.set( "GREP", "target", target )

        # ターゲットが "Project" で、プロジェクトがオープンされていなかったらエラー
        if target.startswith("Project") and not self.project:
            self.setStatusMessage( ckit.strings["project_not_opened"], 3000, error=True, log=True )
            return

        # ディレクトリ名の入力
        if target.startswith("Directory") and mod != MODKEY_CTRL:

            default_location = location

            # 編集中のファイルパス
            location = self.activeEditPane().edit.doc.getFullpath()
            if location:
                location = os.path.dirname(location)
                location = ckit.joinPath(location,"")

                # 前回使用したディレクトリが編集中のファイルパスを含んでいたら前回のディレクトリを使う
                if location.startswith(default_location):
                    location = default_location

            location, tmp, mod = self.inputDirname( "Grep Location", location, None, self.grep_location_history, return_modkey=True )
            if location==None : return

        # 無視するディレクトリ名パターンの入力
        if target.startswith("Directory") and mod != MODKEY_CTRL:
            dirname_exclude_pattern, mod = self.commandLine( "Grep Dirname Exclude", text=dirname_exclude_pattern, auto_complete=False, autofix_list=[";"," ","."], return_modkey=True, candidate_handler=self.grep_dirname_exclude_pattern_history.candidateHandler, candidate_remove_handler=self.grep_dirname_exclude_pattern_history.candidateRemoveHandler )
            if dirname_exclude_pattern==None : return
            self.grep_dirname_exclude_pattern_history.append(dirname_exclude_pattern)

        # ターゲットが "Project" のときは、ログ出力の相対パスはプロジェクトファイルの場所から表示
        if target.startswith("Project"):
            location = self.project.dirname

        # 保存確認
        result = self.saveDocumentAll(confirm=True)
        if result==None:
            return

        word = self.ini.getint( "SEARCH", "word" )
        case = self.ini.getint( "SEARCH", "case" )
        regex = self.ini.getint( "SEARCH", "regex" )

        try:
            search_object = ckit.Search( s, word, case, regex )
        except re.error:
            self.setStatusMessage( ckit.strings["statusbar_regex_wrong"] % s, 3000, error=True )
            return

        def enumFiles():

            target_split = target.split(".")
            file_filter_list = filename_pattern.split(" ")

            def checkFilter(filename):
                result = False
                for pattern in file_filter_list:
                    if pattern.startswith("!"):
                        pattern = pattern[1:]
                        if fnmatch.fnmatch( filename, pattern ):
                            return False
                    else:
                        if fnmatch.fnmatch( filename, pattern ):
                            result = True
                return result

            if target_split[0]=="Directory":

                if len(target_split)<=1:
                    recursive = False
                elif target_split[1]=="Recursive":
                    recursive = True

                print( 'Grep : %s : %s : %s' % ( target, location, s ) )

                dir_ignore_list = dirname_exclude_pattern.split(" ")

                for root, dirs, files in os.walk( location ):

                    if not recursive : del dirs[:]

                    # 無視するディレクトリを除外
                    for item in dirs:
                        for pattern in dir_ignore_list:
                            if fnmatch.fnmatch( item, pattern ):
                                dirs.remove(item)
                                break

                    for filename in files:
                        if checkFilter(filename):
                            fullpath = os.path.join( root, filename )
                            yield fullpath

            elif target_split[0]=="Project":

                print( 'Grep : %s : %s' % (target,s) )

                for filename in self.project.enumFullpath():
                    if checkFilter(filename):
                        yield filename

        for edit in self.edit_list:
            edit.clearDiffColor()

        jump_list = []
        self.jump_list = jump_list
        self.jump_selection = None

        def jobGrep( job_item ):

            def onFound( filename, lineno, line ):

                path_from_here = ckit.normPath(filename[len(os.path.join(location,"")):])
                text = "%s:%d: %s" % ( path_from_here, lineno, line.strip() )
                print( text )

                jump_list.append(
                    GrepJumpItem(
                        self,
                        filename,
                        lineno,
                        search_object,
                        text
                    )
                )

            self.setProgressValue(None)
            try:
                lredit_grep.grep( job_item, enumFiles, s, word, case, regex, found_handler=onFound )
            finally:
                self.clearProgress()

        def jobGrepFinished( job_item ):

            if job_item.isCanceled():
                self.setStatusMessage( ckit.strings["statusbar_aborted"], 3000 )
            else:
                self.setStatusMessage( ckit.strings["statusbar_grep_finished"] % len(jump_list) )

            if self.jump_selection==None:
                self.command.SearchResultNext()
                self.paint()

        job_item = ckit.JobItem( jobGrep, jobGrepFinished )
        self.taskEnqueue( job_item, "Grep" )


    ## 行番号やTAGSでジャンプする
    def command_Jump( self, info ):

        edit = self.activeEditPane().edit
        active_edit_lineno = edit.selection.cursor().line

        # プロジェクトファイルの隣のTAGSファイルをロードする
        if self.project:
            tags_filename = ckit.joinPath(os.path.dirname(self.project.filename),"tags")
            try:
                self.loadTags(tags_filename)
            except IOError:
                pass

        symbol_list = set()
        for tags in self.tags_list:
            symbol_list = symbol_list.union( list( tags.symbols() ) )
        symbol_list = list(symbol_list)
        symbol_list.sort()

        if len(info.args)>=1:
            destination = info.args[0]
        else:
            destination = str(active_edit_lineno+1)
            destination = self.inputString( "Jump", destination, symbol_list )
            if not destination : return

        if re.match( "[0-9]+", destination ):
            info = ckit.CommandInfo()
            info.args = [ destination ]
            self.command.JumpLineNo(info)
        else:
            info = ckit.CommandInfo()
            info.args = [ destination ]
            self.command.TagsJump(info)


    ## 指定された行番号にジャンプする
    def command_JumpLineNo( self, info ):

        edit = self.activeEditPane().edit
        active_edit_lineno = edit.selection.cursor().line

        if len(info.args)>=1:
            try:
                lineno = int(info.args[0]) - 1
            except ValueError:
                self.setStatusMessage( ckit.strings["statusbar_jump_failed"], 3000, error=True )
                return
        else:
            lineno = self.inputNumber( "JumpLineNo", str(active_edit_lineno+1) )
            if lineno==None : return
            lineno = int(lineno) - 1

        edit.jumpLineNo(lineno)


    def _searchResultCommon(self,direction):

        if not self.jump_list:
            return

        if self.jump_selection==None:
            if direction>0:
                self.jump_selection = 0
            else:
                self.jump_selection = len(self.jump_list)-1
        else:
            if 0 <= self.jump_selection + direction < len(self.jump_list):
                self.jump_selection += direction
            else:
                self.setStatusMessage( ckit.strings["statusbar_jump_failed"], 3000, error=True )
                return

        if self.jump_selection>=len(self.jump_list):
            return

        jump = self.jump_list[self.jump_selection]
        jump()


    ## 次の位置にジャンプする
    def command_SearchResultNext( self, info ):
        self._searchResultCommon(1)


    ## 前の位置にジャンプする
    def command_SearchResultPrev( self, info ):
        self._searchResultCommon(-1)


    ## 検索結果をリスト表示
    def command_SearchResultList( self, info ):

        if not self.jump_list:
            return

        select = self.jump_selection

        def onStatusMessage( width, select ):
            return ""

        items = []
        for jump in self.jump_list:
            items.append( ( jump.text, jump ) )

        pos = self.centerOfWindowInPixel()
        list_window = lredit_listwindow.ListWindow( pos[0], pos[1], 20, 2, self.width()-5, self.height()-3, self, self.ini, True, "Jump", items, initial_select=select, onekey_search=False, statusbar_handler=onStatusMessage )
        self.enable(False)
        list_window.messageLoop()
        result = list_window.getResult()
        self.enable(True)
        self.activate()
        list_window.destroy()

        if result<0 : return
        if not items : return

        self.jump_selection = result
        jump = self.jump_list[self.jump_selection]
        jump()


    ## アクティブな文書をもうひとつのPaneに移動させる
    def command_AnotherPane( self, info ):

        if len(self.edit_list)<=1:
            self.command.New()

        edit = self.activeEditPane().edit
        self.inactiveOpen( edit=edit )
        self.command.FocusInactiveEdit()


    ## プロジェクトファイルを開く
    def command_OpenProject( self, info ):

        if len(info.args)>=1:
            filename = info.args[0]
        else:
            filename = self.activeEditPane().edit.doc.getFullpath()
            if filename:
                filename = os.path.dirname(filename)
                filename = ckit.joinPath(filename,"")
            filename = self.inputFilename( "Project", filename, ensure_exists=True )
            if not filename : return

        try:
            self.project = lredit_project.Project(filename)
        except IOError:
            print( ckit.strings["error_open_failed"] % filename )
            self.setStatusMessage( ckit.strings["statusbar_open_failed"] % filename, 3000, error=True )
            self.filename_history.remove(filename)
            return

        self.updateTitleBar()
        self.setStatusMessage( ckit.strings["statusbar_project_opened"] % filename, 3000 )

        # ファイル名を履歴に残す
        filename = os.path.abspath(filename)
        filename = os.path.normpath(filename)
        if not filename.lower().startswith(ckit.getTempPath().lower()):
            self.filename_history.append( ckit.normPath(filename) )


    ## プロジェクトファイルを閉じる
    def command_CloseProject( self, info ):

        if not self.project:
            self.setStatusMessage( ckit.strings["project_not_opened"], 3000, error=True )
            return

        self.project = None

        self.updateTitleBar()

        self.setStatusMessage( ckit.strings["statusbar_project_closed"], 3000 )


    ## プロジェクトファイルを編集する
    def command_EditProject( self, info ):

        if not self.project:
            self.setStatusMessage( ckit.strings["project_not_opened"], 3000, error=True )
            return

        self.activeOpen( filename = self.project.filename )


    ## プロジェクト中のファイルを一覧表示する
    def command_ProjectFileList( self, info ):

        if not self.project:
            self.setStatusMessage( ckit.strings["project_not_opened"], 3000, error=True )
            return

        edit = self.activeEditPane().edit
        active_edit_filename = edit.doc.getFullpath()

        loop = [False]
        fullpath_mode = [False]
        select = None

        def onKeyDown( vk, mod ):

            if vk==VK_SPACE and mod==0:
                fullpath_mode[0] = not fullpath_mode[0]
                loop[0] = True
                list_window.quit()
                return True

        def onStatusMessage( width, select ):
            return ""

        while True:

            loop[0] = False

            items = []
            for filename, fullpath in zip( self.project.enumName(), self.project.enumFullpath() ):
                if fullpath_mode[0]:
                    items.append( ( fullpath, ) )
                else:
                    items.append( ( filename, ) )

                if select==None and active_edit_filename==fullpath:
                    select = len(items)-1

            if select==None:
                select = 0

            pos = self.centerOfWindowInPixel()
            list_window = lredit_listwindow.ListWindow( pos[0], pos[1], 20, 2, self.width()-5, self.height()-3, self, self.ini, True, "Files", items, initial_select=select, onekey_search=False, keydown_hook=onKeyDown, statusbar_handler=onStatusMessage )
            self.enable(False)
            list_window.messageLoop()

            # チラつき防止の遅延削除
            class DelayedCall:
                def __call__(self):
                    self.list_window.destroy()
            delay = DelayedCall()
            delay.list_window = list_window
            self.delayedCall( delay, 10 )

            if not loop[0]:
                break

            select = list_window.getResult()

        result = list_window.getResult()
        self.enable(True)
        self.activate()

        if result<0 : return

        filename = items[result][0]

        if fullpath_mode[0]:
            fullpath = filename
        else:
            fullpath = ckit.normPath( ckit.joinPath( self.project.dirname, filename ) )

        self.activeOpen( filename=fullpath )


    ## 最近開いたファイルを一覧表示する
    def command_RecentFileList( self, info ):

        loop = [False]
        fullpath_mode = [False]
        project_mode = [False]
        select = [None]

        def onKeyDown( vk, mod ):

            if vk==VK_SPACE and mod==0:
                fullpath_mode[0] = not fullpath_mode[0]
                loop[0] = True
                list_window.quit()
                return True

            elif vk==VK_LEFT and mod==0:
                if project_mode[0]:
                    project_mode[0] = False
                    select[0] = 0
                    loop[0] = True
                    list_window.quit()
                return True

            elif vk==VK_RIGHT and mod==0:
                if not project_mode[0]:
                    project_mode[0] = True
                    select[0] = 0
                    loop[0] = True
                    list_window.quit()
                return True

            elif vk==VK_DELETE and mod==0:
                select[0] = list_window.getResult()
                filename = items[select[0]][1]
                self.filename_history.remove(filename)
                list_window.remove(select[0])
                return True

        def onStatusMessage( width, select ):
            return ""

        while True:

            loop[0] = False

            items = []
            for filename in self.filename_history.items:

                if fnmatch.fnmatch( filename, "*.lre" ):
                    if not project_mode[0]:
                        continue
                else:
                    if project_mode[0]:
                        continue

                if fullpath_mode[0]:
                    s = "%s" % filename
                else:
                    s = "%s" % ckit.splitPath(filename)[1]

                items.append( ( s, filename ) )

            if select[0]==None:
                select[0] = 0

            if project_mode[0]:
                title = "Recent Projects"
            else:
                title = "Recent Files"

            pos = self.centerOfWindowInPixel()
            list_window = lredit_listwindow.ListWindow( pos[0], pos[1], 20, 2, self.width()-5, self.height()-3, self, self.ini, True, title, items, initial_select=select[0], onekey_search=False, keydown_hook=onKeyDown, statusbar_handler=onStatusMessage )
            self.enable(False)
            list_window.messageLoop()

            # チラつき防止の遅延削除
            class DelayedCall:
                def __call__(self):
                    self.list_window.destroy()
            delay = DelayedCall()
            delay.list_window = list_window
            self.delayedCall( delay, 10 )

            if not loop[0]:
                break

            select[0] = list_window.getResult()

        result = list_window.getResult()
        self.enable(True)
        self.activate()

        if result<0 : return
        if not items : return

        filename = items[result][1]

        if project_mode[0]:
            info = ckit.CommandInfo()
            info.args = [ filename ]
            self.command.OpenProject(info)
        else:
            self.activeOpen( filename=filename )


    ## モードを切り替える
    def command_Mode( self, info ):

        if len(info.args)>=1:
            mode_name = info.args[0]
        else:
            def statusString( update_info ):
                for mode in self.mode_list:
                    if mode.__name__==update_info.text:
                        return "OK"
                return "  "

            mode_name = self.commandLine( "Mode", auto_complete=False, autofix_list=[], candidate_handler=None, status_handler=statusString )
            if mode_name==None : return

        for mode in self.mode_list:
            if mode.__name__==mode_name:
                break
        else:
            self.setStatusMessage( ckit.strings["mode_not_found"] % mode_name, 3000, error=True, log=True )
            return

        edit = self.activeEditPane().edit

        edit.doc.setMode( mode() )
        edit.configure()

        self.setStatusMessage( ckit.strings["mode_enabled"] % mode_name, 3000 )


    ## マイナーモードをOn/Off
    def command_MinorMode( self, info ):

        if len(info.args)>=1:
            mode_name = info.args[0]
        else:
            def statusString( update_info ):
                for mode in self.minor_mode_list:
                    if mode.__name__==update_info.text:
                        return "OK"
                return "  "

            mode_name = self.commandLine( "MinorMode", auto_complete=False, autofix_list=[], candidate_handler=None, status_handler=statusString )
            if mode_name==None : return

        for mode in self.minor_mode_list:
            if mode.__name__==mode_name:
                break
        else:
            self.setStatusMessage( ckit.strings["mode_not_found"] % mode_name, 3000, error=True, log=True )
            return

        edit = self.activeEditPane().edit

        if edit.doc.hasMinorMode( mode.name ):
            edit.doc.removeMinorMode( mode.name )
            edit.configure()
            self.setStatusMessage( ckit.strings["mode_disabled"] % mode_name, 3000 )
        else:
            edit.doc.appendMinorMode( mode() )
            edit.configure()
            self.setStatusMessage( ckit.strings["mode_enabled"] % mode_name, 3000 )


    ## メニューを出す
    def menu( self, title, items, pos=None ):

        selection = 0

        keydown_func = [None]

        keymap = ckit.Keymap()
        for item in items:
            if item[1]:
                keymap[ item[1] ] = item[2]

        def onKeyDown( vk, mod ):
            try:
                keydown_func[0] = keymap.table[ ckit.KeyEvent(vk,mod) ]
                list_window.cancel()
                return True
            except KeyError:
                pass

        list_window = lredit_listwindow.ListWindow( 0, 0, 5, 1, self.width()-5, self.height()-3, self, self.ini, False, title, items, initial_select=selection, keydown_hook=onKeyDown, onekey_search=False )

        if pos:
            x, y = pos
            screen_x, screen_y1 = self.charToScreen( x, y )
            screen_x, screen_y2 = self.charToScreen( x, y+1 )
            pos = ( screen_x, screen_y2 )
            list_window.setPosSize( pos[0], pos[1], list_window.width(), list_window.height(), ORIGIN_X_LEFT | ORIGIN_Y_TOP )
        else:
            pos = self.centerOfWindowInPixel()
            list_window.setPosSize( pos[0], pos[1], list_window.width(), list_window.height(), ORIGIN_X_CENTER | ORIGIN_Y_CENTER )

        list_window.show(True)
        self.enable(False)
        list_window.messageLoop()
        result = list_window.getResult()
        self.enable(True)
        self.activate()
        list_window.destroy()

        if result>=0:
            items[result][2]( ckit.CommandInfo() )
        elif keydown_func[0]:
            keydown_func[0]( ckit.CommandInfo() )


    ## 拡張メニューを出す
    def command_ExtensionMenu( self, info ):
        edit = self.activePane().edit
        if not edit: return
        self.menu( None, self.ext_menu_items, pos=edit.getCursorPos() )


    ## TAGSファイルを生成する
    def command_GenerateTags( self, info ):

        if not self.project:
            self.setStatusMessage( ckit.strings["project_not_opened"], 3000, error=True )
            return

        tags_filename = ckit.joinPath( self.project.dirname, "tags" )
        srcs_filename = ckit.joinPath( self.project.dirname, "tags.srcs" )

        class SubThread( threading.Thread ):

            def __init__(thread_self):
                threading.Thread.__init__(thread_self)
                thread_self.p = None

            def createSourceFilesList( thread_self, filename ):

                fd = open( filename, "w", encoding="mbcs" )

                for filename in self.project.enumName():
                    fd.write(os.path.normpath(filename))
                    fd.write("\r\n")

                fd.close()

            def run(thread_self):
                lredit_native.setBlockDetector()

                thread_self.createSourceFilesList(srcs_filename)

                cmd = [ os.path.join( ckit.getAppExePath(), "bin/ctags.exe" ) ]
                cmd += [ "-o", tags_filename ]
                cmd += [ "-n" ] # タグ情報として行番号を使用する
                cmd += [ "-L", srcs_filename ]

                thread_self.p = ckit.SubProcess(cmd,cwd=self.project.dirname,env=None)
                thread_self.p()
                thread_self = None

                os.unlink(srcs_filename)

            def cancel(thread_self):
                if thread_self.p:
                    thread_self.p.cancel()
                    thread_self.p = None

        def jobGenerateTags( job_item ):

            self.setStatusMessage( ckit.strings["statusbar_tags_generating"] )

            self.setProgressValue(None)

            sub_thread = SubThread()
            sub_thread.start()
            while sub_thread.isAlive():
                if job_item.isCanceled():
                    sub_thread.cancel()
                    break
                time.sleep(0.1)
            sub_thread.join()

        def jobGenerateTagsFinished( job_item ):

            self.clearProgress()

            if job_item.isCanceled():
                self.setStatusMessage( ckit.strings["statusbar_aborted"], 3000 )
            else:
                self.setStatusMessage( ckit.strings["statusbar_tags_generated"], 3000 )

        job_item = ckit.JobItem( jobGenerateTags, jobGenerateTagsFinished )
        self.taskEnqueue( job_item, "GenerateTags" )

    def loadTags( self, filename ):

        filename = ckit.normPath(filename)

        for tags in self.tags_list:
            if tags.getFullpath() == filename:
                if tags.isFileModified():
                    self.tags_list.remove(tags)
                    break
                else:
                    return

        tags = lredit_tags.Tags(filename)

        cancel_requested = [False]
        def cancel():
            cancel_requested[0] = True
            tags.cancel()

        self.setStatusMessage( ckit.strings["statusbar_tags_loading"] )

        self.setProgressValue(None)
        try:
            self.subThreadCall( tags.parse, (), cancel )
        finally:
            self.clearProgress()

        if cancel_requested[0]:
            self.setStatusMessage( ckit.strings["statusbar_aborted"], 3000 )
        else:
            self.setStatusMessage( ckit.strings["statusbar_tags_loaded"], 3000 )

        if not cancel_requested[0]:
            self.tags_list.insert( 0, tags )

    ## TAGSファイルをロードする
    def command_LoadTags( self, info ):

        if len(info.args)>=1:
            filename = info.args[0]
        else:
            filename = self.inputFilename( "Tags", "", ensure_exists=True )
            if not filename : return

        self.loadTags(filename)


    ## TAGSにしたがってシンボルの定義位置にジャンプする
    #
    #  引数にシンボル名を渡すことができます。
    #  引数を渡さなかった場合は、カーソル位置の単語をシンボル名として扱います。
    #
    def command_TagsJump( self, info ):

        edit = self.activeEditPane().edit

        if len(info.args):
            symbol = info.args[0]
        else:
            if edit.selection.direction==0:
                cursor = edit.selection.cursor()
                right = cursor.wordRight(False)
                left = right.wordLeft(False)
                symbol = edit.getText( left, right )
            else:
                symbol = edit.getText( edit.selection.left(), edit.selection.right() )

        if not symbol:
            return

        # プロジェクトファイルの隣のTAGSファイルをロードする
        if self.project:
            tags_filename = ckit.joinPath(os.path.dirname(self.project.filename),"tags")
            try:
                self.loadTags(tags_filename)
            except IOError:
                pass

        for tags in self.tags_list:
            tags_items = tags.find(symbol)
            if tags_items:
                break
        else:
            self.setStatusMessage( ckit.strings["statusbar_symbol_not_found"] % symbol, 3000, error=True )
            return

        if len(tags_items)>=2:

            list_items = []
            for item in tags_items:
                name = "%s (%s)" % ( ckit.normPath(item[1]), item[2] )
                name = ckit.adjustStringWidth( self, name, self.width()-5, align=ckit.ALIGN_LEFT, ellipsis=ckit.ELLIPSIS_MID )
                name = name.rstrip()
                list_items.append( ( name, item ) )

            def onStatusMessage( width, select ):
                return ""

            pos = self.centerOfWindowInPixel()
            list_window = lredit_listwindow.ListWindow( pos[0], pos[1], 5, 1, self.width()-5, self.height()-3, self, self.ini, True, "Symbols : [%s]" % symbol, list_items, initial_select=0, onekey_search=False, statusbar_handler=onStatusMessage )
            self.enable(False)
            list_window.messageLoop()
            result = list_window.getResult()
            self.enable(True)
            self.activate()
            list_window.destroy()

            if result<0 : return

            tags_item = list_items[result][1]

        else:
            tags_item = tags_items[0]

        symbol2, filename, position = tags_item
        
        # TagsJumpの履歴に現在位置を追加する
        current = ( edit.doc.getFullpath(), edit.selection.cursor() )
        self.tags_jump_history.append(current)

        filename = ckit.joinPath( ckit.splitPath(tags.getFullpath())[0], filename )

        self.activeOpen(filename=filename)
        edit = self.activePane().edit

        if isinstance( position, str ):
            try:
                search_object = ckit.Search( position, word=False, case=True, regex=False )
            except re.error:
                self.setStatusMessage( ckit.strings["statusbar_regex_wrong"] % position, 3000, error=True )
                return
            edit.setCursor( edit.pointDocumentBegin() )
            edit.search( search_object=search_object, direction=1, select=False, hitmark=False )
        if isinstance( position, int ):
            point = edit.point(position-1)
            edit.setCursor( point, make_visible=False, paint=False )
            edit.makeVisible( point, jump_mode=True )
        else:
            return


    ## TAGSジャンプのジャンプ元に戻る
    def command_TagsBack( self, info ):
        
        if not self.tags_jump_history:
            return

        filename, point = self.tags_jump_history.pop()

        self.activeOpen( filename=filename )
        edit = self.activePane().edit
        edit.setCursor( point, make_visible=False, paint=False )
        edit.makeVisible( point, jump_mode=True )


    ## アウトライン解析結果をリスト表示
    def command_Outline( self, info ):

        edit = self.activeEditPane().edit
        src_filename = edit.doc.getFullpath()
        current_lineno = edit.selection.cursor().line
        encoding = edit.doc.encoding

        if src_filename==None:
            return

        if edit.doc.isModified():
            src_filename = ckit.makeTempFile( "tags.src_", os.path.splitext(src_filename)[1] )
            fd = open( src_filename, "wb" )
            edit.doc.writeFile(fd)
            fd.close()

        tags_filename = ckit.makeTempFile("tags_")

        cmd = [ os.path.join( ckit.getAppExePath(), "bin/ctags.exe" ) ]
        cmd += [ "-o", tags_filename ]
        cmd += [ "--sort=no" ] # ソートしない
        cmd += [ "--excmd=pattern" ] # 文字列による検索パターン
        cmd += [ "--fields=mKnsStz" ] # http://ctags.sourceforge.net/ctags.html
        cmd += [ src_filename ]

        self.subProcessCall(cmd)

        select = 0

        def onStatusMessage( width, select ):
            return ""

        items = []

        fd = open( tags_filename, "r", encoding=encoding.encoding, errors="ignore" )
        lines = fd.readlines()
        fd.close()

        pattern_line = re.compile( '(.*)\t(.*)\t/\^(.*)\$/;".*line:([0-9]+).*' )
        for line in lines:
            result = pattern_line.match(line)
            if result:
                s = result.group(3)
                s = ckit.removeBom(s)
                s = ckit.expandTab( self, s, edit.doc.mode.tab_width )
                lineno = int(result.group(4))-1
                if lineno <= current_lineno:
                    select = len(items)
                items.append( ( s, lineno ) )

        pos = self.centerOfWindowInPixel()
        list_window = lredit_listwindow.ListWindow( pos[0], pos[1], 20, 2, self.width()-5, self.height()-3, self, self.ini, True, "Outline", items, initial_select=select, onekey_search=False, statusbar_handler=onStatusMessage )
        self.enable(False)
        list_window.messageLoop()
        result = list_window.getResult()
        self.enable(True)
        self.activate()
        list_window.destroy()

        if result<0 : return

        edit.jumpLineNo( items[result][1] )


#--------------------------------------------------------------------

## @} mainwindow

