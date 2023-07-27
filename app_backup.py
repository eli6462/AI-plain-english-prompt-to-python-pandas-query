import os
import openai

from flask import  Flask, redirect, render_template, request, url_for

app = Flask(__name__)
openai.api_key = os.getenv("OPENAI_API_KEY")

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/', methods=['POST'])
def get_text():
    text = request.form['text']

    #return f'The text you entered was: {text}'


app.run()