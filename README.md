# sql-data

This repository contains the tables used in Nick Ross's [SQL Course](https://www.nickross.site/datamanagement/). Specific information on the data sources can be found in this repository.

This repository contains two other things. First, a docker image which can be used rather than installing postgres itself. There are also a number of associated scripts which process and load the raw data. Information on data changes are documented in this file (and in the code itself).

Complete data dictionaries can be found in the Appendix of the notes provided for the course.

## How to load the data

The command "load_data.py" (python 3) can be used to load the data into any postgres database. It requires the following environment variables to be set:

* PGUSER
* PGDATABASE
* PGPASSWORD
* PGHOST

Running load_data.py without any arguments will load all datasets. If a list of datasets are provided afterwards on the command line than only those datasets will be loaded. 

## Using Docker for a database

Assuming that docker and docker compose are installed properly, then typing `docker-compose up` in the directory should start a working postgres server which contains the information required for this class. For this instance the username and password are `postgres` and the database name is `sql_class`. It is *strongly* recommended that, if you choose to use this option that you change the username and password to something a bit more secure.

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



