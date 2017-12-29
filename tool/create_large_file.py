import json
import random

filesize = 5 * 1024 * 1024 * 1024 # 5GB

with open( "large.txt", "w" ) as fd:

    i = 0
    
    while True:
        
        d = {}
        d["index"] = i
        d["data"] = []
        for j in range(16):
            d2 = {}
            d2["a"] = random.random() * random.randint( 0, 10000 )
            d2["b"] = random.random() * random.randint( 0, 10000 )
            d2["c"] = random.random() * random.randint( 0, 10000 )
            d2["d"] = random.random() * random.randint( 0, 10000 )
            d["data"].append(d2)

        s = json.dumps(d)

        fd.write( s + "\n" )
        if fd.tell() >= filesize:
            break
        
        if i % 10000 == 0:
            print( "num lines = %d, file size=%d\n", i, fd.tell() )
        
        i+=1
