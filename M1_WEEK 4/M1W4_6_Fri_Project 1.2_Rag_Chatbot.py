
import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv() # Load variables from the .env file

# OpenAI automatically looks for the OPENAI_API_KEY environment variable,
# so you don't even need to pass api_key=... manually!
client = OpenAI()

client

messages = []
messages.append({"role":"user", "content":"hi"})
resp = client.chat.completions.create(
    model = 'gpt-4o-mini',
    messages=messages,
    temperature=0
)

print(resp.choices[0].message.content)

'''
Jupyter Notebooks vs. standard Python .py scripts:

Jupyter Notebook: The notebook automatically prints/displays the evaluation of the final line in a code cell.

Python Scripts: When executing a .py file via the terminal, Python executes statements but does not automatically print values unless you explicitly wrap them in a print() function.
'''

