class LogError(Exception):
    pass


def stLog(type, msg):
    """
    Logs information to OP via STDOUT.
    INFO : Normal text
    WARN : Problem
    ERROR : Important problem but can be fixed
    FATAL : Important problem but cannot be fixed
    """

    if type in ["INFO","WARN","ERROR","FATAL"]:
        print("["+type+"] "+msg)
    else:
        raise LogError("Failed logging message '"+msg+"'.")
