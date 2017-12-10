import os
import re
import fnmatch

import ckit

import lredit_resource


def grep( job_item, enum_files, pattern, word=False, case=False, regex=False, found_handler=None ):

    if regex:
        if word:
            re_pattern = r"\b" + pattern + r"\b"
        else:
            re_pattern = pattern
    else:
        re_pattern = ""
        for c in pattern:
            if c in "\\[]":
                c = "\\" + c;
            re_pattern += "[" + c + "]"

        if word:
            re_pattern = r"\b" + re_pattern + r"\b"

    re_option = re.UNICODE
    if not case:
        re_option |= re.IGNORECASE

    re_object = re.compile( re_pattern, re_option )

    for fullpath in enum_files():

        if job_item.isCanceled(): break
        
        try:
            fd = open( fullpath, "rb" )

            try:
                
                # FIXME : 巨大ファイルに対応するべき
            
                data = fd.read()
            
                encoding = ckit.detectTextEncoding( data, ascii_as="utf-8" )
                if encoding.bom:
                    data = data[ len(encoding.bom) : ]

                if encoding.encoding:
                    data = data.decode( encoding=encoding.encoding, errors='replace' )
                else:
                    # FIXME : バイナリでも検索する
                    continue
    
                lines = data.splitlines(True)

                lineno = 1
                for line in lines:
                    if job_item.isCanceled(): break
                    if re_object.search(line):
                        found_handler( fullpath, lineno-1, line )
                    lineno += 1

            finally:
                fd.close()
        
        except MemoryError as e:
            print( ckit.strings["error_out_of_memory"] % fullpath )
        
        except IOError as e:
            print( "  %s" % str(e) )

    if job_item.isCanceled():
        print( ckit.strings["common_aborted"] )
    else:
        print( ckit.strings["common_done"] )

