import ckit

lredit_appname = "LREdit"
lredit_dirname = "LREdit"
lredit_version = "1.78 beta1"

_startup_string_fmt = """\
%s version %s:
  http://sites.google.com/site/craftware/
"""

def startupString():
    return _startup_string_fmt % ( lredit_appname, lredit_version )

ckit.strings.setString( "common_yes",
    en_US = "Yes",
    ja_JP = "はい" )
ckit.strings.setString( "common_no",
    en_US = "No",
    ja_JP = "いいえ" )
ckit.strings.setString( "common_done",
    en_US = "Done.",
    ja_JP = "完了." )
ckit.strings.setString( "common_aborted",
    en_US = "Aborted.",
    ja_JP = "中断しました." )
ckit.strings.setString( "common_failed",
    en_US = "Failed.",
    ja_JP = "失敗." )

ckit.strings.setString( "menu_file",
    en_US = "&File",
    ja_JP = "ファイル(&F)" )
ckit.strings.setString( "menu_new",
    en_US = "&New",
    ja_JP = "新規作成(&N)" )
ckit.strings.setString( "menu_open",
    en_US = "&Open",
    ja_JP = "開く(&O)" )
ckit.strings.setString( "menu_reopen",
    en_US = "&Reopen",
    ja_JP = "開き直す(&R)" )
ckit.strings.setString( "menu_close",
    en_US = "&Close",
    ja_JP = "閉じる(&C)" )
ckit.strings.setString( "menu_project",
    en_US = "&Project",
    ja_JP = "プロジェクト(&P)" )
ckit.strings.setString( "menu_open_project",
    en_US = "&Open",
    ja_JP = "開く(&O)" )
ckit.strings.setString( "menu_close_project",
    en_US = "&Close",
    ja_JP = "閉じる(&C)" )
ckit.strings.setString( "menu_edit_project",
    en_US = "&Edit",
    ja_JP = "編集(&E)" )
ckit.strings.setString( "menu_project_file_list",
    en_US = "Project &File List",
    ja_JP = "プロジェクトファイル一覧(&F)" )
ckit.strings.setString( "menu_save",
    en_US = "&Save",
    ja_JP = "保存(&S)" )
ckit.strings.setString( "menu_save_as",
    en_US = "Save &As",
    ja_JP = "名前を付けて保存(&A)" )
ckit.strings.setString( "menu_save_all",
    en_US = "Save A&ll",
    ja_JP = "すべて保存(&L)" )
ckit.strings.setString( "menu_encoding",
    en_US = "&Encoding",
    ja_JP = "エンコーディング(&E)" )
ckit.strings.setString( "menu_recent_files",
    en_US = "Recent F&iles",
    ja_JP = "最近のファイル(&I)" )
ckit.strings.setString( "menu_recent_projects",
    en_US = "Recent Pro&jects",
    ja_JP = "最近のプロジェクト(&J)" )
ckit.strings.setString( "menu_quit",
    en_US = "&Quit",
    ja_JP = "終了(&Q)" )

ckit.strings.setString( "menu_edit",
    en_US = "&Edit",
    ja_JP = "編集(&E)" )
ckit.strings.setString( "menu_undo",
    en_US = "&Undo",
    ja_JP = "元に戻す(&U)" )
ckit.strings.setString( "menu_redo",
    en_US = "&Redo",
    ja_JP = "やり直し(&R)" )
ckit.strings.setString( "menu_cut",
    en_US = "Cu&t",
    ja_JP = "切り取り(&T)" )
ckit.strings.setString( "menu_copy",
    en_US = "&Copy",
    ja_JP = "コピー(&C)" )
ckit.strings.setString( "menu_paste",
    en_US = "&Paste",
    ja_JP = "貼り付け(&P)" )
ckit.strings.setString( "menu_delete",
    en_US = "&Delete",
    ja_JP = "削除(&D)" )
ckit.strings.setString( "menu_select_all",
    en_US = "Select A&ll",
    ja_JP = "すべてを選択(&L)" )
ckit.strings.setString( "menu_convert_char",
    en_US = "Con&vert",
    ja_JP = "文字変換(&V)" )
ckit.strings.setString( "menu_to_upper",
    en_US = "&Uppercase",
    ja_JP = "大文字化(&U)" )
ckit.strings.setString( "menu_to_lower",
    en_US = "&Lowercase",
    ja_JP = "小文字化(&L)" )
