import requests
import sys, re, os, json
import docker
from subprocess import Popen, PIPE, STDOUT
import socket


client = docker.from_env()

def send_to_telegram(message, urgent = False):
    token = '6510035307:AAHNzrejYAXZlq4J5aETtSaXWGyv__U-1xo'
    if urgent:
        token = '6916180331:AAEKuNRQiiVj2RK6D8DC4Hqa_AuXFJU-C0I'
    apiURL = 'https://api.telegram.org/bot'+token+'/sendMessage'
    try:
        requests.post(apiURL, json={'chat_id': 441913881, 'text': message})
    except Exception as e:
        print(e)


def check_rep(name, file):
    host = socket.gethostname()
    tw_mail = ""
    isLocked = False
    print("Checking "+name+" container")
    dkg = client.containers.get(name).logs(stream = True, follow = False, tail=500)
    try:
        list_rep_found = []
        while True:
            line = next(dkg).decode("utf-8")
            if "INFO:root:        twitter" in line:
                tail = line.split("|")
                list_rep_found.append(tail[-1])
            if "[Twitter] Email provided =" in line:
                tail = line.split("=")
                tw_mail = tail[-1]
            if "https://twitter.com/account/access" in line:
                isLocked = True
                break
            
    except StopIteration:
        print(f'log stream ended for '+name)   

    totrep = list_rep_found[-1].replace(" ","")
    with open(file, 'r') as openfile:
        json_object = json.load(openfile)
    
    if isLocked:
        send_to_telegram("Your twitter account "+str(tw_mail)+" is locked. please remote desktop and try to login", True)
        return "Your twitter account "+str(tw_mail)+" is locked"
    else:
        if totrep != json_object["rep"]:
            dictionary = {
                "rep": totrep
            }
            with open(file, "w") as outfile:
                json.dump(dictionary, outfile)
            
            return "["+str(host)+"] ["+name+"] "+str(tw_mail)+": "+str(totrep)
        else:
            send_to_telegram("Total rep from "+str(host)+" server ["+name+"] "+str(tw_mail)+" rate limited, change container: "+str(totrep), True)
            return str(host)+" server ["+name+"] rate limited"
    

data = {"exorde1":"rep1.json","exorde2":"rep2.json"}
message = ""
for x,y in data.items():
    message += check_rep(x,y)

send_to_telegram(message)