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
basesearchstring = "https://www.songkick.com/search?page=1&per_page=10&type=artists&query="
queryurl = basesearchstring + urllib2.quote(sys.argv[1])

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
artists = s.get(queryurl)
artist_soup = BeautifulSoup(artists.content)

artist_list = artist_soup.select('li.artist > p.subject > a')
for a in artist_list:
    print a.text
