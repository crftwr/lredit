import random

filesize = 1024 * 1024 * 1024

with open( "large.txt", "w" ) as fd:
    while True:
        fd.write( "%d\n" % random.randint(0, 999999999999999999999999 ) )
        if fd.tell() >= filesize:
            break

