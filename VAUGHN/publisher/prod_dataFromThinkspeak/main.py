import paho.mqtt.client as mqtt
import urllib
import json
import time
import sys
from datetime import datetime

BROKER_HOST = ""
topic = "root/temperature/ext"

def on_connect(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))

def on_message(client, userdata, msg):
    print(msg.topic+" "+str(msg.payload))

def main(argv):
    BROKER_HOST = str(argv)
    client = mqtt.Client(client_id="Thingspeak_Public_IoT", clean_session=True, userdata=None, protocol="MQTTv31")
    client.on_connect = on_connect
    client.on_message = on_message

    old_dt = datetime.today()
    client.connect(BROKER_HOST)

    while True:
        print("enter while")
        url = "https://thingspeak.com/channels/75183/field/3.json"
        response = urllib.urlopen(url)
        data = json.loads(response.read())

        for new_dt_counter in range(0, len(data["feeds"])):
            new_dt = datetime.strptime(data["feeds"][new_dt_counter]["created_at"], '%Y-%m-%dT%H:%M:%SZ')
            if new_dt > old_dt:
                print(data["feeds"][new_dt_counter])
                # publish(topic, msg, qos)
                client.publish(topic, str("2017-01-30T06:22:26Z"+"_"+"8.00'c"))
                #client.publish(topic, str(data["feeds"][new_dt_counter]["created_at"]+"_"+data["feeds"][new_dt_counter]["field3"]+"'c"), 1)
                old_dt = new_dt
                client.loop(timeout=1.0, max_packets=1)

        time.sleep(60)

if __name__ == '__main__':
   main(sys.argv[1])




