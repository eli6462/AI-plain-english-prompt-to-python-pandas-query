import ast
import re


# a function to check if a query string (returned by the GPT API is an ) is an assignment statement
# if it's an assignment statement, then it should be run by the command "exec()" instead of "eval()"

def is_assignment_statement(query_string):
    try:
        parsed = ast.parse(query_string)
        if len(parsed.body) == 1 and isinstance(parsed.body[0], ast.Assign):
            return True
    except SyntaxError:
        pass
    
    return False


# same function but for multiple lines, returns a bool list where each bool corresponds to each line by index
# a function to check if a query string (returned by the GPT API ) is an assignment statement

def multi_is_assignment_statements(query_string_list):
    #lines = query_string.splitlines()
    lines = query_string_list

    # if the first element of the "lines" list is an empty string, remove it (if the gpt returns an answer starting with "\n")
    if lines[0] == "":
        del lines[0]

    assignment_results = []

    for line in lines:
        try:
            parsed = ast.parse(line)
            # if it's an assigment statement
            if len(parsed.body) == 1 and isinstance(parsed.body[0], ast.Assign):
                assignment_results.append(True)
            # OR if it's starts with one of the following python syntaxes
            elif line.startswith('import') or line.startswith('df.dropna') or line.startswith('from'):
                assignment_results.append(True)
            else:
                assignment_results.append(False)
        except SyntaxError:
            assignment_results.append(False)

    return assignment_results

# !!! this is code that was written by gpt-4
# this function extracts all the code lines that not python or pandas code snippets

def extract_code_snippets(response_string):
    #print("response_string:")
    #print(response_string)

    #if the string is one line, it's probably a single code line, so just return it as it is.    
    if response_string.count("\n") == 0:
        print("\none line")
        return [response_string]
    '''
    response_string_list = response_string.splitlines()
    if len(response_string_list) <= 1:
         print("\none line OR LESS")
         return [response_string]
    '''
    print("\nmore than one line")
    # Use a regex pattern to match lines that look like Python or Pandas code
    #this regular experssion ALSO accounts for code that is starting with "df.", followed by a word character sequence, and then either round parentheses or square brackets.
    code_pattern = re.compile(r'^\s*(?:import|from|def|class|df.|plt.|\w+\s*=\s*|\w+\.\w+\s*(?:\(.*\)|\[.*\])|pd\.\w+\s*\(.*\)|df\.\w+\s*(?:\(.*\)|\[.*\])|\s{4}|\t).+', flags=re.MULTILINE)


    code_snippets = code_pattern.findall(response_string)        

    #print("from stringHandler.extract_code_snippets() func:")
    #print("i return:")
    #print(code_snippets)
    return code_snippets


# TESTING THE FUNCTIONS

response_string_1 = """
To get the company names with the highest and lowest average mileage, the following pandas dataframe query can be used:


# For highest average mileage
df.groupby('Company name')['Kms driven'].mean().sort_values(ascending=False).head(1)

# For lowest average mileage
df.groupby('Company name')['Kms driven'].mean().sort_values(ascending=True).head(1)

"""

response_string_2 = "df.shape[1]"

print(extract_code_snippets(response_string_2))
