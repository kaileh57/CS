from flask import Flask, render_template, redirect, url_for, request, flash, session
from flask_mysqldb import MySQL
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.config['MYSQL_HOST'] = 'mysql.2526.lakeside-cs.org'
app.config['MYSQL_USER'] = 'student2526'
app.config['MYSQL_PASSWORD'] = 'ACSSE2526'
app.config['MYSQL_DB'] = '2526finalproject'
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'
app.secret_key = 'kellen'
mysql = MySQL(app)

@app.route('/')
def index():
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        cur = mysql.connection.cursor()
        query = "SELECT * FROM kellenh_players WHERE username = %s;"
        cur.execute(query, (username,))
        user = cur.fetchone()
        if user and check_password_hash(user['password'], password):
            session['user_id'] = user['id']
            session['username'] = user['username']
            session['trophies'] = user['trophies']
            return redirect(url_for('welcome'))
        else:
            flash('Invalid username or password')
            return redirect(url_for('login'))
    return render_template('login.html.j2')

@app.route('/welcome')
def welcome():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    return render_template('welcome.html.j2')

@app.route('/leaderboard')
def leaderboard():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    cur = mysql.connection.cursor()
    query = "SELECT username, trophies FROM kellenh_players ORDER BY trophies DESC;"
    cur.execute(query)
    users = cur.fetchall()
    cur.close()
    return render_template('leaderboard.html.j2', users=users, current_user=session['username'])

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route('/create_account', methods=['GET', 'POST'])
def create_account():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        hashed_password = generate_password_hash(password)
        cur = mysql.connection.cursor()
        query = "INSERT INTO kellenh_players (username, password, trophies) VALUES (%s, %s, 0);"
        queryVars = (username, hashed_password)
        cur.execute(query, queryVars)
        mysql.connection.commit()
        flash('Account created successfully!')
        return redirect(url_for('login'))
    return render_template('create_account.html.j2')



