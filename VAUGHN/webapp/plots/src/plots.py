
from plots.src import draw
from src.utils import tools, logger
from src.utils import database_cass as db
from dateutil.relativedelta import relativedelta
import pandas as pd
import datetime

log = logger.create_logger(__name__)


def submit(minTS, maxTS, pub ,sub ,topic):

    minTS = tools.strToDT(minTS)
    maxTS = tools.strToDT(maxTS)
    print(minTS, maxTS)

    gridList = draw.drawGrid(minTS, maxTS, pub, sub, topic)
    return gridList


def generateAllCubes(minTS=None, maxTS=None):
    log.info("Generating Cubes")
    min_list_check = ""
    min_list = []
    max_list = []
    session = db.connect()

    if datetime.datetime.now() - minTS > datetime.timedelta(days=1):
        min_list = db.getJoinCntFromX(session, [minTS, maxTS, "day_cnt"])
        min_list_check = "day_cnt"
    elif datetime.datetime.now() - minTS > datetime.timedelta(hours=12):
        min_list = db.getJoinCntFromX(session, [minTS, maxTS, "hour_cnt"])
        min_list_check = "hour_cnt"
    elif datetime.datetime.now() - minTS > datetime.timedelta(hours=3):
        min_list = db.getJoinCntFromX(session, [minTS, maxTS, "half_cnt"])
        min_list_check = "half_cnt"
    elif datetime.datetime.now() - minTS > datetime.timedelta(minutes=15):
        min_list = db.getJoinCntFromX(session, [minTS, maxTS, "quarter_cnt"])
        min_list_check = "quarter_cnt"
    else:
        min_list = db.getJoinCnt(session, [minTS, maxTS])
        min_list_check = "cnt"

    if datetime.datetime.now() - maxTS > datetime.timedelta(days=1) and min_list_check != "day_cnt":
        max_list = db.getJoinCntFromX(session, [minTS, maxTS, "day_cnt"])
    elif datetime.datetime.now() - maxTS > datetime.timedelta(hours=12) and min_list_check != "hour_cnt":
        max_list = db.getJoinCntFromX(session, [minTS, maxTS, "hour_cnt"])
    elif datetime.datetime.now() - maxTS > datetime.timedelta(hours=3) and min_list_check != "half_cnt":
        max_list = db.getJoinCntFromX(session, [minTS, maxTS, "half_cnt"])
    elif datetime.datetime.now() - maxTS > datetime.timedelta(minutes=15) and min_list_check != "quarter_cnt":
        max_list = db.getJoinCntFromX(session, [minTS, maxTS, "quarter_cnt"])
    elif min_list_check != "cnt":
        max_list = db.getJoinCnt(session, [minTS, maxTS])

    df = pd.DataFrame(min_list + max_list)
    if not df.empty:
        df = df.groupby(['prodID', 'consID', 'topic', 'ts']).sum().reset_index()

    return df


def generatePlotGrid(minTS=None, maxTS=None, pub=None, sub=None, top=None):

    if datetime.datetime.now() - minTS > datetime.timedelta(days=2):
        interval = 3600 * 24
    else:
        interval = 3600

    # create a copy of maxTS
    tempMaxTS = maxTS

    allPlots = list()

    while True:

        log.info("window: [{},{}]".format(minTS, maxTS))

        if tempMaxTS is getNextWindow(minTS, maxTS, interval):
            break
        else:
            tempMaxTS = getNextWindow(minTS, maxTS, interval)

        df = generateAllCubes(minTS, tempMaxTS)
        if not df.empty:
            df = df.drop('ts', 1)
            df = df.groupby(['prodID', 'consID', 'topic']).sum().reset_index()
        if len(df) == 0:  # skip next time frame
            minTS = tempMaxTS
            continue
        else:
            df = df[df['prodID'].isin(pub)]
            df = df[df['consID'].isin(sub)]
            df = df[df['topic'].isin(top)]
            # df = df[df.isin({'prodID': pub,
            #                  'consID': sub,
            #                  'topic': top})]
            print(df.to_string())
            # print(df['prodID'].to_string())

            if len(df) == 0:
                minTS = tempMaxTS
                continue

        log.info("loaded df with {} records".format(len(df)))

        # count number of producers  and consumers
        prodCnt = len(df.groupby(['prodID']))
        print(df.groupby(['prodID']))
        consCnt = len(df.groupby(['consID']))
        print(df.groupby(['consID']))
        log.warning("{} prod, {} cons".format(prodCnt, consCnt))

        maxCnt = 0  # scale of Y axis is calibrated on max cnt across all groups
        allTopics = list()  # x ticks common to all plots
        maxConsCnt = 0

        gByProd = df.groupby('prodID')  # groups with same (prod, cons)
        log.warning("gbyProd {}".format(str(gByProd)))
        plotGrid = list()  # of lists
        i = 0
        for prodID, prodDF in gByProd:

            gByCons = prodDF.groupby('consID')
            log.warning("gbyCons {}".format(str(gByCons)))
            plotGrid.append(list())  # row of cells

            plotRow = plotGrid[i]
            j = 0
            for consID, consDF in gByCons:

                # remove the index from the DF (??)
                cnt = [cnt for cnt in consDF['cnt']]  # cnt are the values plotted on the bar
                topics = [topics for topics in consDF['topic']]
                log.warning(cnt)
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

        plot = {'minTS': minTS,
                'maxTS': tempMaxTS,
                'maxConsCnt': maxConsCnt,
                'prodCnt': prodCnt,
                'allTopics': allTopics,
                'plotGrid': plotGrid
                }
        minTS = tempMaxTS
        allPlots.append(plot)
        logger.log_textWithIndent(log, "added into AllPlots"+str(plot))
        logger.log_newline(log)
    return allPlots


def getNextWindow(fromTS, maxTS, interval):
    while True:
        log.info("available window size: {}".format(maxTS - fromTS))
        soughtMaxTS = fromTS + relativedelta(seconds=interval)
        if soughtMaxTS <= maxTS:
            log.info("next window is complete. From {} to {}".format(fromTS, soughtMaxTS))
            return soughtMaxTS
        else:
            log.info("next window unavailable, return fromTS")
            return fromTS
