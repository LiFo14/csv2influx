#!/usr/bin/env python3

import sys
import time
import datetime
import gzip
import csv


def main(filename, type):
    if type == 'gz':
        with gzip.open(filename, 'rb') as gz_f:
            gz_content = gz_f.read()
            out_filename = datetime.datetime.fromtimestamp(time.time()).strftime    ('%d%m%Y%H%M%S')+'-data.csv'
            with open(out_filename, 'wb') as f:
                f.write(gz_content)
    else:
        with open(filename, newline='') as csvfile:
            reader = csv.reader(csvfile, delimiter=',', quoting=csv.QUOTE_NONE)
            for row in reader:
                print(row)

if __name__ == '__main__':
    # Add first line skip support
    if len(sys.argv) > 1:
        filename = sys.argv[1]
        if filename[-2:] == 'gz':
            main(filename, 'gz')
        elif 'csv' in filename and 'gz' not in filename:
            main(filename, 'csv')
    else:
        print('Usage: ./csv2influx.py [CSV FILE]|[GZIP FILE]')
