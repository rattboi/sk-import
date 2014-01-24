#!/usr/bin/env python3
from bs4 import BeautifulSoup
import urllib.parse
import requests
import sys
import getpass
import json
import os

__version__ = '0.2'

songkick_base_url = "https://www.songkick.com"
session_base_url  = songkick_base_url + "/session"
new_login_url     = session_base_url  + "/new"
create_login_url  = session_base_url  + "/create"
query_base_url    = songkick_base_url + "/search?type=artists&query="

ajax_headers = {'Content-Type':'application/json',
                'Accept':'*/*',
                'X-Requested-With':'XMLHttpRequest'}

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
               headers=ajax_headers)

def do_login(username, password):
    # create session for SongKick
    s = requests.session()

    # get initial login page to get authenticity token
    try:
        r = s.get(new_login_url)
    except:
        print("Couldn't get to login page")
        return None

    try:
        login_soup         = BeautifulSoup(r.content)
        authenticity_token = login_soup.select('input[name="authenticity_token"]')
        auth_key = authenticity_token[0].attrs['value']
    except:
        print("Couldn't find auth token in login page")
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
        r = s.post(create_login_url, data=payload)
    except:
        print("Couldn't log in")
        return None

    if r.status_code != 200:
        print("Some error logging in")
        return None
    else:
        return s

def search_for_artist(s, queryurl):
    # Get artists related to given CLI argument
    artistspage = s.get(queryurl)
    artist_soup = BeautifulSoup(artistspage.content)
    return artist_soup

def build_query(artist):
    return query_base_url+ urllib.parse.quote(artist)

def cleanup(s):
    return s.lower().replace('the ','',-1)

def attempt_to_track(s, artists, searchterm):
    distance = ""
    trackstatus = ""
    if len(artists) == 0:
        trackstatus = "No Results"
    else:
        distances = [levenshtein(cleanup(n),cleanup(searchterm)) for (n,t,u,attrs) in artists]
        min_dist, idx = min((val, idx) for (idx, val) in enumerate(distances))
        #now we have the index of our most likely candidate. "Track it"
        if min_dist < 10: #arbitrary number at the moment
            if artists[idx][1] != 'Stop tracking':
                track_artist(s, artists[idx])
                trackstatus = "Added as {}".format(artists[idx][0])
            else:
                trackstatus = "Already tracking as {}".format(artists[idx][0])
        else:
            trackstatus = "Skipping. Too dissimilar. Closest is {}".format(artists[idx][0])
        distance = "Distance = {}".format(min_dist)
    print("{0: <50} : {1: <70} : {2:}".format(searchterm, trackstatus, distance))

def get_dirs(path):
    return [f for f in os.listdir(path) if os.path.isdir(os.path.join(path,f)) and not f.startswith('.')]

def print_help():
    print("{0} v{1}".format(sys.argv[0],__version__))
    print("  To use: sk-import <username> <path>")
    print("   where: <username> = SongKick username")
    print("          <path>     = root directory containing subdirectories named after artists")
    print("                       (Imagine the root of your music directory)")

def main():
    if len(sys.argv) != 3:
        print_help()
        sys.exit(1)
    else:
        username = sys.argv[1]
        path = sys.argv[2]

    password = getpass.getpass()

    s = do_login(username, password)
    artist_dirs = sorted(get_dirs(path))
    for idx, artist_dir in enumerate(artist_dirs):
        if idx % 10 == 0:
            print("{0}/{1}".format(idx, len(artist_dirs)))
        queryurl = build_query(artist_dir)
        artist_soup = search_for_artist(s, queryurl)
        artists = get_artists(artist_soup)
        attempt_to_track(s, artists, artist_dir)

if __name__ == '__main__':
    sys.exit(main())
