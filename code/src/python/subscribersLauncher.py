#!/usr/bin/env python

import paho.mqtt.client as mqtt
from datetime import datetime
import logging
import mysql.connector
from random import random, randint

from threading import Thread
from multiprocessing import Process, Pool
from subscriber import Subscriber


VAS_ID_LIST  = ["VAS_1","VAS_2","VAS_3","VAS_4", "VAS_5"]

## move to a constants module share with publisher.
## These are the available topics that producers and consumers both know about
TOPICS = ["root/t1", "root/t2", "root/t3", "root/t4", "root/t5", "root/t6", "root/t7"]
MAXTOPICS = 4


#########
### MAIN 
## launches len(VAS_ID_LIST) threads one for each VAS
#########

def launch(VAS_ID):
	sub = Subscriber(VAS_ID)

	subList = []
	for i in range(MAXTOPICS-1):
		added = False
		while not added:
			t = TOPICS[randint(0,len(TOPICS)-1)]
			if (t not in subList):
				subList.append(t)
				added = True
	sub.setTopics(subList)
	sub.subLoop()


if __name__ == '__main__':
	with Pool(processes=len(VAS_ID_LIST)) as pool:
		pool.map(launch, VAS_ID_LIST)

