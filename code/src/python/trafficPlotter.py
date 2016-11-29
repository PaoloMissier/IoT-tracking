#!/usr/bin/env python

import paho.mqtt.client as mqtt
from datetime import datetime
import logging
import mysql.connector
import pandas as pd
import matplotlib.pyplot as plt

import numpy as np
from numpy.random import randn

logger = logging.getLogger('Subscriber')
logger.setLevel(logging.DEBUG)
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

CNT_QUERY = "SELECT prodID, consID, topic, count(*) as cnt  FROM CONS C group by prodID, consID, topic"
DF_COLUMNS = [ "prodID", "consID",   "topic", "cnt"]

TOPIC_COUNT = 5
TOPIC_ROOT="root/"


def DBConnect(h=DB_HOST, db=DB_NAME):
	## init DB connection and acquire context
	return mysql.connector.connect(user='paolo', password='riccardino', host=h, database=db)  # returns connection object

def DBWRead(db, cursor, parameters):
	try:
		readCONS = CNT_QUERY
		# loads resultSet into a pandas DF
		df = pd.read_sql(readCONS, con=db)
		return df
				
	except mysql.connector.Error as e:
		print(e)
	

def genTopics(n):
	return [ TOPIC_ROOT+str(i) for i in range(n)]


##
# main
##	
if __name__ == '__main__':

	db = DBConnect()
	cursor = db.cursor()
	logger.debug("mysql connection successful")

	parameters = ("2016-11-25 12:50:01")  # FIXME
	df  = DBWRead(db, cursor, parameters)
	print("loaded df with {}  records".format(len(df)))

	# count number of producers  and consumers
	prodCnt = len(df.groupby(['prodID']))
	consCnt = len(df.groupby(['consID']))
	print("{} prod, {} cons".format(prodCnt, consCnt))

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


	## plot everything
	# create prodCnt x consCnt plots:
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

# 	topicList = genTopics(TOPIC_COUNT)
# 	
# 	## topics are x axis labels
# 	allTopics =  topicList
# 	print(allTopics)
# 	x_pos = np.arange(len(allTopics))			
# 	print(x_pos)			
# 
# 	plt.setp(axes, xticks=x_pos, xticklabels=allTopics)
# 	
# 	# groups with same (prod, cons)
# 	groupedByProd = df.groupby('prodID')
# 
# 	# each group needs further grouping by 'consID'	
# 	i = 0
# 	prodConsGroup = []
# 	for prodID, prodDF in groupedByProd:
# 		prodGroup = {}
# 		groupedByCons = prodDF.groupby('consID')
# 		j = 0
# 		for consID, consDF in groupedByCons:
# 			prodGroup[consID] = consDF
# 			
# 			## cnt are the values plotted on the bar
# 			cnt  = [cnt for cnt in consDF['cnt']]
# 			topics = [topics  for topics in consDF['topic']]
# 			
# 			# set cnt = 0 for missing topics			
# 			actualCnt = []
# 			for k in range(len(allTopics)):
# 				if allTopics[k] in topics:
# 					actualCnt.append(cnt[i])
# 				else:
# 					actualCnt.append(0)
# 
# 			print("****\nx_pos: {}".format(x_pos))
# 			print("these topics: {}".format(topics))
# 			print("cnt: {}".format(cnt))
# 			print("actualCnt: {}".format(actualCnt))
# 			
# # 			print("***\n plot ({},{}):\n topics: {} \n cnt: {}\n***".format(i,j,topics, cnt))
# 			j = j+1
# 			
# 		prodConsGroup[prodID] = prodGroup
# 		i = i+1


# 
# 	objects = ('Python', 'C++', 'Java', 'Perl', 'Scala', 'Lisp')
# 	y_pos = np.arange(len(objects))
# 	performance = [10,8,6,4,2,1]
#  
# 	plt.barh(y_pos, performance, align='center', alpha=0.5)
# 	plt.yticks(y_pos, objects)
# 	plt.xlabel('Usage')
# 	plt.title('Programming language usage')
#  
# 	plt.show()	
	
	
	
	
	
	
	
	
	