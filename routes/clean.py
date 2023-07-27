from flask import Blueprint
import os
import pandas as pd
from flask import  Flask, redirect, render_template, request, url_for

import sys
sys.path.append('./handlers')

# my mudules
from handlers import dataCleaner as dtCln
from handlers import csvHandler as csvHdl

clean_bp = Blueprint('clean_data', __name__)

@clean_bp.route('/clean_data',methods=("GET", "POST"))
def clean_data():
    # define the df variable
    df = None

    if request.form.get('prompt_type') == "chat":
        prompt_type = "chat"
    else:
        prompt_type = "query"

    # Get the current script's directory
    current_dir = os.path.dirname(os.path.abspath(__file__))
    # Move up one directory to the root folder
    root_dir = os.path.dirname(current_dir)
    # Construct the path to the target file in the root folder
    columnMetadata_df_path = os.path.join(root_dir, 'mod_run_df_columnMetadata.csv')
    running_df_path =  os.path.join(root_dir, 'modified_running_dataframe.csv')
    mydata_path = os.path.join(root_dir, 'mydata.csv')
    
    # LOAD the CSV into a DATAFRAME
    if os.path.isfile(running_df_path):
        #df = pd.read_csv(running_df_path) 
        # opens a modified running dataframe csv, and specifies to what data type each date time type column should be parsed to (based on the column metadata in the corresponding 'mod_run_df_columnMetadata.csv' file)
        df = csvHdl.open_csv_parse_datetime(running_df_path,columnMetadata_df_path)   
        print('running')
    elif os.path.isfile(mydata_path): 
        df = pd.read_csv(mydata_path)
        print('mydata')
    
    # clean the date time data columns and convert them into an int if it's a year type (that's what gpt 4 recommended), or timedelta64 if it's an amount of time, or datetime64 if it's a specific point in time, and there is also a 'Period' date time format that we don't yet cover in our prototype,(when the GPT API returns an answer that says convert it into 'Period' date time type, our system will throw a custom error)
    df = dtCln.df_clean_datetime_columns(df)
    # clean the numerical data columns and convert them into a float data type    
    df = dtCln.df_clean_numeric_columns(df)
    
    # save the "cleaned" dataframe instead of the previous csv, and also saves it's column info (column names and data types, into a seperate csv)
    #df.to_csv('modified_running_dataframe.csv', index=False)
    csvHdl.save_df_with_columnMetadata_csv(df)
    print(df.head())

    return render_template('index.html', prompt_type = prompt_type,result_type = "text_display_radio")