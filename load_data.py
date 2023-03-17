#!/usr/bin/env python
### This loads data into postgres for the course
import psycopg2
import glob
import csv
import pandas as pd
import os
import json
import sys
import numpy as np
from datetime import date,timedelta
from random import random,randrange,seed
from scipy.stats import skewnorm,expon
from tqdm import tqdm
from dateutil.relativedelta import relativedelta

holiday_list = ['27-May-2002' , '04-Jul-2002' , '02-Sep-2002' , '28-Nov-2002' , '25-Dec-2002', '01-Jan-2003'
, '20-Jan-2003', '17-Feb-2003', '18-Apr-2003', '26-May-2003', '04-Jul-2003', '01-Sep-2003', '27-Nov-2003', '25-Dec-2003'
,'01-Jan-2010', '18-Jan-2010', '15-Feb-2010', '02-Apr-2010', '31-May-2010', '05-Jul-2010', '06-Sep-2010', '25-Nov-2010', '24-Dec-2010'
, '17-Jan-2011' ,'21-Feb-2011', '22-Apr-2011', '30-May-2011', '04-Jul-2011', '05-Sep-2011', '24-Nov-2011', '26-Dec-2011']

def exp_dist(x,lam):
    exp_dist = expon.pdf(x,1,lam)
    exp_dist = exp_dist/exp_dist.sum()
    return exp_dist

def dist(num):
    r = skewnorm.pdf(a=4,x= range(1,11),loc=num,scale = 2)
    rem = 1- sum(r)
    r[1] += rem
    return r

def generate_soap_data( output_file_name, random_seed = 1 ):

    # Necessary variables
    Coupons = [0, 10, 25, 35]
    LocaleList = ['U.S.', 'Canada', 'Mexico']    
    months = [ None,1,2]
    transaction = ['Single bar', 'Double bar']
    nrows = 1100000

    # Date range between 2017 and 2018 
    x = list(range(1,11))
    start = date(2016,1,1)
    end = date(2018,12,31)
    seed( random_seed )
    finalData = []

    units_no_sub = dist(2)
    units_with_sub = dist(1)

    delta     = end - start
    deltadays = delta.days
    finalData = []
    trytq = True
    print("\n Building Trans Data")
    if trytq : pbar = tqdm(total = nrows+1)
    userid = 1
    x = list(range(1,11))
    i=0

    while(i<nrows):

        rand_draw = random()        

    # Coupon and months
        if rand_draw<=0.65:
            Coupon = Coupons[0]
            months = None
            mntstr = ''

        elif rand_draw >= 0.65 and rand_draw <0.75:
            Coupon = Coupons[1]
            months = int( 1 )
            mntstr = '1'
            
        elif rand_draw >= 0.75 and rand_draw <0.85:
            Coupon = Coupons[3]
            months = int( 2 ) 
            mntstr = '2'
        else:
            Coupon = Coupons[2]
            months = int( 2 )
            mntstr = '2'

    # locale       
        if rand_draw<=.75:
            Locale = 'U.S.'
        elif rand_draw>0.75 and rand_draw<0.9:
            Locale = 'Canada'
        else:
            Locale = 'Mexico'

    # trans
        trans = np.random.choice(transaction)

    # type, units and date

        if rand_draw >=0.65:
            user_rows = np.random.choice(x,p=units_with_sub)
            n_user_rows = user_rows #+ user_rows%months #if months != 1 else 0 # number of times a user shows up        
            Date = start + timedelta(days = randrange(deltadays))
            j = 0        
            if rand_draw >0.95: # multiple records for units different number of units (defined by skewed normal dist) 
                Type = 'Units'
                units = np.random.choice(x,p=units_no_sub)
                finalData.append([i, userid,trans,Type,Locale,Date,int(units),0,None])
                i += 1
                j += 1
                if trytq :pbar.update(1)  
                
            # multiple subscription records 
            Type   = 'Sub'
            units = np.random.choice(x,p=units_with_sub)

            while j <(n_user_rows) and Date<end:
                finalData.append([i + j , userid,trans,Type,Locale,Date,int(units),Coupon,mntstr])
                Date  = Date + relativedelta(months=months)
                j +=1
            i += n_user_rows
            if trytq : pbar.update(n_user_rows)
              
        elif rand_draw <0.1: # Change of locale
            units = np.random.choice(x,p=units_no_sub)
            Type  = 'Units'
            Date  = start + timedelta(days = randrange(deltadays))
            finalData.append([i, userid,trans,Type,Locale,Date,int(units),Coupon,mntstr])
            Locale = np.random.choice(['Canada','Mexico'])
            i +=1
            if trytq : pbar.update(1)
            
        else: # users buying stuff 
            n_user_rows = np.random.choice(x,p=exp_dist(x,1))
            units = np.random.choice(x,p=units_no_sub)
            Type  = 'Units'
            Date = start + timedelta(days = randrange(deltadays))
            j = 0
            while j <(n_user_rows) and Date<end:
                units = np.random.choice(x,p=units_with_sub)

                switchlocale = random()
                if switchlocale < .25:            
                    Locale = np.random.choice( list( set(LocaleList) - set([Locale])))

                finalData.append([i + j, userid,trans,Type,Locale,Date,int(units),Coupon,mntstr])
                # delta_new = end - Date
                Date  = start + timedelta(days = randrange(deltadays))
                j +=1
            i += n_user_rows
            if trytq : pbar.update(n_user_rows)
            
        # userids
        userid +=1

    unit_price = {'Single bar': 11.99,'Double bar': 19.99}

    data = pd.DataFrame(finalData, columns=['orderid', 'Userid','Trans','Type','Locale','Date','Units','Coupons','Months'])
    data['amt'] = round( data['Trans'].apply(lambda x: unit_price[x]) *data['Units']*(1 - data['Coupons']/100), 2)
    data.loc[data['Coupons'] == 0,'Coupons'] = None
    data.to_csv(output_file_name, sep='\t',index=False, header=False)

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

