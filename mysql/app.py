from flask import Flask, render_template, request, redirect, url_for
from flask_mysqldb import MySQL

app = Flask(__name__)

# MySQL Configuration
app.config['MYSQL_HOST'] = 'mysql.2526.lakeside-cs.org'
app.config['MYSQL_USER'] = 'student2526'
app.config['MYSQL_PASSWORD'] = 'ACSSE2526'
app.config['MYSQL_DB'] = '2526playground'
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'

mysql = MySQL(app)

# Main page - shows all active posts (lives > 0)
# Each time a post is displayed, it loses 1 life
@app.route('/')
def index():
    cur = mysql.connection.cursor()
    
    # Get all posts with lives > 0, ordered by newest first
    query = "SELECT * FROM kellenh_posts WHERE lives > 0 ORDER BY created_at DESC;"
    # I'm not actually deleting the posts, just only rendering the ones that have lives left
    cur.execute(query)
    posts = cur.fetchall()
    # Decrement life for each post that was just viewed/displayed
    for post in posts:
        decrement_query = "UPDATE kellenh_posts SET lives = lives - 1 WHERE post_id = %s;"
        cur.execute(decrement_query, (post['post_id'],))
    mysql.connection.commit()
    cur.close() # Good practice
    return render_template('index.html.j2', posts=posts)

# Create new post page (GET shows form, POST creates post)
# Neat little trick I had on a past project (not lakeside), not 100% sure where it came from originally
@app.route('/create', methods=['GET', 'POST'])
def create():
    if request.method == 'GET':
        return render_template('create_post.html.j2')
    elif request.method == 'POST':
        # Get form data
        message = request.values.get("message", "").strip()
        # Server-side validation, extensible
        errors = []
        # Validate message (required, not empty)
        if not message:
            errors.append("Message cannot be empty")
        # If validation errors, show them
        if errors:
            return render_template('create_post.html.j2', errors=errors, message=message)
        # All posts start with exactly 10 lives
        cur = mysql.connection.cursor()
        # Had to look up some details on SQL rules, credit to the internet (i think it was stack overflow? i dont remember 100%)
        query = "INSERT INTO kellenh_posts (message, lives) VALUES (%s, 10);"
        queryVars = (message,)
        cur.execute(query, queryVars)
        mysql.connection.commit()
        cur.close()
        # Show success page that tells user to close window
        return render_template('post_created.html.j2')

# Add life to a post (increment lives by 2, max 10)
# We add 2 because redirecting to index will immediately decrement 1 when viewing
@app.route('/addlife/<int:post_id>', methods=['POST'])
def add_life(post_id):
    cur = mysql.connection.cursor()
    # Secured query to add 2 lives (but don't exceed 10)
    # Adding 2 compensates for the -1 that happens when index page loads after redirect
    query = "UPDATE kellenh_posts SET lives = LEAST(lives + 2, 10) WHERE post_id = %s;"
    queryVars = (post_id,)
    cur.execute(query, queryVars)
    mysql.connection.commit()
    cur.close()
    # Redirect back to main page
    return redirect(url_for('index'))
