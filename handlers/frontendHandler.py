import re
# a func used in the frontend to check if a var is a table
def is_html_table(value):
    return bool(re.match(r'^\s*<table[^>]*>.*</table>\s*$', value, re.IGNORECASE | re.DOTALL))