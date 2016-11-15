#!/usr/bin/env python

import paho.mqtt.client as mqtt
from datetime import datetime
import logging

logger = logging.getLogger('Subscriber')
logger.setLevel(logging.DEBUG)
logger.handlers = []
ch = logging.StreamHandler()
ch.setFormatter(logging.Formatter('%(asctime)s %(levelname)s %(message)s'))
logger.addHandler(ch)



TOPICS = ["root/t1", "root/t2", "root/t3", "root/t4"]
sep = '|'
datetimeFormat = "%y%m%d%H%M%S%f"

# The callback for when the client receives a CONNACK response from the server.
def on_connect(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))    
    client.subscribe([(t,0) for t in TOPICS])
    
def on_disconnect(client,  userdata,  rc):
    print("Client disconnected with result code "+str(rc))

# The callback for when a PUBLISH message is received from the server.
def on_message(client, userdata, msg):
	(client_id, ts, payload) = extractMD(msg.payload)
	print("msg from client {c}:\ntopic {t}\npayload {p}\nts {ts}".format(c=client_id, t=msg.topic, p=payload, ts=ts))


def extractMD(payloadBytes):
	
	payload = payloadBytes.decode("utf-8")
	
	sep ='|'
	parts = payload.split('|')
	print("extract: *** \npayload: {}\nparts:{}".format(payload,parts))
	client_id = parts[0]
	ts = datetime.strptime(parts[1],datetimeFormat)
	payload = parts[2]
	return (client_id, ts, payload)
		


client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message

client.connect("localhost")
client.loop_forever()

