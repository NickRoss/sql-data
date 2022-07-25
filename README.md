# sql-data

This repository contains the tables used in Nick Ross's [SQL Course](https://www.nickross.site/datamanagement/). Specific information on the data sources can be found in this repository.

This repository contains two other things. First, a docker image which can be used rather than installing postgres itself. There are also a number of associated scripts which process and load the raw data. Information on data changes are documented in this file (and in the code itself).


## Iowa Cars Data

The Iowa Cars Data can be found [here](https://data.iowa.gov/Transportation-Operations/Iowa-Fleet-Summary-By-Year-County-And-Vehicle-Type/6rrx-2vwt). Per the website, this was the version released on February 8th, 2022. 

There were a few revisions made to the data. Specifically the county name "O'Brien" had two spelling variants in the data (due to opening vs. straight single quotes). Secondly, rows with "No County" were removed. 

Finally, a number of columns are dropped from the original data ( Year Ending, County FIP, Feature ID, Primary County Lat, Primary County Long, and Primary County Coordinates) while a column (CompleteCategory) was created which is a combination of Vehicle Type and Tonnage.

