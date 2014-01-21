#!/usr/bin/env python
from bs4 import BeautifulSoup
import urllib2
import requests
import sys
import re
import getpass
import json

if len(sys.argv) < 3:
    sys.exit(1);
else:
    username = sys.argv[1]
    searchterm = ' '.join(sys.argv[2:])

songkick_base_url = "https://www.songkick.com"
basesessionurl = "https://www.songkick.com/session/"
newloginurl    = basesessionurl + "new"
createloginurl = basesessionurl + "create"
basequerystring = "https://www.songkick.com/search?page=1&per_page=10&type=artists&query="
queryurl = basequerystring + urllib2.quote(searchterm)

re_auth_token = re.compile("input name=\"authenticity_token\" type=\"hidden\" value=\"(.*)\"")

headers = {'Content-Type':'application/json','Accept':'*/*','X-Requested-With':'XMLHttpRequest'}

def get_artists(soup):
    artist_names    = soup.select('li.artist > p.subject > a')
    artist_tracking = soup.select('input.artist')
    artist_form     = soup.select('li.artist > div > div > form')
    return [(artist_names[i].text, 
             artist_tracking[i].attrs['value'], 
             artist_form[i].attrs['action'],
             get_attrs(artist_form[i])) 
             for i in range(len(artist_names))]

def get_attrs(elem):
    form_attrs = filter(lambda x: x.has_attr('name'), elem.select('input'))
    return {x.attrs['name']: x.attrs['value'] for x in form_attrs}

def track_artist(s, artist_to_track):
    r = s.post(songkick_base_url + artist_to_track[2], 
               data=json.dumps(artist_to_track[3]), 
               headers=headers)

def levenshtein(a,b):
    "Calculates the Levenshtein distance between a and b."
    n, m = len(a), len(b)
    if n > m:
        # Make sure n <= m, to use O(min(n,m)) space
        a,b = b,a
        n,m = m,n

    current = range(n+1)
    for i in range(1,m+1):
        previous, current = current, [i]+[0]*n
        for j in range(1,n+1):
            add, delete = previous[j]+1, current[j-1]+1
            change = previous[j-1]
            if a[j-1] != b[i-1]:
                change = change + 1
            current[j] = min(add, delete, change)

    return current[n]

def do_login(username, password):
    # create session for SongKick
    s = requests.session()

    # get initial login page to get authenticity token
    try:
        r = s.get(newloginurl)
    except:
        print "Couldn't get to login page"
        return None

    try:
        auth_key = re_auth_token.findall(r.content)[0]
    except:
        print "Couldn't find auth token in login page"
        return None

    # add authenticity token to login info, and login
    payload = {'authenticity_token': auth_key,
               'cancel_url': '/',
               'success_url': '/',
               'username_or_email': username,
               'password': password,
               'persist': 'y',
               'commit': 'Log in'}
    try:
        r = s.post(createloginurl, data=payload)
    except:
        print "Couldn't log in"
        return None

    if r.status_code != 200:
        print "Some error logging in"
        return None
    else:
        return s

def search_for_artist(s, queryurl):
    # Get artists related to given CLI argument
    artistspage = s.get(queryurl)
    artist_soup = BeautifulSoup(artistspage.content)
    return artist_soup

def attempt_to_track(s, artists, searchterm):
    if len(artists) == 0:
        print "No Results: " + searchterm
    elif any(filter(lambda (n,t,u,a): t == u'Stop tracking', artists)):
        print "Already tracking: " + searchterm
    else:
        distances = [levenshtein(n,searchterm) for (n,t,u,attrs) in artists]
        val, idx = min((val, idx) for (idx, val) in enumerate(distances))
        #now we have the index of our most likely candidate. "Track it"
        track_artist(s, artists[idx])

password = getpass.getpass()

s = do_login(username, password)
artist_soup = search_for_artist(s, queryurl)
artists = get_artists(artist_soup)
attempt_to_track(s, artists, searchterm)
