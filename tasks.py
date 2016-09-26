from celery import Celery
from MarkovPlaylist import createPlaylist

cel = Celery()
cel.config_from_object("celery_settings")

@cel.task(bind=True)
def task1(self):
	returnVal = createPlaylist(session.get('username', None))
	session['probMatrix'] = returnVal['probMatrix']
	session['artistTrackLists'] = returnVal['artistTrackLists']
	return redirect("/user/"+session['username'])