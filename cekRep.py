import requests
import sys, re, os, json
import docker
from subprocess import Popen, PIPE, STDOUT
import socket
from datetime import datetime, timedelta

global data
data = {}
client = docker.from_env()

def check_rep(name):
    since_time = datetime.now() - timedelta(days=1)
    print("Checking "+name+" container")
    dkg = client.containers.get(name).logs(stream = True, follow = False, since=since_time, timestamps=True)
    try:
        list_rep_found = 0
        while True:
            line = next(dkg).decode("utf-8")
            if "INFO:root:Building a spot-data transaction" in line:
                tail = line.split("(")
                list_rep_found += int(re.findall(r'\d+', tail[1])[0])
                data[name] = list_rep_found
    except StopIteration:
        print(f'log stream ended for '+name)   


get_con = client.containers.list(filters={"status":"running", "name":"exorde"})
for con in get_con:
    check_rep(con.name)
print(data)
