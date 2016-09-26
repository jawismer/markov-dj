from flask import Flask, render_template, request, redirect, session
from MarkovPlaylist import createPlaylist
from tasks import task1
app = Flask(__name__)
app.secret_key = 'A0Zr98j/3yX R~XHH!jmN]LWX/,?RT'


# @celery.task(bind=True)
# def long_task(self):
#     """Background task that runs a long function with progress reports."""
#     verb = ['Starting up', 'Booting', 'Repairing', 'Loading', 'Checking']
#     adjective = ['master', 'radiant', 'silent', 'harmonic', 'fast']
#     noun = ['solar array', 'particle reshaper', 'cosmic ray', 'orbiter', 'bit']
#     message = ''
#     total = random.randint(10, 50)
#     for i in range(total):
#         if not message or random.random() < 0.25:
#             message = '{0} {1} {2}...'.format(random.choice(verb),
#                                               random.choice(adjective),
#                                               random.choice(noun))
#         self.update_state(state='PROGRESS',
#                           meta={'current': i, 'total': total,
#                                 'status': message})
#         time.sleep(1)
#     return {'current': 100, 'total': 100, 'status': 'Task completed!',
#             'result': 42}

# @app.route('/longtask', methods=['POST'])
# def longtask():
#     task = task1.apply_async()
#     return jsonify({}), 202, {'Location': url_for('taskstatus', task_id=task.id)}

@app.route("/")
def start():
	return render_template("homepage.html")

@app.route('/', methods=['POST'])
def redirectToUser():
    text = request.form['text']
    session['username'] = text
    task = task1.apply_async()
    return "Task started"

@app.route("/user/<username>")
def displayUser(username):
	session['username'] = username
	#task1.delay()
	return render_template("userpage.html")

@app.route('/user/', methods=['POST'])
def redirectToPlaylist():
    text = request.form['text']
    return redirect("/user/"+session.get('username', None)+"/seed/"+text)

@app.route("/user/<username>/seed/<trackID>")
def displayPlaylist(username, trackID):
	return render_template("playlist.html", testList=createPlaylist(session['probMatrix'], session['artistTrackLists'], trackID))

if __name__ == "__main__":
	app.run(debug=True)