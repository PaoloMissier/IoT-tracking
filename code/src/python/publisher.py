#!/usr/bin/env python

import paho.mqtt.client as mqtt
from random import random, randint
from time import sleep
from datetime import datetime
import logging
import mysql.connector
from uuid import uuid1

logger = logging.getLogger('Publisher')
logger.setLevel(logging.INFO)
logger.handlers = []
ch = logging.StreamHandler()
ch.setFormatter(logging.Formatter('%(asctime)s %(levelname)s %(message)s'))
logger.addHandler(ch)

## simulates multiple sensors. one is chosen randomly for each new message
CLIENT_ID_LIST = ["s1", "s2", "s3"]  
SLEEP_INT = 5

BROKER_HOST = "localhost"

sep = '|'
datetimeFormat = "%y%m%d%H%M%S%f"
TOPICS = ["root/t1", "root/t2", "root/t3", "root/t4", "root/t5", "root/t6", "root/t7"]

## DB constants
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





#########
##  MAIN BODY
#########

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
    topic = TOPICS[randint(0,len(TOPICS)-1)]
    currentClient = CLIENT_ID_LIST[randint(0,len(CLIENT_ID_LIST)-1)]
    
    dt = datetime.utcnow()
    dateTime = datetime.strftime(dt, datetimeFormat)
    msgID = genDataID()
    md = (currentClient, msgID, dateTime)
    md1 = (currentClient, msgID, dt, topic)  ## like md but raw datetime for SQL insert, and added topic
    logger.debug("Metadata produced: {}".format(md))
    
    payload = injectMD(md, payload)
    client.publish(topic, str(payload))
    logger.info("published: {} on topic {}".format(payload,  topic))
    
    DBWrite(cnx, cursor, md1)
    sleep(SLEEP_INT)


## this goes in some catch clause as we don't have a clean way to exit
cursor.close()
cnx.close()
