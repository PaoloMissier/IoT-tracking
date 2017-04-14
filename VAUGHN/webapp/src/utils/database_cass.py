from src.utils import logger, tools
from cassandra.cluster import Cluster
import pandas as pd

log = logger.create_logger(__name__)

CNT_QUERY = "SELECT prodID, consID, topic, count(*) as cnt " \
            "FROM CNT  " \
            "WHERE ts >= %s " \
            "AND ts <= %s"\
            "GROUP BY id, prodID, consID, topic ALLOW FILTERING"


CNT_QUERY_FROM_X = "SELECT * FROM {} WHERE ts >= %s " \
            "AND ts <= %s ALLOW FILTERING"



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


def getJoinCnt(session, params):
    l = []
    minTS = params[0].strftime('%Y-%m-%d %H:%M:%S')
    maxTS = params[1].strftime('%Y-%m-%d %H:%M:%S')
    rows = session.execute(query=CNT_QUERY, parameters=(minTS, maxTS), trace=True)
    print(rows.get_query_trace())
    for row in rows:
        d = {'prodID': row.prodid, 'consID': row.consid, 'topic': row.topic, 'cnt': row.cnt}
        l.append(d)
        log.info("cnt: {}, {}, {}, {}".format(row.prodid, row.consid, row.topic, row.cnt))

    return l


def getJoinCntFromX(session, params):
    if session is None:
        session = connect()
    l = []
    minTS = params[0].strftime('%Y-%m-%d %H:%M:%S')
    maxTS = params[1].strftime('%Y-%m-%d %H:%M:%S')
    rows = session.execute(query=CNT_QUERY_FROM_X.format(params[2]), parameters=(minTS, maxTS), trace=True)
    for row in rows:
        d = {'prodID': row.prodid, 'consID': row.consid, 'topic': row.topic, 'cnt': row.cnt}
        l.append(d)
        log.info("cnt: {}, {}, {}".format(row.prodid, row.consid, row.topic))
    return l


def getTopics():
    topics = []
    session = connect()
    QUERY = "SELECT DISTINCT topic FROM topic_list"
    rows = session.execute(QUERY)
    for row in rows:
        topics.append(row.topic)
    return topics


def getSubscribers():
    subs = []
    session = connect()
    QUERY = "SELECT DISTINCT cons FROM cons_list"
    rows = session.execute(QUERY)
    for row in rows:
        subs.append(row.cons)
    return subs


def getPublisher():
    pubs = []
    session = connect()
    QUERY = "SELECT DISTINCT prod FROM prod_list"
    rows = session.execute(QUERY)
    for row in rows:
        pubs.append(row.prod)
    return pubs
