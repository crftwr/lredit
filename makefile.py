import os
import sys
import subprocess
import shutil
import zipfile
import hashlib

sys.path[0:0] = [
    os.path.join( os.path.split(sys.argv[0])[0], '..' ),
    ]

import lredit_resource

DIST_DIR = "dist/lredit"
DIST_SRC_DIR = "dist/src"
VERSION = lredit_resource.lredit_version.replace(".","")
ARCHIVE_NAME = "lredit_%s.zip" % VERSION

PYTHON_DIR = "c:/python33"
PYTHON = PYTHON_DIR + "/python.exe"
SVN_DIR = "c:/Program Files/TortoiseSVN/bin"
DOXYGEN_DIR = "c:/Program Files/doxygen"

def unlink(filename):
    try:
        os.unlink(filename)
    except OSError:
        pass

def makedirs(dirname):
    try:
        os.makedirs(dirname)
    except OSError:
        pass

def rmtree(dirname):
    try:
        shutil.rmtree(dirname)
    except OSError:
        pass

def createZip( zip_filename, items ):
    z = zipfile.ZipFile( zip_filename, "w", zipfile.ZIP_DEFLATED, True )
    for item in items:
        if os.path.isdir(item):
            for root, dirs, files in os.walk(item):
                for f in files:
                    f = os.path.join(root,f)
                    print( f )
                    z.write(f)
        else:
            print( item )
            z.write(item)
    z.close()

DIST_FILES = [
    "lredit/lredit.exe",
    "lredit/lib",
    "lredit/bin",
    "lredit/python33.dll",
    "lredit/library.zip",
    "lredit/_config.py",
    "lredit/readme_ja.txt",
    "lredit/readme_en.txt",
    "lredit/theme/black",
    "lredit/theme/white",
    "lredit/license",
    "lredit/doc",
    "lredit/src.zip",
    "lredit/dict/.keepme",
    "lredit/extension/.keepme",
    ]

def all():
    doc()
    exe()

def exe():
    subprocess.call( [ PYTHON, "setup.py", "build" ] )

    if 1:
        rmtree( DIST_SRC_DIR )
        makedirs( DIST_SRC_DIR )
        os.chdir(DIST_SRC_DIR)
        subprocess.call( [ SVN_DIR + "/svn.exe", "export", "--force", "../../../ckit" ] )
        subprocess.call( [ SVN_DIR + "/svn.exe", "export", "--force", "../../../pyauto" ] )
        subprocess.call( [ SVN_DIR + "/svn.exe", "export", "--force", "../../../lredit" ] )
        os.chdir("..")
        createZip( "lredit/src.zip", [ "src" ] )
        os.chdir("..")

    if 1:
        os.chdir("dist")
        createZip( ARCHIVE_NAME, DIST_FILES )
        os.chdir("..")
    
    fd = open( "dist/%s" % ARCHIVE_NAME, "rb" )
    m = hashlib.md5()
    while 1:
        data = fd.read( 1024 * 1024 )
        if not data: break
        m.update(data)
    fd.close()
    print( "" )
    print( m.hexdigest() )

def clean():
    rmtree("dist")
    rmtree("build")
    rmtree("doc/html")
    unlink( "tags" )

def doc():
    rmtree( "doc/html" )
    makedirs( "doc/html" )
    subprocess.call( [ DOXYGEN_DIR + "/bin/doxygen.exe", "doc/doxyfile" ] )
    subprocess.call( [ PYTHON, "tool/rst2html_pygments.py", "--stylesheet=tool/rst2html_pygments.css", "doc/index.txt", "doc/html/index.html" ] )
    subprocess.call( [ PYTHON, "tool/rst2html_pygments.py", "--stylesheet=tool/rst2html_pygments.css", "doc/changes.txt", "doc/html/changes.html" ] )
    shutil.copytree( "doc/image", "doc/html/image", ignore=shutil.ignore_patterns(".svn","*.pdn") )

def run():
    subprocess.call( [ PYTHON, "lredit_main.py", "--multi" ] )

def debug():
    subprocess.call( [ PYTHON, "lredit_main.py", "--multi", "--debug" ] )

def debug_bigfile():
    subprocess.call( [ PYTHON, "lredit_main.py", "--multi", "--debug", "c:/Users/tom/Desktop/big_file.txt" ] )

def profile():
    subprocess.call( [ PYTHON, "lredit_main.py", "--multi", "--debug", "--profile" ] )

def profile_bigfile():
    subprocess.call( [ PYTHON, "lredit_main.py", "--multi", "--debug", "--profile", "--text", "c:/Users/tom/Desktop/big_file.txt", "2500000" ] )

if len(sys.argv)<=1:
    target = "all"
else:
    target = sys.argv[1]

eval( target + "()" )

