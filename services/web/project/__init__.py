import os
import sqlalchemy
from flask import Flask, jsonify, send_from_directory, request, render_template, make_response, redirect
from flask_sqlalchemy import SQLAlchemy
from werkzeug.utils import secure_filename
app = Flask(__name__)
app.config.from_object("project.config.Config")
db = SQLAlchemy(app)


class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(128), unique=True, nullable=False)
    active = db.Column(db.Boolean(), default=True, nullable=False)

    def __init__(self, email):
        self.email = email


@app.route("/static/<path:filename>")
def staticfiles(filename):
    return send_from_directory(app.config["STATIC_FOLDER"], filename)


@app.route("/media/<path:filename>")
def mediafiles(filename):
    return send_from_directory(app.config["MEDIA_FOLDER"], filename)


@app.route("/upload", methods=["GET", "POST"])
def upload_file():
    if request.method == "POST":
        file = request.files["file"]
        filename = secure_filename(file.filename)
        file.save(os.path.join(app.config["MEDIA_FOLDER"], filename))
    return """
    <!doctype html>
    <title>upload new File</title>
    <form action="" method=post enctype=multipart/form-data>
      <p><input type=file name=file><input type=submit value=Upload>
    </form>
    """


def hello_world():
    return jsonify(hello="world")


@app.route('/')
def root():
    print_debug_info()
    '''
    text = 'hello cs40'
    text = '<strong>' + text + '</strong>' # + 100
    return text
    '''
    messages = []

    # check if logged in correctly
    username = request.cookies.get('username')
    password = request.cookies.get('password')
    good_credentials = are_credentials_good(username, password)
    print('good_credentials=', good_credentials)

    # present the pages of messages
    try:
        page_number = int(request.args.get('page', 1))
    except (ValueError, TypeError):
        page_number = 1

    sql = sqlalchemy.sql.text("""
    SELECT username, message, created_at
    FROM messages JOIN users USING (user_id)
    ORDER BY created_at DESC LIMIT 20 OFFSET :offset * 20;
    """)

    res = db.session.execute(sql, {
        'offset': page_number - 1
    })

    for row_messages in res.fetchall():
        messages.append({
            'message': row_messages[1],
            'username': row_messages[0],
            'created_at': row_messages[2],
        })

    return render_template('root.html', logged_in=good_credentials, messages=messages, page_number=page_number)


def print_debug_info():
    # GET method
    print('request.args.get("username")=', request.args.get("username"))
    print('request.args.get("password")=', request.args.get("password"))

    # POST method
    print('request.form.get("username")=', request.form.get("username"))
    print('request.form.get("password")=', request.form.get("password"))

    # cookies
    print('request.cookies.get("username")=', request.cookies.get("username"))
    print('request.cookies.get("password")=', request.cookies.get("password"))


def are_credentials_good(username, password):
    sql = sqlalchemy.sql.text('''
        SELECT user_id FROM users
        WHERE username = :username
        AND password = :password;
    ''')

    res = db.session.execute(sql, {
        'username': username,
        'password': password
    })

    if res.fetchone() is None:
        return False
    else:
        return True


@app.route('/login', methods=['GET', 'POST'])
def login():
    print_debug_info()
    
    username = request.form.get('username')
    password = request.form.get('password')
    print('username=', username)
    print('password=', password)

    good_credentials = are_credentials_good(username, password)
    print('good_credentials=', good_credentials)

    # the first time we've visited, no form submission
    if username is None:
        return render_template('login.html', missing=False, bad_credentials=False, logged_in=good_credentials)
    elif not username or not password:
        return render_template('login.html', missing=True, bad_credentials=False, logged_in=good_credentials)

    else:
        if not good_credentials:
            return render_template('login.html', bad_credentials=True, missing=False, logged_in=good_credentials)
        else:
            # create a cookie that contains the username/password info
            response = make_response(redirect('/'))
            response.set_cookie('username', username)
            response.set_cookie('password', password)
            return response


@app.route('/logout')
def logout():
    print_debug_info()
    response = make_response(render_template('logout.html'))
    response.delete_cookie('username')
    response.delete_cookie('password')
    return response