ckit.strings.setString( "menu_to_zenkaku",
    en_US = "&Zenkaku",
    ja_JP = "全角に変換(&Z)" )
ckit.strings.setString( "menu_to_hankaku",
    en_US = "&Hankaku",
    ja_JP = "半角に変換(&H)" )
ckit.strings.setString( "menu_complete",
    en_US = "&Word Completion",
    ja_JP = "単語補完(&W)" )
ckit.strings.setString( "menu_jump_lineno",
    en_US = "&Goto Line",
    ja_JP = "指定行ジャンプ(&G)" )

ckit.strings.setString( "menu_search",
    en_US = "&Search",
    ja_JP = "検索(&S)" )
ckit.strings.setString( "menu_search_next",
    en_US = "Search &Next",
    ja_JP = "次を検索(&N)" )
ckit.strings.setString( "menu_search_prev",
    en_US = "Search &Prev",
    ja_JP = "前を検索(&P)" )
ckit.strings.setString( "menu_grep",
    en_US = "&Grep",
    ja_JP = "ファイルから検索(&G)" )
ckit.strings.setString( "menu_tags",
    en_US = "S&ymbol Search",
    ja_JP = "シンボル検索(&Y)" )
ckit.strings.setString( "menu_tags_jump",
    en_US = "&Jump to Definition",
    ja_JP = "定義位置へジャンプ(&J)" )
ckit.strings.setString( "menu_tags_back",
    en_US = "&Back to Original Position",
    ja_JP = "ジャンプ元へ戻る(&B)" )
ckit.strings.setString( "menu_load_tags",
    en_US = "&Load TAGS",
    ja_JP = "TAGSの読み込み(&L)" )
ckit.strings.setString( "menu_generate_tags",
    en_US = "&Generate TAGS",
    ja_JP = "TAGSの生成(&G)" )
ckit.strings.setString( "menu_replace",
    en_US = "&Replace",
    ja_JP = "置換(&R)" )
ckit.strings.setString( "menu_compare",
    en_US = "&Compare",
    ja_JP = "比較(&C)" )

ckit.strings.setString( "menu_view",
    en_US = "&View",
    ja_JP = "表示(&V)" )
ckit.strings.setString( "menu_another_pane",
    en_US = "&Another Pane",
    ja_JP = "他方のペイン(&A)" )
ckit.strings.setString( "menu_doclist",
    en_US = "&Document List",
    ja_JP = "文書選択(&D)" )

ckit.strings.setString( "menu_tool",
    en_US = "&Tool",
    ja_JP = "ツール(&T)" )
ckit.strings.setString( "menu_bookmark_list",
    en_US = "&Bookmark List",
    ja_JP = "ブックマーク一覧(&B)" )
ckit.strings.setString( "menu_bookmark1",
    en_US = "Bookmark&1",
    ja_JP = "ブックマーク1(&1)" )
ckit.strings.setString( "menu_bookmark2",
    en_US = "Bookmark&2",
    ja_JP = "ブックマーク2(&2)" )
ckit.strings.setString( "menu_bookmark3",
    en_US = "Bookmark&3",
    ja_JP = "ブックマーク3(&3)" )
ckit.strings.setString( "menu_bookmark_next",
    en_US = "&Next Bookmark",
    ja_JP = "次のブックマークへ(&N)" )
ckit.strings.setString( "menu_bookmark_prev",
    en_US = "&Prev Bookmark",
    ja_JP = "前のブックマークへ(&P)" )
ckit.strings.setString( "menu_outline",
    en_US = "&Outline",
    ja_JP = "アウトライン(&O)" )
ckit.strings.setString( "menu_expand_tab",
    en_US = "Expand &Tab",
    ja_JP = "タブをスペースに展開(&T)" )
ckit.strings.setString( "menu_remove_trailing_space",
    en_US = "Remove Trailing &Space",
    ja_JP = "行末の空白を削除(&S)" )
ckit.strings.setString( "menu_remove_empty_lines",
    en_US = "Remove &Empty Lines",
    ja_JP = "空行を削除(&E)" )
ckit.strings.setString( "menu_remove_marked_lines",
    en_US = "Remove &Marked Lines",
    ja_JP = "ブックマークされている行を削除(&M)" )
ckit.strings.setString( "menu_remove_unmarked_lines",
    en_US = "Remove &Unmarked Lines",
    ja_JP = "ブックマークされていない行を削除(&U)" )
