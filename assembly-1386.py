# version 1.4
#
# this is hardcoded to look for very early Parliaments -
# currently only MPs in the HoP 1386-1421/1509-1558 volumes
# 
# 1.1 adds born/died dates
# 1.2 adds constituencies if possible
# 1.3 adds a user-agent field to the request
# 1.4 adds support for multiple HoP volumes (by picking the later one)
#     and drops "medieval" to allow bringing in 1500s

version = '1386-1.4' # set version here for logging
headers = { 'User-Agent': 'everympbot/1386-1.4 (https://github.com/generalist/everympbot)' }

import requests
import json
import pandas as pd
from num2word import word
from datetime import datetime

# first let us find a member - list of suitable IDs is in sourceids.txt

with open("sourceids-1386.txt", "r") as read_file:
    identifiers = pd.read_csv(read_file)

member = identifiers.sample().to_string(index=False, header=False)

# extract our sample ID as a *string*

print(member)

# now the SPARQL queries
# A gets name, born, died, seat count, seat name, party count, party name, and links
# no need for B as not handling continuing terms


url = 'https://query.wikidata.org/sparql'
query1 = """# script to generate items for @everympbot - andrew@generalist.org.uk
# using early HoP data

select distinct ?mp ?mpLabel ?parliaments ?seats (sample(?seatname) as ?seat)
?wikipedia ?odnb 
(min(?startyear) as ?earliest) (max(?endyear) as ?latest)
(sample(?i) as ?image)
(max(?hop) as ?histparl)
(year(?born) as ?birthyear) (year(?died) as ?deathyear) 
where
{ 
  VALUES ?mp { wd:"""
query2 = """ } # set MP here
  ?mp wdt:P31 wd:Q5 . ?mp p:P39 ?ps . ?ps ps:P39 ?position . ?position wdt:P279 wd:Q18018860.
  optional { ?mp wdt:P569 ?born .
  ?mp p:P569/psv:P569 [ wikibase:timePrecision ?bprec ; wikibase:timeValue ?born ] .
  filter (?bprec >= "9"^^xsd:integer ) } .
  # at least year precision 
  optional { ?mp wdt:P570 ?died .
  ?mp p:P570/psv:P570 [ wikibase:timePrecision ?dprec ; wikibase:timeValue ?died ] .
  filter (?dprec >= "9"^^xsd:integer ) } .
  # at least year precision 
  ?position wdt:P571 ?start. bind(year(?start) as ?startyear) .
  ?position wdt:P576 ?end. bind(year(?end) as ?endyear) .
  optional { ?ps pq:P768 ?const . ?const rdfs:label ?seatname . filter(lang(?seatname) = "en") }
  filter not exists { ?ps pq:P1534 wd:Q50393121 }
    SERVICE wikibase:label { bd:serviceParam wikibase:language "[AUTO_LANGUAGE],en". }
  { select distinct ?mp ?mpLabel ?parliaments (count(distinct ?seatname) as ?seats) 
      WHERE {
        ?mp wdt:P31 wd:Q5 . ?mp p:P39 ?ps . ?ps ps:P39 ?position . ?position wdt:P279 wd:Q18018860.
        optional { ?ps pq:P768 ?seat . ?seat rdfs:label ?seatname . filter(lang(?seatname) = "en") }
        filter not exists { ?ps pq:P1534 wd:Q50393121 } # omit any where it was turned down
        { select ?mp (count(distinct ?position) as ?parliaments) where
             { ?mp p:P39 ?ps . ?ps ps:P39 ?position . ?position wdt:P279 wd:Q18018860. 
               filter not exists { ?ps pq:P1534 wd:Q50393121 } } group by ?mp }
        # count number of distinct Parliaments served
    SERVICE wikibase:label { bd:serviceParam wikibase:language "[AUTO_LANGUAGE],en". }
  } group by ?mp ?mpLabel ?parliaments }
  optional { ?wikipedia schema:about ?mp .
             ?wikipedia schema:isPartOf <https://en.wikipedia.org/>. }
  optional { ?mp wdt:P1415 ?odnb }
  optional { ?mp wdt:P18 ?i }
  ?mp wdt:P1614 ?hop .
} group by ?mp ?mpLabel ?parliaments ?seats ?wikipedia ?odnb ?born ?died """

