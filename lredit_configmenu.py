import os
import sys
import traceback

import ckit
from ckit.ckit_const import *

import lredit_listwindow
import lredit_wallpaper
import lredit_resource

#--------------------------------------------------------------------

def _configTheme( main_window ):

    def enumThemes():
        
        theme_list = []
        theme_parent = os.path.join( ckit.getAppExePath(), 'theme' )
        theme_dir_list = os.listdir(theme_parent)
        
        for theme_dir in theme_dir_list:
            
            if os.path.exists( os.path.join( theme_parent, theme_dir, "theme.ini" ) ):
                theme_list.append( theme_dir )
        
        return theme_list

    theme_list = enumThemes()

    current_theme_name = main_window.ini.get( "THEME", "name" )

    try:
        initial_select = theme_list.index(current_theme_name)
    except:
        initial_select = 0

    result = lredit_listwindow.popMenu( main_window, ckit.strings["theme"], theme_list, initial_select )
    if result<0 : return

    main_window.ini.set( "THEME", "name", theme_list[result] )
    
    main_window.reloadTheme()
    
    return False

def _configFontName( main_window ):
    font_list = main_window.enumFonts()

    current_font_name = main_window.ini.get( "FONT", "name" )

    try:
        initial_select = font_list.index(current_font_name)
    except:
        initial_select = 0

    select = lredit_listwindow.popMenu( main_window, ckit.strings["font"], font_list, initial_select )
    if select<0 : return

    main_window.ini.set( "FONT", "name", font_list[select] )

    main_window.setFont( main_window.ini.get("FONT","name"), main_window.ini.getint( "FONT", "size" ) )
    window_rect = main_window.getWindowRect()
    main_window.setPosSize( window_rect[0], window_rect[1], main_window.width(), main_window.height(), 0 )

def _configFontSize( main_window ):

    size_list = range(6,33)

    current_font_size = main_window.ini.getint( "FONT", "size" )

    try:
        initial_select = size_list.index(current_font_size)
    except:
        initial_select = 0

    size_list = list(map( str, size_list ))

    select = lredit_listwindow.popMenu( main_window, ckit.strings["font_size"], size_list, initial_select )
    if select<0 : return

    main_window.ini.set( "FONT", "size", size_list[select] )

    main_window.setFont( main_window.ini.get("FONT","name"), main_window.ini.getint( "FONT", "size" ) )
    window_rect = main_window.getWindowRect()
    main_window.setPosSize( window_rect[0], window_rect[1], main_window.width(), main_window.height(), 0 )

def _configMenuBar( main_window ):

    items = []

    items.append( ( ckit.strings["invisible"], "0" ) )
    items.append( ( ckit.strings["visible"],   "1" ) )

    visible = main_window.ini.get( "MENUBAR", "visible" )

    initial_select = 0
    for i in range(len(items)):
        if items[i][1]==visible:
            initial_select = i
            break

    select = lredit_listwindow.popMenu( main_window, ckit.strings["menubar_visibility"], items, initial_select )
    if select<0 : return

    main_window.ini.set( "MENUBAR", "visible", items[select][1] )
    
    main_window.applyMenuBar()

def _configWallpaperVisible( main_window ):

    items = []

    items.append( ( ckit.strings["invisible"], "0" ) )
    items.append( ( ckit.strings["visible"],   "1" ) )

    visible = main_window.ini.get( "WALLPAPER", "visible" )

    initial_select = 0
    for i in range(len(items)):
        if items[i][1]==visible:
            initial_select = i
            break

    select = lredit_listwindow.popMenu( main_window, ckit.strings["wallpaper_visibility"], items, initial_select )
    if select<0 : return

    main_window.ini.set( "WALLPAPER", "visible", items[select][1] )
    
    main_window.updateWallpaper()

def _configWallpaperStrength( main_window ):

    items = []

    items.append( ( " 10 %", "10" ) )
    items.append( ( " 20 %", "20" ) )
    items.append( ( " 30 %", "30" ) )
    items.append( ( " 40 %", "40" ) )
    items.append( ( " 50 %", "50" ) )
    items.append( ( " 60 %", "60" ) )
    items.append( ( " 70 %", "70" ) )
    items.append( ( " 80 %", "80" ) )
    items.append( ( " 90 %", "90" ) )
    items.append( ( "100 %", "100" ) )

    strength = main_window.ini.get( "WALLPAPER", "strength" )

    initial_select = 0
    for i in range(len(items)):
        if items[i][1]==strength:
            initial_select = i
            break

    select = lredit_listwindow.popMenu( main_window, ckit.strings["wallpaper_strength"], items, initial_select )
    if select<0 : return

    main_window.ini.set( "WALLPAPER", "strength", items[select][1] )
    
    main_window.updateWallpaper()

