# sql-data

This repository contains the tables used in Nick Ross's [SQL Course](https://www.nickross.site/datamanagement/). Specific information on the data sources can be found in this repository.

For this class you will need to set up a local version of PostgresSQL that you can work off of. Any version of PostgresSQL 14+ should work for the course (and honestly older ones _should_ work too, but they haven't been tested). There are two common ways that you can use this repository.

1. (Preferred way) You can install this via [docker](https://www.docker.com/)
1. You can install [PostgresSQL](https://www.postgresql.org/) directly.

If you choose the second method you are a bit on your own. Installing PostgresSQL is difficult and very system dependent. If you choose this method there are some hints at the end of the document.

This repository contains multiple things. There is a docker image which can be used to run a PostgresSQL server rather than loading the data itself.There are also a number of associated scripts which process and load the raw data. Information on data changes are documented in this file (and in the code itself).

Complete data dictionaries can be found in the Appendix of the notes provided for the course.

A common hurdle when installing PostgreSQL for this class is trying to remember if you have installed it previously. If you have installed it previously, but do not remember why or how, it is recommended to uninstall whatever you currently have and begin fresh. 

PostgresSQL uses [port](https://www.cloudflare.com/learning/network-layer/what-is-a-computer-port/) 5432 as its default location on your computer. If you have it installed already, PostgresSQL is probably using the port and trying to install another version (either via docker or directly) will create a conflict and lead to issues. 

### First step: Determine if PostgresSQL is already installed or not

How do I know if PostgresSQL is already installed? 

It is quite difficult, but really important to try to determine if PostgresSQL is already installed. While there is no perfect method for identifying if it was installed or not, there are a few ways that you can test.

#### On Mac / Linux systems

1. Use `ps` to look for a `postgres` process. When I run the command `ps -ax | grep postgres` on the command line I see someting like the below:
```
nickross@nickrosss-Air sql-data % ps -ax | grep postgres
98704 ??         0:00.04 /opt/homebrew/opt/postgresql@14/bin/postgres -D /opt/homebrew/var/postgresql@14
98708 ??         0:00.00 postgres: checkpointer
98709 ??         0:00.00 postgres: background writer
98710 ??         0:00.00 postgres: walwriter
98711 ??         0:00.00 postgres: autovacuum launcher
98712 ??         0:00.00 postgres: stats collector
98713 ??         0:00.00 postgres: logical replication launcher
98751 ttys000    0:00.01 grep postgres
``` 
The process at the bottom refers to the command I'm currently running, but the other processes (ids 98704, 98708-13) refer to processes associated with PostgresSQL.

2. Check to see if there is something running on the default PostgresSQL TCP port of 5432. The command `lsof -i -n -P | grep TCP | grep 5432` will identify them. When I run it on my machine when PostgresSQL is running I see:
```
nickross@nickrosss-Air sql-data % lsof -i -n -P | grep TCP | grep 5432
postgres  98704 nickross    7u  IPv6 0x16c810b99448ebad      0t0  TCP [::1]:5432 (LISTEN)
postgres  98704 nickross    8u  IPv4 0x16c810afed5d2ce5      0t0  TCP 127.0.0.1:5432 (LISTEN)
```

Importantly none of the above methods are full proof. There are (very uncommon) methods of installing this software which will not be caught by the above. 

#### On Windows Machines

I do not have access to a windows machine, but there is a similar tool in windows to get a list of [processes](https://superuser.com/questions/914782/how-do-you-list-all-processes-on-the-command-line-in-windows) as well as a tool to get a list of ports that [are being used](https://help.extensis.com/hc/en-us/articles/360010122594-Identifying-ports-in-use-on-macOS-and-Windows)

### If PostgresSQL is already installed

If PostgresSQL is already installed then you need to either uninstall it and follow the directions below or use that installation and load the data directly, either using the scripts in this repository or the SQL commands that can be found in the text provided in class.

Unless you are actively using PostgresSQL for a project and have the current login information I would strongly recommend you uninstall it and start fresh.

If you are on Mac and installed PostgreSQL via homebrew you can simply turn the service off using the command `brew services stop postgersql@[WHATEVER VERSION YOU HAVE INSTALLED`. This will not uninstall it, but just shut it down. At the end of this course you can turn it on by using `brew services start postgresql@[WHATEVER VERSION]`. To get the version you have installed use `brew list`.

## How to use install PostgreSQL via docker

This repository users docker in order run a detached version of the PostgresSQL database. There are a few helper scripts, which are described below.

Before running anything, you need to set the following environment variables. 

* PGUSER (postgres)
* PGDATABASE (sql_class)
* PGPASSWORD (postgres)
* PGHOST (localhost)

For example, in my `~/.zshrc` file, the following lines can be found:

```
export PGHOST=localhost
export PGDATABASE=sql_class
export PGUSER=postgres
export PGPASSWORD=postgres
```

which sets these varaibles to the default values. I only run this locally so the username and password being set as they are is fine. However if you are planning on using this on public networks, etc. I strong recommend using a different username and password combination. It is *strongly* recommended that, if you choose to use this option that you change the username and password to something a bit more secure.

You also need to install docker and docker-compose (v2). For information on how to do this, please start [here](https://docs.docker.com/compose/install/). Make sure that you **enable docker compose V2.**

If you are unfamiliar with docker, I strongly recommend you take a look at [this docker tutorial](https://docker-curriculum.com/) which I have found to be the most straightforward way to jump into docker/docker-compose.

Assuming that everything is installed there is a bash script `init.sh` which _should_ start when the database initalizes. This script creates all necessary schemas and tables as well as loading all of the required data.

The script will run a docker container in the background which has all the data for the course. The connection string and connection information are set by the environment variables. 

The most common issue that has been found with the scripts herein is that the python environment is not installed correctly. In that case you will run into errors about finding packages, etc. In this case you need to make sure that your pip and python executables align properly.

## Common problems and solutions

### I get an error about pip3 not found

The `init.sh` script assumes that pip3 is how to install packages. If you use conda or pip as an alias you'll need to remove the `pip3 install` line from `init.sh` and either install the contents of `requirements.txt` by hand or replace that line with the appropriate package management tool.

### How do I know if the container is running? 

You can type in `docker ps`  at the terminal and you should see a process with a NAME that looks like `sql-data-db_postgres_class-1`. 

### How do I start the container?

You can always type `docker-compose up -d` in order to start the container.

## How do I stop the container?

You can type `docker-compose down` (making sure to be in the correct directory) and that will stop the container. 

## I'm getting an error about root

You may see an error of the form ```sql-data-db_postgres_class-1  | 2023-03-22 19:25:13.953 UTC [2389] FATAL:  role "root" does not exist```

this is a known bug and a to-do to fix. It does not effect the performance or access.

# Data Sources

## Iowa Cars Data (cls.cars)

The Iowa Cars Data can be found [here](https://data.iowa.gov/Transportation-Operations/Iowa-Fleet-Summary-By-Year-County-And-Vehicle-Type/6rrx-2vwt). Per the website, this was the version released on February 8th, 2022. 

There were a few revisions made to the data. Specifically the county name "O'Brien" had two spelling variants in the data (due to opening vs. straight single quotes). Secondly, rows with "No County" were removed. 

Finally, a number of columns are dropped from the original data (Year Ending, County FIP, Feature ID, Primary County Lat, Primary County Long, and Primary County Coordinates) while a column (CompleteCategory) was created which is a combination of Vehicle Type and Tonnage.

## 2010 Stock Data (stocks.s2010)

## 2011 Stock Data (stocks.s2011)

These two tables provide information about NYSE and NASDAQ stock returns from 2010 and 2011. 

## Fundamental Data (stocks.fnd)

This table provides information about 2010 and 2011 fundamental information. Fundamental Information is data (usually) reported in a 10K. 

## MTA Data (cls.mta)

The MTA data can be found [here](https://catalog.data.gov/dataset/hourly-traffic-on-metropolitan-transportation-authority-mta-bridges-and-tunnels-beginning-). Per the website, this is _not_ the current version, but an earlier version.
