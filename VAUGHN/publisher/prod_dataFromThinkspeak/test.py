
import paho.mqtt.client as mqtt
import time
import sys

BROKER_HOST = ""
topic = "root/temperature/ext/test"

def on_connect(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))

def on_message(client, userdata, msg):
    print(msg.topic+" "+str(msg.payload))

def main(argv):
    BROKER_HOST = str(argv)
    client = mqtt.Client(client_id="Thingspeak_Public_IoT", clean_session=True, userdata=None, protocol="MQTTv31")
    client.on_connect = on_connect
    client.on_message = on_message
    client.connect(BROKER_HOST)

    while True:
        client.publish(topic, str("2017-01-30T06:22:26Z"+"_"+"8.00'c"))
        client.loop(timeout=1.0, max_packets=1)
        time.sleep(30)

if __name__ == '__main__':
   main(sys.argv[1])




