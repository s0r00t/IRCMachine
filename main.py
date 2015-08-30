import irc.bot
import json
import sys
import os
import time
import importlib

quiet = False
cmds = {}
#json fields that must be filled, else bot won't start
importantCFG = ["server","chans"]
#json fields that should be filled, but can have a default value (hence a dictionary)
optionalCFG = {"nick":"IRCMachine","cmd":":","autorejoin":True,"owner":"s0r00t"}

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

    def on_welcome(self, c, e):
        stLog("INFO","Connected!")
        for i in self.chans:
            c.join(i)
            stLog("INFO","Joining \'"+i+"\'...")
        
    def on_nicknameinuse(self, c, e):
        stLog("WARN","Nick in use. Using temporary one.")
        c.nick(c.get_nickname() + "_")
        
    def on_privmsg(self, c, e):
        self.runCmd(c, e, e.source.nick,True)

    def on_pubmsg(self, c, e):
        self.runCmd(c, e, e.target,False)

    def runExit(self, c):
        if not self.channels:
            stLog("INFO","Connected to no channels. Exiting.")
            stLog("INFO","IRCMachine stopped.")
        else:
            stLog("INFO","Leaving all channels.")
            for i in self.channels: c.leave(i)
            stLog("INFO","IRCMachine stopped.")
        sys.exit(0)

    def on_kick(self, c, e):
        if e.arguments[0] == self.cfgJson["nick"]:
            stLog("WARN","Kicked from '"+e.target+"' by "+e.source.nick+" with reason '"+e.arguments[1]+"'.")
            if self.cfgJson["autorejoin"]:
                stLog("INFO","Auto-rejoining '"+e.target+"'.")
                c.join(e.target)
            else: self.runExit(c)            

    def on_bannedfromchan(self, c, e):
        stLog("ERROR","Banned from '"+e.arguments[0]+"', unable to join.")
        if not self.channels:
            self.cfgJson["chans"].remove(e.arguments[0])
            if not self.cfgJson["chans"]:self.runExit(c)
        
    def on_mode(self, c, e):
        if e.arguments[1] and e.arguments[1] == self.cfgJson["nick"]:
            if self.cfgJson["nick"] in e.arguments[1]:
                if e.arguments[0] == '+b':
                    stLog("WARN","Ban applied by "+e.source.nick+".")
                elif e.arguments[0] == '-b':
                    stLog("INFO","Ban lifted by "+e.source.nick+".")
                elif e.arguments[0] == '+o':
                    stLog("INFO","Operator rights given by "+e.source.nick+".")
                elif e.arguments[0] == '-o':
                    stLog("WARN","Operator rights removed by "+e.source.nick+".")  
        
    def runCmd(self, c, e, dest, isPriv):
        if e.arguments[0].startswith(self.cfgJson["cmd"]):
            cmdArray = e.arguments[0].split(self.cfgJson["cmd"],1)[1].split(' ')
            if not cmdArray[0] in cmds:
                c.privmsg(dest, e.source.nick+": Command not found!")
                return
        
            #cmdArray[0] : command
            if isPriv:
                stLog("INFO","User "+e.source.nick+" sent command '"+cmdArray[0]+"' in private.")
            else:
                stLog("INFO","User "+e.source.nick+" sent command '"+cmdArray[0]+"'.")
            try:
                cmds[cmdArray.pop(0)].command(c,e,dest,cmdArray,isPriv)
            except Exception as ex:
                c.privmsg(dest, "Failed to run command, check output for more info")
                stLog("ERROR","Command '"+cmdArray[0]+"' failed with error "+str(type(ex).__name__)+": "+str(ex))
                
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
            #TODO : rewrite this horror
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
            try:
                cfgJson = json.load(file)
            except:
                stLog("FATAL","Config file is malformed. Aborting.")
                sys.exit(1)
        stLog("INFO","Config parsed.")
    except IOError:
        stLog("FATAL","No config file in '"+cfgPath+"'. Aborting.")
        sys.exit(1)
        
    for i in importantCFG:
        if not i in cfgJson:
            stLog("FATAL","No '"+i+"' field in the config file. IRCMachine cannot run without '"+i+"' field defined.")
            stLog("INFO","IRCMachine stopped.")
            sys.exit(1)
        else:
            if i != "chans": stLog("INFO","'"+i+"' : "+cfgJson[i])

    for i in optionalCFG:
        if not i in cfgJson:
            stLog("WARN","No '"+i+"' field, using default value.")
            cfgJson[i] = optionalCFG[i]
        stLog("INFO","'"+i+"' : "+str(cfgJson[i]))
            
    for i in os.listdir("cmds"):
        global cmds
        if os.path.isfile(os.path.join("cmds",i)) and i.endswith(".py") and os.path.splitext(i)[0] != "__init__":
            try:
                cmds[os.path.splitext(i)[0]] = importlib.import_module("cmds."+os.path.splitext(i)[0])
                stLog("INFO","Imported command '"+os.path.splitext(i)[0]+"'.")
            except Exception as e:
                stLog("ERROR","Importing command '"+os.path.splitext(i)[0]+"' failed with error "+str(type(e).__name__)+": "+str(e))

    stLog("INFO","IRCMachine started.")
    try:
        IRCMachine(cfgJson["chans"], cfgJson["nick"], cfgJson["server"],cfgJson).start()
    except UnicodeDecodeError:
        #TODO : find wtf is that error
        stLog("FATAL","Unknown error. Please restart IRCMachine.")

try:
    if __name__ == "__main__":
        main()
except KeyboardInterrupt: #^C
    stLog("FATAL","Force shutdown by operator.")
    sys.exit(1)
