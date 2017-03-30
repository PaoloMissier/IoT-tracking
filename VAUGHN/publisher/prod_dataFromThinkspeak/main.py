import paho.mqtt.client as mqtt
from bs4 import BeautifulSoup
import json
import time
import logger
import certifi
import requests
import urllib3
import sys
from datetime import datetime, timedelta

# http = urllib3.PoolManager(cert_reqs='CERT_REQUIRED', ca_certs=certifi.where())

log = logger.create_logger(__name__)

def initClient(clientName):
    client = mqtt.Client(client_id=clientName,
                         clean_session=True,
                         userdata=None,
                         protocol="MQTTv31")  # init
    client.on_connect = on_connect #set connect callback
    client.on_message = on_message #set message callback
    return client


def on_connect(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))


def on_message(client, userdata, msg):
    print(msg.topic+" "+str(msg.payload))


def getJSON(url):
    response = requests.get(url, verify=True)
    data = response.json()
    return data


# input: param tag, scrap webpage to get channel link return
# return: dict {tag : [ "channels/<channelIDs>", "channels/<channelIDs>", ... ]}
def getChannelLinks(tag):
    fullList = list()
    pageIncrement = 1  # start from page 1
    while True:
        pageList = list()
        url = 'https://thingspeak.com/channels/public?page={}&tag={}'.format(pageIncrement, tag)
        log.info("[HTTPS REQUEST] {}".format(url))
        r = requests.get(url, verify=True)  # download webpage page:(N=pageIncrement)
        soup = BeautifulSoup(r.text, "html.parser")
        for link in soup.find_all('a', class_='link-no-hover'):
            # get link only the channel link
            pageList.append(str(link.get('href')))  # add all channel IDs in a page to pageList
        if not pageList:
            log.info("[HTML PARSER] page empty")
            break
        fullList.extend(pageList)  # add all pageList into fullList ()
        log.info("[HTTPS RESULT PARSED] {} ".format(pageList))
        pageIncrement += 1
    return {tag: fullList}


# input: dict {tag:[list of channels]}
# return : result code
# desc: publish all channels given in the dict {tag:[list of channels]}
def publishAll(ammo, BROKER_HOST):

    for tag in ammo.keys():  # loop all tags
        for channelLink in ammo[tag]:  # loops all channel ids

            clientName = 'Thinkspeak{}'.format(channelLink.replace("/","_"))
            client = initClient(clientName)
            try:
                client.connect(BROKER_HOST)
            except ConnectionRefusedError:
                client.disconnect()
                continue

            # this will result https://thingspeak.com/channels/<channel_id>/feed.json
            url = "https://thingspeak.com{}/feed.json".format(channelLink)
            webCh = getJSON(url)
            webChID = webCh["channel"]["id"]
            try:
                webChLastEntry = int(webCh["channel"]["last_entry_id"])  # retrieve lastEntryID from thingspeak json
            except TypeError:
                client.disconnect()
                log.error("[Type Error] webChLastEntry: None")
                continue

            # retrieve fields name
            fieldMap = {}  # example: fieldMap:{ 'field1': Temperature, 'field2':Light ...}
            for field in webCh["channel"].keys():
                if "field" in field:
                    fieldMap[field] = webCh["channel"][field]

            localChLastEntry = 0  # init local lastEntryID
            json_decoded = {}   # init empty dict for local json
            try:
                # read local json: see more at localdata.json
                # Format
                # {'data':
                #           {'light':
                #                      {'channel_id': {'last_entry_id':<id>},
                #                      {'channel_id': {'last_entry_id':<id>},
                #                       ...
                #           }
                #           {'temp':
                #                      {'channel_id': {'last_entry_id':<id>},
                #                      {'channel_id': {'last_entry_id':<id>},
                #                       ...
                #           }
                # }
                with open('localdata.json') as json_file:
                    json_decoded = json.load(json_file)

                # get local json last_entry_id
                localChLastEntry = int(json_decoded["data"][str(tag)][str(webChID)]["last_entry_id"])
            except ValueError:
                log.error("[Value Error] JSON decode failed")
            except KeyError:
                log.error("[Key Error] JSON decode failed")

            #  compare local last entry and new feed last entry id, skip that channel if no new updates
            log.info("Comparing [Web Last Entry]{} vs [Local Last Entry]{}".format(webChLastEntry, localChLastEntry))
            if webChLastEntry <= localChLastEntry:
                client.disconnect()
                continue

            for feedCounter in range(0, len(webCh["feeds"])):  # loop all the feeds (about 40)
                webEntryID = webCh["feeds"][feedCounter]["entry_id"]  # get the entry_id for all the current feeds
                if webEntryID > localChLastEntry:  # on webEntryID > localLastEntryID
                    for f in fieldMap.keys():  # for all the field in fieldMap publish message to broker
                        topic = '{}/{}/{}'.format(tag, webEntryID, fieldMap[f])
                        print("C: {} T: {}  M: {}".format(clientName, topic, str(webCh["feeds"][feedCounter][f])))

                        # make sure don't send (null) terminate to broker, it will mess with my broker memory address
                        # (need to add this fault tolerance in broker side)
                        if str(webCh["feeds"][feedCounter][f]) == "":
                            payload = "Empty"
                        else:
                            payload = str(webCh["feeds"][feedCounter][f])

                        client.publish(topic, payload)
                        client.loop(timeout=1.0, max_packets=1)
                        # time.sleep(1)  # prevent publisher too fast

            client.disconnect()
            # update local json entry_id
            if "data" not in json_decoded: json_decoded["data"] = {}
            if tag not in json_decoded["data"]: json_decoded["data"][tag] = {}
            if webChID not in json_decoded["data"][tag]: json_decoded["data"][tag][webChID] = {}
            if "last_entry_id" not in json_decoded["data"][tag][webChID]: json_decoded["data"][tag][webChID]["last_entry_id"] = 0

            json_decoded["data"][tag][webChID]["last_entry_id"] = webChLastEntry
            with open('localdata.json', 'w') as json_file:
                json.dump(json_decoded, json_file)
    return 0


def main(argv):
    BROKER_HOST = str(argv) # set the ipaddress of the brokerhost
    past = datetime.now() - timedelta(hours=2)
    dictOfTagsToChID = {}
    while True:  # infinite loop
        now = datetime.now()
        tags = list()  # get all the tags from text file (tags.txt)
        file = open("tags.txt", "r")
        for line in file:
            tags.append(line.rstrip())  # add tag into tags

        # compare current time and the previous tag update time
        # this is to prevent update all the tags on every loop as
        # accessing the webpage(thingspeak.com) at this frequency
        # will be block by thingspeak.com
        if (now - past).seconds // 3600 >= 2:
            for tag in tags:
                dictOfTagsToChID.update(getChannelLinks(tag))
            past = now

        if publishAll(dictOfTagsToChID, BROKER_HOST) == 0:
            time.sleep(40)


if __name__ == '__main__':
   main(sys.argv[1]) #bring in ipaddress of the broker
   #main()
