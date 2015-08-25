#GitHub command
#by s0r00t
import requests
from main import stLog

def command(c,e,args,json):
    if json['gh-token']:
        stLog("INFO","Using GitHub token to connect to the API...")
        GHApiLog = requests.get('https://api.github.com/user', auth=(json['gh-token'], 'x-oauth-basic'))
    else:
        stLog("WARN","No GitHub token provided. There may be limitations when using GitHub API.")

    if GHApiLog.status_code == 200:
        stLog("INFO","Logged to GitHub API!")
    else:
        stLog("WARN","Failed to log into GitHub API. Perhaps the token is not working?")
