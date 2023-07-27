import pandas as pd
from pandas.api.types import is_string_dtype
import openai
import os
import re
import numpy as np
import inspect
from dateutil.parser import parse, ParserError
from datetime import datetime

openai.api_key = os.getenv("OPENAI_API_KEY")


def test_finish_printout(name):
    current_frame = inspect.currentframe()
    function_name = current_frame.f_code.co_name
    print("\n****************************")
    print(name + " HAS FINISHED!")
    print("\n****************************")


# a function that cleans a string and converts it to float
def clean_and_convert_float(string):
    # check if it's a string, becuase if it's not you can't use the replace methode on it
    if isinstance(string, str):
        # remove any commas and whitespace from the string
        string = string.replace(',', '').strip()
        # strip any charter that is not a number between 0-9
        string = re.sub(r'[^\d\.]+', '', string)

        # check if the string is empty, return NaN if so
        if string is not string:
            return float('nan')
        
        # convert the string to a float and return the value
        try:
            return float(string)
        except Exception as err:
            print(err)
            return float('nan')
    else:
        return(string)
    
# a function that cleans a string and converts it to int
def clean_and_convert_int(string):
     # check if it's a string, becuase if it's not you can't use the replace methode on it
    if isinstance(string, str):
        # remove any commas and whitespace from the string
        string = string.replace(',', '').strip()
        # strip any charter that is not a number between 0-9
        string = re.sub(r'[^\d\.]+', '', string)
        
        # check if the string is empty, return NaN if so
        if string is not string:
            return np.nan

        # convert the string to a float and return the value
        try:
            return int(string)
        except Exception as err:
            print(err)
            return np.nan
    else:
        return(string)

# a function that cleans a string and converts it to either: 'datetime64','timedelta64' or 'Period', depending on the input parameter
def clean_and_convert_datatime(string,datetime_type):
    # Regular expression pattern to match digits, colons, hyphens, and slashes
    pattern = r"[^0-9:\-/]"

    # check if it's a string, becuase if it's not you can't use the replace methode on it
    if isinstance(string, str):
        # Substitute the non-date/time characters with an empty string
        string = re.sub(pattern, "", string)
        # check if the string is empty, return NaN if so
        if string is not string:
            return None

        # convert the string to a datetime format of your choice and return the value
        try:
            if datetime_type == 'datetime64':
                return pd.to_datetime(string) # !!! there may be a need to add the 'format='%H:%M:%S' argument inside the Parenthesis, or some other type of format
            elif datetime_type == 'timedelta64':
                return pd.to_timedelta(string)
            elif datetime_type == 'Period':
                raise RuntimeError("This is a custom error message made by the app developers. there is currently no support for converting a pandas object to a 'Period' format, support will be available in the near future.")
            else:
                raise RuntimeError("This is a custom error message made by the app developers. the type of the date time format (that the object needs to be converted to) is not recognised by our app's system. the date time type return by the AI API is: " + datetime_type)
        except Exception as err:
            print(err)
            return None
    else:
        return(string)

