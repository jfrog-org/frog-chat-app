from flask import render_template, redirect, url_for, session, request
from . import auth_blueprint
from project import app
from project.models import db, User, arc4_encrypt_password
from sqlalchemy import text


@auth_blueprint.route("/login", methods=["GET", "POST"])
def login():
    print("Entered Login")
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        print(f"Log: username: {username}, password: {password}")
        password_hash = arc4_encrypt_password(password, app.config['XOR_SECRET_KEY'])

        # SQL injection
        sql = f"SELECT username, password_hash FROM frogs WHERE username='{username}' AND password_hash='{password_hash}';"
        print(sql)
        result = None
        result = db.session.execute(text(sql))
        print(result, flush=True)
        fetch_res = result.fetchone()
        print(fetch_res, flush=True)
        print(fetch_res)
        if result and fetch_res:
            session['username'] = str(fetch_res[0])
            frog = User.query.filter_by(username=session['username']).first()
            session['is_admin'] = frog.is_admin
            session.permanent = True
            return redirect(url_for('chat.home'))
        else:
            print("No result")
            error = 'Invalid username or password. Please try again.'
            return render_template('login.html', error=error)
    # If it's a GET request, render the login form
    return render_template('login.html')


@auth_blueprint.route("/register", methods=["GET", "POST"])
def register():
    if request.method == 'POST':
        email = request.form['email']
        username = request.form['username']
        password = request.form['password']
        confirm_password = request.form['confirm_password']

        # Check if the passwords match
        if password != confirm_password:
            error = 'Passwords do not match. Please try again.'
            return render_template('register.html', error=error)

        user = User.query.filter_by(username=username).first()
        if user:
            error = "Username already exists"
            return render_template('register.html', error=error)
        else:
            password_hash = arc4_encrypt_password(password, app.config['XOR_SECRET_KEY'])
            # SQL Injection.
            sql = f"INSERT INTO frogs (email,username,password_hash,is_admin) VALUES ('{email}','{username}','{password_hash}',false);"
            print(sql)
            db.session.execute(text(sql))
            db.session.commit()
            return redirect(url_for('auth.login'))
    return render_template('register.html')


@auth_blueprint.route("/logout", methods=["POST"])
def logout():
    session.pop('username', None)
    return redirect(url_for('chat.home'))
