#!/usr/bin/env python

import paho.mqtt.client as mqtt
from datetime import datetime
from dateutil.relativedelta import relativedelta
import logging
import mysql.connector
import pandas as pd
import matplotlib.pyplot as plt
import time


import numpy as np
from numpy.random import randn

logger = logging.getLogger('Subscriber')
logger.setLevel(logging.INFO)
logger.handlers = []
ch = logging.StreamHandler()
ch.setFormatter(logging.Formatter('%(asctime)s %(levelname)s %(message)s'))
logger.addHandler(ch)

## 
# periodically query the derived MSGCNT table and extracts:
## for each window W and consumer C, the tuples (P,top, cnt) of msg cnt for each producer P and topic top
## updates a plot to show the msgcnt per topic and global (sum over all topics)
##

## DB constants
DB_HOST = "localhost"
DB_NAME='BrokerTracker'

MIN_MAX_TS_QERY = "SELECT min(timestamp) as min, max(timestamp) as max FROM CONS"
CNT_QUERY = "SELECT prodID, consID, topic, count(*) as cnt  FROM CONS C  where timestamp between date(%s) and date(%s) group by prodID, consID, topic"
# DB_COLUMNS = [ "prodID", "consID",   "topic", "cnt"]

REPLOT_INTERVAL = 5  #sec

TOPIC_COUNT = 5
TOPIC_ROOT="root/"


def DBConnect(h=DB_HOST, db=DB_NAME):
	## init DB connection and acquire context
	return mysql.connector.connect(user='paolo', password='riccardino', host=h, database=db)  # returns connection object 

def DB_MinMax(cursor):
	try:
		cursor.execute(MIN_MAX_TS_QERY)		
		row = cursor.fetchone()
		if row is not None:
			logger.info(row)
			return (row[0], row[1])

	except mysql.connector.Error as e:
		print(e)


def DBRead(cursor, query, parameters):
	try:
		cursor.execute("SELECT prodID, consID, topic, count(*) as cnt  FROM CONS C  where timestamp between %s and %s group by prodID, consID, topic", ("2016-12-10 11:08:12", "2016-12-10 11:08:22"))		
		# loads resultSet into a pandas DF
		# 		df = pd.read_sql(CNT_QUERY, db, parameters)
	
		## create a df from the results  -- pandas can do this but couldn't get the parameter passing to work
		l = list()
		for (prodID, consID, topic, cnt) in cursor:
			## create a dict
			d = { 'prodID': prodID, 'consID': consID, 'topic': topic, 'cnt':cnt } 
			l.append(d)
			logger.info("cnt: {}, {}, {}, {}".format(prodID, consID, topic, cnt))

		return pd.DataFrame(l)
				
	except mysql.connector.Error as e:
		print(e)
	

def genTopics(n):
	return [ TOPIC_ROOT+str(i) for i in range(n)]


## blocks if not enough records in the next window
def getNextWindow(fromTS):

	while True:
		_, maxTS = DB_MinMax(cursor)  # get current latest timestamp

		logger.info("available window size: {}".format(maxTS - fromTS))
		soughtMaxTS = fromTS + relativedelta(seconds=REPLOT_INTERVAL) 
		if soughtMaxTS <= maxTS:
			logger.info("next window is complete. From {} to {}".format(fromTS, soughtMaxTS))
			return soughtMaxTS
		else:
			logger.info("next window is INcomplete. From {} to {} but max is {}".format(fromTS, soughtMaxTS, maxTS))
			time.sleep(REPLOT_INTERVAL)

# 		print("mintS: {}, delta: {}, new maxTS: {}".format(minTS, REPLOT_INTERVAL, minTS + relativedelta(second=REPLOT_INTERVAL)))
		



##
# main
##	
if __name__ == '__main__':

	db = DBConnect()
	cursor = db.cursor()
	logger.debug("mysql connection successful")

	# find min and max timestamps -- this is the largest window we can turn into a counter cube
	minTS, maxTS = DB_MinMax(cursor)

	firstWindow = True

	while True:
	
		logger.info("window: [{},{}]".format(minTS, maxTS))
		maxTS = getNextWindow(minTS)
		
		df  = DBRead(cursor, CNT_QUERY, [minTS, maxTS])
		logger.info("loaded df with {}  records".format(len(df)))

		# count number of producers  and consumers
		prodCnt = len(df.groupby(['prodID']))
		consCnt = len(df.groupby(['consID']))
		logger.info("{} prod, {} cons".format(prodCnt, consCnt))

		maxCnt = 0   # scale of Y axis is calibrated on max cnt across all groups
		allTopics = list()   # xticks common to all plots
		prodCnt = 0
		maxConsCnt = 0
	
		gByProd = df.groupby('prodID') 		# groups with same (prod, cons)

		plotGrid = list()  # of lists
		i = 0
		for prodID, prodDF in gByProd:
	
			gByCons = prodDF.groupby('consID')
	
			plotGrid.append(list())  # row of cells		

			plotRow = plotGrid[i]
			j = 0
			for consID, consDF in gByCons:
		
				# remove the index from the DF (??)
				cnt  = [cnt for cnt in consDF['cnt']]  	## cnt are the values plotted on the bar			
				topics = [topics  for topics in consDF['topic']]

				m = max(cnt)						
				if m > maxCnt:
					maxCnt = m				
			
				logger.debug("cell ({},{}) has\ntopics: {}\ncnt:{}".format(i,j,topics, cnt))

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
				j = j+1
			i = i+1
		
		if maxConsCnt < j:
			maxConsCnt = j
		prodCnt = i
	
		logger.debug("plotting {}x{} grid".format(prodCnt, maxConsCnt))

		if firstWindow: 
			# init the plot grid
			# create prodCnt x consCnt plots:
			plt.ioff()  # ODD! should be on

			fig, axes = plt.subplots(prodCnt, maxConsCnt, figsize=(30, 10))	

			## set properties across all plots
			x_pos = np.arange(len(allTopics))			
			logger.debug("x ticks pos for all plots: {}".format(x_pos))			
			logger.debug("x axis labels: {}".format(allTopics))

		plt.setp(axes, xticks=x_pos, xticklabels=allTopics, ylim=[0,maxCnt])

		for i in range(prodCnt):
			for j in range(maxConsCnt):

				(prodID, consID, topicsCnt) = plotGrid[i][j]
			
				for t in allTopics:			
					if t not in topicsCnt:
						topicsCnt[t] = 0  			# set cnt = 0 for missing topics in this cell						

				logger.debug("plot ({},{}) bar values: {}".format(i,j,topicsCnt.values()))

				# add prodID, consID to legend / title
				axes[i,j].bar(x_pos, topicsCnt.values(), alpha=0.2, color='k')
				axes[i,j].set_title("P={}/C={}".format(prodID,consID))

		plt.show()
		print("are we here?")
		fig.canvas.draw()
		firstWindow = False

		print("are we here yet?")
		
		minTS = maxTS
	
	
	
	
	
	
	