# Project Title

A complete testbed on Experiments in tracking Personal Data from the Internet of Things for Data Contracts

## Getting Started

These instructions will get you a copy of the project up and running on your local machine for development and testing purposes. See deployment for notes on how to deploy the project on a live system.

## Prerequisites

Install Prerequisites through terminal

### Ubuntu VM / Raspberry Pi for Mosquitto Broker
For Raspberry Pi use 'sudo apt-get'
```
sudo apt install build-essential python quilt devscripts python-setuptools python3
sudo apt install libssl-dev uuid-dev libc-ares-dev cmake libmysqlclient-dev
sudo apt install libwebsocket* libwebsocketpp-dev libwebsockets7
sudo apt install mysql-server mysql-client
```
Make sure mysql-server is installed and database is ready (database model 'Tracking-DB-model-mysql.mwb')

## Installing

There are 3 components to be setup. Mosquitto Broker, Paho Python Publisher and Django WebApp

### Mosquitto Broker
```
Modify Database Config
1. Download/Clone the repository
2. Locate both the file 'database.c' 'read_handle.c'  in src folder
3. Edit the database config(username, password, mysql-server destination, db name)
    - line 231 + 'read_handle.c'
    - line 843 + 'database.c'
4. Save the files

Add Build Libraries
1. Go to terminal and execute these 2 commands
    $ mysql_config --libs
    $ mysql_config --cflags

    Example
    (libs) -L/usr/lib/x86_64-linux-gnu -lmysqlclient -lpthread -lz -lm -lrt
    (cflags) -I/usr/include/mysql -fdebug-prefix-map=/build/mysql-5.7-L3SQl5/mysql-5.7-5.7.16=. -fabi-version=2 -fno-omit-frame-pointer

2. Locate Makefile config 'config.mk'
3. Append the flags to according line 111(CFLAGS) and line 123(LIBS)
4. (Raspberry Pi)
    Symlink 'libmysqlclient.a'
    $ sudo ln -s /usr/lib/arm-linux-gnueabihf/libmysqlclient.so.18        /usr/local/lib/libmysqlclient.so.18
    $ sudo ln -s /usr/lib/arm-linux-gnueabihf/libmysqlclient.a /usr/local/lib/libmysqlclient.a

Remove Any Object files
1. $ cd Mosquitto-1.4.10/
2. $ find . -type f -name '*.o' -delete

Build & Install via terminal
1. $ cd Mosquitto-1.4.10/
2. $ sudo make
2. $ sudo make install
3. $ mosquitto -v
```

### Python Publisher
```
1. $ cd publisher/prod_dataFromThinkspeak/
2. python3 main.py 'broker ip address'
```

### Web Application
Start web app
```
1. $ cd webapp/
2. $ python3 manage.py runserver
3. Navigate to browser 127.0.0.1/home/
```

## Running the tests

N/A

## Deployment

Add additional notes about how to deploy this on a live system

## Built With

* [Django](https://www.djangoproject.com) - The python web framework
* [Bootstrap](http://getbootstrap.com) - Front end web template
* [Python3](https://www.python.org/download/releases/3.0/) - Python 3
* [Paho](https://eclipse.org/paho/) - MQTT Client Library
* [Mosquitto](https://mosquitto.org) - MQTT Broker Library

## Authors

* **Vaughn Chong** - *Initial work* - [phantomlinux](https://github.com/phantomlinux)

See also the list of [contributors](https://github.com/PaoloMissier/IoT-tracking/graphs/contributors) who participated in the whole project.
