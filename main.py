import  os
import urllib

import  jinja2
from flask import Flask, render_template, redirect, request,url_for
from google.appengine.ext import ndb

app=Flask(__name__)
app.debug=True

JINJA2_ENVIRONMENT= jinja2.Environment(
    loader= jinja2.FileSystemLoader(os.path.dirname(__file__)),
    extensions= ['jinja2.ext.autoescape'],
    autoescape=True
)
DEFAULT_BBS='home'

def create_ndbKey(_roomName=DEFAULT_BBS):
    return ndb.Key('Message',_roomName)

class MyKind(ndb.Model):
    content= ndb.StringProperty(indexed=False)
    date=ndb.DateTimeProperty(auto_now_add=True)

@app.route('/')
def index():
    room_name = request.args.get('q')

    if room_name == '' or room_name== None:
        room_name= 'home'

    query= MyKind.query(ancestor=create_ndbKey(room_name)).order(-MyKind.date)
    messages= query.fetch(10)

    for msg in messages:
        msg.content=urllib.unquote((msg.content).encode('utf-8'))
        msg.content=(msg.content).decode('utf-8')

    obj={
        'messages':messages,
        'room':room_name
    }

    return render_template('index.html',data=obj)

@app.route('/add',methods=['POST'])
def add():
    room_name= request.args.get('q','')
    myEntity= MyKind(parent=create_ndbKey(room_name))
    myEntity.content = (request.form['content']).encode('utf-8')
    myEntity.put()

    return redirect(url_for('index',q=room_name))
