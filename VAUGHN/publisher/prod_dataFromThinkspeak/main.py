import paho.mqtt.client as mqtt
from bs4 import BeautifulSoup
import json
import time
import logger
import certifi
import requests
import urllib3

# http = urllib3.PoolManager(cert_reqs='CERT_REQUIRED', ca_certs=certifi.where())

BROKER_HOST = "10.58.46.30"

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
# return: dict {tag : [channels]}
def getChannelLinks(tag):
    fullList = list()
    pageIncrement = 1
    while True:
        pageList = list()
        url = 'https://thingspeak.com/channels/public?page={}&tag={}'.format(pageIncrement, tag)
        log.info("[HTTPS REQUEST] {}".format(url))
        r = requests.get(url, verify=True) #pip installed certifi
        soup = BeautifulSoup(r.text, "html.parser")
        for link in soup.find_all('a', class_='link-no-hover'):
            # get link only the channel link
            pageList.append(str(link.get('href')))
        if not pageList:
            log.info("[HTML PARSER] page empty")
            break
        fullList.extend(pageList)
        log.info("[HTTPS RESULT PARSED] {} ".format(pageList))
        pageIncrement += 1
    return {tag: fullList}


# input: dict {tag:[list of channels]}
# return : result code
# desc: publish all channels given in the dict {tag:[list of channels]}
def machineGun(ammo):

    for tag in ammo.keys():
        for channelLink in ammo[tag]:
            clientName = 'Thinkspeak{}'.format(channelLink.replace("/","_"))
            client = initClient(clientName)
            client.connect(BROKER_HOST)

            url = "https://thingspeak.com{}/feed.json".format(channelLink)
            webCh = getJSON(url)
            webChID = webCh["channel"]["id"]
            webChLastEntry = -1
            try:
                webChLastEntry = int(webCh["channel"]["last_entry_id"])
            except TypeError:
                log.error("[Type Error] webChLastEntry: None")


            fieldMap = {}
            for field in webCh["channel"].keys():
                if "field" in field:
                    fieldMap[field] = webCh["channel"][field]

            localChLastEntry = 0
            json_decoded = {}
            try:
                # open local json
                with open('localdata.json') as json_file:
                    json_decoded = json.load(json_file)

                localChLastEntry = int(json_decoded["data"][str(tag)][str(webChID)]["last_entry_id"])
            except ValueError:
                log.error("[Value Error] JSON decode failed")
            except KeyError:
                log.error("[Key Error] JSON decode failed")

            log.info("Comparing [Web Last Entry]{} vs [Local Last Entry]{}".format(webChLastEntry, localChLastEntry))
            if webChLastEntry <= localChLastEntry: continue

            for feedCounter in range(0, len(webCh["feeds"])):
                webEntryID = webCh["feeds"][feedCounter]["entry_id"]
                if webEntryID > localChLastEntry:
                    for f in fieldMap.keys():
                        topic = '{}/{}/{}'.format(tag, webEntryID, fieldMap[f])
                        print("C: {} T: {}  M: {}".format(clientName, topic, str(webCh["feeds"][feedCounter][f])))
                        client.publish(topic, str(webCh["feeds"][feedCounter][f]))
                        client.loop(timeout=1.0, max_packets=1)

            # update local json
            if "data" not in json_decoded: json_decoded["data"] = {}
            if tag not in json_decoded["data"]: json_decoded["data"][tag] = {}
            if webChID not in json_decoded["data"][tag]: json_decoded["data"][tag][webChID] = {}
            if "last_entry_id" not in json_decoded["data"][tag][webChID]: json_decoded["data"][tag][webChID]["last_entry_id"] = 0

            json_decoded["data"][tag][webChID]["last_entry_id"] = webChLastEntry
            with open('localdata.json', 'w') as json_file:
                json.dump(json_decoded, json_file)
    return 0


def main():
    BROKER_HOST = str(argv) # set the ipaddress of the brokerhost
    while True:
        ammo = {}
        tags = list()  # get from text file
        file = open("tags.txt", "r")
        for line in file:
            tags.append(line.rstrip())

        for tag in tags:
            ammo.update(getChannelLinks(tag))
        if machineGun(ammo) == 0:
            time.sleep(40)


if __name__ == '__main__':
   main(sys.argv[1]) #bring in ipaddress of the broker
   #main()
