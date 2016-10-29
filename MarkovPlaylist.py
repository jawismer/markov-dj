import urllib2
import time
import json
import random


def createMarkovChain(userName):
	baseurl = ''.join(["http://ws.audioscrobbler.com/2.0/",
	                   "?method=user.getrecenttracks",
	                   "&user="+userName+"&api_key=720ae7757fd7bfc22f347f3f21941ffd&limit=200"])

	f = urllib2.urlopen(baseurl+"&page=1&format=json", timeout=200)
	jsonResponse = json.loads(f.read())

	#parse last.fm track log
	probMatrix = {}
	artistTrackLists = {}
	wholeTrackList = []
	tracksList = []
	trackDict = {}

	prevArtist = ''
	prevUTS = '0'

	for track in jsonResponse['recenttracks']['track']:
		#print track['artist']['#text']+", "+track['name']
		trackDict = {}
		trackDict['artist'] = track['artist']['#text']
		trackDict['song'] = track['name']
		trackDict['uts'] = track['date']['uts'] # todo: add exception handling for now playing (no 'date' key)
		trackDict['date'] = track['date']['#text']
		tracksList.append(trackDict)
		if track['artist']['#text'] not in artistTrackLists:
			artistTrackLists[track['artist']['#text']] = []
			artistTrackLists[track['artist']['#text']].append(track['name'])
		else:
			if track['name'] not in artistTrackLists[track['artist']['#text']]:
				artistTrackLists[track['artist']['#text']].append(track['name'])
		if track['artist']['#text'] != prevArtist:
			#print track['artist']['#text']+", "+track['date']['#text']+", ", (int(prevUTS)-int(track['date']['uts']))/60, "min"
			prevArtist = track['artist']['#text']
			if track['artist']['#text'] not in probMatrix:
				probMatrix[track['artist']['#text']] = {}
		else:
			#print track['artist']['#text']+", "+track['date']['#text']
			prevUTS = track['date']['uts']
	#print "page: 1"

	numPages = jsonResponse['recenttracks']['@attr']['totalPages']
	i = 2
	while i < int(numPages)+1:
		time.sleep(0.2)
		f = urllib2.urlopen(baseurl+"&page="+str(i)+"&format=json", timeout=200)
		jsonResponse = json.loads(f.read())
		for track in jsonResponse['recenttracks']['track']:
			trackDict = {}
			trackDict['artist'] = track['artist']['#text']
			trackDict['song'] = track['name']
			trackDict['uts'] = track['date']['uts']
			trackDict['date'] = track['date']['#text']
			tracksList.append(trackDict)
			if track['artist']['#text'] not in artistTrackLists:
				artistTrackLists[track['artist']['#text']] = []
				artistTrackLists[track['artist']['#text']].append(track['name'])
			else:
				if track['name'] not in artistTrackLists[track['artist']['#text']]:
					artistTrackLists[track['artist']['#text']].append(track['name'])
			if track['artist']['#text'] != prevArtist:
				#print track['artist']['#text']+", ", (int(prevUTS)-int(track['date']['uts']))/60, "min"
				prevArtist = track['artist']['#text']
				if track['artist']['#text'] not in probMatrix:
					probMatrix[track['artist']['#text']] = {}
			prevUTS = track['date']['uts']
			#print track['artist']['#text']+", "+track['name']
		#print "page: "+str(i)
		i = i + 1 

	# separate into smaller lists with time difference between artists less than 90 minutes 
	prevArtist = ''
	prevUTS = '0'
	minorList = []
	majorList = []
	tracksList.reverse()
	for track in tracksList:
		if track['artist'] != prevArtist:
			#print track['date']+", "+track['artist']+", ", (int(track['uts'])-int(prevUTS))/60, "min"
			prevArtist = track['artist']
			# todo: if curUTS-prevUTS < 60, add to minor list. else, start new minor list
			if (int(track['uts'])-int(prevUTS))/60 < 90:
				minorList.append(track['artist'])
			else:
				majorList.append(minorList)
				minorList = []
				minorList.append(track['artist'])
		prevUTS = track['uts']

	#create markov chain of artists
	for mList in majorList:
		#print mList
		for i in range(len(mList)-1):
			if mList[i+1] not in probMatrix[mList[i]]:
				probMatrix[mList[i]][mList[i+1]] = 1
			else:	
				probMatrix[mList[i]][mList[i+1]] = probMatrix[mList[i]][mList[i+1]] + 1

	#print probMatrix
	return {'probMatrix': probMatrix, 'artistTrackLists': artistTrackLists}



#enter seed track, generate new playlist

# todo: go to next artist based on generated probabilities
# next track probability = probMatrix[currentArtist][nextArtist] / sum of all values in probMatrix[currentArtist]
# select random track of nextArtist from last plays

def createPlaylist(probMatrix, artistTrackLists, trackID):
	seedArtist = trackID # add user input for seed track
	done = False
	current = seedArtist
	playlistStrings = []
	songCount = 0
	while(done != True):
		time.sleep(0.1)
		if not artistTrackLists[current]:
			break
		randTrack = random.choice(artistTrackLists[current])
		#print current+", "+randTrack
		playlistStrings.append(current+", "+randTrack)
		artistTrackLists[current].remove(randTrack)
		if not probMatrix[current]:
			done = True
		else:
			if len(probMatrix[current]) == 1:
				current = probMatrix[current].keys()[0]
			else:
				total = 0
				rand = random.randint(1, sum(probMatrix[current].values()))
				for key in probMatrix[current]: # todo: if probMatrix[current] dict is empty, set done = true
					total = total + probMatrix[current][key]
					if rand <= total:
						current = key
						break
	#retString = '\n'.join(playlistStrings)
	return playlistStrings