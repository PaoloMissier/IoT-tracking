
from utils import logger
from cassandra.cluster import Cluster
import pandas as pd

log = logger.create_logger(__name__)


CNT_QUERY_CLIENTS = "SELECT prodID, consID, topic , count(*) as cnt " \
            "FROM CNT WHERE prodid = %s AND consid = %s"\
            "GROUP BY id, prodID, consID, topic ALLOW FILTERING"


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


def getJoinCntDF(session, query, params):
    l = []
    try:
        rows = session.execute(query=query, parameters=(params[0], params[1]), trace=True)
        print(rows.get_query_trace())
        for row in rows:
            d = {'prodID': row.prodid, 'consID': row.consid, 'topic': row.topic, 'cnt': row.cnt}
            l.append(d)
            log.info("cnt: {}, {}, {}, {}".format(row.prodid, row.consid, row.topic, row.cnt))

    except :
        log.error("Error while executing JoinCntDF query")
    return pd.DataFrame(l)


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


def getJoinCntDFClients(pub, sub):

    params = [pub, sub]
    session = connect()

    return getJoinCntDF(session, CNT_QUERY_CLIENTS, params)