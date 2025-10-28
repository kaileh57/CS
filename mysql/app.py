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

# Main page - shows all active posts (not expired)
# Posts expire when current time exceeds expire_at timestamp
@app.route('/')
def index():
    cur = mysql.connection.cursor()
    
    # Get all posts that haven't expired yet, ordered by newest first. Had to extnsively reference documentation for this one, and play around a ton (w3 and stack overflow)
    query = "SELECT *, TIMESTAMPDIFF(SECOND, NOW(), expire_at) as seconds_remaining FROM kellenh_posts WHERE expire_at > NOW() ORDER BY created_at DESC;"
    # I'm not actually deleting the posts, just only rendering the ones that haven't expired
    cur.execute(query)
    posts = cur.fetchall()
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
        # Validate message length (max 1000 characters)
        if len(message) > 1000:
            errors.append("Message cannot exceed 1000 characters")
        # If validation errors, show them
        if errors:
            return render_template('create_post.html.j2', errors=errors, message=message)
        # All posts start with 10 minutes of life (expire_at = created_at + 10 minutes)
        cur = mysql.connection.cursor()
        # Had to look up some details on SQL rules, credit to the internet (i think it was stack overflow? i dont remember 100%)
        query = "INSERT INTO kellenh_posts (message, expire_at) VALUES (%s, DATE_ADD(NOW(), INTERVAL 10 MINUTE));"
        queryVars = (message,)
        cur.execute(query, queryVars)
        mysql.connection.commit()
        cur.close()
        # Show success page that tells user to close window
        return render_template('post_created.html.j2')

# Add time to a post (extend expire_at by 1 minute, max 10 minutes from now)
# Each +1 adds 1 minute to the expiration time
@app.route('/addlife/<int:post_id>', methods=['POST'])
def add_life(post_id):
    cur = mysql.connection.cursor()
    # Only add time if post hasn't expired yet (prevents bringing back dead posts)
    # also referenced online docs (w3 and stack overflow) as well as generally searching "is there a least operation in mysql"
    # but basically this code updates the expireation time with the lower value of either 10 minutes in the future, or one minute from now.
    # this pretty much clamps it at 10 minutes
    # and also we check real fast if the post has expiered or not
    query = "UPDATE kellenh_posts SET expire_at = LEAST(DATE_ADD(expire_at, INTERVAL 1 MINUTE), DATE_ADD(NOW(), INTERVAL 10 MINUTE)) WHERE post_id = %s AND expire_at > NOW();"
    queryVars = (post_id,)
    cur.execute(query, queryVars)
    mysql.connection.commit()
    cur.close()
    # Redirect back to main page
    return redirect(url_for('index')) # need this for deployment to server i think