queryA = query1 + member + query2

rA = requests.get(url, params = {'format': 'json', 'query': queryA})
wdqsA = rA.json()

print(wdqsA)

# dump to check we got it all

with open("wdqsA.json", "w") as write_file:
    json.dump(wdqsA, write_file)

# now to break it down

for item in wdqsA['results']['bindings']:
    mp = item['mp']['value']
    name = item['mpLabel']['value']
    parliaments = item['parliaments']['value']
    parliamentsword = word(parliaments)
    earliest = item['earliest']['value']
    latest = item['latest']['value']
    if 'birthyear' in item:
        born = item['birthyear']['value']
        # both birth and death
        if 'deathyear' in item:
            died = item['deathyear']['value']
            slug = name + " (" + born + " - " + died + ")"
        # birth no death
        else:
            slug = name + " (b. " + born + ")"
    # no birth
    else:
        # but death
        if 'deathyear' in item:
            died = item['deathyear']['value']
            slug = name + " (d. " + died + ")"
        # no birth or death
        else:
            slug = name
    if 'seat' in item:
        seats = item['seats']['value']
        seatsword = word(seats)
        seat = item['seat']['value']
        if seats == '1':
            slug = slug + " was an English MP, who represented " + seat + " in"
        else:
            slug = slug + " was an English MP, who represented " + seatsword.lower() + " constituencies in"
    else:
        slug = slug + " was an English MP, who served for"
    
    if parliaments == '1':
        slug = slug + " one parliament in " + earliest
    else:
        slug = slug + " " + parliamentsword.lower() + " parliaments in " + earliest + "-" + latest
    # currently only counts terms
    hop = item['histparl']['value']
    if 'wikipedia' in item:
        wikilink = item['wikipedia']['value']
        links = " | Wikipedia: " + wikilink
    else:
        links = " | Wikidata: " + mp
    links = links + " | History of Parliament: https://www.historyofparliamentonline.org/volume/" + hop
    # assumes HoP is always present (it is required in the search)
    # max() ensures we get the newest one in all cases
    if 'odnb' in item:
        odnb = item['odnb']['value']
        links = links + ' | ODNB: https://doi.org/10.1093/ref:odnb/' + odnb
    if 'image' in item:
        image = item['image']['value']
        imagelink = image + '?width=640'
        if image.find('/'):
          imagetype = image.rsplit('.', 1)[1]
        
# trim off the leading comma on terms

links = links.replace(' |', '\n*')

# turn the links into a pretty multi-line element

print(slug)
print(links)

tweet = slug + "." + "\n" + links

# set up the tweet content

print(tweet)

with open("nexttweet.txt", "w") as candidates:
    candidates.write(tweet + "\n")

# drop the tweet coment into a clean file

# but wait, we forgot our images!

if 'imagelink' in globals():
    print(imagelink)
    print(imagetype)
    img = requests.get(imagelink, allow_redirects=True)
    filename = 'twitterimage.' + imagetype
    print(filename)
    open(filename, 'wb').write(img.content)
    open("nextimage.txt", "w").write(filename)
    with open("generatedlog.txt", "a") as logfile:
        logfile.write(member + "\t" + str(datetime.now()) + "\t" + version + "\t" + tweet.replace('\n', ' | ') + "\t" + image + "\n")
# log includes image filename

else:
    print('no image')
    with open("generatedlog.txt", "a") as logfile:
        logfile.write(member + "\t" + str(datetime.now()) + "\t" + version + "\t" + tweet.replace('\n', ' | ') + "\tno_image\n")
# log padded with tabs to be blank

quit ()
