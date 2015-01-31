# IRCMachine -- Python IRC Bot

IRCMachine is my own Python IRC bot made to help with development related channels.
This is a Python 2.7 version, although I could make a Py3 version.
It's based on [requests](http://docs.python-requests.org/en/latest/) and [irc](https://bitbucket.org/jaraco/irc) libs.

[Todo list is here.](https://github.com/s0r00t/IRCMachine/issues/1)

## Installation
After cloning, run those commands (you may need admin rights to run those) :
>pip install -r requirements.txt

## Usage

First, you must configure the bot via ircmachine.json. Check the wiki for help.
If IRCMachine fails to find a config file, it will download the one currently in the repo; please note it's not recommended to use it (right now it's just mine :P).
Then, run main.py with your favourite interpreter :
>python main.py

## Commands list

[Check this wiki page for commands list.](https://github.com/s0r00t/IRCMachine/wiki/Commands-list)
