from flask import Flask, render_template, redirect, url_for, request, flash, session
from flask_socketio import SocketIO, emit, join_room, leave_room
from flask_mysqldb import MySQL
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from urllib.request import urlopen

app = Flask(__name__)
app.config['MYSQL_HOST'] = 'mysql.2526.lakeside-cs.org'
app.config['MYSQL_USER'] = 'student2526'
app.config['MYSQL_PASSWORD'] = 'ACSSE2526'
app.config['MYSQL_DB'] = '2526finalproject'
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'
app.secret_key = 'kellen'
socketio = SocketIO(app)
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

@app.route('/matches')
def matches():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    show_all = request.args.get('show_all') == '1'
    
    cur = mysql.connection.cursor()
    if show_all:
        query = "SELECT * FROM kellenh_matchmaking;"
    else:
        query = "SELECT * FROM kellenh_matchmaking WHERE (p2name IS NULL OR p2name = '') AND p1lastping >= DATE_SUB(NOW(), INTERVAL 10 MINUTE);"
    
    cur.execute(query)
    matches = cur.fetchall()
    cur.close()
    return render_template('matches.html.j2', matches=matches, show_all=show_all)

@app.route('/join_match/<int:match_id>', methods=['POST'])
def join_match(match_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM kellenh_matchmaking WHERE id = %s", (match_id,))
    match = cur.fetchone()
    
    if match and (match['p2name'] is None or match['p2name'] == '') and match['p1name'] != session['username']:
        cur.execute("UPDATE kellenh_matchmaking SET p2name = %s, p2lastping = %s WHERE id = %s", 
                    (session['username'], datetime.now(), match_id))
        mysql.connection.commit()
    
    cur.close()
    return redirect(url_for('game', match_id=match_id))

@app.route('/game/<int:match_id>')
def game(match_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM kellenh_matchmaking WHERE id = %s", (match_id,))
    match = cur.fetchone()
    cur.close()
    
    if not match:
        return redirect(url_for('matches'))
        
    is_host = match['p1name'] == session['username']
    
    return render_template('game.html.j2', match=match, is_host=is_host)

@app.route('/api/match/<int:match_id>')
def match_api(match_id):
    if 'user_id' not in session:
        return {'error': 'Unauthorized'}, 401
        
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM kellenh_matchmaking WHERE id = %s", (match_id,))
    match = cur.fetchone()
    cur.close()
    
    if not match:
        return {'error': 'Match not found'}, 404
        
    return match

@app.route('/create_match', methods=['POST'])
def create_match():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    name = request.form['name']
    ipaddress = request.remote_addr
    if ipaddress == '127.0.0.1':
        ipaddress = urlopen('https://api.ipify.org').read().decode('utf8')
    p1name = session['username']
    p1lastping = datetime.now()

    cur = mysql.connection.cursor()
    query = "INSERT INTO kellenh_matchmaking (name, ipaddress, p1name, p1lastping) VALUES (%s, %s, %s, %s);"
    cur.execute(query, (name, ipaddress, p1name, p1lastping))
    mysql.connection.commit()
    match_id = cur.lastrowid
    cur.close()

    return redirect(url_for('game', match_id=match_id))

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




@socketio.on('join')
def on_join(data):
    username = data['username']
    room = data['room']
    join_room(room)
    emit('status', {'msg': username + ' has entered the room.'}, room=room)

@socketio.on('message')
def on_message(data):
    room = data['room']
    msg = data['msg']
    username = data['username']
    emit('message', {'user': username, 'msg': msg}, room=room)

if __name__ == '__main__':
    socketio.run(app, debug=True)
