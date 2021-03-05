from flask import Flask, request, url_for, redirect, session
import pymongo
from pymongo import MongoClient
from flask_pymongo import PyMongo
from authlib.integrations.flask_client import OAuth
from dotenv import dotenv_values

config = dotenv_values(".env")

mongo = PyMongo()
client = pymongo.MongoClient(config.MONGO_URL)
db = client["users"]
collection = db["user"]

app = Flask(__name__)
app.secret_key = 'thisissupposedtobearandomkeybutimtoolazytocomeupwithonesohereyougo'

oauth = OAuth(app)
google = oauth.register(
    name="google",
    client_id=config.GOOGLE_CLIENT_ID,
    client_secret=config.GOOGLE_SECRET
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
    return redirect('/home')

@app.route('/home')
def home(): 
    profile = dict(session)['profile']
    email = profile['email']
    userid = profile['id']

    # query to MongoDB
    collection.insert_one({
        "id": userid,
        "email": email
    })

    return f"Hello, {email}\n" + f"ID: {userid}"


    
if __name__ == '__main__':
    app.run()











# @app.route('/adduser')
# def usertest():
#     collection.insert_one({"name": "anefa"})
#     return "hello"

# @app.route('/finduser')
# def finduser():
#     print(collection.find_one({"name": "devin"}))
#     return "lol"

# @app.route('/deleteuser')
# def deleteuser():
#     collection.find_one_and_delete({"name": "devin"})
#     print(collection.find({}))
#     return "lol2"
