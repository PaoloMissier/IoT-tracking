import mysql.connector
import pandas as pd
from dateutil.relativedelta import relativedelta
from mysql.connector import errorcode

from utils import logger

###
### periodically query the derived MSGCNT(MSG counter) table and extracts:
### for each window W and consumer C, the tuples (prod,topic, cnt) of msg cnt for each producer P and topic top
### updates a plot to show the msgcnt per topic and global (sum over all topics)
###

## QUERIES
MIN_MAX_TS_QUERY = "SELECT min(PROD.timestamp) as min, max(PROD.timestamp) as max " \
                   "FROM PROD JOIN CONS ON CONS.dataID=PROD.dataID"

CNT_QUERY = "SELECT PROD.prodID, CONS.consID, CONS.topic , count(*) as cnt " \
            "FROM PROD JOIN CONS ON CONS.dataID=PROD.dataID  " \
            "where CONS.timestamp between %s and %s " \
            "group by PROD.prodID, CONS.consID, CONS.topic"


CNT_QUERY_CLIENTS = "SELECT PROD.prodID, CONS.consID, CONS.topic , count(*) as cnt " \
            "FROM PROD JOIN CONS ON CONS.dataID=PROD.dataID  " \
            "where PROD.prodID=%s and CONS.consID=%s " \
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
        log.error(e)

    return pd.DataFrame(l)


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


def getJoinCntDFClients(pub, sub):

    params = [pub, sub]
    conn = DBConnect()
    cursor = conn.cursor()

    return getJoinCntDF(cursor, CNT_QUERY_CLIENTS, params)