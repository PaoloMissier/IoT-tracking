#!/usr/bin/env python

import paho.mqtt.client as mqtt
from datetime import datetime
import logging
import mysql.connector
from time import sleep
from random import random, randint

MAXTOPICS = 2

## DB constants
DB_HOST = "localhost"
DB_NAME='BrokerTracker'

BROKER_HOST = "localhost"

logger = logging.getLogger('Subscriber')
logger.setLevel(logging.INFO)
logger.handlers = []
ch = logging.StreamHandler()
ch.setFormatter(logging.Formatter('%(asctime)s %(levelname)s %(message)s'))
logger.addHandler(ch)

sep = '|'
datetimeFormat = "%y%m%d%H%M%S%f"

# all sub objects connect to the same DB instance in this simulation
def DBConnect(h=DB_HOST, db=DB_NAME):
	## init DB connection and acquire context
	return mysql.connector.connect(user='paolo', password='riccardino', host=h, database=db)  # returns connection object

# module util 
def DBWrite(cnx, cursor, md):
	add_PROD_msg = ("insert into CONS (`CONSid`, `dataID`, `timestamp`, `topic`) values (%s, %s, %s, %s)")
	cursor.execute(add_PROD_msg, md)
	cnx.commit()
	logger.debug("mysql commit successful")

# module util
def extractMD(payloadBytes):
	payload = payloadBytes.decode("utf-8")	
	parts = payload.split(sep)
	logger.debug("extract: *** \npayload: {}\nparts:{}".format(payload,parts))
	client_id = parts[0]
	dataID = parts[1]
	ts = datetime.strptime(parts[2],datetimeFormat)
	payload = parts[3]
	return (client_id, dataID, ts, payload)



class Subscriber:

## instance vars
# client 
# cnx, cursor
# workerId
# tList

	def __init__(self, workerId):
		self.workerId = workerId
		logger.debug("sub created")

		self.client = mqtt.Client()
		self.client.on_connect = self.on_connect
		self.client.on_message = self.on_message

		self.cnx = DBConnect()
		self.cursor = self.cnx.cursor()
		logger.debug("mysql connection successful")


	# The callback for when the client receives a CONNACK response from the server.
	def on_connect(self, client, userdata, flags, rc):
		print("Connected with result code "+str(rc))    
		client.subscribe([(t,0) for t in self.tList])   

	def on_disconnect(self, client,  userdata,  rc):
		print("Client disconnected with result code "+str(rc))

	# The callback for when a PUBLISH message is received from the server.
	def on_message(self, client, userdata, msg):
		(client_id, dataID, ts, payload) = extractMD(msg.payload)
	
		logger.debug("msg from client {c} dataID {d} topic {t} timestamp {ts}".format(c=client_id, d=dataID, t=msg.topic, p=payload, ts=ts))
		logger.debug("generating {} msg...".format(DB_HOST))
	
		trackRecord = (self.workerId, dataID, ts, msg.topic)
		DBWrite(self.cnx, self.cursor, trackRecord)

		
	def subLoop(self):
		logger.info("VAS {} connecting to broker host {}".format(self.workerId, BROKER_HOST))
		self.client.connect(BROKER_HOST)
		self.client.loop_forever()


	def setTopics(self, tList):
		self.tList = tList
		logger.info("VAS {} subscribed to topics ".format(self.workerId))
		for t in tList:
			print(t)
		
		
		





## test only
if __name__ == '__main__':
		sub = Subscriber("VAS-1")
		sub.subLoop()


