from __future__ import print_function # In python 2.7
from flask import Flask, render_template, request, redirect, session, jsonify
from MarkovPlaylist import createPlaylist, createMarkovChain
from tasks import task1
from celery import Celery
from flask.ext.sqlalchemy import SQLAlchemy
import requests
import sys
import os

app = Flask(__name__)
app.secret_key = 'A0Zr98j/3yX R~XHH!jmN]LWX/,?RT'
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'postgresql://localhost/testDatabase')
db = SQLAlchemy(app)

app.config['CELERY_BROKER_URL'] = os.environ.get('REDISTOGO_URL', 'redis://localhost:6379/0')
app.config['CELERY_RESULT_BACKEND'] = os.environ.get('REDISTOGO_URL', 'redis://localhost:6379/0')
app.config['CELERY_ACCEPT_CONTENT'] = ['json']
app.config['CELERY_TASK_SERIALIZER'] = 'json'
app.config['CELERY_RESULT_SERIALIZER'] = 'json'

celery = Celery(app.name, broker=app.config['CELERY_BROKER_URL'])
celery.conf.update(app.config)


class User(db.Model):
    __tablename__ = "users"
    id = db.Column(db.String(50), primary_key=True)
    data = db.Column(db.PickleType)

@celery.task(bind=True)
def task1(self, username):
    print('cel route', file=sys.stderr)
    with app.test_request_context():
        self.update_state(state='IN_PROGRESS')
        returnVal = createMarkovChain(username)
        print('cel proc complete', file=sys.stderr)
        self.update_state(state='DONE')
        s = User(id=username, data=returnVal)
        db.session.add(s)
        db.session.commit()
        return returnVal

@app.route('/status/<task_id>')
def taskstatus(task_id):
    task = long_task.AsyncResult(task_id)
    return task.state

@app.route('/getstatus/', methods=['POST'])
def getStatus():
    username = request.json['user']
    user = User.query.filter_by(id=username).first()
    print('get status route'+username, file=sys.stderr)
    if user is not None:
        print('get status done', file=sys.stderr)
        return jsonify({'done': 'T'}), 202, {'Location': ''}
    else:
        return jsonify({'done': 'F'}), 202, {'Location': ''}

@app.route('/autocomplete', methods=['GET'])
def autocomplete():
    resp = request.args.get('q') # send username%query
    username = resp.split(';')[0]
    search = resp.split(';')[1]
    user = User.query.filter_by(id=username).first()
    data = user.data
    artists = data['artistTrackLists'].keys()
    results = []
    for item in artists:
        if item.lower().startswith(search.lower()):
            results.append(item)
    return jsonify(matching_results=results)

@app.route("/")
def start():
    print('route 1', file=sys.stderr)
    print('route 1 !!!!', file=sys.stderr)
    return render_template("homepage.html")

@app.route('/', methods=['POST'])
def redirectToUser():
    print('route 2', file=sys.stderr)
    text = request.form['text']
    session['username'] = text
    user = User.query.filter_by(id=text).first()
    if user is None:
        task = task1.apply_async(kwargs={'username': text})
        session['taskID'] = task.id
    return redirect("/user/"+text)

@app.route('/done', methods=['POST'])
def doneRedirect():
    print('done', file=sys.stderr)
    print(request.data, file=sys.stderr)
    return redirect("/user/poop")

@app.route("/user/<username>")
def displayUser(username):
    print('route 3', file=sys.stderr)
    session['username'] = username
	#task1.delay()
    return render_template("userpage.html")

@app.route('/user/', methods=['POST'])
def redirectToPlaylist():
    text = request.form['text']
    return redirect("/user/"+session.get('username', None)+"/seed/"+text)

@app.route("/user/<username>/seed/<trackID>")
def displayPlaylist(username, trackID):
    user = User.query.filter_by(id=username).first()
    data = user.data
    # todo: https://api.spotify.com/v1/search?q=artist:artistName%20trackName&type=track
    # todo: <iframe src="https://embed.spotify.com/?uri=spotify:trackset:Playlist name:<track URIs(comma separated)>" frameborder="0" allowtransparency="true"></iframe>
    return render_template("playlist.html", testList=createPlaylist(data['probMatrix'], data['artistTrackLists'], trackID))

if __name__ == "__main__":
    app.run(debug=True)
    celery.start()