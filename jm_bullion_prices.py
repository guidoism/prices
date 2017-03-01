import collections
import datetime
import json
import re
import requests
from bs4 import BeautifulSoup
import pickle
from pprint import pprint

BASE = 'http://www.jmbullion.com/'
URLS = [
    ('1-kilo-copper-bullion-bar', 'Cu', 'Cu 1kg'),
    ('10-pound-copper-bullion-bar', 'Cu', 'Cu 10lb'),
    ('2017-1-oz-american-platinum-eagle-coin', 'Pt', 'Pt 1oz 2017'),
    ('1-oz-american-platinum-eagle-varied', 'Pt', 'Pt 1oz'),
    ('american-silver-eagle-varied-year', 'Ag', 'Ag 1oz'),
    ('2017-american-silver-eagle-tube', 'Ag', 'Ag 1oz x20'),
    ('2017-american-silver-eagle-monster-box', 'Ag', 'Ag 1oz x500'),
    ('1-kilogram-geiger-security-line-silver-bar', 'Ag', 'Ag 1kg'),
    ('5000-gram-geiger-security-line-silver-bar', 'Ag', 'Ag 5kg'),
    ('1-oz-american-gold-eagle', 'Au', 'Au 1oz'),
]

def extract_prices(url):
    soup = BeautifulSoup(requests.get(BASE + url + '/').text, 'html.parser')
    for table in soup.findAll('table', {'class': 'price_table'}):
        for tbody in table.findAll('tbody'):
            for tr in tbody.findAll('td', {'class': 'ptd_3'}):
                return tr.text.strip().replace(',', '').split()

today = datetime.date.today().isoformat()

prices = json.load(open('jm_bullion.json'))
prices_today = {}
for url, symbol, name in URLS:
    prices_today[name] = extract_prices(url)
prices.append((today, prices_today))
json.dump(prices, open('jm_bullion.json', 'w'), indent=2)

sizes = collections.defaultdict(int)
for date, items in prices:
    for _, _, name in URLS:
        sizes[name] = max(len(items.get(name, [])), sizes[name])

line = ['Date']
for _, _, name in URLS:
    c = sizes[name]
    if c < 2:
        line.append(name)
    else:
        for i in range(c):
            line.append("%s (%i)" % (name, i))
print '\t'.join(line)
csv = ','.join(line) + '\n'

for date, items in prices:
    line = [date]
    for _, _, name in URLS:
        columns = items.get(name, [])
        for i in range(sizes[name]):
            try:
                line.append(columns[i])
            except:
                line.append('')
    print '\t'.join(line)
    csv += ','.join(line) + '\n'
       
open('jm_bullion.csv', 'w').write(csv)

