
gpt_response_content = ["`df['Kms driven'] = df['Kms driven'].astype(int)`"]
print("before:") 
print(gpt_response_content)

print(len(gpt_response_content))
if len(gpt_response_content) == 1:
    gpt_response_content[0] = gpt_response_content[0].replace('```python', '')
    gpt_response_content[0] = gpt_response_content[0].replace('```', '')
    gpt_response_content[0] = gpt_response_content[0].strip('`')
else:
    for line in gpt_response_content:
        print("line is:  " + line)
        line = line.replace('```python', '')
        line = line.replace('```', '')
        line = line.strip('`')

print("after:") 
print(gpt_response_content)