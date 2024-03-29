from flask import render_template, jsonify, request, redirect, url_for, send_file, session, make_response,flash
import json
from flask import Flask
from pymongo.mongo_client import MongoClient
from flask_session import Session
from datetime import timedelta
import uuid

import os
uri = "mongodb+srv://nidhibangera179:oKZgap67oQm2VnL6@gymwebsite.lfev9qe.mongodb.net/?retryWrites=true&w=majority&appName=GymWebsite"
# Create a new client and connect to the server
client = MongoClient(uri)


db = client['maindb'] 
collection = db['users']
creds = db["user_creds"]

x=0



app = Flask(__name__)

app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"

app.secret_key = "fitness"


Session(app)

def generate_session_id():
    a = uuid.uuid1()
    return str(a)

@app.route('/')
def hello():
    return render_template("index.html") 

@app.route('/register', methods=['GET','POST'])
def register():
    return render_template("register.html")

@app.route('/data', methods=["GET", "POST"])
def data():
    data = {}
    if request.method == "POST":
        data['Name'] = request.form['username']
        data['Email'] = request.form['email']
        data['Number'] = request.form['number']
        data['Gender'] = request.form['gender']
        data['Age'] = request.form['age']
        data['Address'] = ""

        useremail = str(request.form['email'])
        password = request.form['pswd1']

        if creds.find_one({'username': useremail}):
            flash('User already exists. Choose a different one.', 'danger')
            return render_template("register.html")
        else:
            creds.insert_one({'username': useremail,'password':password})
            db.collection.insert_one(data);
            flash('Registration successful. You can now log in.', 'success')
            return redirect(url_for('login'))

        print(data)
       
    return render_template("register.html")
       
@app.route('/user/<uname>/<sid>')
def user(uname,sid):
    return render_template("main.html",uname=uname)




@app.route('/logout')
def logout():
    session.pop('fitness', None)
    return render_template("login.html")


@app.route('/login')
def logg():
    return render_template("login.html")

@app.route('/page/<name>/<sid>')
def page(name,sid):
    userdata=db.collection.find()
    return render_template('admin.html', userdata=userdata,name=name)
    

@app.errorhandler(401)
def unauthorized_error(error):
    return render_template('abort.html'), 401

@app.route('/login', methods=["POST"])
def login():
    unname=request.form['username'];
    passwd=request.form['pass'];
    user = creds.find_one({"username": unname, "password": passwd})
    if user:
        ssid = generate_session_id()
        if unname == "Admin":
            if passwd == user["password"]:
                userdata=db.collection.find()
                session["user"] = "Admin"
                return redirect(url_for('page', name="admin",sid=ssid))
        
        else:
            n = db.collection.find_one({"Email": unname})
            uname = n["Name"]        
            session["user"] = uname
            return redirect(url_for('user',uname=uname ,sid=ssid))

    else:
        flash('Enter the correct Email ID/password!')
        return render_template("login.html")



if __name__ == "__main__":
    try:
        client.admin.command('ping')
        print("Pinged your deployment. You successfully connected to MongoDB!")
    except Exception as e:
        print(e)
    app.run(debug=True)