def clean_and_convert_datetime_AUTOchoice(string):

    if isinstance(string, str):
        # Remove leading and trailing whitespaces
        string = string.strip()

        # Replace non-standard separators with a standard separator
        string= string.replace('/', '-').replace('.', '-')

        # Convert non-standard month names or abbreviations to a standard format
        month_mapping = {
            'Jan': '01', 'January': '01',
            'Feb': '02', 'February': '02',
            'Mar': '03', 'March': '03',
            'Apr': '04', 'April': '04',
            'May': '05',
            'Jun': '06', 'June': '06',
            'Jul': '07', 'July': '07',
            'Aug': '08', 'August': '08',
            'Sep': '09', 'September': '09',
            'Oct': '10', 'October': '10',
            'Nov': '11', 'November': '11',
            'Dec': '12', 'December': '12'
        }
        for month_name, month_number in month_mapping.items():
            string = string.replace(month_name, month_number)

        # Remove any unnecessary characters or symbols that are not part of the date or time information
        cleaned_string = re.sub(r'[^0-9\s:\-]', '', string)
        
        #decide what format to convert it to function
        def contains_date_information(string):            
            '''code made by gpt 4'''
            # Define a list of date patterns
            date_patterns = [
                r'\b\d{4}-\d{1,2}-\d{1,2}\b',  # YYYY-MM-DD
                r'\b\d{1,2}-\d{1,2}-\d{4}\b',  # DD-MM-YYYY or MM-DD-YYYY
                r'\b\d{1,2}/\d{1,2}/\d{4}\b',  # DD/MM/YYYY or MM/DD/YYYY
                r'\b(?:\d{1,2} )?(?:jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)[a-z]*(?: \d{1,2})?,? \d{4}\b'  # DD Month YYYY or Month DD, YYYY
            ]

            # Define a list of date formats corresponding to the date patterns
            date_formats = [
                "%Y-%m-%d",
                "%d-%m-%Y",
                "%m-%d-%Y",
                "%d/%m/%Y",
                "%m/%d/%Y",
                "%d %B %Y",
                "%d %b %Y",
                "%B %d %Y",
                "%b %d %Y",
                "%d %B, %Y",
                "%d %b, %Y",
                "%B %d, %Y",
                "%b %d, %Y"
            ]

            for pattern in date_patterns:
                match = re.search(pattern, string, re.IGNORECASE)
                if match:
                    for date_format in date_formats:
                        try:
                            datetime.strptime(match.group(), date_format)
                            return True
                        except ValueError:
                            pass

            return False
        # end of function.

        try:
            if contains_date_information(cleaned_string):
                return pd.to_datetime(cleaned_string)
            else:                
                #print("entered \'pd.to_timedelta()\' scope ")
                # Check if the time_string has the format 'h:mm' or 'hh:mm', and if it does, add missing seconds to it (turn it to h/hh:mm:ss), so it can be converted to 'timedelta64' successfully.
                hour_minute_pattern = r'^\d{1,2}:\d{2}$'
                if re.match(hour_minute_pattern,cleaned_string):
                    cleaned_string = cleaned_string + ':00'
                return pd.to_timedelta(cleaned_string)
            
        except Exception as err:
                print("Error is:" + str(err))
                return None
    else:
        print("custom app system error: NOT A STRING TYPE, can't convert from " + str(type(string)) + " type. ('dateutil.parser.parse()' can only parse strings)")
        return(string)


# if the string_list contains more than 50% strings that are time or date information, return true.
def contains_date_or_time_information(string_list):
    is_dateOrTime_counter = 0
    not_strings_counter = 0

    for string in string_list:
        if isinstance(string, str): # parse() func can't parse non-strings
            
            float_pattern = r'^\d+\.\d+$'
            # check if this string looks like a float value, else continue to try parsing it as a date (the 'dateutil.parser.parse()' func is very flexible, and can parse float looking strings as a date (example format is 'day.month') )
            if re.match(float_pattern, string):
                print("The input string appears to be a float-like string")
            else:
                try:
                    parse(string) # parse function 'from dateutil.parser import parse'
                    is_dateOrTime_counter +=1

                except (ValueError, ParserError) as errors:
                    print(errors)
        else:
            not_strings_counter += 1
    
    # from all the strings in the list, if more than 50% of them contain date or time info, return true.
    if is_dateOrTime_counter > 0 and (len(string_list)-not_strings_counter) / is_dateOrTime_counter <= 2:
        return True
    else:
        return False



