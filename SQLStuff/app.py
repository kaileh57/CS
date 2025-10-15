from flask import Flask, render_template, request, redirect, flash
import requests
from flask_mysqldb import MySQL

app = Flask(__name__)
app.config['MYSQL_HOST'] = 'mysql.2526.lakeside-cs.org'
app.config['MYSQL_USER'] = 'student2526'
app.config['MYSQL_PASSWORD'] = 'ACSSE2526'
app.config['MYSQL_DB'] = '2526playground'
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'
app.secret_key = 'kellen'
mysql = MySQL(app)

@app.route('/')
def index():
    cur = mysql.connection.cursor()
    query = 'SELECT * FROM kellenh_test'
    cur.execute(query)
    mysql.connection.commit()
    data = cur.fetchall()
    return render_template('index.html.j2', rows=data)

@app.route('/search')
def search():
    return render_template('search.html.j2')

@app.route('/searchresults')
def searchresults():
    name = request.values.get("name")
    cur = mysql.connection.cursor()
    query = "SELECT * FROM kellenh_test WHERE name=%s;"
    queryVars = (name,)
    cur.execute(query, queryVars)
    mysql.connection.commit()
    data = cur.fetchall()
    count = len(data)
    return render_template('searchresults.html.j2', count=count, data=data)

@app.route('/insert', methods=['GET', 'POST'])
def insert():
    if request.method == 'GET':
        return render_template('insert.html.j2')
    elif request.method == 'POST':
        name = request.values.get("name")
        birthday = request.values.get("birthday")
        cur = mysql.connection.cursor()
        query = "INSERT INTO kellenh_test (name, birthday) VALUES (%s, %s);"
        queryVars = (name, birthday)
        cur.execute(query, queryVars)
        mysql.connection.commit()
        new_id = cur.lastrowid
        flash(f'Successfully inserted! New ID: {new_id}')
        return redirect('/insert')



