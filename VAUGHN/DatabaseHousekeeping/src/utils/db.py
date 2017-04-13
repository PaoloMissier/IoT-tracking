from cassandra.query import BatchStatement, ConsistencyLevel
from src.utils import logger, tools
from cassandra.cluster import Cluster
import datetime


log = logger.create_logger(__name__)

CNT_QUERY = "SELECT prodID, consID, topic FROM cnt WHERE ts >= %s " \
            "AND ts <= %s ALLOW FILTERING"

CNT_QUERY_FROM_X = "SELECT prodID, consID, topic, cnt FROM {} WHERE ts >= %s " \
            "AND ts <= %s ALLOW FILTERING"

# DELETE_CNT_QUERY = "DELETE FROM CNT  " \
#             "WHERE id = %s "

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


def deleteFromCNT(session, params):
    minTS = params[0].strftime('%Y-%m-%d %H:%M:%S')
    maxTS = params[1].strftime('%Y-%m-%d %H:%M:%S')
    rows = session.execute(query="SELECT * FROM CNT  " \
                                "WHERE ts >= %s " \
                                "AND ts <= %s ALLOW FILTERING", parameters=(minTS, maxTS))

    DELETE_CNT_QUERY = session.prepare("DELETE FROM CNT  " \
                                        "WHERE id = ? ")
    batch = BatchStatement()
    for row in rows:
        # print("\n {} {} {} {} {} \n".format(row['prodID'], row['consID'], row['topic'], row['ts'], row['cnt']))
        # session.execute(query=statement, parameters=(row.prodid, row.consid, row.topic, row.ts, int(row.cnt)))
        batch.add(DELETE_CNT_QUERY, (row.id,))
    session.execute(batch)

    # for row in rows:
    #     print("row id"+str(row.id))
    #     print(type(row.id))
    #     session.execute(query=DELETE_CNT_QUERY, parameters=row.id, trace=True)
    log.info("Executed delete from cnt query")
    return True


def deleteFromCNTX(session, params):
    minTS = params[0].strftime('%Y-%m-%d %H:%M:%S')
    maxTS = params[1].strftime('%Y-%m-%d %H:%M:%S')
    rows = session.execute(query="SELECT * FROM {}  " \
                                "WHERE ts >= %s " \
                                "AND ts <= %s ALLOW FILTERING".format(params[2]), parameters=(minTS, maxTS))


    DELETE_CNT_QUERY = session.prepare("DELETE FROM {}  " \
                                        "WHERE prodID = ? and consID = ? and topic = ? and ts = ? ".format(params[2]))
    batch = BatchStatement()
    for row in rows:
        # print("\n {} {} {} {} {} \n".format(row['prodID'], row['consID'], row['topic'], row['ts'], row['cnt']))
        # session.execute(query=statement, parameters=(row.prodid, row.consid, row.topic, row.ts, int(row.cnt)))
        batch.add(DELETE_CNT_QUERY, (row.prodid, row.consid, row.topic, row.ts,))
    session.execute(batch)

    # for row in rows:
    #     print("row id"+str(row.id))
    #     print(type(row.id))
    #     session.execute(query=DELETE_CNT_QUERY, parameters=row.id, trace=True)
    log.info("Executed delete from cnt query")
    return True



def getJoinCnt(session, params):
    l = []
    minTS = params[0].strftime('%Y-%m-%d %H:%M:%S')
    maxTS = params[1].strftime('%Y-%m-%d %H:%M:%S')
    try:
        rows = session.execute(query=CNT_QUERY, parameters=(minTS, maxTS), trace=True)
        print(rows.get_query_trace())
        for row in rows:
            d = {'prodID': row.prodid, 'consID': row.consid, 'topic': row.topic, 'ts': params[0]}
            l.append(d)
            log.info("cnt: {}, {}, {}".format(row.prodid, row.consid, row.topic))

    except :
        log.error("Error while executing JoinCntDF query")

    return l


def getJoinCntFromX(session, params):
    l = []
    minTS = params[0].strftime('%Y-%m-%d %H:%M:%S')
    maxTS = params[1].strftime('%Y-%m-%d %H:%M:%S')
    try:
        rows = session.execute(query=CNT_QUERY_FROM_X.format(params[2]), parameters=(minTS, maxTS), trace=True)
        print(rows.get_query_trace())
        for row in rows:
            d = {'prodID': row.prodid, 'consID': row.consid, 'topic': row.topic, 'ts': params[0], 'cnt': row.cnt}
            l.append(d)
            log.info("cnt: {}, {}, {}".format(row.prodid, row.consid, row.topic))

    except :
        log.error("Error while executing JoinCntDF query")

    return l


def getMinTimestamp(session, tableName):
    mints = None
    try:
        rows = session.execute(query=MINTS_QUERY.format(tableName))
        mints = rows[0].mints
        log.info("Executed getMinTS query")
    except:
        log.error("Error while executing getMinTimestamp query")

    return mints


def insertCnt(session, statement, df, ts):
    batch = BatchStatement()
    for index, row in df.iterrows():
        # print(row['prodID'])
        # print("\n {} {} {} {}\n".format(row['prodID'], row['consID'], row['topic'], row['cnt']))
            # session.execute(query=statement, parameters=(row.prodid, row.consid, row.topic, row.ts, int(row.cnt)))
        batch.add(statement, (row['prodID'], row['consID'], row['topic'], ts, int(row['cnt'])))
    session.execute(batch)
    log.info("Executed insert query")

    # log.error("Error while executing insertCnt")

    return True
