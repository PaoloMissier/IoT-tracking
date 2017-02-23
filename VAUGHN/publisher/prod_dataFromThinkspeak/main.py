import paho.mqtt.client as mqtt
from bs4 import BeautifulSoup
import urllib
import json
import time
import sys
import requests
from datetime import datetime

BROKER_HOST = ""

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
    response = urllib.urlopen(url)
    data = json.loads(response.read())
    return data


# input: param tag, scrap webpage to get channel link return
# return: dict {tag : [channels]}
def getChannelLinks(tag):
    # requests.get('https://github.com', verify='/path/to/certfile') // need to verify cert for later
    fullList = list()
    pageIncrement = 1
    while True:
        pageList = list()
        url = 'https://thingspeak.com/channels/public?page={}&tag={}'.format(pageIncrement, tag)
        r = requests.get(url, verify=False) #skip cert check for now
        soup = BeautifulSoup(r.text, "html.parser")
        data = soup.find_all('a', class_='link-no-hover')
        for link in soup.find_all('a', class_='link-no-hover'):
            # get link only the channel link
            pageList.append(link.get('href'))
        if not pageList:
            break
        fullList.extend(pageList)
        print(pageList)
        pageIncrement += 1
    return {tag: pageList}


# input: dict {tag:[list of channels]}
# return : result code
# desc: publish all channels given in the dict {tag:[list of channels]}
def machineGun(ammo):

    for tag in ammo.keys():
        for channelLink in ammo[tag]:
            clientName = 'Thinkspeak_{}'.format(channelLink)
            client = initClient(clientName)
            client.connect(BROKER_HOST)

            url = "https://thingspeak.com{}/feed.json".format(channelLink)
            webCh = getJSON(url)
            webChID = webCh["channel"]["id"]
            webChLastEntry = webCh["channel"]["last_entry_id"]
            fieldMap = {}
            for field in webCh["channel"].keys():
                if "field" in field:
                    fieldMap[field] = webCh["channel"][field]

            # open local json
            with open('localdata.json') as json_file:
                json_decoded = json.load(json_file)

            localChLastEntry = json_decoded["data"][tag][webChID]["last_entry_id"]

            if webChLastEntry <= localChLastEntry: continue

            for feedCounter in range(0, len(webCh["feeds"])):
                webEntryID = webCh["feeds"][feedCounter]["entry_id"]
                if webEntryID > localChLastEntry:
                    for f in fieldMap.keys():
                        topic = '{}/{}/{}'.format(tag, webEntryID, fieldMap[f])
                        client.publish(topic, str(webCh["feeds"][feedCounter][f]))
                        client.loop(timeout=1.0, max_packets=1)

            # update local json
            json_decoded["data"][tag][webChID]["last_entry_id"] = webChLastEntry
            with open(json_file, 'w') as json_file:
                json.dump(json_decoded, json_file)


def main(argv):
    BROKER_HOST = str(argv) # set the ipaddress of the brokerhost
    while True:
        ammo = list()
        tags = list()  # get from text file
        file = open("tags.txt", "r")
        for line in file:
            tags.append(line)

        for tag in tags:
            ammo.append(getChannelLinks(tag))
        machineGun(ammo)
        time.sleep(40)


if __name__ == '__main__':
   main(sys.argv[1]) #bring in ipaddress of the broker