ckit.strings.setString( "menu_config_menu",
    en_US = "&Config",
    ja_JP = "設定(&C)" )
ckit.strings.setString( "menu_config_edit",
    en_US = "&Edit config.py",
    ja_JP = "config.pyの編集(&E)" )
ckit.strings.setString( "menu_config_reload",
    en_US = "&Reload config.py",
    ja_JP = "config.pyの再読み込み(&R)" )

ckit.strings.setString( "menu_help",
    en_US = "&Help",
    ja_JP = "ヘルプ(&H)" )
ckit.strings.setString( "menu_about",
    en_US = "&About",
    ja_JP = "バージョン情報(&A)" )

ckit.strings.setString( "config_menu",
    en_US = "Configuration Menu",
    ja_JP = "設定メニュー" )
ckit.strings.setString( "display_option",
    en_US = "Display Options",
    ja_JP = "表示オプション" )
ckit.strings.setString( "operation_option",
    en_US = "Operation Options",
    ja_JP = "操作オプション" )
ckit.strings.setString( "misc_option",
    en_US = "Misc Options",
    ja_JP = "その他のオプション" )
ckit.strings.setString( "theme",
    en_US = "Theme",
    ja_JP = "テーマ" )
ckit.strings.setString( "font",
    en_US = "Font",
    ja_JP = "フォント" )
ckit.strings.setString( "font_size",
    en_US = "Font Size",
    ja_JP = "フォントサイズ" )
ckit.strings.setString( "visible",
    en_US = "Visible",
    ja_JP = "表示" )
ckit.strings.setString( "invisible",
    en_US = "Invisible",
    ja_JP = "非表示" )
ckit.strings.setString( "menubar",
    en_US = "Menu Bar",
    ja_JP = "メニューバー" )
ckit.strings.setString( "menubar_visibility",
    en_US = "Menu Bar Visibility",
    ja_JP = "メニューバーの表示" )
ckit.strings.setString( "wallpaper",
    en_US = "Wallpaper",
    ja_JP = "壁紙" )
ckit.strings.setString( "wallpaper_visibility",
    en_US = "Wallpaper Visibility",
    ja_JP = "壁紙の表示" )
ckit.strings.setString( "wallpaper_strength",
    en_US = "Wallpaper Strength",
    ja_JP = "壁紙の濃さ" )
ckit.strings.setString( "application_name",
    en_US = "Application Name",
    ja_JP = "アプリケーション名" )
ckit.strings.setString( "locale",
    en_US = "Display Language",
    ja_JP = "表示言語" )
ckit.strings.setString( "locale_en_US",
    en_US = "English",
    ja_JP = "英語" )
ckit.strings.setString( "locale_ja_JP",
    en_US = "Japanese",
    ja_JP = "日本語" )
ckit.strings.setString( "isearch_type",
    en_US = "Incremental Search Behavior",
    ja_JP = "インクリメンタルサーチ動作" )
ckit.strings.setString( "isearch_type_strict",
    en_US = "Strict     : ABC*",
    ja_JP = "厳密     : ABC*" )
ckit.strings.setString( "isearch_type_partial",
    en_US = "Partial    : *ABC*",
    ja_JP = "部分一致 : *ABC*" )
ckit.strings.setString( "isearch_type_inaccurate",
    en_US = "Inaccurate : *A*B*C*",
    ja_JP = "あいまい : *A*B*C*" )
ckit.strings.setString( "isearch_type_migemo",
    en_US = "Migemo     : *AIUEO*",
    ja_JP = "Migemo   : *AIUEO*" )
ckit.strings.setString( "beep_type",
    en_US = "Beep Sound",
    ja_JP = "ビープ音" )
ckit.strings.setString( "beep_type_disabled",
    en_US = "Diabled",
    ja_JP = "無効" )
ckit.strings.setString( "beep_type_enabled",
    en_US = "Enabled",
    ja_JP = "有効" )
ckit.strings.setString( "directory_separator",
    en_US = "Directory Separator",
    ja_JP = "ディレクトリ区切り文字" )
ckit.strings.setString( "directory_separator_slash",
    en_US = "Slash       : / ",
    ja_JP = "スラッシュ       : / " )
ckit.strings.setString( "directory_separator_backslash",
    en_US = "BackSlash   : \\ ",
    ja_JP = "バックスラッシュ : \\ " )
