from flask import Flask
from flask_mysqldb import MySQL

app = Flask(__name__) #this has 2 underscores on each side

@app.route('/')
def hello_world():
  return 'Hello World! -Kellen'