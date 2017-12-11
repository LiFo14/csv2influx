#!/usr/bin/python3

import sys
import csv
import json
from datetime import datetime
from pprint import pprint
from influxdb import InfluxDBClient

HOSTNAME = "localhost" #ПЕРВАЯ ЧАСТЬ ДО ТОЧКИ

INFLUX_SERVER_IP = "localhost"
INFLUX_SERVER_DATABASE = "test"
INFLUX_SERVER_PORT = "8086"
INFLUX_MEASUREMENT_ID = "CPUPERF" #ВТОРАЯ ЧАСТЬ ДО .CSV

def make_influx_dict(table_data):
    d = datetime.strptime(table_data['EndDateTime'],'%m/%d/%y %H:%M:%S')
    data = [{
        "measurement": INFLUX_MEASUREMENT_ID,
        "tags": {
           "host": HOSTNAME
        },
        "time": d.strftime('%Y-%m-%dT%H:%m:%SZ'),
        "fields": table_data,
    },]
    return data

def upload_data(data):
    client = InfluxDBClient(INFLUX_SERVER_IP, INFLUX_SERVER_PORT, '', '', INFLUX_SERVER_DATABASE)
    client.write_points(data,database='test')
    #client.write(data)
    #pprint(client.query('SELECT * FROM CPUPERF', database='test'))

def read_csv(file):
    with open(file) as csvfile:
        titles = csv.DictReader(csvfile).fieldnames
        reader = csv.reader(csvfile)
        values = []
        point = {}
        for row in reader:
            if len(row):
                for title, value in zip(titles, row):
                    point[title] = value
                data = make_influx_dict(point)
                upload_data(data)

if __name__ == "__main__":
    read_csv(sys.argv[1])
