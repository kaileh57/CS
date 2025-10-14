from flask import Flask, render_template, request
import requests
from flask_mysqldb import MySQL

app = Flask(__name__) #this line is already in your code
app.config['MYSQL_HOST'] = 'mysql.2526.lakeside-cs.org'
app.config['MYSQL_USER'] = 'student2526'
app.config['MYSQL_PASSWORD'] = 'ACSSE2526'
app.config['MYSQL_DB'] = '2526playground'
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'
mysql = MySQL(app)

@app.route('/')
def index():
    cursor = mysql.connection.cursor()
    query = 'SELECT * FROM kellenh_test'
    cursor.execute(query)
    mysql.connection.commit()
    data = cursor.fetchall()
    return render_template('index.html.j2', rows=data)



