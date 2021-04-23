from flask import Flask, request, url_for, redirect, session
import pymongo
from pymongo import MongoClient
from flask_pymongo import PyMongo
from authlib.integrations.flask_client import OAuth
from dotenv import dotenv_values

config = dotenv_values(".env")

mongo = PyMongo()
client = pymongo.MongoClient(config["MONGO_URL"])
db = client["users"]
collection = db["user"]

app = Flask(__name__)
app.secret_key = 'thisissupposedtobearandomkeybutimtoolazytocomeupwithonesohereyougo'

oauth = OAuth(app)
google = oauth.register(
    name="google",
    client_id=config["GOOGLE_CLIENT_ID"],
    client_secret=config["GOOGLE_SECRET"],
    access_token_url='https://accounts.google.com/o/oauth2/token',
    access_token_params=None,
    authorize_url='https://accounts.google.com/o/oauth2/auth',
    authorize_params=None,
    api_base_url='https://www.googleapis.com/oauth2/v1/',
    client_kwargs={'scope': 'openid profile email'},
) 

@app.route('/')
def root():
    return redirect('/login')

@app.route('/login')  
def login():
    google = oauth.create_client('google')
    redirect_uri = url_for('authorize', _external=True)
    return google.authorize_redirect(redirect_uri)

@app.route('/authorize')
def authorize():
    google = oauth.create_client('google')
    token = google.authorize_access_token()
    resp = google.get('userinfo')   
    session['profile'] = resp.json()

    # query to MongoDB collection
    users = collection.find()
    userExists = False
    profile = session['profile']
    for user in users:
        if user['id'] == profile['id'] and user['email'] == profile['email']:
            userExists = True
    if not userExists:
        collection.insert_one({"id": profile['id'], "email": profile['email'],"progress": 0})

    return redirect('/home')

@app.route('/home')
def home(): 
    profile = session['profile']
    email = profile['email']
    userid = profile['id']

    return f"Hello, {email}\n" + f"ID: {userid}"

@app.route('/progress')
def progress():
    profile = session['profile']
    collection.update_one(
        {"id": profile['id']},
        {"$inc": {"progress": 1}}
    )
    return redirect('/home')

    
if __name__ == '__main__':
    app.run()

