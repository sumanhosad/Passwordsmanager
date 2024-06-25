import random
import json
import base64
import string
from sqlalchemy import String, Column
from flask import Flask, render_template, request, redirect, session, url_for
from flask_sqlalchemy import SQLAlchemy
import hashlib
from datetime import datetime, timedelta
from website.encryption import generate_key, encrypt_message, decrypt_message, concatenate_sublists, split_into_sublists

db = SQLAlchemy()


class User(db.Model):
    username = db.Column(db.String(50), primary_key=True)
    master_password = db.Column(db.String(100), nullable=False)
    passwords = db.Column(db.Text, nullable=True)  

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'passwordmanager'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///passwordmanager.db'

    db.init_app(app)
    with app.app_context():
        db.create_all()


    @app.route('/login', methods=["POST","GET"])
    def login():
        session.pop("user", None)
        if request.method == "POST":
            user = request.form["username"]
            master_password = request.form["password"]
            existing_user = User.query.filter_by(username=user).first()
            if existing_user is None:
                return render_template('login.html', message="Username doesn't exists!!")   
            if existing_user and existing_user.master_password == hash_password(master_password):
                session["user"] = user
                session["mp"]=hash_password(master_password)
                mp=session['mp']
                return redirect(url_for("home"))
            else:
                return render_template('login.html', message="Password Doesnt MAtch!!")   

        else:
            session.clear()
            return render_template('login.html')
    @app.route('/')
    def home():
        if "user" in session:
            user = session["user"]
            return render_template('homepage.html')
        else:
            return render_template('login.html')

    @app.route('/signin', methods=["POST","GET"])
    def signin():
        if request.method == "POST":
            user = request.form["username"]
            mp=request.form["password"]
            hashed_mp = hash_password(mp)
            
            existing_user = User.query.filter_by(username=user).first()
            if existing_user:
                return render_template('signin.html', message="Username already exists. Please choose a different username.")            
            
            session["user"] = user
            session["mp"]=hash_password(mp)
            mp=session['mp']
            useradd(user, mp)
            db.create_all()
            return redirect(url_for("home", usr=user))
        else:
            return render_template('signin.html')

    
    @app.route('/addpassword', methods=['GET', 'POST'])
    def addpassword():
        if(session["user"]==None):
            return redirect(url_for("login"))
        user=session.get('user')
        if request.method == 'POST':
        # Extract form inputs
            website_details = [
                request.form['website'],
                request.form['url'],
                request.form['email'],
                request.form['username'],
                request.form['password']
            ]

        # Encrypt password details
            mp = session.get('mp')
            if mp is None:
                # Handle case where master password is not in session
                return "Error: Master password not found in session."

            # Update user record with encrypted details
            userdata = User.query.filter_by(username=session.get("user")).first()
            user=userdata.username
            if userdata is None:
                # Handle case where user record does not exist
                return "Error: User not found."
            existpassword=retrieve_passwords(user)
            if existpassword==False:
                encrypted_message=encrypt_message(website_details,session['mp'])
                replace_passwords(user,encrypted_message)
                db.session.commit()
            else:
                existdecrypass=decrypt_message(existpassword,session["mp"])
                existdecrypass= existdecrypass + website_details
                encrypted_messages=encrypt_message(existdecrypass,session['mp'])
                replace_passwords(user,encrypted_messages)
                db.session.commit()
            # Redirect to the same page to clear form data
            return redirect(url_for("addpassword"))
        else:
            # Render the addpassword.html template for GET requests
            return render_template('addpassword.html')
        

    @app.route('/accesspassword')
    def accesspassword():
        if "user" not in session:
            return redirect(url_for('login'))

        username = session["user"]
        if retrieve_passwords(username)==False:
            return render_template('accesspassword.html', error="No Password added")
        else: 
            encrypted_passwords=retrieve_passwords(username)
            decrypted_passwords=decrypt_message(encrypted_passwords,session['mp'])
            passwords=split_into_sublists(decrypted_passwords)

            return render_template('accesspassword.html', message=passwords)

    @app.route('/managepassword')
    def managepassword():
        if "user" not in session:
            return redirect(url_for('login'))
        username = session["user"]
        if retrieve_passwords(username)==False:
            return render_template('managepassword.html', error="No Password added")
        else: 
            encrypted_passwords=retrieve_passwords(username)
            decrypted_passwords=decrypt_message(encrypted_passwords,session['mp'])
            passwords=split_into_sublists(decrypted_passwords)

            return render_template('managepassword.html', message=passwords)
        
    @app.route('/editpassword/<int:sublist_index>', methods=['GET', 'POST'])    
    def editpassword(sublist_index):
        if "user" not in session:
            return redirect(url_for('login'))

        username = session["user"]

        encrypted_passwords=retrieve_passwords(username)
        decrypted_passwords=decrypt_message(encrypted_passwords,session['mp'])
        passwords=split_into_sublists(decrypted_passwords)
        elements=passwords[sublist_index]
        if request.method == 'POST':
            passwords[sublist_index][0]=request.form['website']
            passwords[sublist_index][1]=request.form['url']
            passwords[sublist_index][2]=request.form['email']
            passwords[sublist_index][3]=request.form['username']
            passwords[sublist_index][4]=request.form['password']
            encrypted_messages=encrypt_message(concatenate_sublists(passwords),session['mp'])
            replace_passwords(username,encrypted_messages)
            db.session.commit()
            return render_template('editpassword.html', message=elements, sublist_index=sublist_index, success="Passwordss edited Succesfully" )


        return render_template('editpassword.html', message=elements, sublist_index=sublist_index )

    @app.route('/deletepassword/<int:sublist_index>', methods=['POST'])
    def deletepassword(sublist_index):
        if "user" not in session:
            return redirect(url_for('login'))

        username = session["user"]

        if retrieve_passwords(username)==False:
            return render_template('managepassword.html', error="No Password added")
        encrypted_passwords=retrieve_passwords(username)
        decrypted_passwords = decrypt_message(encrypted_passwords, session['mp'])
        passwords = split_into_sublists(decrypted_passwords)
        if len(passwords)==1:
            replace_passwords(username,None)
            db.session.commit()
            return render_template('managepassword.html', error="no Password Added")
        else:
            del passwords[sublist_index]
            encrypted_messages = encrypt_message(concatenate_sublists(passwords), session['mp'])
            replace_passwords(username, encrypted_messages)
            db.session.commit()
            return render_template('managepassword.html', success='Password deleted successfully', message=passwords)
                    

    return app

def useradd(username, master_password):
    new_user = User(username=username, master_password=master_password)
    db.session.add(new_user)
    db.session.commit()

def hash_password(mp):
    hashed_mp = hashlib.sha256(mp.encode()).hexdigest()
    return hashed_mp

def retrieve_passwords(username):
    user = User.query.filter_by(username=username).first()
    if user:
        if user.passwords==None:
            return False        
        else:
            return user.passwords
    else:
        return None


def replace_passwords(username, new_passwords):
    user = User.query.filter_by(username=username).first()

    if user:
        user.passwords = new_passwords
        db.session.commit()
        return True
    else:
        return False

