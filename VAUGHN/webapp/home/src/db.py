import mysql.connector
from mysql.connector import errorcode
from . import logger
from dateutil.relativedelta import relativedelta
import pandas as pd

###
### periodically query the derived MSGCNT(MSG counter) table and extracts:
### for each window W and consumer C, the tuples (prod,topic, cnt) of msg cnt for each producer P and topic top
### updates a plot to show the msgcnt per topic and global (sum over all topics)
###

## QUERIES
MIN_MAX_TS_QUERY = "SELECT min(PROD.timestamp) as min, max(PROD.timestamp) as max " \
                   "FROM PROD JOIN CONS ON CONS.dataID=PROD.dataID"
CNT_QUERY = "SELECT PROD.prodID, CONS.consID, CONS.topic , count(*) as cnt FROM PROD JOIN CONS ON CONS.dataID=PROD.dataID  " \
            "where CONS.timestamp between %s and %s group by PROD.prodID, CONS.consID, CONS.topic"

# DB constants
DB_USER = "root"
DB_PW = ""
DB_HOST = "localhost"
DB_NAME = 'BrokerTracker'

TOPIC_ROOT = "root/temperature/ext"
REPLOT_INTERVAL = 3600  # sec

log = logger.create_logger(__name__)


def DBConnect():
    # init DB connection and acquire context
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


def DB_MinMax(cursor):
    try:
        cursor.execute(MIN_MAX_TS_QUERY)
        row = cursor.fetchone()
        if row is not None:
            log.info(row)
            return row[0], row[1]

    except mysql.connector.Error as e:
        print(e)


def DBRead(cursor, query, params):
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
            _, maxTS = DB_MinMax(cursor)  # get current latest timestamp

            log.info("available window size: {}".format(maxTS - fromTS))
        soughtMaxTS = fromTS + relativedelta(seconds=interval)
        if soughtMaxTS <= maxTS:
            log.info("next window is complete. From {} to {}".format(fromTS, soughtMaxTS))
            return soughtMaxTS
        else:
            return fromTS
            # logger.info(
            #     "next window is Incomplete. From {} to {} but max is {}".format(fromTS, soughtMaxTS, maxTS))
            # time.sleep(REPLOT_INTERVAL)


def generatePlotGrid(minTS=None, maxTS=None, interval=None, cursor=None):

    # create a copy of maxTS
    tempMaxTS = maxTS

    if interval is None:
        # if no interval given, set default value
        interval = REPLOT_INTERVAL

    if cursor is None:
        db = DBConnect()
        cursor = db.cursor()

    if minTS is None and maxTS is None:
        # find min and max timestamps if none given -- this is the largest window we can turn into a counter cube
        minTS, maxTS = DB_MinMax(cursor)

    if minTS is None:
        # if minTS not given
        minTS, _ = DB_MinMax(cursor)
        print(minTS)

    allPlots = list()

    while True:

        log.info("window: [{},{}]".format(minTS, maxTS))

        if tempMaxTS is getNextWindow(cursor, minTS, maxTS, interval):
            break
        else:
            tempMaxTS = getNextWindow(cursor, minTS, maxTS, interval)

        df = DBRead(cursor, CNT_QUERY, [minTS, tempMaxTS])
        log.info("loaded df with {}  records".format(len(df)))

        if len(df) == 0:  # prevent error for df to check
            minTS = tempMaxTS
            continue

        # count number of producers  and consumers
        prodCnt = len(df.groupby(['prodID']))
        consCnt = len(df.groupby(['consID']))
        log.info("{} prod, {} cons".format(prodCnt, consCnt))

        maxCnt = 0  # scale of Y axis is calibrated on max cnt across all groups
        allTopics = list()  # x ticks common to all plots
        maxConsCnt = 0

        gByProd = df.groupby('prodID')  # groups with same (prod, cons)

        plotGrid = list()  # of lists
        i = 0
        for prodID, prodDF in gByProd:

            gByCons = prodDF.groupby('consID')

            plotGrid.append(list())  # row of cells

            plotRow = plotGrid[i]
            j = 0
            for consID, consDF in gByCons:

                # remove the index from the DF (??)
                cnt = [cnt for cnt in consDF['cnt']]  # cnt are the values plotted on the bar
                topics = [topics for topics in consDF['topic']]

                # set maxCnt for all the graph
                m = max(cnt)
                if m > maxCnt:
                    maxCnt = m
                    log.debug("cell ({},{}) has topics: {} cnt:{}".format(i, j, topics, cnt))

                topicsCnt = {}
                # create a topic -> cnt dict
                for k in range(len(topics)):
                    topicsCnt[topics[k]] = cnt[k]

                for t in topics:
                    if t not in allTopics:
                        allTopics.append(t)

                if len(cnt) > maxCnt:
                    maxCnt = len(cnt)

                plotRow.append((prodID, consID, topicsCnt))
                j += 1
            i += 1

        if maxConsCnt < j:
            maxConsCnt = j
        prodCnt = i
        minTS = tempMaxTS
        plot = {'minTS': minTS,
                'maxTS': maxTS,
                'maxConsCnt': maxConsCnt,
                'prodCnt': prodCnt,
                'allTopics': allTopics,
                'plotGrid': plotGrid
                }
        allPlots.append(plot)
        logger.log_textWithIndent(log, "added into AllPlots"+str(plot))
        logger.log_newline(log)
    return allPlots