def _configWallpaper( main_window ):

    select = 0
    
    while True:

        items = []

        items.append( ( ckit.strings["wallpaper_visibility"], _configWallpaperVisible ) )
        items.append( ( ckit.strings["wallpaper_strength"], _configWallpaperStrength ) )

        select = lredit_listwindow.popMenu( main_window, "壁紙オプション", items, select )
        if select<0 : return

        items[select][1]( main_window )

def _configAppName( main_window ):

    RESULT_CANCEL = 0
    RESULT_OK     = 1

    class AppNameWindow( ckit.Window ):

        FOCUS_EDIT = 0

        def __init__( self, x, y, parent_window, ini ):

            ckit.Window.__init__(
                self,
                x=x,
                y=y,
                width=48,
                height=3,
                origin= ORIGIN_X_CENTER | ORIGIN_Y_CENTER,
                parent_window=parent_window,
                bg_color = ckit.getColor("bg"),
                resizable = False,
                title = ckit.strings["application_name"],
                minimizebox = False,
                maximizebox = False,
                cursor = True,
                close_handler = self.onClose,
                keydown_handler = self.onKeyDown,
                char_handler = self.onChar,
                )

            self.setCursorPos( -1, -1 )

            self.focus = AppNameWindow.FOCUS_EDIT
            self.result = RESULT_CANCEL

            app_name = main_window.ini.get( "MISC", "app_name" )

            self.edit = ckit.EditWidget( self, 22, 1, self.width()-24, 1, app_name, [0,len(app_name)] )

            try:
                self.wallpaper = lredit_wallpaper.Wallpaper(self)
                self.wallpaper.copy( parent_window )
                self.wallpaper.adjust()
            except:
                self.wallpaper = None

            self.paint()

        def onClose(self):
            self.result = RESULT_CANCEL
            self.quit()

        def onEnter(self):
            self.result = RESULT_OK
            self.quit()

        def onKeyDown( self, vk, mod ):

            if vk==VK_RETURN:
                self.onEnter()

            elif vk==VK_ESCAPE:
                self.result = RESULT_CANCEL
                self.quit()

            else:
                if self.focus==AppNameWindow.FOCUS_EDIT:
                    self.edit.onKeyDown( vk, mod )

        def onChar( self, ch, mod ):
            if self.focus==AppNameWindow.FOCUS_EDIT:
                self.edit.onChar( ch, mod )
            else:
                pass

        def paint(self):

            if self.focus==AppNameWindow.FOCUS_EDIT:
                attr = ckit.Attribute( fg=ckit.getColor("fg"), bg=ckit.getColor("select_bg" ))
            else:
                attr = ckit.Attribute( fg=ckit.getColor("fg" ))
            self.putString( 2, 1, self.width()-2, 1, attr, ckit.strings["application_name"] )

            self.edit.enableCursor(self.focus==AppNameWindow.FOCUS_EDIT)
            self.edit.paint()

        def getResult(self):
            if self.result:
                return [ self.edit.getText() ]
            else:
                return None

    pos = main_window.centerOfWindowInPixel()
    appname_window = AppNameWindow( pos[0], pos[1], main_window, main_window.ini )
    main_window.enable(False)
    appname_window.messageLoop()
    result = appname_window.getResult()
    main_window.enable(True)
    main_window.activate()
    appname_window.destroy()

    if result==None : return

    main_window.ini.set( "MISC", "app_name", result[0] )

    lredit_resource.lredit_appname = result[0]
    main_window.updateTitleBar()
    main_window.command.About()


def _configLocale( main_window ):

    items = []

    items.append( ( ckit.strings["locale_en_US"], "en_US" ) )
    items.append( ( ckit.strings["locale_ja_JP"], "ja_JP" ) )

    visible = main_window.ini.get( "MISC", "locale" )

    initial_select = 0
    for i in range(len(items)):
        if items[i][1]==visible:
            initial_select = i
            break

    select = lredit_listwindow.popMenu( main_window, ckit.strings["locale"], items, initial_select )
    if select<0 : return

    main_window.ini.set( "MISC", "locale", items[select][1] )
    
    lredit_resource.setLocale(items[select][1])
    main_window.configure()


def _configISearch( main_window ):

    items = []

    items.append( ( ckit.strings["isearch_type_strict"], "strict" ) )
    items.append( ( ckit.strings["isearch_type_partial"], "partial" ) )
    items.append( ( ckit.strings["isearch_type_inaccurate"], "inaccurate" ) )
    items.append( ( ckit.strings["isearch_type_migemo"], "migemo" ) )

    isearch_type = main_window.ini.get( "MISC", "isearch_type" )

    initial_select = 0
    for i in range(len(items)):
        if items[i][1]==isearch_type:
            initial_select = i
            break

    select = lredit_listwindow.popMenu( main_window, ckit.strings["isearch_type"], items, initial_select )
    if select<0 : return

    main_window.ini.set( "MISC", "isearch_type", items[select][1] )

