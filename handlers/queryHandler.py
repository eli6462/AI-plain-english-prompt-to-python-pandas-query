import pandas as pd #pandas as pd can be used inside the query string recived from GPT
import matplotlib 
import matplotlib.pyplot as plt
from matplotlib.ticker import ScalarFormatter, FuncFormatter
import re
# for a specific test to perform anomaly detection in data
from sklearn.ensemble import IsolationForest

# my modules
from handlers import csvHandler as csvHdl

# try to make it a global variable
#onlyNew_runningVars_dict = {}

# print df columns when specific code line comes up (code line made by GPT API)
def is_commands(df,code_line,patternX):
    pattern = patternX
    match = re.search(pattern, code_line)
    if match:
        print("************** DF COLUMNS: ****************")
        print(df.columns)

# checks if the string got line has specific commands
def got_oneOF_commands(code_line,patterns):

    for pattern in patterns:
        match = re.search(pattern, code_line)
        if match:
            return True
    return False

def execute_multiline_response(df,query_string_list,is_assigment_statement__list):

    # a dictionary that will hold all the running time variables created inside the local scope of the 'exec()' func when executing the query string list
    original_vars_dict = {}
    includingNew_vars_dict = {}
    onlyNew_runningVars_dict = {}

    # register if the first ""assigment statement"" (executable code, and not an eval() statement) was executed, when the first exec() statement needs to be executed - record the original variables just before the first exec(), (to get an understanding (later) of what new variables were created by the exec() statements)
    first_statement_was_executed = False
    # lock csv var doesn't allow to save the df to csv if there where any problematic modification to the df, like for example: converting categorical variables into dummy variables
    lock_csv = False

    #lines = query_string.splitlines()
    lines = query_string_list

    # if the first element of the "lines" list is an empty string, remove it (if the gpt returns an answer starting with "\n")
    if lines[0] == "":
        del lines[0]

    print("lines:")  
    print(is_assigment_statement__list)
    print(lines)

    #database_query_result = ""
    database_query_result = pd.DataFrame()

    for i in range(len(lines)):
        
        # for tests
        print('i =')
        print(i)

        if(is_assigment_statement__list[i]):

            # test, and might be necesery also
            matplotlib.use('Agg')

            # Combine local and global variables
            # This modification should allow you to access the df variable within the function's scope and update it using the exec() function.
            all_vars = locals().copy()
            all_vars.update(globals())

            # record the original variabels before the first execution
            if not(first_statement_was_executed):
                original_vars_dict.update(all_vars)

            includingNew_vars_dict.update(all_vars)
            
            # test func
            #pattern = r"pd\.get_dummies"
            #testFunc_printDfColumns_whenX(df,lines[i],pattern)

            # Pass the combined dictionary as the second argument to exec()
            exec(lines[i], includingNew_vars_dict)
            #df = all_vars['df']
            df = includingNew_vars_dict['df']

            # update and merge all the local scope variables (including old) and new 'exec()' local scope variables into the outer-scope variables dictionary 
            #includingNew_vars_dict.update(all_vars)

            # Create a new dictionary with keys that appear only in 'includingNew_vars_dict'(and not in prev_vars_dict), and merge it to the 'onlyNew_runningVars_dict'
            onlyNew_runningVars_dict.update({key: value for key, value in includingNew_vars_dict.items() if key not in original_vars_dict}) 

            #print(df)

            #df.to_csv('modified_running_dataframe.csv', index=False)
            # save the  dataframe, and it also saves it's column info (column names and data types, into a seperate csv)
            # but only save the dataframe if it wasn't changed in a problematic manner (for example: like turning the categorical variables into dummy variables  )
            patterns = [r"pd\.get_dummies"]
            if got_oneOF_commands(lines[i],patterns):
                lock_csv = True
            if lock_csv == False:
                csvHdl.save_df_with_columnMetadata_csv(df)

            print("line number" + str(i+1) + " has been executed")
            database_query_result += "line no\' " + str(i+1) + " is an assigment statment, and it has been executed.\n"

        else:
            print()
            
            matplotlib.use('Agg') #run this to avoid the "RuntimeError: main thread is not in main loop" error, (maybe move this out of the loop)
            #if it's the "plt.savefig('plot.png..." command (to save it as an image), instead run the following code, to save the plot in 100% size (fixes cut off borders issues in plot.png)        
            # in the future, maybe we can change change the if statement to check for the last line, and if it's in the plot display mode, that last line should start with "plt.savefig(...)", this way should be more computationally cheap than comparing strings...
            if lines[i].startswith('plt.savefig'):

                ax = plt.gca() # ax is the axes object of the plot

                def formatter(x, pos):
                    return f'{x:,.2f}' #f'{x:.0f}'

                # Change x-axis tick labels to regular notation
                # either this
                #ax.xaxis.set_major_formatter(ScalarFormatter(useMathText=False, useOffset=False))
                # or this
                ax.xaxis.set_major_formatter(FuncFormatter(formatter))
                # Change y-axis tick labels to regular notation
                #ax.yaxis.set_major_formatter(ScalarFormatter(useMathText=False, useOffset=False))
                #ax.yaxis.set_major_formatter(FuncFormatter(formatter))
                # Automatically adjust the axis limits and tick positions
                # (may be not necessary)
                #ax.autoscale(enable=True, axis='both', tight=True)

                #pd.options.display.float_format = '{:,.2f}'.format
                plt.subplots_adjust(left=0.2, right=0.8, top=0.8, bottom=0.2) 
                plt.savefig('plot.png', bbox_inches='tight') # bbox_inches='tight'
                # clear the current figure, so it's axis and other thing wont effect the next plot
                fig, ax = plt.subplots()                
                plt.close(fig)
                #plt.clf()
                #import matplotlib.pyplot as plt
            # else run the line normally, it's just a regular line 
            else:          
                print('onlyNew_runningVars_dict:')   
                print(onlyNew_runningVars_dict)
                # version 1
                '''
                all_vars = globals().copy()
                all_vars.update(onlyNew_runningVars_dict)
                '''
                # version 2
                '''
                all_vars = locals().copy()
                all_vars.update(globals())
                all_vars.update(onlyNew_runningVars_dict)
                '''
                # version 3
                '''
                all_vars = globals().copy()
                all_vars.update(onlyNew_runningVars_dict)

                onlyNew_runningVars_dict.update({'df': df})
                '''
                # version 4
                all_vars = locals().copy()
                all_vars.update(globals())
                all_vars.update(onlyNew_runningVars_dict)

                #onlyNew_runningVars_dict.update({'df': df})

                #database_query_result += str(eval(lines[i],all_vars,onlyNew_runningVars_dict)) + "\n"
                database_query_result = eval(lines[i],all_vars,onlyNew_runningVars_dict)
            print("line no\' " + str(i+1) + " query result is: " + str(eval(lines[i],all_vars,onlyNew_runningVars_dict)))

    # for tests
    print("\nonlyNew_runningVars_dict =")
    print(onlyNew_runningVars_dict.keys())
    print()

    if 'predictions' in onlyNew_runningVars_dict:
        print("PREDICTIONS =")
        print(onlyNew_runningVars_dict['predictions'])

    return database_query_result, onlyNew_runningVars_dict 

# TESTING THE FUNCTIONS