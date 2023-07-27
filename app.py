import os
import openai
from dotenv import load_dotenv
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from flask import  Flask, redirect, render_template, request, url_for
import shutil
from jinja2 import Environment, FileSystemLoader

import sys
sys.path.append('./handlers')

# my modules 
import stringHandler as strHdl 
from handlers import queryHandler as qryHdl
from handlers import dataCleaner as dataCln
from handlers import csvHandler as csvHdl
from handlers import frontendHandler as frntHdl

# routes
from routes.clean import clean_bp



# run this in terminal
# for a hot reaload option of the app (debug mode)
# flask --app app.py --debug run

#(in vs code add): 
# set FLASK_APP=app.py
# 
load_dotenv()

app = Flask(__name__)
openai.api_key = os.getenv("OPENAI_API_KEY")

csv_file = None

# register outer module routes
app.register_blueprint(clean_bp)

# register the 'frntHdl.is_html_table' func in the jinja enviorment, so this func can be used in the jinja frontend
app.jinja_env.globals['is_table'] = frntHdl.is_html_table

# root route
@app.route('/', methods=("GET", "POST"))
def index():

    prompt_type = "query"

    # post request
    if request.method == "POST":

        # reset all the "runtime" variables
        df = None
        database_query_result = ""
        #message = "You are a helpful assistant."

        prompt_type = request.form.get('prompt_type')
        form_name = request.form.get('form_name')
        print(form_name)

        #display very big or very small numbers normally and not in scientific notation
        pd.options.display.float_format = '{:,.2f}'.format

        # prompt form
        if form_name == "prompt":
            
            print("prompt type: " + str(prompt_type)) # verify type
            if prompt_type == "query":
                message = "When you are asked a question about a dataframe, you only return a valid pandas dataframe query without additional explanation. the name of the pandas dataframe is 'df'."


            # query scope
            if prompt_type == "query":
                text = " return a pandas dataframe query that should return an answer to this question: " + request.form['text'] + ". only return the code snippet, without additional explanation!"
                message = "When you are asked a question about a dataframe, you only return a valid pandas dataframe query without additional explanation. the name of the pandas dataframe is 'df'."
            # model scope
            elif prompt_type == "model":
                text = "return python code that creates the following machine machine learning model type in python: " + request.form['model_text'] + ". here is what I want the model to accomplish: " + request.form['text']
                message = "When you are asked to make a python machine learning model, you only return valid python code that accomplishes the task you where asked to accomplish with python code, without additional explanation. to fit or train the model use the data in the already existing pandas dataframe (no need to import data from csv), the name of the pandas dataframe is 'df'."

            # LOAD the CSV into a DATAFRAME and extract column names
            if os.path.isfile('modified_running_dataframe.csv') and os.path.isfile('mod_run_df_columnMetadata.csv'):
            #df = pd.read_csv('modified_running_dataframe.csv')
                # opens a modified running dataframe csv, and specifies to what data type each date time type column should be parsed to (based on the column metadata in the corresponding 'mod_run_df_columnMetadata.csv' file)
                df = csvHdl.open_csv_parse_datetime('modified_running_dataframe.csv','mod_run_df_columnMetadata.csv')
                print("\n \'modified_running_dataframe.csv\' OPENED \n")
                message = message + " the python pandas dataframe column names and data types are: " + str(df.dtypes) #str(','.join(df.columns) )
            elif os.path.isfile('mydata.csv'):
                df = pd.read_csv('mydata.csv')
                print("\n \'mydata.csv\' OPENED \n")
                message = message + " the python pandas dataframe column names and data types are: " + str(df.dtypes)  #str(','.join(df.columns) )

            print("system message:\n" + message + "\n")     
            print("user prompt:\n" + text + "\n")        


            # GPT API call
            response = openai.ChatCompletion.create(
                api_key= openai.api_key,
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": str(message)},
                    {"role": "user", "content": str(text)}
                ],
                temperature=0.0,
                max_tokens = 2048
            )

            gpt_response_content = response['choices'][0]['message']['content']
            print("gpt_response_content:\n" + gpt_response_content)
            
                
            #clean the response content from:
            gpt_response_content = gpt_response_content.replace('```python', '')
            gpt_response_content = gpt_response_content.replace('```', '')
            gpt_response_content = gpt_response_content.strip('`')
            # Split the string into lines, filter out empty lines, and join the remaining lines
            gpt_response_content = "\n".join([line for line in gpt_response_content.splitlines() if line.strip()])
            print("code snippet mark cleaning result:")
            print(gpt_response_content)
            print()

            #extract all the code lines
            gpt_response_content = strHdl.extract_code_snippets(gpt_response_content)
            print("CLEANED_gpt_response_content:(extract_code_snippets FUNCTION returned:)")
            print(gpt_response_content)
            print()


            # returns a bool list stating if each line is an assinment statement or not
            is_assignment_list = strHdl.multi_is_assignment_statements(gpt_response_content)

            # executes the queries or assiment statements
            database_query_result, new_vars = qryHdl.execute_multiline_response(df,gpt_response_content,is_assignment_list)
            # if the query result is a pandas series, convert it to data frame (so '.to_html()' can be applied to it)

            if isinstance(database_query_result, pd.Series):
                database_query_result = database_query_result.to_frame().T
            # if the returned query result is a dataframe, convert it to html (so it can be displayed as a table in the frontend)
            if isinstance(database_query_result, pd.DataFrame):
                database_query_result = database_query_result.to_html(border=0,classes='df_table')
            else:
                database_query_result = str(database_query_result)

            return render_template('index.html',
                                   prev_text= request.form['text'],
                                   prev_model_text = request.form['model_text'],
                                   result=  str(gpt_response_content),
                                   database_query_result = database_query_result,
                                   new_vars = new_vars,
                                   prompt_type = prompt_type,
                                   #df=df.to_html(classes='table table-striped')
                                   result_type = "text_display_radio",
                                   prompt_radio_choice = prompt_type
                                )
        # file upload form
        elif form_name == "file_upload":
            csv_file = request.files['csv_file']
            df = pd.read_csv(csv_file)
            #print(df.dtypes)
            df.to_csv('mydata.csv', index=False)
            #delete modified_running_dataframe csv and it's column metadata csv
            if os.path.isfile('modified_running_dataframe.csv'):
                os.remove('modified_running_dataframe.csv')
            if os.path.isfile('mod_run_df_columnMetadata.csv'):
                os.remove('mod_run_df_columnMetadata.csv')
            print(df.head())


    return render_template('index.html', prompt_type = prompt_type,result_type = "text_display_radio")

    #return f'The text you entered was: {text}'





