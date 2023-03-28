# sql-data

This repository contains the tables used in Nick Ross's [SQL Course](https://www.nickross.site/datamanagement/). Specific information on the data sources can be found in this repository.

This repository contains multiple things. There is a docker image which canbe used to run a postgres server rather than loading the data itself.There are also a number of associated scripts which process and load the raw data. Information on data changes are documented in this file (and in the code itself).

Complete data dictionaries can be found in the Appendix of the notes provided for the course.

## How to use this repository

This repository users docker in order run a detached version of the postgres datababse. There are a few helper scripts, which are described below.

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

Finally, a number of columns are dropped from the original data ( Year Ending, County FIP, Feature ID, Primary County Lat, Primary County Long, and Primary County Coordinates) while a column (CompleteCategory) was created which is a combination of Vehicle Type and Tonnage.

## 2010 Stock Data (stocks.s2010)

## 2011 Stock Data (stocks.s2011)

These two tables provide information about NYSE and NASDAQ stock returns from 2010 and 2011. 

## Fundamental Data (stocks.fnd)

This table provides information about 2010 and 2011 fundamental information. Fundamental Information is data (usually) reported in a 10K. 

## MTA Data (cls.mta)

The MTA data can be found [here](https://catalog.data.gov/dataset/hourly-traffic-on-metropolitan-transportation-authority-mta-bridges-and-tunnels-beginning-). Per the website, this is _not_ the current version, but an earlier version.
