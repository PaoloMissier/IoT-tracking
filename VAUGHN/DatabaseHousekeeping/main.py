from src.utils import logger, db, tools
import time
import datetime
import pandas
log = logger.create_logger(__name__)

last_update_quarter = None
last_update_half = None
last_update_hour = None
last_update_day = None
session = None


def updateQuarter():
    global last_update_quarter, session

    # first time execution
    if last_update_quarter is None:
        log.info("last_update_quarter is None")

        if session is None:
            session = db.connect()  # connect to database
            if session is None:
                return False

        last_update_quarter = db.getMinTimestamp(session, "cnt")  # get minTS
        if last_update_quarter is None:
            return False
        last_update_quarter = datetime.datetime(last_update_quarter.year,
                                                last_update_quarter.month,
                                                last_update_quarter.day,
                                                last_update_quarter.hour,
                                                15 * (last_update_quarter.minute // 15))
        # convert first time to local timestamp, because cassandra driver reads TS in UTC
        # last_update_quarter = tools.toUSTZ(first_time) not required in VM (VM time is UTC)

    # 1 hour window not complete
    if last_update_quarter.replace(tzinfo=None) + datetime.timedelta(minutes=15) > datetime.datetime.now():
        log.info("1hour window not complete")
        return False

    # 1 hour window completed
    log.info("window complete, executing update quarter")
    if session is None:
        session = db.connect()  # connect to db
        if session is None:
            return False

    # get cubes
    rows = db.getJoinCnt(session, [last_update_quarter, last_update_quarter + datetime.timedelta(minutes=15)])
    if rows is None:  # None result means error
        return False

    # check empty result
    df = pandas.DataFrame(rows)
    if not df.empty:  # if empty change window run again
        df = df.groupby(['prodID', 'consID', 'topic']).size().reset_index()
        df = df.rename(columns={0: 'cnt'})

        if db.deleteFromCNT(session, [last_update_quarter, last_update_quarter + datetime.timedelta(minutes=15)]):
            insert_statement = session.prepare("INSERT INTO quarter_cnt (prodid, consid, topic, ts, cnt) "
                                               "VALUES (?, ?, ?, ?, ?)")
            db.insertCnt(session, insert_statement, df, last_update_quarter)
        else:
            tools.logfile("Delete at update quarter failed at {} : {}\n".format(last_update_quarter, last_update_quarter
                                                                                + datetime.timedelta(minutes=15)))

    last_update_quarter = last_update_quarter + datetime.timedelta(minutes=15)
    return True


def updateHalf():
    global last_update_half, session

    # first time execution
    if last_update_half is None:
        log.info("last_update_half is None")

        if session is None:
            session = db.connect()  # connect to database
            if session is None:
                return False

        last_update_half = db.getMinTimestamp(session, "quarter_cnt")
        if last_update_half is None:
            return False
        last_update_half = datetime.datetime(last_update_half.year,
                                             last_update_half.month,
                                             last_update_half.day,
                                             last_update_half.hour,
                                             30 * (last_update_half.minute // 30))
        # last_update_half = tools.toUSTZ(first_time)  # convert localize to UTC time VM doesnt need this

    # 6 hours window not complete
    if last_update_half.replace(tzinfo=None) + datetime.timedelta(hours=3) > datetime.datetime.now():
        log.info("6 hours window not complete")
        return False

    log.info("window complete, executing update half")
    if session is None:
        session = db.connect()  # connect to db
        if session is None:
            return False

    # get cubes
    rows = db.getJoinCntFromX(session, [last_update_half, last_update_half + datetime.timedelta(minutes=30),
                                        "quarter_cnt"])
    if rows is None:  # None means error
        return False

    # check empty result
    df = pandas.DataFrame(rows)
    if not df.empty:
        df = df.groupby(['prodID', 'consID', 'topic', 'ts']).sum().reset_index()

        if db.deleteFromCNTX(session, [last_update_half, last_update_half + datetime.timedelta(minutes=30),
                                       "quarter_cnt"]):
            insert_statement = session.prepare("INSERT INTO half_cnt (prodid, consid, topic, ts, cnt) "
                                               "VALUES (?, ?, ?, ?, ?)")
            db.insertCnt(session, insert_statement, df, last_update_half)
        else:
            tools.logfile("Delete at update half failed at {} : {} \n".format(last_update_half, last_update_half
                                                                              + datetime.timedelta(minutes=30)))

    last_update_half = last_update_half + datetime.timedelta(minutes=30)
    return True


def updateHour():
    global last_update_hour, session

    # first time execution
    if last_update_hour is None:
        log.info("last_update_hour is None")

        if session is None:
            session = db.connect()  # connect to database
            if session is None:
                return False

        last_update_hour = db.getMinTimestamp(session, "half_cnt")
        if last_update_hour is None:
            return False
        last_update_hour = last_update_hour.replace(microsecond=0, second=0, minute=0)
        # last_update_hour = tools.toUSTZ(first_time)  # convert localize to UTC time

    # 12 hours window not complete
    if last_update_hour.replace(tzinfo=None) + datetime.timedelta(hours=12) > datetime.datetime.now():
        log.info("12 hours window not complete")
        return False

    # 12 hours window completed
    log.info("window complete, executing last_update_hour")
    if session is None:
        session = db.connect()  # connect to db
        if session is None:
            return False

    # get cubes
    rows = db.getJoinCntFromX(session, [last_update_hour, last_update_hour + datetime.timedelta(hours=1), "half_cnt"])
    if rows is None: # None means error
        return False

    # check empty result
    df = pandas.DataFrame(rows)
    if not df.empty:  # if not empty
        df = df.groupby(['prodID', 'consID', 'topic', 'ts']).sum().reset_index()

        if db.deleteFromCNTX(session, [last_update_hour, last_update_hour + datetime.timedelta(hours=1), "half_cnt"]):
            insert_statement = session.prepare("INSERT INTO hour_cnt (prodid, consid, topic, ts, cnt) "
                                               "VALUES (?, ?, ?, ?, ?)")
            db.insertCnt(session, insert_statement, df, last_update_hour)
        else:
            tools.logfile("Delete at UpdateHour Failed {} : {}\n".format(last_update_hour, last_update_hour
                                                                         + datetime.timedelta(hours=1)))

    last_update_hour = last_update_hour + datetime.timedelta(hours=1)
    return True


def updateDay():
    global last_update_day, session

    # first time execution
    if last_update_day is None:
        log.info("last_update_day is None")

        if session is None:
            session = db.connect()  # connect to database
            if session is None:
                return False

        last_update_day = db.getMinTimestamp(session, "hour_cnt")
        if last_update_day is None:
            return False
        last_update_day = last_update_day.replace(hour=0, microsecond=0, second=0, minute=0)
        # last_update_day = tools.toUSTZ(first_time)  # convert localize to UTC time

    # 2 days window not complete
    if last_update_day.replace(tzinfo=None) + datetime.timedelta(days=1) > datetime.datetime.now():
        log.info("2 days window not complete")
        return False

    # 2 days window completed
    log.info("window complete, executing last_update_day")
    if session is None:
        session = db.connect()  # connect to db
        if session is None:
            return False

    # get cubes
    rows = db.getJoinCntFromX(session, [last_update_day, last_update_day + datetime.timedelta(hours=12), "hour_cnt"])
    if rows is None:  # None means error
        return False

    # check empty result
    df = pandas.DataFrame(rows)
    if not df.empty:
        df = df.groupby(['prodID', 'consID', 'topic', 'ts']).sum().reset_index()
        if db.deleteFromCNTX(session, [last_update_day, last_update_day + datetime.timedelta(hours=12), "hour_cnt"]):
            insert_statement = session.prepare("INSERT INTO day_cnt (prodid, consid, topic, ts, cnt) "
                                               "VALUES (?, ?, ?, ?, ?)")
            db.insertCnt(session, insert_statement, df, last_update_day)
        else:
            tools.logfile("Delete at update day failed at {} : {}\n".format(last_update_day, last_update_day +
                                                                            datetime.timedelta(hours=12)))

    last_update_day = last_update_day + datetime.timedelta(hours=12)
    return True


def main():
    global last_update_quarter, last_update_half, last_update_hour, last_update_day, session
    time.sleep(60)
    session = db.connect()
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

        log.info("Sleep")
        time.sleep(10 * 60)

if __name__ == '__main__':
    # main(sys.argv[1])
    main()
