
import datetime
from src.utils import logger, tools, db
import pandas

log = logger.create_logger(__name__)

last_update_half = None

def test():

    now = datetime.datetime.now()

    now = now.replace(hour=0, microsecond=0, second=0, minute=0)

    print(now)

    return



def code():
    print("x\n")
    global last_update_half
    session = None

    if last_update_half is None:
        log.info("last_update_half is None")
        session = db.connect()
        first_time = db.getMinTimestamp(session, "quarter")
        first_time = datetime.datetime(first_time.year, first_time.month, first_time.day, first_time.hour,
                                       30 * (first_time.minute // 30))
        last_update_half = tools.toUSTZ(first_time) # convert localize to UTC time

    if last_update_half.replace(tzinfo=None) + datetime.timedelta(minutes=30) > datetime.datetime.now():
        log.info("last_update_quarter + 30mins is more than now (window not complete)")
        return False
    else:
        log.info("window complete, executing update half")
        if session is None:
            session = db.connect()  # connect to db
        rows = db.getJoinCntFromX(session, [last_update_half, last_update_half + datetime.timedelta(minutes=30), "quarter"])

        df = pandas.DataFrame(rows)
        if not df.empty:
            df = df.groupby(['prodID', 'consID', 'topic', 'ts']).sum().reset_index()
            print(df)
            insert_statement = session.prepare("INSERT INTO half (prodid, consid, topic, ts, cnt) "
                                               "VALUES (?, ?, ?, ?, ?)")
            db.insertCnt(session, insert_statement, df, tools.toUTC(last_update_half))  ## insert as UTC time
            # db.deleteFromCNT(session, [last_update_half, last_update_half + datetime.timedelta(minutes=15)])

        # last_update_half = last_update_half + datetime.timedelta(minutes=15)
        return True

if __name__ == '__main__':
    # main(sys.argv[1]) #bring in ipaddress of the broker
    code()
