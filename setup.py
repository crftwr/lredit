import sys
import os
import fnmatch

sys.path[0:0] = [
    os.path.join( os.path.split(sys.argv[0])[0], ".." ),
    ]
 
import lredit_resource

from cx_Freeze import setup, Executable

executable = Executable( 
    script = "lredit_main.py",
    icon = "app.ico",
    base = "Win32GUI",
    targetName = "lredit.exe"
    )

options = {
    "build" : {
        "build_exe" : "dist/lredit",
    },

    "build_exe": {
        "optimize" : 2,
        
        "excludes" : [
            "tkinter",
            ],
        
        "includes" : [
            "lredit"
            ],
        
        "packages" : [
        ],
        "compressed" : 1,
        #"copy_dependent_files" : 1,
        #"create_shared_zip" : 1,
        #"append_script_to_exe" : 1,
        "include_files": [ 
            "bin",
            "dict",
            "extension",
            "license",
            "theme",
            "readme_en.txt",
            "readme_ja.txt",
            "migemo.dll",
            "_config.py",
            ( "doc/html", "doc" ),
            ],
        #"include_msvcr" : 1,
    },
}

setup( 
    name = "lredit",
    version = lredit_resource.lredit_version,
    description = "",
    executables = [executable],
    options = options,
    )

def fixup():
    
    exe_dirname = options["build"]["build_exe"]
    lib_dirname = os.path.join( exe_dirname, "lib" )
    
    if not os.path.exists(lib_dirname):
        os.mkdir(lib_dirname)
    
    for name in os.listdir(exe_dirname):
        if ( fnmatch.fnmatch(name,"*.dll") or fnmatch.fnmatch(name,"*.pyd") ) and not name=="python34.dll":
            old_path = os.path.join( exe_dirname, name )
            new_path = os.path.join( lib_dirname, name )

            print( "moving %s -> %s" % (old_path,new_path) )

            if os.path.exists(new_path):
                os.unlink(new_path)
            os.rename( old_path, new_path )

fixup()

