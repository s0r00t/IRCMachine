import irc.bot
import json
import sys
import os
import time
import importlib

quiet = False
cmds = {}

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
        if not os.path.exists("logs"): os.makedirs("logs")
        with open("logs/"+time.strftime("%Y-%m-%d")+".log","a") as file:
            file.write("\n"+time.strftime("%H:%M:%S")+": ["+type+"] "+msg)
        print(time.strftime("%H:%M:%S")+": ["+type+"] "+msg)
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
        if cmds[cmdArray[0]]:
           cmds[cmdArray[0]].command(c,e,cmdArray, self.cfgJson)


    def on_welcome(self, c, e):
        stLog("INFO","Connected! Joining channels...")
        for i in self.chans:
            c.join(i)
            stLog("INFO","Joined \'"+i+"\'.")

def main():
    cfgPath = "ircmachine.json"
    #TODO : MORE ARGUMENTS
    for i in sys.argv[1:]:
        if i=="main.py":pass
        elif i == "-h":
            print("IRCMachine help\n-h: Show this message\n-q: Quiet mode (no INFO or WARN)\n-c <file>: use <file> as config file")
            sys.exit(1)
        elif i == "-q":
            global quiet
            quiet = True
        elif i == "-c":
            if not "ircmachine.json" in sys.argv[sys.argv.index(i)+1] and not os.path.isfile(sys.argv[sys.argv.index(i)+1]+"/ircmachine.json"):
                print("FATAL : The specified config file does not exists.")
                sys.exit(1)
            elif os.path.isfile(sys.argv[sys.argv.index(i)+1]+"/ircmachine.json"):
                cfgPath = sys.argv[sys.argv.index(i)+1]+"/ircmachine.json"
            else:
                cfgPath = sys.argv[sys.argv.index(i)+1]

    try:
        stLog("INFO","Parsing config file...")
        with open(cfgPath,"r") as file:
            cfgJson = json.load(file)
        stLog("INFO","Config parsed.")
    except IOError:
        stLog("FATAL","No config file in \'"+cfgPath+"\'.")
        stLog("INFO","IRCMachine stopped.")
    for i in ["nick","server"]:
        if not i in cfgJson:
            stLog("FATAL","No \'"+i+"\' field in the config file. IRCMachine cannot run without \'"+i+"\'   field defined.")
            stLog("INFO","IRCMachine stopped.")
            sys.exit(1)
        else:
            stLog("INFO","\'"+i+"\' : "+cfgJson[i])

    for i in os.listdir("cmds"):
        global cmds
        if os.path.isfile(os.path.join("cmds",i)) and i.endswith(".py") and os.path.splitext(i)[0] != "__init__":
            cmds[os.path.splitext(i)[0]] = importlib.import_module("cmds."+os.path.splitext(i)[0])
            stLog("INFO","Imported command '"+os.path.splitext(i)[0]+"'")

    stLog("INFO","IRCMachine started.")
    try:
        IRCMachine(cfgJson["chans"], cfgJson["nick"], cfgJson["server"],cfgJson).start()
    except UnicodeDecodeError:
        #TODO : find wtf is that error
        #seems to be a problem with clients
        stLog("FATAL","Unknown error. Please restart IRCMachine.")

if __name__ == "__main__":
    main()
