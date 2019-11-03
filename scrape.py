import requests, csv
from bs4 import BeautifulSoup
 

URLS = [f"https://www.volunteermatch.org/search/?categories=17&s={s}" for s in [x*10+1 for x in range(9)]]
#print(URLS)


opps = []

for URL in URLS:

    r = requests.get(URL) 
    #print(r.content)

    soup = BeautifulSoup(r.content, 'html5lib') 
    #print(soup.prettify())
    table = soup.find('div', attrs = {'class':'search-page'})
    for row in table.findAll('div', attrs = {'class':'searchitem PUBLIC'}):
        opp = {}
        opp['title'] = row.h3.text.strip()
        opp['org'] = row.find_all("a")[1].text.strip()
        desc_search = row.find_all("p")
        desc_index = 0
        for i in range(0,len(desc_search)):
            #print(desc_search[i].getText())
            if len(desc_search[i].getText()) > 100:
                desc_index = i
                #print(i)
        opp['desc'] = row.find_all("p")[desc_index].getText().strip()
        opp['desc'] = opp['desc'].split("\n")[0]
        print(opp)
        opps.append(opp)

#print(table)


with open("vmatch_scrape_disabilities.csv", "w") as f:
    w = csv.DictWriter(f,['title','org','desc']) 
    w.writeheader()
    for opp in opps: 
        w.writerow(opp) 
f.close()

