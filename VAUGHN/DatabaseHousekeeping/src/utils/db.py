from cassandra.query import BatchStatement, ConsistencyLevel
from src.utils import logger, tools
from cassandra.cluster import Cluster
from cassandra import ReadFailure
import datetime


log = logger.create_logger(__name__)

CNT_QUERY = "SELECT prodID, consID, topic FROM cnt WHERE ts >= %s " \
            "AND ts <= %s ALLOW FILTERING"

CNT_QUERY_FROM_X = "SELECT prodID, consID, topic, cnt FROM {} WHERE ts >= %s " \
            "AND ts <= %s ALLOW FILTERING"

MINTS_QUERY = "SELECT MIN(ts) as mints from {}"

CASS_CONTACT_POINTS = ["127.0.0.1"]
CASS_KEYSPACE = "brokertracker"


def connect():
    try:
        cluster = Cluster(CASS_CONTACT_POINTS)
        session = cluster.connect(CASS_KEYSPACE)
        log.info("Connected to Cassandra.")
        return session
    except AttributeError as e:
        log.error("Error connecting to Cassandra: {}".format(e.args))
        tools.logfile("Error connecting to Cassandra: {}".format(e.args))
        return None


def deleteFromCNT(session, params):
    try:
        minTS = params[0].strftime('%Y-%m-%d %H:%M:%S')
        maxTS = params[1].strftime('%Y-%m-%d %H:%M:%S')
        rows = session.execute(query="SELECT * FROM CNT  " \
                                    "WHERE ts >= %s " \
                                    "AND ts <= %s ALLOW FILTERING", parameters=(minTS, maxTS))

        DELETE_CNT_QUERY = session.prepare("DELETE FROM CNT  " \
                                            "WHERE id = ? ")
        batch = BatchStatement()
        for row in rows:
            batch.add(DELETE_CNT_QUERY, (row.id,))
        rowss = session.execute(batch, trace=True)
        print(rowss.get_query_trace())
        log.info("Executed delete from cnt query")
        return True
    except ReadFailure as rf:
        log.error("Error executing deleteFromCNT to Cassandra: {}".format(rf.args))
        return False


def deleteFromCNTX(session, params):
    try:
        minTS = params[0].strftime('%Y-%m-%d %H:%M:%S')
        maxTS = params[1].strftime('%Y-%m-%d %H:%M:%S')
        rows = session.execute(query="SELECT * FROM {}  " \
                                    "WHERE ts >= %s " \
                                    "AND ts <= %s ALLOW FILTERING".format(params[2]), parameters=(minTS, maxTS))

        DELETE_CNT_QUERY = session.prepare("DELETE FROM {}  " \
                                            "WHERE prodID = ? and consID = ? and topic = ? and ts = ? ".format(params[2]))
        batch = BatchStatement()
        for row in rows:
            batch.add(DELETE_CNT_QUERY, (row.prodid, row.consid, row.topic, row.ts))
        session.execute(batch, trace=True)
        log.info("Executed delete from cnt query")
        return True
    except ReadFailure as rf:
        log.error("Error executing deleteFromCNTX to Cassandra: {}".format(rf.args))
        return False


def getJoinCnt(session, params):
    try:
        l = []
        minTS = params[0].strftime('%Y-%m-%d %H:%M:%S')
        maxTS = params[1].strftime('%Y-%m-%d %H:%M:%S')
        rows = session.execute(query=CNT_QUERY, parameters=(minTS, maxTS), trace=True)
        print(rows.get_query_trace())
        for row in rows:
            d = {'prodID': row.prodid, 'consID': row.consid, 'topic': row.topic, 'ts': params[0]}
            l.append(d)
            log.info("cnt: {}, {}, {}".format(row.prodid, row.consid, row.topic))
        return l
    except ReadFailure as rf:
        log.error("Error executing getJoinCnt to Cassandra: {}".format(rf.args))
        tools.logfile("Error executing getJoinCnt to Cassandra: {}".format(rf.args))
        return None


def getJoinCntFromX(session, params):
    try:
        l = []
        minTS = params[0].strftime('%Y-%m-%d %H:%M:%S')
        maxTS = params[1].strftime('%Y-%m-%d %H:%M:%S')
        rows = session.execute(query=CNT_QUERY_FROM_X.format(params[2]), parameters=(minTS, maxTS), trace=True)
        for row in rows:
            d = {'prodID': row.prodid, 'consID': row.consid, 'topic': row.topic, 'ts': params[0], 'cnt': row.cnt}
            l.append(d)
            log.info("cnt: {}, {}, {}".format(row.prodid, row.consid, row.topic))
        return l
    except ReadFailure as rf:
        log.error("Error executing getJoinCntFromX to Cassandra: {}".format(rf.args))
        tools.logfile("Error executing getJoinCntFromX to Cassandra: {}".format(rf.args))
        return None


def getMinTimestamp(session, tableName):
    try:
        mints = None
        rows = session.execute(query=MINTS_QUERY.format(tableName))
        mints = rows[0].mints
        log.info("Executed getMinTS query")
        return mints
    except ReadFailure as rf:
        log.error("Error executing getMinTS to Cassandra: {}".format(rf.args))
        tools.logfile("Error executing getMinTS to Cassandra: {}".format(rf.args))
        return None


def insertCnt(session, statement, df, ts):
    batch = BatchStatement()
    for index, row in df.iterrows():
        batch.add(statement, (row['prodID'], row['consID'], row['topic'], ts, int(row['cnt'])))
    session.execute(batch)
    log.info("Executed insert query")
    return True