# a function that cleans all the numerical columns in the pandas dataframe, and converts them to float
def df_clean_numeric_columns(df):

    # system message to openai api
    sys_message = "You are a helpful assistant."

    # loop through all columns using iteritems()
    for column_name, column_data in df.iteritems():
        
        column_data_desc = "Column name: " + column_name + "\nColumn data-\n"
        
        # add first range(x) columns items into the string
        for row_index in range(10):
            # if row index is less than number of rows in the dataframe column, exit for loop.
            if row_index >= len(df[column_name]):
                break
            # ****** TRY TO FIX IT THIS WAY: check if the first range(x) rows have more strings that has no numbers in them, or more numerics that has no alphabetic chars in them, and then decide wich object type to ommit (ommit strings or ommit numerical types), and send the "less confusing" data to the GPT API
            column_data_desc += "column item number " + str(row_index+1) + ": " + str(df.iloc[row_index][column_name]) + "\n"
        
        # call the openAi api and ask it if this column need to be converted to a numerical data type
        response = openai.ChatCompletion.create(
                api_key= openai.api_key,
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": str(sys_message)},
                    {"role": "user", "content": "do you think this python pandas dataframe column should be converted to a numeric data type? (it's critical that you only answer in one word, true or false.) and if it seems that the column is of a specific date type like a specific year or a specific date, answer False. or if it's a time type or an amount of time type (like an amount of hours or an amount of minutes and any other time type amount), answer False.\n" + column_data_desc}
                ],
                temperature=0.0,
                max_tokens = 2048
            )        
        gpt_response_content = response['choices'][0]['message']['content']
        print(column_data_desc)
        print(gpt_response_content + "\n") 

        # clean the column data and convert it into a float, IF the data should be converted into a numeric type accoring to the GPT API response
        if gpt_response_content.startswith('True'):
            print(column_name)
            df[column_name] = df[column_name].apply(clean_and_convert_float)
            # Drop rows with NaN values in the current column 
            df.dropna(subset=[column_name])

    print(df.head())
    print(df.dtypes)

    #test_finish_printout()

    return(df)



