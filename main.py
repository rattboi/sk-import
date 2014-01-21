import urllib2
import requests
import sys
import re
import getpass

if len(sys.argv) < 2:
    sys.exit(1);

re_authkey = re.compile("input name=\"authenticity_token\" type=\"hidden\" value=\"(.*)\"")

password = getpass.getpass()

newloginurl    = "https://www.songkick.com/session/new"
createloginurl = "https://www.songkick.com/session/create"

newlogin = requests.get(newloginurl)

auth_key = re_authkey.findall(newlogin.content)[0]

payload = {'authenticity_token': auth_key,
           'cancel_url': '/',
           'success_url': '/',
           'username_or_email': 'rattboi',
           'password': password,
           'persist': 'y',
           'commit': 'Log in'}

r = requests.post(createloginurl, data=payload, cookies=newlogin.cookies)

basesearchstring = "https://www.songkick.com/search?page=1&per_page=10&type=artists&query="
queryurl = basesearchstring + urllib2.quote(sys.argv[1])

'''
testquery = requests.get(queryurl, cookies=r.cookies)

f = open('somefile.htm', 'w')
f.writelines(testquery.content)
f.close()
'''
