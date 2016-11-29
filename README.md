# IoT-tracking
IoT data tracking experiments with MQTT


starting moquitto broker:

**mosquitto -c /usr/local/etc/mosquitto/mosquitto.conf**

Publisher:

**publisher.py -n -t \<topics count> -p \<publishers count> -r \<msg generation rate (sec)>**

where: <br/>
-p \<publishers count>  number of publishers  <br/>
-t \<topics count>  generate n random topics. Each publisher may generate messages on each of the topics <br/>
-r \<msg generation rate (sec) <br/>
-n: do not write to DB

Subscriber:

**subscriberLauncher.py -n -t \<topics count> -s \<subscribers count>**

where: </br>
-s \<subscribers count>  number of subscribers  <br/>
-t \<topics count>  subscribers subscribe to n random topics. This number should match the number of topics used by the publishers<br/>
-n: do not write to DB
