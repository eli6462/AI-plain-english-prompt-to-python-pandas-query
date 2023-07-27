import pandas as pd
import os

# used in opening a csv with date time columns, in the 'converters' parameter in pd.read_csv()
def timedelta_parser(s):
    return pd.to_timedelta(s)
# used in opening a csv with date time columns, in the 'converters' parameter in pd.read_csv()
def datetime_parser(s):
    return pd.to_datetime(s)


# saves the dataframe into a csv, and saves it's column names and data type info into a seperate csv (the column metadata csv will be used for referance in knowing what format to convert the main csv columns into when loading the main csv,(because pandas saves it's date time format columns as a string when saving df into csv))
def save_df_with_columnMetadata_csv(df):
    column_names = df.columns
    column_types = df.dtypes
    column_info_df = pd.DataFrame({'Column Name': column_names, 'Data Type': column_types})

    df.to_csv('modified_running_dataframe.csv', index=False)
    column_info_df.to_csv('mod_run_df_columnMetadata.csv', index=False)

    print("***************** POST EXECUTION DATAFRAME HAS BEEN SAVED SUCCESSFULLY *****************")

# opens a modified running dataframe csv, and specifies to what data type each date time type column should be parsed to (based on the column metadata in the corresponding 'mod_run_df_columnMetadata.csv' file)
def open_csv_parse_datetime(csv_path,columnMetadata_csv_path):
    if os.path.isfile(columnMetadata_csv_path):
        column_info_df = pd.read_csv(columnMetadata_csv_path)
    else:
        raise RuntimeError("This is a custom error message made by the app developers. error: the is no column metadata csv file in the path: " + columnMetadata_csv_path)

    # dict used in the 'converters' parameter of the pd.read_csv() func
    conveters_dict = {}
    # loop thru column metadata df rows
    for index, row in column_info_df.iterrows():
        if row['Data Type'] == 'datetime64[ns]':
            conveters_dict[row['Column Name']] = datetime_parser
        elif row['Data Type'] == 'timedelta64[ns]':
            conveters_dict[row['Column Name']] = timedelta_parser

    # open the csv, convert to dataframe, and parse date time data types in the methods i specified in the conveters_dict.
    df = pd.read_csv(csv_path,converters=conveters_dict)
    return df


# ***********************************
#**************** TESTS *************
'''
data = {
    'col1': [1, 2, 3],
    'col2': ['A', 'B', 'C']
}
df = pd.DataFrame(data)

for index, row in df.iterrows():
        print(row)
'''