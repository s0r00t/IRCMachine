import irc.bot
import json
import requests
import sys
from fncts import *

class IRCMachine(irc.bot.SingleServerIRCBot):
    def __init__(self, chans, nick, server, port=6667):
        irc.bot.SingleServerIRCBot.__init__(self, [(server, port)], nick, nick)
        self.chans = chans

    def on_nicknameinuse(self, c, e):
        stLog("WARN","Nick in use. Using temp one.")
        c.nick(c.get_nickname() + "_")

    def on_welcome(self, c, e):
        stLog("INFO","Connected! Joining channels...")
        for i in self.chans:
            c.join(i)

def main():
    GHApi = "https://api.github.com"
    GHRaw = "https://raw.githubusercontent.com"
    #to gen token : https://github.com/settings/tokens/new
    #use public_repo and gist
    cfgJson = None
    while cfgJson is None:
        try:
            stLog("INFO","Parsing config file...")
            with open("ircmachine.json","r") as file:
                cfgJson = json.load(file)
            stLog("INFO","Config parsed.")
        except IOError:
            stLog("WARN","No config file found. Fetching latest one from repo...")
            cfgReq = requests.get(GHRaw+"/s0r00t/IRCMachine/master/ircmachine.json")
            with open("ircmachine.json","w") as file:
                file.write(cfgReq.text)
            stLog("INFO","Restarting config parse.")

    stLog("INFO","IRCMachine started.")
    #TODO : this is the check for important fields. ADD MORE FIELDS
    for i in ["nick","server"]:
        if not i in cfgJson:
            stLog("FATAL","No \'"+i+"\' field in the config file. IRCMachine cannot run without \'"+i+"\'   field defined.")
            stLog("INFO","IRCMachine stopped.")
            sys.exit(1)
        else:
            stLog("INFO","\'"+i+"\' : "+cfgJson[i])

    bot = IRCMachine(cfgJson["chans"], cfgJson["nick"], cfgJson["server"])
    bot.start()

if __name__ == "__main__":
    main()
