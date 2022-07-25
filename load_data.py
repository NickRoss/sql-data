### This loads data into postgres for the course
import psycopg2
import glob
import csv
import pandas as pd
host = 'localhost'
user_name = 'postgres'
password = 'postgres'
dbname = 'sql_class'

conn_string = "host='%s' dbname='%s' user='%s' password='%s'" % (host, dbname, user_name, password)
postgres_conn = psycopg2.connect(conn_string)

holiday_list = ['27-May-2002' , '04-Jul-2002' , '02-Sep-2002' , '28-Nov-2002' , '25-Dec-2002', '01-Jan-2003'
, '20-Jan-2003', '17-Feb-2003', '18-Apr-2003', '26-May-2003', '04-Jul-2003', '01-Sep-2003', '27-Nov-2003', '25-Dec-2003'
,'01-Jan-2010', '18-Jan-2010', '15-Feb-2010', '02-Apr-2010', '31-May-2010', '05-Jul-2010', '06-Sep-2010', '25-Nov-2010', '24-Dec-2010'
, '17-Jan-2011' ,'21-Feb-2011', '22-Apr-2011', '30-May-2011', '04-Jul-2011', '05-Sep-2011', '24-Nov-2011', '26-Dec-2011']

control_dict_list = [
    {'schema' : 'stocks', 'tablename' : 's2010', 'file' :  'raw_data/stocks/2010.tdf'}
    , {'schema' : 'stocks', 'tablename' : 's2011', 'file' :  'raw_data/stocks/2011.tdf'}
    , {'schema' : 'stocks', 'tablename' : 'fnd', 'file' : 'raw_data/stocks/fnd.tdf'}
    , {'schema' : 'cls', 'tablename' : 'cars', 'file' : 'raw_data/iowa_cars.tdf'} 
    , {'schema' : 'cls', 'tablename' : 'mta', 'file' : 'raw_data/mta/MTA_Hourly.tdf'}
    , {'schema' : 'cls', 'tablename' : 'null_test', 'file' : 'raw_data/in_class/null_test.tdf'}
]

def run_sql_commands(cmds, conn):
    Scur = conn.cursor()
    for x in cmds:
        try:
            Scur.execute(x)
            conn.commit()
        except psycopg2.ProgrammingError:
            print( """CAUTION FAILED: '%s' """ % x)
            conn.rollback()
    return None

def combineNN(year, inputdir):
    ### This function will take all the CSV Files for a particular year and return them, with all headers removed
    output = []
    for x in ['NASDAQ', 'NYSE']:

        filestoprocess = glob.glob(inputdir + '/' + x + year + '/*.csv')
        print(x, year)
        for fl in filestoprocess:
            
            with open(fl, 'r') as csvfile:
                flreader = csv.reader(csvfile)
                next(flreader)
                for row in flreader:
                    if row[1] in holiday_list:
                        pass
                    else:
                        row.append(x)
                        output.append(row)
    return output

def writeNYSE(data, outputfile):
    with open(outputfile, 'w') as tdffile:
        flwriter = csv.writer(tdffile, delimiter='\t')
        flwriter.writerows( data )

### Schemas
create_schema_commands = ["""CREATE SCHEMA IF NOT EXISTS cls;""", """CREATE SCHEMA IF NOT EXISTS stocks;"""]
run_sql_commands( create_schema_commands, postgres_conn)

### Creating Tables

drop_tables =["""drop table if exists stocks.s2010;""" 
, """drop table if exists stocks.s2011;"""  
, """drop table if exists stocks.fnd;"""
, """drop table if exists cls.cars;"""
, """drop table if exists cls.mta;"""
, """drop table if exists cls.null_test;"""]

run_sql_commands( drop_tables, postgres_conn)

create_tables = [ """create table stocks.s2010 (
        symb varchar(6)
        , retdate date
        , opn float
        , high float
        , low  float
        , cls float
        , vol int
        , exch varchar(8));"""
, """create table stocks.s2011 (
        symb varchar(6)
        , retdate date
        , opn float
        , high float
        , low  float
        , cls float
        , vol int
        , exch varchar(8));"""
, """create table stocks.fnd (
        gvkey varchar(8)
        , datadate date
        , fyear int
        , indfmr varchar(4)
        , consol varchar(1)
        , popsrc varchar(1)
        , datafmt varchar(3)
        , tic varchar(8)
        , cusip varchar(11)
        , conm varchar(30)
        , fyr int
        , cash float
        , dp float
        , ebitda float
        , emp float
        , invt float
        , netinc float
        , ppent float
        , rev float
        , ui float
        , cik varchar(10)
    );"""
, """create table cls.cars (
    year int
    , countyname varchar(20)
    , motorvehicle varchar(3)
    , vehiclecat varchar(15)
    , vehicletype varchar(55)
    , tonnage  varchar(30)
    , registrations int
    , annualfee float
    , completecategory varchar(90)
);""", 
"""create table cls.mta (
    plaza int
    , mtadt date
    , hr int
    , direction varchar(1)
    , vehiclesEZ int
    , vehiclesCASH int);""",
"""create table cls.null_test (
    val int, cond varchar(1));"""]

run_sql_commands(create_tables, postgres_conn)

### Process stock data
writeNYSE(combineNN('2010', 'raw_data/stocks'), 'raw_data/stocks/2010.tdf')

writeNYSE(combineNN('2011', 'raw_data/stocks'), 'raw_data/stocks/2011.tdf')

### Process Iowa Cars Data
## Removes some unnessary columns and adds a column with complete category information.
raw_cars_data = (pd.read_csv('raw_data/iowa_cars/Iowa_Fleet_Summary_By_Year__County_And_Vehicle_Type.tsv', sep='\t')
                 .drop(['Primary County Lat','Feature ID', 'County FIP', 'Year Ending', 'Primary County Long', 'Primary County Coordinates'], axis=1)
                )
raw_cars_data.loc[:, 'CompleteCategory'] = raw_cars_data.loc[:, 'Vehicle Type']
raw_cars_data.loc[ ~(raw_cars_data.Tonnage.isna()), 'CompleteCategory'] = raw_cars_data.loc[ ~(raw_cars_data.Tonnage.isna()), 'CompleteCategory'] + ' -- ' + raw_cars_data.loc[ ~(raw_cars_data.Tonnage.isna()), 'Tonnage']
raw_cars_data.loc[ (raw_cars_data.loc[:, 'County Name'] == 'O’Brien'), 'County Name'] = "O'Brien"
raw_cars_data = raw_cars_data.loc[ (raw_cars_data.loc[:, 'County Name'] != 'No County'), :].copy()
raw_cars_data.to_csv( 'raw_data/iowa_cars.tdf', header=False, sep='\t', index=False)

### Load all data into SQL

def load_data_from_control_dict_list( control_dict_list, postgres_conn ):
    SQL_STATEMENT = """
        COPY %s FROM STDIN WITH
            CSV        
            DELIMITER AS E'\t';
        """    
    cursor = postgres_conn.cursor()
    for tbl in control_dict_list:
        tablename = tbl['schema'] + '.' + tbl['tablename']
        my_file = open(tbl['file'])
        cursor.copy_expert(sql=SQL_STATEMENT % tablename, file=my_file)
        postgres_conn.commit()

load_data_from_control_dict_list( control_dict_list, postgres_conn)

