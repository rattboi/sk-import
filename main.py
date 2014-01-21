from bs4 import BeautifulSoup
import urllib2
import requests
import sys
import re
import getpass

if len(sys.argv) < 2:
    sys.exit(1);

basesessionurl = "https://www.songkick.com/session/"
newloginurl    = basesessionurl + "new"
createloginurl = basesessionurl + "create"
basequerystring = "https://www.songkick.com/search?page=1&per_page=10&type=artists&query="
queryurl = basequerystring + urllib2.quote(sys.argv[1])

re_authkey = re.compile("input name=\"authenticity_token\" type=\"hidden\" value=\"(.*)\"")

password = getpass.getpass()

# create session for SongKick
s = requests.session()

# get initial login page to get authenticity token
newlogin = s.get(newloginurl)
auth_key = re_authkey.findall(newlogin.content)[0]

# add authenticity token to login info, and login
payload = {'authenticity_token': auth_key,
           'cancel_url': '/',
           'success_url': '/',
           'username_or_email': 'rattboi',
           'password': password,
           'persist': 'y',
           'commit': 'Log in'}
r = s.post(createloginurl, data=payload)

# Get artists related to given CLI argument
artistspage = s.get(queryurl)
artist_soup = BeautifulSoup(artistspage.content)

def get_artists(soup):
    artist_names    = soup.select('li.artist > p.subject > a')
    artist_tracking = soup.select('input.artist')
    return [(artist_names[i].text, artist_tracking[i].attrs['value']) for i in range(len(artist_names))]

artists = get_artists(artist_soup)

if any(filter(lambda (x,y): y == u'Stop tracking', artists)):
    print "Already tracking"
else:
    distances = [levenshtein(a,sys.argv[1]) for (a,b) in artists]
    val, idx = min((val, idx) for (idx, val) in enumerate(distances))
    #now we have the index of our most likely candidate. "Track it"

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
