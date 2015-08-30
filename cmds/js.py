#JS minifier
#by s0r00t, based on jsmin
#pip install jsmin
from jsmin import jsmin

def command(c,e,s,args,iP):
    if "".join(args) == "":
        c.privmsg(s, e.source.nick+": No JS to minify!")
        return
    c.privmsg(s, e.source.nick+": "+jsmin("".join(args)))
