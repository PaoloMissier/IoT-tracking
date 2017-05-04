
import time
import datetime
import pytz

user_tz = \
    pytz.timezone('Europe/London')


def toUSTZ(datetime):
    datetime = pytz.utc.localize(datetime)
    return datetime.astimezone(user_tz)
    # return timestamp_presented


def toUTC(d):
    return user_tz.normalize(d).astimezone(pytz.utc)


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
