from . import draw, tools, logger
from . import database as db

log = logger.create_logger(__name__)


def submit(minTS, maxTS, pub ,sub ,topic , interval):
    if interval is not None: interval = int(interval)

    minTS = tools.strToDT(minTS)
    maxTS = tools.strToDT(maxTS)

    script, div = draw.drawGrid(minTS, maxTS, pub, sub ,topic ,interval)
    return script, div


def generatePlotGrid(minTS=None, maxTS=None, pub=None, sub=None, top=None, interval=None, cursor=None):

    # create a copy of maxTS
    tempMaxTS = maxTS

    if cursor is None:
        conn = db.DBConnect()
        cursor = conn.cursor()

    if minTS is None and maxTS is None:
        # find min and max timestamps if none given -- this is the largest window we can turn into a counter cube
        minTS, maxTS = db.getMinMax(cursor)

    if minTS is None:
        # if minTS not given
        minTS, _ = db.getMinMax(cursor)

    allPlots = list()

    while True:

        log.info("window: [{},{}]".format(minTS, maxTS))

        if tempMaxTS is db.getNextWindow(cursor, minTS, maxTS, interval):
            break
        else:
            tempMaxTS = db.getNextWindow(cursor, minTS, maxTS, interval)

        df = db.getJoinCntDF(cursor, db.CNT_QUERY, [minTS, tempMaxTS])

        if len(df) == 0:  # skip next time frame
            minTS = tempMaxTS
            continue
        else:
            df = df[df['prodID'].isin(pub)]
            df = df[df['consID'].isin(sub)]
            df = df[df['topic'].isin(top)]

            if len(df) == 0:
                minTS = tempMaxTS
                continue

        log.info("loaded df with {}  records".format(len(df)))

        # count number of producers  and consumers
        prodCnt = len(df.groupby(['prodID']))
        consCnt = len(df.groupby(['consID']))
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

