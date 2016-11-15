#!/usr/bin/env python

import paho.mqtt.client as mqtt
from random import random, randint
from time import sleep
from datetime import datetime
import logging
import mysql.connector

logger = logging.getLogger('Publisher')
logger.setLevel(logging.DEBUG)
logger.handlers = []
ch = logging.StreamHandler()
ch.setFormatter(logging.Formatter('%(asctime)s %(levelname)s %(message)s'))
logger.addHandler(ch)


CLIENT_ID = "s1"
sep = '|'
datetimeFormat = "%y%m%d%H%M%S%f"

TOPICS = ["root/t1", "root/t2", "root/t3", "root/t4"]

pid = 0
# The callback for when the client receives a CONNACK response from the server.
def on_connect(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))

def on_disconnect(client,  userdata,  rc):
    print("Client disconnected with result code "+str(rc))
    
def on_publish(client, userdata, mid) :
	print("publish done with [client = {c}, userdata={ud}, mid={m}]".format(c=client._client_id, ud=userdata, m=mid))
	print("logging prov event:  packet {p_id} wasGeneratedBy {cid}".format(p_id=pid, cid=client._client_id))


def injectMD( (CLIENT_ID, dataID, timestamp, topic), payload) :
	sep ='|'
	# add sensor ID
	# add timestamp
	# pack payload into a bytearray
	return CLIENT_ID + sep + dataID + sep + timestamp + sep + str(payload)
	## TODO this must become a bytearray encoding 


def DBWrite( md ):
	cursor.execute(add_PROD_msg, md)
	cnx.commit()
	logger.debug("mysql commit successful")



#########
##  MAIN BODY
#########

## init DB connection and acquire context
cnx = mysql.connector.connect(user='paolo', password='riccardino', host='127.0.0.1', database='BrokerTracker')
cursor = cnx.cursor()
add_PROD_msg = ("insert into PROD (`PRODid`, `dataID`, `timestamp`, `topic`) values (%s, %s, %s, %s)")
logger.debug("mysql connection successful")


client = mqtt.Client(client_id=CLIENT_ID)
client.on_connect = on_connect
client.on_publish = on_publish

client.connect("localhost")
client.loop_start()


mySQLTest()
 
while True:
    payload = random()
    topic = TOPICS[randint(0,len(TOPICS)-1)]
    
    md = (CLIENT_ID, genDataID(), datetime.strftime(datetime.utcnow(), datetimeFormat), topic )
    
    payload = injectMD(md, payload)
    client.publish(topic, str(payload))
    print("published value {}\n on topic {}".format(payload,  topic))
    
    DBWrite(md)
    sleep(2)


## this goes in some catch clause as we don't have a clean way to exit
cursor.close()
cnx.close()
