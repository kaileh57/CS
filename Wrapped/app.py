from flask import Flask, render_template, request
import requests

app = Flask(__name__)

GEMINI_URL = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-flash-lite-latest:generateContent?key=AIzaSyDg3bYNunnFphk9HcKDHv4vslcgAaJhRJE"

@app.route('/')
def index():
    return render_template('index.html.j2')


@app.route('/result')
def result():
    prompt = request.args.get('prompt')
    # Gemini response code literally just stolen from the Google Gemini docs
    data = {
        "system_instruction": {
            "parts": [{ # I did modify the system prompt
                "text": "Never use markdown formatting in your responses. Always respond with plain text only."
            }]
        },
        "contents": [{
            "parts": [{
                "text": prompt
            }]
        }]
    }
    response = requests.post(GEMINI_URL, json=data)
    if response.status_code == 200:
        result_data = response.json()
        gemini_response = result_data['candidates'][0]['content']['parts'][0]['text']
    else:
        gemini_response = f"Error: {response.status_code}"
    #End of stolen code
    return render_template('result.html.j2', response=gemini_response)
