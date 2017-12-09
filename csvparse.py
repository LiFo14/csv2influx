#!/usr/bin/python3

from influxdb import InfluxDBClient
import sys
import csv
import json
import pprint

HOSTNAME = "localhost" #ПЕРВАЯ ЧАСТЬ ДО ТОЧКИ
MEASUREMENT = "CPUPERF" #ВТОРАЯ ЧАСТЬ ДО .CSV

INFLUX_SERVER_IP = "localhost"
INFLUX_SERVER_DATABASE = "test"
INFLUX_SERVER_PORT = "8086"
INFLUX_MEASUREMENT_ID = MEASUREMENT

def make_influx_dict(table_data):
    data = [{
        "measurement": MEASUREMENT,
        "tags": {
           "host": HOSTNAME
         },
        "fields": table_data,
    },]
    return data

def read_csv(file):
    with open(file) as csvfile:
        titles = csv.DictReader(csvfile).fieldnames
        reader = csv.reader(csvfile)
        values = []
        point = {}
        for value in zip(*reader):
            values.append(','.join(value))
        for title, value in zip(titles, values):
            point[title] = value
        return make_influx_dict(point)

if __name__ == "__main__":
    data = read_csv(sys.argv[1])
    pprint.pprint(data)
    influxclient = InfluxDBClient(INFLUX_SERVER_IP, INFLUX_SERVER_PORT, '', '', INFLUX_SERVER_DATABASE)
    influxclient.write_points(data,database='test') 