ckit.strings.setString( "drive_case",
    en_US = "Case of Drive Letter",
    ja_JP = "ドライブ文字の大文字/小文字" )
ckit.strings.setString( "drive_case_nocare",
    en_US = "Don't care",
    ja_JP = "気にしない" )
ckit.strings.setString( "drive_case_upper",
    en_US = "Upper case",
    ja_JP = "大文字" )
ckit.strings.setString( "drive_case_lower",
    en_US = "Lower case",
    ja_JP = "小文字" )
ckit.strings.setString( "edit_config",
    en_US = "Edit config.py",
    ja_JP = "config.py を編集" )
ckit.strings.setString( "reload_config",
    en_US = "Reload config.py",
    ja_JP = "config.py を再読み込み" )

ckit.strings.setString( "msgbox_title_generic_error",
    en_US = "Error",
    ja_JP = "エラー" )
ckit.strings.setString( "msgbox_title_insert_task",
    en_US = "Task Order",
    ja_JP = "タスクの処理順序の確認" )
ckit.strings.setString( "msgbox_ask_insert_task",
    en_US = "proceed preferentially?",
    ja_JP = "優先的に処理を行いますか？" )
ckit.strings.setString( "msgbox_title_save",
    en_US = "Save",
    ja_JP = "保存確認" )
ckit.strings.setString( "msgbox_ask_save_document",
    en_US = "Save [%s] ?",
    ja_JP = "[%s] を保存しますか？" )
ckit.strings.setString( "msgbox_title_modified_reload",
    en_US = "Reload",
    ja_JP = "再読み込み確認" )
ckit.strings.setString( "msgbox_ask_modified_reload",
    en_US = "%s is modified from outside. Reload this file?",
    ja_JP = "%sが外部で変更されています。再読み込みしますか？" )
ckit.strings.setString( "msgbox_title_wallpaper_error",
    en_US = "Wallpaper",
    ja_JP = "壁紙のエラー" )
ckit.strings.setString( "msgbox_wallpaper_filename_empty",
    en_US = "Using Wallpaper command, specify the filename of wallpaper.",
    ja_JP = "Wallpaperコマンドを使って、壁紙ファイルを指定してください。" )
ckit.strings.setString( "msgbox_title_modified_reopen",
    en_US = "Reopen",
    ja_JP = "変更内容破棄の確認" )
ckit.strings.setString( "msgbox_ask_modified_reopen",
    en_US = "%s is modified. Is it OK to destroy this modification and reopen this file?",
    ja_JP = "%sは変更されていますが、開きなおしますか？" )
ckit.strings.setString( "msgbox_title_new_window",
    en_US = "New LREdit window",
    ja_JP = "新規 LREdit ウインドウの確認" )
ckit.strings.setString( "msgbox_ask_new_window",
    en_US = "Open a new window?",
    ja_JP = "新しいウインドウを開きますか？" )
    
ckit.strings.setString( "statusbar_task_reserved",
    en_US = "Reserved task : %s",
    ja_JP = "タスクを予約しました : %s" )
ckit.strings.setString( "statusbar_open_failed",
    en_US = "Open failed : %s",
    ja_JP = "オープン失敗 : %s" )
ckit.strings.setString( "statusbar_switch_doc_failed",
    en_US = "Wwitching document failed : %s",
    ja_JP = "ドキュメント切り替え失敗 : %s" )
ckit.strings.setString( "statusbar_regex_wrong",
    en_US = "Regular expression [%s] is wrong.",
    ja_JP = "正規表現 [%s] に誤りがあります." )
ckit.strings.setString( "statusbar_aborted",
    en_US = "Aborted Task.",
    ja_JP = "タスクを中断しました." )
ckit.strings.setString( "statusbar_grep_finished",
    en_US = "Grep : found %d lines.",
    ja_JP = "Grep : %d 件ヒットしました." )
ckit.strings.setString( "statusbar_replace_finished",
    en_US = "Replace : Replaced %d places.",
    ja_JP = "Replace : %d 箇所置換しました." )
ckit.strings.setString( "statusbar_not_saved",
    en_US = "Not saved.",
    ja_JP = "ファイルが保存されていません." )
ckit.strings.setString( "statusbar_jump_failed",
    en_US = "Jump failed.",
    ja_JP = "ジャンプできません." )
ckit.strings.setString( "statusbar_symbol_not_found",
    en_US = "Symbol [%s] is not found.",
    ja_JP = "シンボル [%s] の定義位置が見つかりません." )
