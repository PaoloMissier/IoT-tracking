#!/usr/bin/env python

import paho.mqtt.client as mqtt
from random import random, randint
from time import sleep
from datetime import datetime
import logging
import mysql.connector
from uuid import uuid1
import sys, getopt



logger = logging.getLogger('Publisher')
logger.setLevel(logging.INFO)
logger.handlers = []
ch = logging.StreamHandler()
ch.setFormatter(logging.Formatter('%(asctime)s %(levelname)s %(message)s'))
logger.addHandler(ch)

## simulates multiple sensors. one is chosen randomly for each new message
# default -- see CL options
CLIENT_COUNT = 3
CLIENT_ID = "s"
SLEEP_INT = 5
TOPIC_COUNT = 5
TOPIC_ROOT="root/"

sep = '|'
datetimeFormat = "%y%m%d%H%M%S%f"


BROKER_HOST = "localhost"
DB_HOST = "localhost"
DB_NAME='BrokerTracker'


# The callback for when the client receives a CONNACK response from the server.
def on_connect(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))

def on_disconnect(client,  userdata,  rc):
    print("Client disconnected with result code "+str(rc))
    
def on_publish(client, userdata, mid) :
	logger.debug("publish done with [client = {c}, userdata={ud}, mid={m}]".format(c=client._client_id, ud=userdata, m=mid))


def genDataID():
	return str(uuid1())
	

def injectMD( md, payload):
	(CLIENT_ID, dataID, timestamp) = md
	# add producer ID, dataID, timestamp to  payload into a bytearray
	return CLIENT_ID + sep + dataID + sep + timestamp + sep + str(payload)
	## TODO this must become a bytearray encoding 


def DBConnect(h=DB_HOST, db=DB_NAME):
	## init DB connection and acquire context
	return mysql.connector.connect(user='paolo', password='riccardino', host=h, database=db)  # returns connection object


def DBWrite(cnx, cursor, md):
	add_PROD_msg = ("insert into PROD (`PRODid`, `dataID`, `timestamp`, `topic`) values (%s, %s, %s, %s)")
	cursor.execute(add_PROD_msg, md)
	cnx.commit()
	logger.debug("mysql commit successful")


def genClients(n):
	return [ CLIENT_ID+"_"+str(i) for i in range(n)]

def genTopics(n):
	return [ TOPIC_ROOT+str(i) for i in range(n)]


#########
##  MAIN BODY
#########

def main(argv):

	#init to default
	sleepInt = SLEEP_INT  
	clientCount = CLIENT_COUNT 
	topicCount = TOPIC_COUNT
	doDBWrite = True
	
	try:
		opts, args = getopt.getopt(argv,"nt:p:r:",["noWrite","topics=","publishers=","rate="])
	except getopt.GetoptError:
		print("publisher.py -n -t <topics count> -p <publishers count> -r <msg generation rate (sec)>")
		sys.exit(2)

	for opt, arg in opts:
		if opt in ("-r", "--rate"):
			sleepInt = float(arg)
		if opt in ("-p", "--publishers"):
			clientCount = int(arg)
		if opt in ("-t", "--topics"):
			topicCount = int(arg)
		if opt in ("-n", "--noWrite"):
			doDBWrite = False
	
	print("msg generation rate: {} secs".format(sleepInt))	
	print("publishers count: {}".format(clientCount))	
	print("topics count: {}".format(topicCount))	
	print("writing to DB: {}".format(doDBWrite))	

	clientIdList = genClients(clientCount)
	topicList = genTopics(topicCount)
		
	client = mqtt.Client()
	client.on_connect = on_connect
	client.on_publish = on_publish

	cnx = DBConnect()
	cursor = cnx.cursor()
	logger.debug("mysql connection successful")


	logger.debug("connecting to broker host {}".format(BROKER_HOST))
	client.connect(BROKER_HOST)
	client.loop_start()


	while True:
		# simulates one sensor generating a msg (random payload) with a random topic
		payload = random()
		topic = topicList[randint(0,len(topicList)-1)]
		currentClient = clientIdList[randint(0,len(clientIdList)-1)]
	
		dt = datetime.utcnow()
		dateTime = datetime.strftime(dt, datetimeFormat)
		msgID = genDataID()
		md = (currentClient, msgID, dateTime)
		md1 = (currentClient, msgID, dt, topic)  ## like md but raw datetime for SQL insert, and added topic
		logger.debug("Metadata produced: {}".format(md))
	
		payload = injectMD(md, payload)
		client.publish(topic, str(payload))
		logger.info("published: {} on topic {}".format(payload,  topic))
	
		if doDBWrite:
			DBWrite(cnx, cursor, md1)

		sleep(sleepInt)

	## this goes in some catch clause as we don't have a clean way to exit
	cursor.close()
	cnx.close()



if __name__ == "__main__":
   main(sys.argv[1:])
   
   
