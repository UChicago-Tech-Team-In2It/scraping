import requests
import threading
import sys
import os
from bs4 import BeautifulSoup
from pandas import DataFrame
from functools import reduce

if len(sys.argv) == 1:
    CSV_FNAME = 'volunteermatch_data.csv'
else:
    CSV_FNAME = sys.argv[1]

URL_PART1 = 'https://www.volunteermatch.org/search/'

locations = ['New+York%2C+NY%2C+USA', 'Chicago%2C+IL%2C+USA',
             'San+Francisco%2C+CA%2C+USA', 'Boston%2C+MA%2C+USA',
             'Houston%2C+TX%2C+USA', 'Los+Angeles%2C+CA%2C+USA',
             'Philadelphia%2C+PA%2C+USA', 'Seattle%2C+WA%2C+USA',
             'Atlanta%2C+GA%2C+USA', 'Dallas%2C+TX%2C+USA',
             'Portland%2C+OR%2C+USA', 'Cleveland%2C+OH%2C+USA',
             'Denver%2C+CO%2C+USA', 'Washington%2C+DC%2C+USA']

categories = {
    'community': 25,
    'arts_culture': 34,
    'advocacy': 23,
    'seniors': 12,
    'homeless_housing': 7,
    'health_med': 11,
    'child_youth': 22,
    'animals': 30,
    'edu_lit': 15,
    'crisis_support': 14,
    'women': 3
}

dfs = []

def url_to_df(urls, cat):
    opps = []
    for url in urls:
        r = requests.get(url)
        soup = BeautifulSoup(r.content, 'html5lib')
        table = soup.find('div', attrs={'class': 'search-page'})
        for row in table.findAll('div', attrs={'class': 'searchitem PUBLIC'}):
            opp = {}
            opp['title'] = row.h3.text.strip()
            opp['org'] = row.find_all('a')[1].text.strip()
            desc_search = row.find_all('p')
            desc_index = 0
            for i in range(len(desc_search)):
                if len(desc_search[i].getText()) > 100:
                    desc_index = i
            opp['desc'] = row.find_all('p')[desc_index].getText().strip()
            opp['desc'] = opp['desc'].split('\n')[0]
            opp[cat] = True
            opps.append(opp)
    df = DataFrame(opps)
    df = df.drop_duplicates(keep=False)
    dfs.append(df)

threads = []
for cat, cat_v in categories.items():
    urls = []
    for loc in locations:
        url = URL_PART1 + f'?categories={cat_v}&' \
                        + f'l={loc}'
        urls += [url + f'&s={s}' for s in [x*10+1 for x in range(100)]]
    t = threading.Thread(target=url_to_df, args=(urls, cat))
    threads.append(t)
    t.start()

for t in threads:
    t.join()

final_df = reduce(lambda df1, df2: df1.merge(df2, left_on=['title', 'org', 'desc'],
                                                  right_on=['title', 'org', 'desc'],
                                                  how='outer'), dfs)
final_df = final_df.fillna(False)
final_df.to_csv(CSV_FNAME)

