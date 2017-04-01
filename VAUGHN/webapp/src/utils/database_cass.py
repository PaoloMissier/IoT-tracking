from src.utils import logger
from dateutil.relativedelta import relativedelta
from cassandra.cluster import Cluster
import pandas as pd

log = logger.create_logger(__name__)

CNT_QUERY = "SELECT prodID, consID, topic, count(*) as cnt " \
            "FROM CNT  " \
            "WHERE date >= %s " \
            "AND date <= %s " \
            "AND time >= %s" \
            "AND time <= %s"\
            "GROUP BY prodID, consID, topic"


CASS_CONTACT_POINTS = ["127.0.0.1"]
CASS_KEYSPACE = "brokertracker"


def connect():
    try:
        cluster = Cluster(CASS_CONTACT_POINTS)
        session = cluster.connect(CASS_KEYSPACE)
        log.info("Connected to Cassandra.")
        return session
    except:
        log.error("Error connecting to Cassandra.")


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


def getJoinCntDF(session, query, params):
    try:
        rows = session.execute(query, (params[0], params[1], params[2], params[3]))
        # for (prodID, consID, topic, cnt) in cursor:
        #     # create a dict
        #     d = {'prodID': prodID, 'consID': consID, 'topic': topic, 'cnt': cnt}
        #     l.append(d)
        #     log.info("cnt: {}, {}, {}, {}".format(prodID, consID, topic, cnt))

    except:
        log.error("Error while executing JoinCntDF query")

    return pd.DataFrame(rows)


def getTopics():
    session = connect()
    QUERY = "SELECT DISTINCT id,topic FROM CNT"
    rows = session.execute(QUERY)
    return rows


def getSubscribers():
    session = connect()
    QUERY = "SELECT DISTINCT id,consID FROM CNT"
    rows = session.execute(QUERY)
    return rows


def getPublisher():
    session = connect()
    QUERY = "SELECT DISTINCT id,prodID FROM CNT"
    rows = session.execute(QUERY)
    return rows
