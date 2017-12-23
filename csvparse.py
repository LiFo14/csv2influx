#!/usr/bin/python3

import os
import sys
import csv
import threading
import queue
from pprint import pprint
from datetime import datetime
from influxdb import InfluxDBClient

AMOUNT_OF_THREADS = 7

class CSVParser():

    __slots__ = ['csv_dir', 'csv_files', 'db']

    def __init__(self, csv_dir = '/tmp/XPLSDATA/', csv_files=[]):
        self.csv_dir = csv_dir
        self.csv_files = csv_files[:]
        if len(self.csv_files)==0:
            for f in os.listdir(self.csv_dir):
                self.csv_files.append(f)
        self.db = DBManager()

    @property
    def files(self):
        return self.csv_files

    def parse_csv(self):
        for f in self.csv_files:
            with open(self.csv_dir + f) as csvfile:
                titles = csv.DictReader(csvfile).fieldnames
                reader = csv.reader(csvfile)
                point = {}
                for row in reader:
                    if len(row):
                        for title, value in zip(titles, row):
                            point[title] = value
                        data = self.make_influx_dict(point, f)
                        self.db.upload_data(data)

    def make_influx_dict(self, table_data, filename):
        parsingfile = filename.split('.')
        d = datetime.strptime(table_data['EndDateTime'],'%m/%d/%y %H:%M:%S')
        tags = {}
        with open('metrics') as f:
            for line in f:
                metrics_data = line.split(':') # Split every line by colon
                if metrics_data[0] == parsingfile[1]:
                    metrics = metrics_data[1].split(',') # Split metrics section by comma and add every metric to dict
                    for metric in metrics:
                        metric = metric.rstrip()
                        tags[metric.lower()] = table_data[metric]
        tags.update({'measurement': parsingfile[1], 'host': parsingfile[0]})
        data = [{
            'measurement': parsingfile[1],
            'time': d.strftime('%FT%H:%M:%S+0300'),
            'tags': tags,
            'fields': table_data,
        },]
        return data


class DBManager():

    __slots__ = ['influx_ip', 'influx_port', 'influx_name', 'influx_client']

    def __init__(self, influx_ip = 'localhost', influx_port = '8086', influx_name = 'test'):
        self.influx_ip = influx_ip
        self.influx_port = influx_port
        self.influx_name = influx_name
        self.influx_client = InfluxDBClient(influx_ip, influx_port, '', '', influx_name)
        if 'test' not in self.list_database:
            self.create_db('test')

    @property
    def list_database(self):
        return self.influx_client.get_list_database()

    @property
    def list_measurements(self):
        return self.influx_client.get_list_measurements()

    def upload_data(self, data):
        self.influx_client.write_points(data)
        
    def create_db(self, db_name):
        self.influx_client.create_database(db_name)

    def make_select(self, measurement = 'CPUPERF'):
        return self.influx_client.query('select * from {0};'.format(measurement))


class ThreadManager(threading.Thread):

    __slots__ = ['thread_id', 'parser']

    def __init__(self, thread_id, files):
        threading.Thread.__init__(self)
        self.thread_id = thread_id
        self.files = files
        self.parser = CSVParser(csv_files = self.files)

    def run(self):
        self.do_magic()

    def do_magic(self):
        print('Thread #', self.thread_id, ' started')
        self.parser.parse_csv() 
        print('Thread #', self.thread_id, ' done')
        

if __name__ == '__main__':
    def distribute_files(parser, thread_amount):
        files_per_thread = len(parser.files) // thread_amount # Even number of files per thread distribution
        extra =  len(parser.files) % thread_amount
        f_amount = {} 
        for i in zip(range(thread_amount), [files_per_thread for num in range(thread_amount)]):
            f_amount[i[0]] = int(i[1])
        if extra > 0: # Extra amount of files distribution
            for e in zip(range(thread_amount), str(1)*extra):
                f_amount[e[0]] = f_amount[e[0]] + int(e[1])
        files = parser.files[:]
        for i in range(len(f_amount)): # Replace distributed amount of files with filenames
            dict_index = f_amount[i]
            f_amount[i] = files[:f_amount[i]]
            del files[:dict_index]
        return f_amount

    distrib_files = distribute_files(CSVParser(), AMOUNT_OF_THREADS)    
    threads = []
    print('Threads total:',  AMOUNT_OF_THREADS)
    for a in zip(range(AMOUNT_OF_THREADS),distrib_files.values()):
        thr = ThreadManager(*a)
        thr.start()
        threads.append(thr)
    queue_lock = threading.Lock()
    work_queue = queue.Queue(AMOUNT_OF_THREADS)
    queue_lock.acquire()
    for t in threads:
        work_queue.put(t)
    queue_lock.release()
    #while not work_queue.empty():
    #    pass
    for t in threads:
        t.join()
    print('Done')
