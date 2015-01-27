import irc
import json
import requests

def stLog(type, msg):
    if type in ["INFO","WARN","ERROR","FATAL"]:
        print("["+type+"] "+msg)
    else:
        print("[FATAL] Error while trying to log. Pretty paradoxal, isn't it?")

GHApi = "https://api.github.com"
GHRaw = "https://raw.githubusercontent.com"
cfgParsed = False

while cfgParsed != True:
    try:
        stLog("INFO","Parsing config file...")
        with open("ircmachine.json","r") as file:
            cfgJson = json.load(file)
        stLog("INFO","Config parsed.")
        cfgParsed = True
    except IOError:
        stLog("WARN","No config file found. Fetching latest one from repo...")
        cfgReq = requests.get(GHRaw+"/s0r00t/IRCMachine/master/ircmachine.json")
        with open("ircmachine.json","w") as file:
            file.write(cfgReq.text)
        stLog("INFO","Restarting config parse.")

stLog("INFO","IRCMachine started.")
stLog("INFO","Owner : "+cfgJson["owner"])
