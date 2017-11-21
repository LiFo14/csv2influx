#!/usr/bin/env python3

import sys
import time
import datetime  
import gzip

def ungzip(gz_file):
    with gzip.open(gz_file, 'rb') as gz_f:
        gz_content = gz_f.read()
        out_filename = datetime.datetime.fromtimestamp(time.time()).strftime('%d%m%Y%H%M%S')+'-data.csv'
        with open(out_filename, 'wb') as f:
            f.write(gz_content)
 
if __name__=='__main__': 
    if len(sys.argv) == 2:
        ungzip(sys.argv[1])
    else:
        print('Usage: python3 ungzip.py [GZIP FILE]')   