# a function that cleans all the data and time columns in the data frame and converts them to the hopefully best date data type or time data type, or datetime data type, or something else that suits this column type best.
def df_clean_datetime_columns(df):

     # system message to openai api
    sys_message = "You are a helpful assistant."
    # version 1 GPT API prompt, asking to return an answer out of 4 options: 'false' if it's not a date or time column type, and it is a date time column time, it will return one of 3 remaining options: 'datetime64', 'timedelta64' or 'Period'
    user_message_4options = "do you think this python pandas dataframe column should be converted to a date and time data type, and if the answer is true tell me what data and time pandas data type should it best be converted to, in order to do data analysis on the column. (it's critical that you only answer in one word, \n1. either answer 'false' if the column shouldn't be converted to a data or time data type. \n2. or answer 'datetime64' if the column data contains date or date and time information, so the column should best be converted to datetime64 data type. \n3. or answer 'timedelta64' if the column and it's data is used to represent differences in dates and times, such as durations, intervals, and time spans, and should best be converted to timedelta64 data type. (also if the column data only contains information about an amount of hours or minutes or seconds or other time type and no date information, the column should be converted into a datetime64 data type, so return 'datetime64' in this case.) \n4. or answer 'Period' if the column should best be converted to a Period data type.)\n"
    #user_message_trueOrFalse = "do you think this python pandas dataframe column should be converted to a date data type, or date and time data type in order to do data analysis on the column? (it's critical that you only answer in one word, true or false)\n"
    user_message_trueOrFalse = "do you think this column contains date information, or time information, or date and time information? (it's critical that you only answer in one word, true or false)\n"

    # loop through all columns using iteritems()
    for column_name, column_data in df.iteritems():
        column_data_desc = "Column name: " + column_name + "\nColumn data-\n"
        # add first range(x) columns items into the string
        for row_index in range(10):
            # if row index is less than number of rows in the dataframe column, exit for loop.
            if row_index >= len(df[column_name]):
                break
            # ****** TRY TO FIX IT THIS WAY: check if the first range(x) rows have more strings that has no numbers in them, or more numerics that has no alphabetic chars in them, and then decide wich object type to ommit (ommit strings or ommit numerical types), and send the "less confusing" data to the GPT API
            column_data_desc += "column item number " + str(row_index+1) + ": " + str(df.iloc[row_index][column_name]) + "\n"

        # convert 'year' type columns formatted as '2017' to 'int' data types (this is what gpt 4 recommended in order to best use this column in data analysis)
        # but first ask the GPT API if it's a 'year' type column (there may be many ways to phrase a name for a 'year' type column, so it may be best to use AI for this purpose.)
        response = openai.ChatCompletion.create(
                api_key= openai.api_key,
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": str(sys_message)},
                    {"role": "user", "content": "do you think this python pandas dataframe column is a year type column , and should best be converted to an 'int' data type, in order to do data analysis on the column? note that even if the column contains some historical years between the years 1 and 1000 the answer should be 'true', and also note that it's real world data, and it might be messy and in need of data cleaning.  (it's critical that you only answer in one word, true or false)" + column_data_desc}
                ],
                temperature=0.0,
                max_tokens = 2048        
            )
        gpt_response_content = response['choices'][0]['message']['content']
        print(column_data_desc)
        print("is year type: " + gpt_response_content + "\n") 
        
        # if the answer of GPT API is true (regarding to that it's a year type column), then convert it to int. else: check if it's some type of date time column type and convert it accordingly
        if gpt_response_content.startswith('True'):
            
            was_string = False
            if is_string_dtype(df[column_name]):
                # record if the column was of a string (pandas object) type, if yes, than you can later safely convert it to 'int64'
                was_string = True

            df[column_name] = df[column_name].apply(clean_and_convert_int)
            # Drop rows with NaN values in the current column 
            df.dropna(subset=[column_name])  # This line will drop rows containing NaN values (Nan values cause the whole column to be converted to float64 instead of int64)            
            # convert the values to int64 again, (beucase pandas automatically converted them to float64 when a Nan value was added to the column, (int64 doesn't support Nan values))
            if was_string: # only convert the values to int if the column was originally a string type (pandas object), becuase it can be a datetime64 data type, and we don't want to ruin that column by converting it to 'int64' (thinking it's only a year column (and not a full specific date))
                df[column_name] = df[column_name].astype('int64')

        else:
            '''
            #this following GPT API call should be inside an 'else:' block, in case the GPT API decided the column is not of 'year' column type.
            # call the openai api and ask it what date time format should the column best be converted to  
            response = openai.ChatCompletion.create(
                    api_key= openai.api_key,
                    model="gpt-3.5-turbo",
                    messages=[
                        {"role": "system", "content": str(sys_message)},
                        {"role": "user", "content": user_message_trueOrFalse + column_data_desc}
                    ],
                    temperature=0.0,
                    max_tokens = 2048
                )        
            gpt_response_content = response['choices'][0]['message']['content']
            print("is date time type: " + gpt_response_content + "\n") 

            # convert the column data into the corresponding date time format type (the format type is return by the GPT API inside the 'gpt_response_content' variable)
            # ^ OLD WAY, new way is to ask the GPT API to return 'true' if it should be converted to a date time format, and 'false' otherwise, and my fucntion will decide wether to convert into 'datetime64' or 'timedelta64'
            if not(gpt_response_content.startswith('false')) and not(gpt_response_content.startswith('False')): # if the GPT API didn't return 'false' on matter of converting the column into some type of date time data type
                # old way
                #df[column_name] = df[column_name].apply(lambda x: clean_and_convert_datatime(x, gpt_response_content))                
                # new way
                df[column_name] = df[column_name].apply(clean_and_convert_datetime_AUTOchoice)

                # Drop rows with NaN values in the current column 
                df.dropna(subset=[column_name])
            '''
            
            slice_len = 10
            if len(column_data.tolist()) < 10:
                slice_len = len(column_data.tolist())
            print("column data:")
            print(column_data.tolist()[:slice_len])
            
            if contains_date_or_time_information(column_data.tolist()[:slice_len]):
                print("is date time type: True")
                df[column_name] = df[column_name].apply(clean_and_convert_datetime_AUTOchoice)
                # Drop rows with NaN values in the current column 
                df.dropna(subset=[column_name])
            else:
                print("is date time type: False")

    print(df.head())
    print(df.dtypes)

    #test_finish_printout()

    return(df)

# ***testing functions***
'''
df = pd.DataFrame({'kms': ["4,25,000", "3,25,000", "5,75,000","1,75,000", "1,82,000"], 
                   'usernames': ["eli6462", "idan_123", "aviToledo99", "roi2", "tom_yaar012"], 
                   'C': ["5.4", "54.0222", "6.0", "31.563263", "9.1"], 
                   'year date':['2,017','2003 year','965','1121','2008 year'],
                   'overtime':['0:00:00','0:00:00','2:30:00','1:30:00','0:30:00'], 
                   'normal hours':['8:30:00','7:30:00','0:00:00','8:30:00','7:00:00']                  
                })

print("columns data types (before conversion) are:")
print(df.dtypes)
print()

df = df_clean_datetime_columns(df)
df_clean_numeric_columns(df)

#print(contains_date_or_time_information(df['C'].to_list()))

#print(parse('5.4'))
'''