def _configBeep( main_window ):

    items = []

    items.append( ( ckit.strings["beep_type_disabled"], "disabled" ) )
    items.append( ( ckit.strings["beep_type_enabled"],  "enabled" ) )

    beep_type = main_window.ini.get( "MISC", "beep_type" )

    initial_select = 0
    for i in range(len(items)):
        if items[i][1]==beep_type:
            initial_select = i
            break

    select = lredit_listwindow.popMenu( main_window, ckit.strings["beep_type"], items, initial_select )
    if select<0 : return

    main_window.ini.set( "MISC", "beep_type", items[select][1] )

    ckit.enableBeep( main_window.ini.get( "MISC", "beep_type" )=="enabled" )

def _configDirectorySeparator( main_window ):

    items = []

    items.append( ( ckit.strings["directory_separator_slash"],  "slash" ) )
    items.append( ( ckit.strings["directory_separator_backslash"], "backslash" ) )

    directory_separator = main_window.ini.get( "MISC", "directory_separator" )

    initial_select = 0
    for i in range(len(items)):
        if items[i][1]==directory_separator:
            initial_select = i
            break

    select = lredit_listwindow.popMenu( main_window, ckit.strings["directory_separator"], items, initial_select )
    if select<0 : return

    main_window.ini.set( "MISC", "directory_separator", items[select][1] )

    if items[select][1]=="slash":
        ckit.setPathSlash(True)
    else:
        ckit.setPathSlash(False)

def _configDriveCase( main_window ):

    items = []

    items.append( ( ckit.strings["drive_case_nocare"], "nocare" ) )
    items.append( ( ckit.strings["drive_case_upper"], "upper" ) )
    items.append( ( ckit.strings["drive_case_lower"], "lower" ) )

    drive_case = main_window.ini.get( "MISC", "drive_case" )

    initial_select = 0
    for i in range(len(items)):
        if items[i][1]==drive_case:
            initial_select = i
            break

    select = lredit_listwindow.popMenu( main_window, ckit.strings["drive_case"], items, initial_select )
    if select<0 : return

    main_window.ini.set( "MISC", "drive_case", items[select][1] )

    if items[select][1]=="upper":
        ckit.setPathDriveUpper(True)
    elif items[select][1]=="lower":
        ckit.setPathDriveUpper(False)
    else:    
        ckit.setPathDriveUpper(None)

def _editConfigFile( main_window ):
    main_window.activeOpen( filename = main_window.config_filename )
    return False

def _reloadConfigFile( main_window ):
    main_window.command.ReloadConfig()
    return False

def _configAppearance( main_window ):

    select = 0
    
    while True:

        items = []

        items.append( ( ckit.strings["theme"], _configTheme ) )
        items.append( ( ckit.strings["font"], _configFontName ) )
        items.append( ( ckit.strings["font_size"], _configFontSize ) )
        items.append( ( ckit.strings["menubar"], _configMenuBar ) )
        items.append( ( ckit.strings["wallpaper"], _configWallpaper ) )
        items.append( ( ckit.strings["application_name"], _configAppName ) )
        items.append( ( ckit.strings["locale"], _configLocale ) )
        items.append( ( ckit.strings["directory_separator"], _configDirectorySeparator ) )
        items.append( ( ckit.strings["drive_case"], _configDriveCase ) )

        select = lredit_listwindow.popMenu( main_window, ckit.strings["display_option"], items, select )
        if select<0 : return

        items[select][1]( main_window )


def _configOperation( main_window ):

    select = 0
    
    while True:

        items = []

        items.append( ( ckit.strings["isearch_type"], _configISearch ) )
        items.append( ( ckit.strings["beep_type"], _configBeep ) )

        select = lredit_listwindow.popMenu( main_window, ckit.strings["operation_option"], items, select )
        if select<0 : return

        items[select][1]( main_window )


def doConfigMenu( main_window ):

    select = 0
    
    while True:

        items = []

        items.append( ( ckit.strings["display_option"], _configAppearance ) )
        items.append( ( ckit.strings["operation_option"], _configOperation ) )
        items.append( ( ckit.strings["edit_config"], _editConfigFile ) )
        items.append( ( ckit.strings["reload_config"], _reloadConfigFile ) )

        select = lredit_listwindow.popMenu( main_window, ckit.strings["config_menu"], items, select )
        if select<0 : return

        loop_continue = items[select][1]( main_window )
        if loop_continue==False:
            return