@app.route('/create_user', methods=['GET', 'POST'])
def create_user():
    print_debug_info()

    username = request.cookies.get('username')
    password = request.cookies.get('password')

    good_credentials = are_credentials_good(username, password)
    if good_credentials:
        return redirect('/')

    new_username = request.form.get('new_username')
    new_password = request.form.get('new_password')
    new_password2 = request.form.get('new_password2')
    new_age = request.form.get('new_age')

    if new_username is None:
        return render_template('create_user.html')
    if not new_username:
        return render_template('create_user.html', missing_username=True)
    elif not new_password2 or not new_password:
        return render_template('create_user.html', missing_password=True)
    elif not new_age.isnumeric():
        return render_template('create_user.html', invalid_age=True)
    else:
        if new_password != new_password2:
            return render_template('create_user.html', not_matching=True)
        else:
            try:
                sql = sqlalchemy.sql.text('''
                    INSERT INTO users (username, password, age)
                    VALUES (:username, :password, :age)
                    ''')

                db.session.execute(sql, {
                    'username': new_username,
                    'password': new_password,
                    'age': new_age
                })
                db.session.commit()

                response = make_response(redirect('/'))
                response.set_cookie('username', new_username)
                response.set_cookie('password', new_password)
                return response
            except sqlalchemy.exc.IntegrityError:
                return render_template('create_user.html', already_exists=True)


@app.route('/create_message', methods=['GET', 'POST'])
def create_message():
    print_debug_info()

    username = request.cookies.get('username')
    password = request.cookies.get('password')

    good_credentials = are_credentials_good(username, password)
    if not good_credentials:
        return redirect('/')

    sql = sqlalchemy.sql.text('''
        SELECT user_id FROM users WHERE username = :username
        ''')

    res = db.session.execute(sql, {
        'username': username
    })

    for row in res.fetchall():
        sender_id = row[0]

    message = request.form.get('message')

    if message is None:
        return render_template('create_message.html', logged_in=good_credentials)
    elif not message:
        return render_template('create_message.html', invalid_message=True, logged_in=good_credentials)
    else:
        sql = sqlalchemy.sql.text("""
        INSERT INTO messages (user_id, message) VALUES (:sender_id, :message);
        """)
        db.session.execute(sql, {
            'sender_id': sender_id,
            'message': message
        })

        db.session.commit()

        return render_template('create_message.html', message_sent=True, logged_in=good_credentials)


@app.route('/search', methods=['GET', 'POST'])
def search():

    print_debug_info()

    username = request.cookies.get('username')
    password = request.cookies.get('password')
    good_credentials = are_credentials_good(username, password)

    if request.form.get('query'):
        query = request.form.get('query')
    else:
        query = request.args.get('query', '')

    try:
        page_number = int(request.args.get('page', 1))
    except (ValueError, TypeError):
        page_number = 1

    messages = []
    if query:
        sql = sqlalchemy.sql.text("""
        SELECT
            ts_headline('english', m.message, plainto_tsquery('english', :query)) AS highlight_msg,
            u.username,
            m.created_at,
            ts_rank_cd(m.fts_vector, plainto_tsquery('english', :query)) AS rank
        FROM messages m
        JOIN users u ON m.user_id = u.user_id
        WHERE m.fts_vector @@ plainto_tsquery('english', :query)
        ORDER BY rank DESC, m.created_at DESC
        LIMIT 20 OFFSET :offset * 20;
        """)

        res = db.session.execute(sql, {
            'offset': page_number,
            'query': ' & '.join(query.split())
        })

        for row_messages in res.fetchall():
            messages.append({
                'message': row_messages[0],
                'username': row_messages[1],
                'created_at': row_messages[2],
            })
    else:
        sql = sqlalchemy.sql.text("""
            SELECT username, message, created_at
            FROM messages JOIN users USING (user_id)
            ORDER BY created_at DESC LIMIT 20 OFFSET :offset * 20;
        """)

        res = db.session.execute(sql, {
            'offset': page_number - 1
        })

        for row_messages in res.fetchall():
            messages.append({
                'message': row_messages[1],
                'username': row_messages[0],
                'created_at': row_messages[2],
            })

    return render_template('search.html', logged_in=good_credentials, query=query, messages=messages, page_number=page_number)


if __name__ == "__main__":
    app.run()
