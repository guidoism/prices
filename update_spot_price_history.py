# Yes, I know I'm using regexes to parse html, quick breaking my
# balls, these are simple pages and if the parsing breaks I don't
# care.

import re
import json
import requests

def sort_date(k):
    k = k[0].split('-')
    return (k[2], k[0], k[1])
    
def update_gold():
    r = requests.get('http://onlygold.com/Info/Search-Gold-Prices.asp')

    MONTHS = {
        'Jan': '01',
        'Feb': '02',
        'Mar': '03',
        'Apr': '04',
        'May': '05',
        'Jun': '06',
        'Jul': '07',
        'Aug': '08',
        'Sep': '09',
        'Oct': '10',
        'Nov': '11',
        'Dec': '12',
    }

    prices = dict(json.load(open('gold.json')))
    date = None
    price = None
    for s in r.text.split('\n'):
        if 'priceGriddata' in s:
            m = re.search(r'\s+([A-Z][a-z][a-z]) (\d\d), (\d\d\d\d)', s)
            if m:
                date = '-'.join((m.group(3), MONTHS[m.group(1)], m.group(2)))
            else:
                m = re.search(r'\$(\d?,?\d\d\d\.\d\d)', s)
                if m:
                    price = m.group(1).replace(',', '')
            if date and price:
                prices[date] = price
                date = None
                price = None
    
    out = sorted(prices.items(), reverse=True)
    json.dump(out, open('gold.json', 'w'), indent=2)
    open('gold.csv', 'w').write('\n'.join((','.join(line) for line in out)))

def update_silver():
    html = requests.get('http://www.pmbull.com/silver-price/').text
    r = re.compile(r'<table id="historical-silver(.+?)</table>', re.DOTALL)
    m = r.search(html)
    table = m.group(1).replace('$', '')
    r = re.compile(r'<td>(.*?)</td>', re.DOTALL)
    t = r.findall(table)

    prices = dict(json.load(open('silver.json')))
    prices.update(dict(zip(t[::4], t[1::4])))
    out = sorted(prices.items(), key=sort_date, reverse=True)
    json.dump(out, open('silver.json', 'w'), indent=2)
    open('silver.csv', 'w').write('\n'.join((','.join(line) for line in out)))
    
update_gold()
update_silver()
