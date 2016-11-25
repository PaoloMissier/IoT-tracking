#!/usr/bin/env python

import paho.mqtt.client as mqtt
from datetime import datetime
import logging
import mysql.connector
from random import random, randint

from threading import Thread
from multiprocessing import Process, Pool
from subscriber import Subscriber
import sys, getopt

TOPIC_COUNT = 5
TOPIC_ROOT="root/"
MAX_TOPICS = 4  # max number of topics a subscriber subscribes to
SUB_ID = "VAS"
SUB_COUNT = 5  # def number of subscribers
doDBWrite = True

def genSubs(n):
	return [ SUB_ID+"_"+str(i) for i in range(n)]

def genTopics(n):
	return [ TOPIC_ROOT+str(i) for i in range(n)]

def launch(VAS_ID):
	# create new subscriber
	sub = Subscriber(VAS_ID)

	# randomly subscribe it to topics
	tList = []
	topicsCount = randint(1,maxTopics)
	for i in range(topicsCount):
		added = False
		while not added:
			t = topicList[randint(0,len(topicList)-1)]
			if (t not in tList):
				tList.append(t)
				added = True
	sub.setTopics(tList)
	print("VAS {} subscribed to {} topics: {} ".format(VAS_ID, len(tList), tList))

	sub.setDBWrite(doDBWrite)
	
	# start listener loop for incoming messages
	sub.subLoop()


#########
### MAIN 
## launches len(VAS_ID_LIST) threads one for each VAS
#########

if __name__ == '__main__':

	subCount = SUB_COUNT 
	topicCount = TOPIC_COUNT
	maxTopics = MAX_TOPICS

	argv = sys.argv[1:]
	
	try:
		opts, args = getopt.getopt(argv,"nm:t:s:",["noWrite","maxtopics=","topics=","subscribers="])
	except getopt.GetoptError:
		print("publisher.py -n -t <topics count> -s <subscribers count>")
		sys.exit(2)

	for opt, arg in opts:
		if opt in ("-s", "--subscribers"):
			subCount = int(arg)
		if opt in ("-t", "--topics"):
			topicCount = int(arg)
		if opt in ("-m", "--maxtopics"):
			maxTopics= int(arg)
		if opt in ("-n", "--noWrite"):
			doDBWrite = False

	
	print("subscribers count: {}".format(subCount))	
	print("topics count: {}".format(topicCount))	
	print("max topics / subscriber: {}".format(maxTopics))	
	print("writing to DB: {}".format(doDBWrite))	

	
	subIdList = genSubs(subCount)
	topicList = genTopics(topicCount)

	with Pool(processes=subCount) as pool:
		pool.map(launch, subIdList)

