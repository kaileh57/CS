from flask import Flask, render_template, redirect, url_for

app = Flask(__name__)
app.secret_key = 'kellen'

@app.route('/')
def index():
    return redirect(url_for('login'))

@app.route('/login')
def login():
    return render_template('login.html.j2')

@app.route('/create_account')
def create_account():
    return render_template('create_account.html.j2')



