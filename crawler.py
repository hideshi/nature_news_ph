from bs4 import BeautifulSoup
from urllib.request import urlopen
from sqlite3 import connect, IntegrityError
from requests_oauthlib import OAuth1Session
from configparser import ConfigParser

db_file = 'crawler.db'
conn = connect(db_file)
conn.execute('''
    CREATE TABLE IF NOT EXISTS contents (
        url TEXT PRIMARY KEY,
        title TEXT UNIQUE,
        create_at TEXT
    )''')

config = ConfigParser()
config.read('./config.ini')

CK = config.get('twitter', 'CK')
CS = config.get('twitter', 'CS')
AT = config.get('twitter', 'AT')
AS = config.get('twitter', 'AS')
tweet_url = "https://api.twitter.com/1.1/statuses/update.json"

twitter = OAuth1Session(CK, CS, AT, AS)

url = 'http://weather.com.ph/news'
host = 'http://weather.com.ph'
html = urlopen(url).read()
soup = BeautifulSoup(html, 'html.parser')
for title in soup.select('div > h2 > .link'):
    try:
        conn.execute("INSERT INTO contents (url, title, create_at) VALUES ('{0}', '{1}', datetime())".format(host + title['href'], title.get_text()))

        print(title.get_text() + ' ' + host + title['href'])
        params = {"status": title.get_text() + ' ' + host + title['href']}
        req = twitter.post(tweet_url, params = params)
        if req.status_code == 200:
            print('Succeeded posting on Twitter')
        else:
            print ("Error: {0}".format(req.status_code))
    except IntegrityError:
        pass
conn.commit()
