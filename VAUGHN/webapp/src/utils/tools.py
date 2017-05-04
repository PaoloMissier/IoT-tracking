
import time
import datetime


def strToDT(ts):
    try:
        # datepicker format : 'mm/dd/yyyy hh:mm PM'
        dt = datetime.datetime.strptime(ts,'%m/%d/%Y %I:%M %p')
    except ValueError:
        dt = None
    except TypeError:
        dt = None
    return dt


def dtToStr(dt):
    return dt.strftime('%m/%d/%Y %H:%M %p')
