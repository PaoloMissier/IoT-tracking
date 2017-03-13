
import time
import datetime


def strToDT(ts):
    try:
        # datepicker format : 'mm/dd/yyyy hh:mm PM'
        dt = datetime.datetime.strptime(ts, '%m/%d/%Y %H:%M %p')
    except ValueError:
        dt = None
    except TypeError:
        dt = None
    return dt


def follow(thefile):
    thefile.seek(0,2)
    while True:
        line = thefile.readline()
        if not line:
            time.sleep(0.1)
            continue
        yield line


def openFile(path):
    logfile = open("run/foo/access-log","r")
    loglines = follow(logfile)
    for line in loglines:
        return line,
