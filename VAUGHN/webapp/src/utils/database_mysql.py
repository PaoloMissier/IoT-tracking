import mysql.connector
from mysql.connector import errorcode
from . import logger
from dateutil.relativedelta import relativedelta
import pandas as pd


########################################################################################
### THIS FILE IS FOR REFERENCE / MARKING ONLY (VERSION 1 MOSQUITTO BROKER MYSQL) #######
##################### THIS FILE IS NOT NEEDED ANYMORE  #################################
########################################################################################

## QUERIES
MIN_MAX_TS_QUERY = "SELECT min(PROD.timestamp) as min, max(PROD.timestamp) as max " \
                   "FROM PROD JOIN CONS ON CONS.dataID=PROD.dataID"

CNT_QUERY = "SELECT PROD.prodID, CONS.consID, CONS.topic , count(*) as cnt " \
            "FROM PROD JOIN CONS ON CONS.dataID=PROD.dataID  " \
            "where CONS.timestamp between %s and %s " \
            "group by PROD.prodID, CONS.consID, CONS.topic"

# DB constants
DB_USER = "vaughn"
DB_PW = "zxczxczxc"
DB_HOST = "localhost"
DB_NAME = 'BrokerTracker'

log = logger.create_logger(__name__)


def DBConnect():
    try:
        cnx = mysql.connector.connect(user=DB_USER, password=DB_PW, host=DB_HOST,
                                      database=DB_NAME)
        log.info("DB connected successfully")
        logger.log_newline(log)
        return cnx  # returns connection object
    except mysql.connector.Error as err:
        if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
            log.error("Something is wrong with your user name or password")
            logger.log_newline(log)
        elif err.errno == errorcode.ER_BAD_DB_ERROR:
            log.error("Database does not exist")
            logger.log_newline(log)
        else:
            log.error(err)
            logger.log_newline(log)


def getMinMax(cursor):
    try:
        cursor.execute(MIN_MAX_TS_QUERY)
        row = cursor.fetchone()
        if row is not None:
            log.info(row)
            return row[0], row[1]

    except mysql.connector.Error as e:
        print(e)


def getJoinCntDF(cursor, query, params):
    l = list()
    try:
        cursor.execute(query, (params[0], params[1]))
        for (prodID, consID, topic, cnt) in cursor:
            # create a dict
            d = {'prodID': prodID, 'consID': consID, 'topic': topic, 'cnt': cnt}
            l.append(d)
            log.info("cnt: {}, {}, {}, {}".format(prodID, consID, topic, cnt))

    except mysql.connector.Error as e:
        print(e)

    return pd.DataFrame(l)


# blocks if not enough records in the next window
def getNextWindow(cursor, fromTS, maxTS, interval):
    while True:
        if maxTS is None:
            _, maxTS = getMinMax(cursor)  # get current latest timestamp

            log.info("available window size: {}".format(maxTS - fromTS))
        soughtMaxTS = fromTS + relativedelta(seconds=interval)
        if soughtMaxTS <= maxTS:
            log.info("next window is complete. From {} to {}".format(fromTS, soughtMaxTS))
            return soughtMaxTS
        else:
            return fromTS


def getTopics():
    l = []
    db = DBConnect()
    cursor = db.cursor()
    QUERY = "SELECT DISTINCT CONS.topic FROM PROD JOIN CONS ON CONS.dataID=PROD.dataID " \
            "group by PROD.prodID, CONS.consID, CONS.topic"
    cursor.execute(QUERY)
    for row in cursor:
        l.append(row[0])
    return l


def getSubscribers():
    l = []
    db = DBConnect()
    cursor = db.cursor()
    QUERY = "SELECT DISTINCT CONS.consID FROM PROD JOIN CONS ON CONS.dataID=PROD.dataID " \
            "group by PROD.prodID, CONS.consID, CONS.topic"
    cursor.execute(QUERY)
    for row in cursor:
        l.append(row[0])
    return l


def getPublisher():
    l = []
    db = DBConnect()
    cursor = db.cursor()
    QUERY = "SELECT DISTINCT PROD.prodID FROM PROD JOIN CONS ON CONS.dataID=PROD.dataID " \
            "group by PROD.prodID, CONS.consID, CONS.topic"
    cursor.execute(QUERY)
    for row in cursor:
        l.append(row[0])
    return l