# the response to the change of radio buttons that set the query result display type (text or plot or other)
@app.route('/display_type', methods=['GET', 'POST'])
def radio():
    if request.method == 'POST':

        message = "You are a helpful assistant."

        selected_value = request.form['display_type']

        if selected_value == 'text_display_radio':
            return render_template('index.html',
                                   prev_text= request.form['prev_prompt'],
                                   prev_model_text = request.form['prev_model_text'],
                                   result=  request.form['prev_result'],
                                   database_query_result = request.form['prev_database_query_result'],
                                   new_vars =  request.form['prev_newVars'],
                                   prompt_type = request.form['prev_prompt_type'],
                                   result_type = "text_display_radio"
                                )
        elif selected_value == 'plot_display_radio':
            sys_message = "When you are asked a question about a dataframe, you only return a valid pandas dataframe query without additional explanation. there in no need to import a csv into a dataframe, the dataframe already exists and it's called \'df\'."
            ask_plot = "plot the data with a matplotlib plot, no need to import pandas or matplotlib. save the plot in a file named \"plot\" in a png format"
            text = " return a pandas dataframe query that should return an answer to this question: " + request.form['prev_prompt'] + ask_plot + ". only return the code snippet, without additional explanation!"
            
            # LOAD the CSV into a DATAFRAME and extract column names
            if os.path.isfile('modified_running_dataframe.csv'):
                #df = pd.read_csv('modified_running_dataframe.csv')
                # opens a modified running dataframe csv, and specifies to what data type each date time type column should be parsed to (based on the column metadata in the corresponding 'mod_run_df_columnMetadata.csv' file)
                df = csvHdl.open_csv_parse_datetime('modified_running_dataframe.csv','mod_run_df_columnMetadata.csv')
                sys_message = sys_message  + " the python pandas dataframe column names and data types are: " + str(df.dtypes) # str(','.join(df.columns) )
            elif os.path.isfile('mydata.csv'):
                df = pd.read_csv('mydata.csv')
                sys_message = sys_message + " the python pandas dataframe column names and data types are: " + str(df.dtypes) #str(','.join(df.columns) )

            #send a GPT API request to get the command to create the PLOT
            response = openai.ChatCompletion.create(
                api_key= openai.api_key,
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": str(sys_message)},
                    {"role": "user", "content": str(text)}
                ],
                temperature=0.0,
                max_tokens = 2048
            )
            # load the gpt content from the response
            gpt_response_content = response['choices'][0]['message']['content']
            print("gpt_response_content:\n" + gpt_response_content)

            #clean the response content from:
            gpt_response_content = gpt_response_content.replace('```python', '')
            gpt_response_content = gpt_response_content.replace('```', '')
            gpt_response_content = gpt_response_content.strip('`')
            # Split the string into lines, filter out empty lines, and join the remaining lines
            gpt_response_content = "\n".join([line for line in gpt_response_content.splitlines() if line.strip()])
            print("code snippet mark cleaning result:")
            print(gpt_response_content)
            print()

            #extract all the code lines
            gpt_response_content = strHdl.extract_code_snippets(gpt_response_content)
            print("CLEANED_gpt_response_content:(extract_code_snippets FUNCTION returned:)")
            print(gpt_response_content)
            print()

            print("query is: ")
            print(gpt_response_content)

            # Clear the current plot axes (if there where any plots from before)
            plt.gca().cla()
            # execute the GPT API response
            is_assignment_list = strHdl.multi_is_assignment_statements(gpt_response_content)
            # this vars just exist in this scope to have a place to unpack what the func returns (there is a use for what the func returns in other scopes(like the return query result in text scope))
            database_query_result, new_vars = qryHdl.execute_multiline_response(df,gpt_response_content,is_assignment_list)

            # load the plot PNG
            #plot = ""
            if os.path.isfile('plot.png'):
                #plot = "plot.png"  
                # move png file to "/static" folder
                # (but before that, if there is an old file there, delete old file so it won't interfere)
                if os.path.isfile('./static/plot.png'):
                    os.remove('./static/plot.png')
                shutil.move('plot.png','./static')              
        
            #return template
            return render_template('index.html',
                                   prev_text= request.form['prev_prompt'],
                                   prev_model_text = request.form['prev_model_text'],
                                   result= request.form['prev_result'], #str(gpt_response_content),
                                   database_query_result = request.form['prev_database_query_result'], #database_query_result,
                                   new_vars =  request.form['prev_newVars'],
                                   prompt_type = request.form['prev_prompt_type'],
                                   result_type = request.form['display_type'],
                                   #plot = plot                                   
                                )
app.run()