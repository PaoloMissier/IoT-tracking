from src.utils import logger, db, tools
import time
import datetime
import pandas
log = logger.create_logger(__name__)

last_update_quarter = None
last_update_half = None
last_update_hour = None
last_update_day = None


def updateQuarter():
    global last_update_quarter
    session = None

    if last_update_quarter is None:
        log.info("last_update_quarter is None")
        session = db.connect()  # connect to database
        first_time = db.getMinTimestamp(session, "cnt")  # execute minTS
        if first_time is None:
            return False
        first_time = datetime.datetime(first_time.year,
                                       first_time.month,
                                       first_time.day,
                                       first_time.hour,
                                       15 * (first_time.minute // 15))
        # convert first time to local timestamp, because cassandra driver reads TS in UTC
        last_update_quarter = tools.toUSTZ(first_time)

    # If minTS is more than an hour, proceed updateQuarter
    if last_update_quarter.replace(tzinfo=None) + datetime.timedelta(hours=1) > datetime.datetime.now():
        log.info("last_update_quarter + 15mins is more than now (window not complete)")
        return False
    else:
        log.info("window complete, executing update quarter")

        if session is None:
            session = db.connect()  # connect to db

        rows = db.getJoinCnt(session, [last_update_quarter, last_update_quarter + datetime.timedelta(minutes=15)])

        df = pandas.DataFrame(rows)
        if not df.empty:
            df = df.groupby(['prodID', 'consID', 'topic']).size().reset_index()
            df = df.rename(columns={0: 'cnt'})

            insert_statement = session.prepare("INSERT INTO quarter_cnt (prodid, consid, topic, ts, cnt) "
                                               "VALUES (?, ?, ?, ?, ?)")
            print(last_update_quarter)
            db.insertCnt(session, insert_statement, df, tools.toUTC(last_update_quarter))  # insert as UTC time
            db.deleteFromCNT(session, [last_update_quarter, last_update_quarter + datetime.timedelta(minutes=15)])

        last_update_quarter = last_update_quarter + datetime.timedelta(minutes=15)
        return True


def updateHalf():
    global last_update_half
    session = None

    if last_update_half is None:
        log.info("last_update_half is None")
        session = db.connect()
        first_time = db.getMinTimestamp(session, "quarter_cnt")
        if first_time is None:
            return False
        first_time = datetime.datetime(first_time.year, first_time.month, first_time.day, first_time.hour,
                                       30 * (first_time.minute // 30))
        last_update_half = tools.toUSTZ(first_time)  # convert localize to UTC time

    # If minTS is more than 6 hours, proceed updateHalf
    if last_update_half.replace(tzinfo=None) + datetime.timedelta(hours=6) > datetime.datetime.now():
        log.info("last_update_half + 30mins is more than now (window not complete)")
        return False
    else:
        log.info("window complete, executing update half")
        if session is None:
            session = db.connect()  # connect to db
        rows = db.getJoinCntFromX(session, [last_update_half, last_update_half + datetime.timedelta(minutes=30), "quarter_cnt"])

        df = pandas.DataFrame(rows)
        if not df.empty:
            df = df.groupby(['prodID', 'consID', 'topic', 'ts']).sum().reset_index()
            insert_statement = session.prepare("INSERT INTO half_cnt (prodid, consid, topic, ts, cnt) "
                                               "VALUES (?, ?, ?, ?, ?)")
            db.insertCnt(session, insert_statement, df, tools.toUTC(last_update_half))  ## insert as UTC time
            db.deleteFromCNTX(session, [last_update_half, last_update_half + datetime.timedelta(minutes=30), "quarter_cnt"])

        last_update_half = last_update_half + datetime.timedelta(minutes=30)
        return True


def updateHour():
    global last_update_hour
    session = None

    if last_update_hour is None:
        log.info("last_update_hour is None")
        session = db.connect()
        first_time = db.getMinTimestamp(session, "half_cnt")
        if first_time is None:
            return False
        first_time = first_time.replace(microsecond=0, second=0, minute=0)
        last_update_hour = tools.toUSTZ(first_time)  # convert localize to UTC time

    # If minTS is more than 12 hours, proceed updateHour
    if last_update_hour.replace(tzinfo=None) + datetime.timedelta(hours=12) > datetime.datetime.now():
        log.info("last_update_hour + 1hour is more than now (window not complete)")
        return False
    else:
        log.info("window complete, executing last_update_hour")
        if session is None:
            session = db.connect()  # connect to db
        rows = db.getJoinCntFromX(session, [last_update_hour, last_update_hour + datetime.timedelta(hours=1), "half_cnt"])

        df = pandas.DataFrame(rows)
        if not df.empty:
            df = df.groupby(['prodID', 'consID', 'topic', 'ts']).sum().reset_index()
            insert_statement = session.prepare("INSERT INTO hour_cnt (prodid, consid, topic, ts, cnt) "
                                               "VALUES (?, ?, ?, ?, ?)")
            db.insertCnt(session, insert_statement, df, tools.toUTC(last_update_hour))  ## insert as UTC time
            db.deleteFromCNTX(session, [last_update_hour, last_update_hour + datetime.timedelta(hours=1), "half_cnt"])

        last_update_hour = last_update_hour + datetime.timedelta(hours=1)
        return True


def updateDay():
    global last_update_day
    session = None

    if last_update_day is None:
        log.info("last_update_day is None")
        session = db.connect()
        first_time = db.getMinTimestamp(session, "hour_cnt")
        if first_time is None:
            return False
        first_time = first_time.replace(hour=0, microsecond=0, second=0, minute=0)
        last_update_day = tools.toUSTZ(first_time)  # convert localize to UTC time

    if last_update_day.replace(tzinfo=None) + datetime.timedelta(days=2) > datetime.datetime.now():
        log.info("last_update_day + 1day is more than now (window not complete)")
        return False
    else:
        log.info("window complete, executing last_update_day")
        if session is None:
            session = db.connect()  # connect to db
        rows = db.getJoinCntFromX(session, [last_update_day, last_update_day + datetime.timedelta(days=1), "hour_cnt"])

        df = pandas.DataFrame(rows)
        if not df.empty:
            df = df.groupby(['prodID', 'consID', 'topic', 'ts']).sum().reset_index()
            print(df)
            insert_statement = session.prepare("INSERT INTO day_cnt (prodid, consid, topic, ts, cnt) "
                                               "VALUES (?, ?, ?, ?, ?)")
            db.insertCnt(session, insert_statement, df, tools.toUTC(last_update_day))  ## insert as UTC time
            db.deleteFromCNTX(session, [last_update_day, last_update_day + datetime.timedelta(days=1), "hour_cnt"])

        last_update_day = last_update_day + datetime.timedelta(days=1)
        return True


def main():
    global last_update_quarter, last_update_half, last_update_hour, last_update_day

    while True:

        if updateQuarter():
            log.info("Executed updateQuarter")
            continue

        if updateHalf():
            log.info("Executed updateHalf")
            continue

        if updateHour():
            log.info("Executed updateHour")
            continue

        if updateDay():
            log.info("Executed updateDay")
            continue

        log.info("Sleep 10mins")
        time.sleep(10 * 60)

if __name__ == '__main__':
   # main(sys.argv[1])
   main()