ckit.strings.setString( "statusbar_tags_generating",
    en_US = "Generating Tags.",
    ja_JP = "Tags ファイルを生成中." )
ckit.strings.setString( "statusbar_tags_generated",
    en_US = "Generated Tags.",
    ja_JP = "Tags ファイルを生成しました." )
ckit.strings.setString( "statusbar_tags_loading",
    en_US = "Loading Tags.",
    ja_JP = "Tags ロード中." )
ckit.strings.setString( "statusbar_tags_loaded",
    en_US = "Loaded Tags.",
    ja_JP = "Tags ファイルをロードしました." )
ckit.strings.setString( "statusbar_project_opened",
    en_US = "Opened project file : %s",
    ja_JP = "プロジェクトファイルをオープンしました : %s" )
ckit.strings.setString( "statusbar_project_closed",
    en_US = "Closed project file.",
    ja_JP = "プロジェクトファイルをクローズしました." )
    
ckit.strings.setString( "not_textfile",
    en_US = "Not a text file.",
    ja_JP = "テキストファイルではありません." )
ckit.strings.setString( "saving",
    en_US = "Saving...",
    ja_JP = "保存中..." )
ckit.strings.setString( "memory_statistics",
    en_US = "Memory Statistics",
    ja_JP = "メモリ統計情報" )
ckit.strings.setString( "config_reloaded",
    en_US = "Config file reloaded.",
    ja_JP = "設定スクリプトをリロードしました." )
ckit.strings.setString( "project_reloaded",
    en_US = "Project file reloaded.",
    ja_JP = "プロジェクトファイルをリロードしました." )
ckit.strings.setString( "help_opening",
    en_US = "Opening Help...",
    ja_JP = "Helpを起動" )
ckit.strings.setString( "project_not_opened",
    en_US = "Project is not opened.",
    ja_JP = "プロジェクトファイルがオープンされていません." )
ckit.strings.setString( "mode_not_found",
    en_US = "Mode [%s] is not found.",
    ja_JP = "モード [%s] が見つかりません." )
ckit.strings.setString( "mode_enabled",
    en_US = "Mode [%s] is enabled.",
    ja_JP = "モード [%s] を有効にしました." )
ckit.strings.setString( "mode_disabled",
    en_US = "Mode [%s] is disabled.",
    ja_JP = "モード [%s] を無効にしました." )

ckit.strings.setString( "error_prefix",
    en_US = "ERROR : ",
    ja_JP = "ERROR : " )
ckit.strings.setString( "error_already_exists",
    en_US = "ERROR : Already exists.",
    ja_JP = "ERROR : すでに存在しています." )
ckit.strings.setString( "error_ini_file_load_failed",
    en_US = "ERROR : loading INI file failed.",
    ja_JP = "ERROR : INIファイルの読み込み中にエラーが発生しました." )
ckit.strings.setString( "error_connection_failed",
    en_US = "ERROR : Connection failed : %s",
    ja_JP = "ERROR : 接続失敗 : %s" )
ckit.strings.setString( "error_open_failed",
    en_US = "ERROR : Open failed : %s",
    ja_JP = "ERROR : オープン失敗 : %s" )
ckit.strings.setString( "error_load_failed",
    en_US = "ERROR : Load failed : %s",
    ja_JP = "ERROR : ロード失敗 : %s" )
ckit.strings.setString( "error_out_of_memory",
    en_US = "ERROR : Out of memory : %s",
    ja_JP = "ERROR : メモリ不足 : %s" )
ckit.strings.setString( "error_invalid_wallpaper",
    en_US = "ERROR : Invalid wallpaper file : %s",
    ja_JP = "ERROR : 壁紙ファイルとして使用できない : %s" )
ckit.strings.setString( "error_unknown_parameter",
    en_US = "ERROR : Unknown parameter : %s",
    ja_JP = "ERROR : 不明なパラメタ : %s" )
ckit.strings.setString( "error_unknown_encoding",
    en_US = "ERROR : Unknown encording name : %s",
    ja_JP = "ERROR : 不明なエンコーディング名 : %s" )
ckit.strings.setString( "error_unknown_lineend",
    en_US = "ERROR : Unknown line end name : %s",
    ja_JP = "ERROR : 不明な改行コード : %s" )


def setLocale(locale):
    ckit.strings.setLocale(locale)

