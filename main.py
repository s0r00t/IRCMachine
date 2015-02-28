#! /usr/bin/env python
import irc.bot
import json
import requests
import sys
import os

quiet = False

class LogError(Exception):pass

def stLog(type, msg):
    """
    Logs information to OP via STDOUT.
    INFO : Normal text
    WARN : Problem
    ERROR : Important problem but can be fixed
    FATAL : Important problem but cannot be fixed
    """

    if type in ["INFO","WARN","ERROR","FATAL"] and not quiet:
        print("["+type+"] "+msg)
    elif type in ["INFO","WARN"] and quiet:pass
    else:
        raise LogError("Failed logging message '"+msg+"'.")


class IRCMachine(irc.bot.SingleServerIRCBot):
    def __init__(self, chans, nick, server, cfgJson, port=6667):
        irc.bot.SingleServerIRCBot.__init__(self, [(server, port)], nick, nick)
        self.chans = chans
        self.cfgJson = cfgJson

    def on_nicknameinuse(self, c, e):
        stLog("WARN","Nick in use. Using temp one.")
        c.nick(c.get_nickname() + "_")

    def on_pubmsg(self, c, e):
        if e.arguments[0].startswith(self.cfgJson["cmd"]):
            self.runCmd(e.arguments[0].split(self.cfgJson["cmd"],1)[1].split(' '),e)

    def runCmd(self,cmdArray,e):
        #cmdArray[0] : command
        #cmdArray[>0] : arg
        stLog("INFO","User '"+e.source.nick+"' sent command '"+cmdArray[0]+"'.")
        c = self.connection
        if cmdArray[0] == "hello":
            c.privmsg(e.target,"Hello World from "+e.source.nick+"!")


    def on_welcome(self, c, e):
        stLog("INFO","Connected! Joining channels...")
        for i in self.chans:
            c.join(i)
            stLog("INFO","Joined \'"+i+"\'.")
        #TODO : DO SOMETHING WITH THAT API
        if 'argToken' in globals():
            stLog("INFO","Using GitHub token to connect to the API...")
            GHApiLog = requests.get('https://api.github.com/user', auth=(argToken, 'x-oauth-basic'))
        elif self.cfgJson['gh-token']:
            stLog("INFO","Using GitHub token to connect to the API...")
            GHApiLog = requests.get('https://api.github.com/user', auth=(self.cfgJson['gh-token'], 'x-oauth-basic'))
        else:
            stLog("WARN","No GitHub token provided. There may be limitations when using GitHub API.")

        if GHApiLog.status_code == 200:
            stLog("INFO","Logged to GitHub API!")
        else:
            stLog("WARN","Failed to log into GitHub API. Perhaps the token is not working?")

def main():
    cfgPath = "ircmachine.json"
    #TODO : MORE ARGUMENTS
    for i in sys.argv[1:]:
        if i=="main.py":pass
        elif i == "-h":
            print("IRCMachine help\n-h: Show this message\n-q: Quiet mode (no INFO or WARN)\n-c <file>: use <file> as config file\n-t <token>: use <token> as GitHub API token")
            sys.exit(1)
        elif i == "-q":
            quiet = True
        elif i == "-c":
            if not "ircmachine.json" in sys.argv[sys.argv.index(i)+1] and not os.path.isfile(sys.argv[sys.argv.index(i)+1]+"/ircmachine.json"):
                print("FATAL : The specified config file does not exists.")
                sys.exit(1)
            elif os.path.isfile(sys.argv[sys.argv.index(i)+1]+"/ircmachine.json"):
                cfgPath = sys.argv[sys.argv.index(i)+1]+"/ircmachine.json"
            else:
                cfgPath = sys.argv[sys.argv.index(i)+1]
        elif i == "-t":
            global argToken
            argToken = sys.argv[sys.argv.index(i)+1]

    cfgJson = None
    while cfgJson == None:
        try:
            stLog("INFO","Parsing config file...")
            with open(cfgPath,"r") as file:
                cfgJson = json.load(file)
            stLog("INFO","Config parsed.")
        except IOError:
            stLog("ERROR","No config file found. Fetching latest one from repo...")
            cfgReq = requests.get("https://raw.githubusercontent.com/s0r00t/IRCMachine/master/ircmachine.json")
            with open("ircmachine.json","w") as file:
                file.write(cfgReq.text)
            cfgPath = "ircmachine.json"
            stLog("INFO","Restarting config parse.")

    #TODO : this is the check for important fields. ADD MORE FIELDS
    for i in ["nick","server"]:
        if not i in cfgJson:
            stLog("FATAL","No \'"+i+"\' field in the config file. IRCMachine cannot run without \'"+i+"\'   field defined.")
            stLog("INFO","IRCMachine stopped.")
            sys.exit(1)
        else:
            stLog("INFO","\'"+i+"\' : "+cfgJson[i])

    stLog("INFO","IRCMachine started.")
    try:
        IRCMachine(cfgJson["chans"], cfgJson["nick"], cfgJson["server"],cfgJson).start()
    except UnicodeDecodeError:
        #TODO : find wtf is that error
        #seems to be a problem with clients
        stLog("FATAL","Unknown error. Please restart IRCMachine.")

if __name__ == "__main__":
    main()
