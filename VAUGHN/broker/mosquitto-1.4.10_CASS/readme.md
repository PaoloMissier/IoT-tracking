
## Getting Started

These instructions will get you to build this patched Mosquitto Broker. Original Mosquitto [README.md](readme_mosquitto.md)

## Prerequisites

[Cassandra C/CPP Driver from DataStax](https://datastax.github.io/cpp-driver/)

### Ubuntu
```
$sudo apt install libssl-dev uuid-dev libc-ares-dev cmake libuv-dev build-essential
$sudo apt install libwebsocket* libwebsocketpp-dev libwebsockets7
$sudo apt install cassandra
```

Download and Build the Cassandra C/cpp-driver
```
$git clone https://github.com/datastax/cpp-driver.git
$mkdir cpp-driver/build
$cd cpp-driver/build
$cmake ..
$make
$sudo make install
```
Take note of the installation path, mine was /usr/local/lib/x86_64-linux-gnu for libraries file and /usr/local/include for the header file
```
$sudo nano /etc/ld.so.conf.d/lib64c.conf
```
Add /usr/local/lib/x86_64-linux-gnu into the file and save it. Then update ldconfig. This will add new symlink for Cassandra shared libraries
```
$ sudo ldconfig
```

Make sure Cassandra server is installed and database is ready (keyspace 'brokertracker', table 'CNT')
```
CREATE TABLE brokertracker.cnt (
    prodid text,
    consid text,
    date date,
    time time,
    topic text,
    PRIMARY KEY (prodid, consid, date, time, topic)
)
```


### Build and Install

Modify Database Config
1. Download/Clone the repository
2. Locate file 'database.c' in src folder
3. Edit the cassandra database connection config(contact point and keyspace)
    - line 859/862 + 'database.c'
4. Save the files

Add Build Libraries

1. Locate Makefile config 'config.mk'
2. Append the flags to according line 111(CFLAGS) and line 123(LIBS)
3.  - line 112 CFLAGS : -I/usr/local/include (The location where cassandra.h installed)
    - line 122 BROKER_LIBS : -L/usr/local/lib/x86_64-linux-gnu -lcassandra (where the shared libraries installed)

Remove Any Object files, build and install via terminal
```
1. $ cd Mosquitto-1.4.10/
2. $ make clean
3. $ make
4. $ sudo make install
5. $ mosquitto -v
```

## Authors

* **Vaughn Chong** - *Initial work* - [phantomlinux](https://github.com/phantomlinux)

See also the list of [contributors](https://github.com/PaoloMissier/IoT-tracking/graphs/contributors) who participated in the whole project.
