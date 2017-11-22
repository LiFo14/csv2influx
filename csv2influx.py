#!/usr/bin/env python3

import os
import sys
import time
from datetime import datetime, timedelta
import urllib.request
import gzip
import csv

CURR_DATE=datetime.fromtimestamp(time.time()).strftime('%Y.%m.%d')
CURR_DATETIME=datetime.fromtimestamp(time.time()).strftime('%d%m%Y%H%M%S')
PREV_DATE = datetime.now() - timedelta(days=1)
METHOD='http://'
SERVER_ADDR='127.0.0.1' #insert address and path to file on the server
SERVER_PATH='/'+str(PREV_DATE.strftime('%Y.%m.%d'))+'/path/to/file/'

def download_archive():
    # Downloadable file is supposed to be compressed
  
    f_names = []
    for i in range(3, 6):
        f_names.append('xp7-'+str(i)+'mega_'+str(PREV_DATE.strftime('%Y-%m-%d'))+'_mod.perf.gz')
    for i in range(1, 3):
        f_names.append('xp7-'+str(i)+'croc2_'+str(PREV_DATE.strftime('%Y-%m-%d'))+'_mod.perf.gz')
    f_names.append('xp7-8rt_'+str(PREV_DATE.strftime('%Y-%m-%d'))+'_mod.perf.gz')
    downloaded_files = []
    for d_file in f_names:
        print('Downloading: ', METHOD+SERVER_ADDR+SERVER_PATH+d_file)
        downloaded_file, headers = urllib.request.urlretrieve(METHOD+SERVER_ADDR+SERVER_PATH+d_file)
        downloaded_files.append(downloaded_file)
        decompress(downloaded_file)
        os.remove(downloaded_file) if os.path.exists(downloaded_file) else None

def decompress(file):
    with gzip.open(file, 'rb') as gz_f:
        gz_content = gz_f.read()
        out_filename = '/tmp/'+CURR_DATETIME+'-data.csv'
        with open(out_filename, 'ab') as f:
            f.write(gz_content)
    print('Decompressed:\n',out_filename)
    export(out_filename)
    
def export(filename):
    pass

def show_csv_content(filename):
    with open(filename, newline='') as csvfile:
        reader = csv.reader(csvfile, delimiter=',', quoting=csv.QUOTE_NONE)
        for row in reader:
            print(row)

if __name__ == '__main__':
    if len(sys.argv) > 1:
        cli_arg = sys.argv[1]
        if cli_arg[-2:] == 'gz':
            decompress(cli_rg)
        elif 'csv' in cli_arg and 'gz' not in cli_arg:
            show_csv_content(cli_arg)
        elif cli_arg == 'net':
            download_archive()
    else:
        print('Usage: python3 csv2influx.py [CSV FILE]|[GZIP FILE]|net')