def combine_yearly_stock_files(year, inputdir):
    ### This function will take all the CSV Files for a particular year and return them, with all headers removed
    output = []
    for x in ['NASDAQ', 'NYSE']:

        filestoprocess = glob.glob(inputdir + '/' + x + year + '/*.csv')
        for fl in filestoprocess:
            
            with open(fl, 'r') as csvfile:
                flreader = csv.reader(csvfile)
                next(flreader)
                for row in flreader:
                    if row[1] in holiday_list:
                        ## Holidays have zero volume
                        pass
                    else:
                        row.append(x)
                        output.append(row)
    return output

def write_tdf_file(data, outputfile):
    with open(outputfile, 'w') as tdffile:
        flwriter = csv.writer(tdffile, delimiter='\t')
        flwriter.writerows( data )

def process_stock_data( year ):
    if year == 2010:
        write_tdf_file(combine_yearly_stock_files('2010', 'raw_data/stocks'), 'raw_data/s2010.tdf')
    if year == 2011:
        write_tdf_file(combine_yearly_stock_files('2011', 'raw_data/stocks'), 'raw_data/s2011.tdf')

def process_iowa_data():
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

def load_data_from_control_dict_list(control_dict_list, postgres_conn):
    SQL_STATEMENT = """
        COPY %s FROM STDIN WITH
            CSV        
            DELIMITER AS E'\t';
        """    
    cursor = postgres_conn.cursor()
    tablename = control_dict_list['schema'] + '.' + control_dict_list['tablename']
    my_file = open(control_dict_list['file'])
    cursor.copy_expert(sql=SQL_STATEMENT % tablename, file=my_file)
    postgres_conn.commit()

if __name__ == '__main__':
    
    ## All parameters need to be set an env vars
    pg_parameters = {
        'host' : os.getenv('PGHOST', None)
        , 'user' : os.getenv('PGUSER', None)
        , 'database' : os.getenv('PGDATABASE', None)
        , 'password' : os.getenv('PGPASSWORD', None)
    }

    if len( [x for x in pg_parameters.values() if x is None] ):
        print("Environment Variables Not Set. Expecting PGHOST, PGUSER, PGDATABASE and PGPASSWORD")
        raise Exception("Missing Environment Variable")

    print('Process and Load Data for SQL Class.\n\nDefault Behavior is process and load all data sources.')
    print('To only process and load a specific data source, add the name of the data source as a command line argument.')
    print('Options are: s2010, s2011, fnd, cars, mta, null_test')
    print('Multiple options can be chosen (space delimited)')
    print("\nConnecting to DB...", end = " ")

    conn_string = "host='%s' dbname='%s' user='%s' password='%s'" % (pg_parameters['host'], pg_parameters['database'], pg_parameters['user'], pg_parameters['password'])
    postgres_conn = psycopg2.connect(conn_string)

    print("Connected.")

    print("Loading Control Dicts...", end=" ")

    create_table_dict = json.load( open('control_dicts/create_table.json', 'r'))
    drop_table_dict = json.load( open('control_dicts/drop_table.json', 'r'))
    master_control_dict = json.load( open('control_dicts/master.json', 'r'))

    ## TODO: use master control to build drop table dict.

    print("Control Dicts Loaded.")

    master_process_list = list( master_control_dict.keys() )
    if len(sys.argv) == 1:
        print('No Arguments provided...', end = " ")
        to_process = master_process_list    
    else:
        to_process = sys.argv[1:]
        if len( [x for x in to_process if x not in master_process_list] )> 0: 
            print(f"One of '{' '.join(to_process)}' not in {master_process_list}")

    print(f"Processing and Loading : {' '.join(to_process)}")

    ### Schemas -- this is done no matter what.
    print("Creating Schemas (if they do not exist)...", end=" ")
    create_schema_commands = ["""CREATE SCHEMA IF NOT EXISTS cls;""", """CREATE SCHEMA IF NOT EXISTS stocks;"""]
    run_sql_commands( create_schema_commands, postgres_conn)
    print("Schemas Created.\n")

    ### Dropping Tables
    print("Dropping Tables (if they exist)...", end = " ")
    run_sql_commands( [drop_table_dict[x] for x in to_process], postgres_conn)
    print("Tables Dropped")

    ### Creating Tables
    print("Creating Tables...", end = " ")
    run_sql_commands( [create_table_dict[x] for x in to_process], postgres_conn)
    print("Tables Created")

    for table in to_process:
        print(f"Begining Processing and loading of {table}...", end = ' ', flush=True)

        if table == 'cars' : 
            process_iowa_data()
        elif table == 's2010' : 
            process_stock_data(2010)
        elif table == 's2011' : 
            process_stock_data(2011)
        elif table == 'trans' : 
            generate_soap_data( 'raw_data/soapData.tdf')

        load_data_from_control_dict_list( master_control_dict[table], postgres_conn)

        print(f"Processing of {table} complete")
