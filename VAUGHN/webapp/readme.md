
## Getting Started

These instructions will get you to run the django webapp.

## Prerequisites

* [Cassandra Python Driver from DataStax](https://github.com/datastax/python-driver)
* [Cassandra](http://cassandra.apache.org/)
* [Pyenv](https://github.com/pyenv/pyenv) - With Python3.6.1 installed

### Ubuntu
I used python virtual environment so that we don't modify the default python version of the VM.
It is becaused that I code in python 3.6 and require the latest python 3.6 to run easily.
For example the import lib causing problem in old version of python.
Install pyenv and look at the installation for pyenv and make sure pyenv is working.
Also have a look at pyenv [common problems](https://github.com/pyenv/pyenv/wiki/Common-build-problems)

```
$ pip install mysql-connector==2.1.4
$ pip install cassandra-driver
$ pip install pandas
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

### Running
```
$ cd webapp
$ python manage.py runserver 10.3.2.4:8000
```

## Authors

* **Vaughn Chong** - *Initial work* - [phantomlinux](https://github.com/phantomlinux)

See also the list of [contributors](https://github.com/PaoloMissier/IoT-tracking/graphs/contributors) who participated in the whole project.
