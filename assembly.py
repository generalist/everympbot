# version 1.4
#
# multiline slug that can cope with multiple parties, terms
# adds a counter for seats and parties
# 
# adds a Wikipedia link if present, otherwise WD; adds ODNB and Rush if known
# adds Historic Hansard link if known - one selected at random if 2+ are present
#
# tweet is put into a seperate file to be picked up by the tweeting script
# 
# 1.1 adds an image! if it exists.
#
# image is put into a seperate file, and nextimage.txt contains the filename
#
# 1.2 adds a log to say there was an image
# 1.3 adds Who's Who
# 1.4 adds a user-agent field to the request

version = '1.4' # set version here for logging
headers = { 'User-Agent': 'everympbot/1.4 (https://github.com/generalist/everympbot)' }

import requests
import json
import pandas as pd
from num2word import word
from datetime import datetime

# first let us find a member - list of suitable IDs is in sourceids.txt

with open("sourceids.txt", "r") as read_file:
    identifiers = pd.read_csv(read_file)

member = identifiers.sample().to_string(index=False, header=False)

# extract our sample ID as a *string*

print(member)

# now the SPARQL queries
# A gets name, born, died, seat count, seat name, party count, party name, and links
# B gets the terms in office


url = 'https://query.wikidata.org/sparql'
query1 = """# script to generate items for @everympbot - andrew@generalist.org.uk
#

select distinct ?mp ?mpLabel ?parties ?seats 
(sample(?seatname) as ?seat) (sample(?partyname) as ?party)
(year(?born) as ?birthyear) (year(?died) as ?deathyear) ?wikipedia ?odnb ?rush ?whoswho
(sample(?h) as ?hansard) (sample(?i) as ?image)
where
{
  VALUES ?mp { wd:"""
query2 = """ } # set MP here
  filter(?terms = ?terms_with_parties)
  filter(?terms = ?terms_with_seats)
  ?mp wdt:P31 wd:Q5 . ?mp p:P39 ?ps . ?ps ps:P39 ?position . ?position wdt:P279 wd:Q16707842. 
  ?ps pq:P4100 ?affil . ?affil rdfs:label ?partyname . filter(lang(?partyname) = "en") 
  ?ps pq:P768 ?const . ?const rdfs:label ?seatname . filter(lang(?seatname) = "en") 
  filter not exists { ?ps pq:P1534 wd:Q50393121 }
  ?mp wdt:P569 ?born . optional { ?mp wdt:P570 ?died }
    SERVICE wikibase:label { bd:serviceParam wikibase:language "[AUTO_LANGUAGE],en". }
  { select distinct ?mp ?mpLabel ?terms ?terms_with_parties ?terms_with_seats
    (count(distinct ?party) as ?parties) 
    (count(distinct ?seatname) as ?seats) 
      WHERE {
        ?mp wdt:P31 wd:Q5 . ?mp p:P39 ?ps . ?ps ps:P39 ?position . ?position wdt:P279 wd:Q16707842.
        filter not exists { ?ps ps:P39 wd:Q77685926 }
        filter not exists { ?ps pq:P1534 wd:Q50393121 } # omit any where it was turned down
        optional { ?ps pq:P4100 ?party } optional { ?ps pq:P768 ?seat . ?seat rdfs:label ?seatname . filter(lang(?seatname) = "en") }
        { select ?mp (count(distinct ?ps) as ?terms) where
             { ?mp p:P39 ?ps . ?ps ps:P39 ?position . ?position wdt:P279 wd:Q16707842. 
               filter not exists { ?ps pq:P1534 wd:Q50393121 } } group by ?mp }
        optional { select ?mp (count(distinct ?ps) as ?terms_with_parties) where
             { ?mp p:P39 ?ps . ?ps ps:P39 ?position . ?position wdt:P279 wd:Q16707842. ?ps pq:P4100 ?party .
               filter not exists { ?ps pq:P1534 wd:Q50393121 }} group by ?mp }
        optional { select ?mp (count(distinct ?ps) as ?terms_with_seats) where
             { ?mp p:P39 ?ps . ?ps ps:P39 ?position . ?position wdt:P279 wd:Q16707842. ?ps pq:P768 ?seat .
               filter not exists { ?ps pq:P1534 wd:Q50393121 }} group by ?mp }
    SERVICE wikibase:label { bd:serviceParam wikibase:language "[AUTO_LANGUAGE],en". }
  } group by ?mp ?mpLabel ?terms ?terms_with_parties ?terms_with_seats }
  optional { ?wikipedia schema:about ?mp .
             ?wikipedia schema:isPartOf <https://en.wikipedia.org/>. }
  optional { ?mp wdt:P1415 ?odnb }
  optional { ?mp wdt:P4471 ?rush }
  optional { ?mp wdt:P2015 ?h }
  optional { ?mp wdt:P4789 ?whoswho }
  optional { ?mp wdt:P18 ?i }
} group by ?mp ?mpLabel ?parties ?seats ?born ?died ?wikipedia ?odnb ?rush ?whoswho """

queryA = query1 + member + query2

rA = requests.get(url, params = {'format': 'json', 'query': queryA})
wdqsA = rA.json()

print(wdqsA)

# dump to check we got it all

with open("wdqsA.json", "w") as write_file:
    json.dump(wdqsA, write_file)

# now query B


url = 'https://query.wikidata.org/sparql'
query3 = """# script to generate items for @everympbot - andrew@generalist.org.uk
#

SELECT distinct ?mp ?start (min(?end) as ?end2) 
(concat(str(year(?start)), "-", str(year(?end2))) as ?period) where {
  VALUES ?mp { wd:"""
query4 = """ } # set MP here
  ?mp wdt:P569 ?born . optional { ?mp wdt:P570 ?died }
  # find all terms for each continuing period of office
  { SELECT distinct ?mp ?start
    WHERE {
      ?mp p:P39 ?ps. ?ps ps:P39 ?term . ?term wdt:P279 wd:Q16707842. ?ps pq:P580 ?start. 
      # find all terms of office and their start date
      filter not exists { ?ps pq:P2715 ?elec . ?elec wdt:P31 wd:Q15283424 . 
                          # omit any terms which started at a general election
                          ?mp p:P39 ?ps0 . ?ps0 ps:P39 ?term0 . ?term0 wdt:P156 ?term .
                          ?ps0 pq:P1534 wd:Q741182 . }
                          # and where the MP served at dissolution in the previous term
      filter not exists { ?ps pq:P1534 wd:Q50393121 } # omit any double-return seats which were not taken up
      filter not exists { ?mp p:P39 ?ps0 . ?ps0 ps:P39 ?term . ?ps0 pq:P582 ?date . ?ps pq:P580 ?date }
                          # omit any where an earlier term ended on the same date - ie party switch
  } ORDER BY (?mp) ?start }
  # and all corresponding end dates
  { SELECT distinct ?mp ?end
    WHERE {
      ?mp p:P39 ?ps. ?ps ps:P39 ?term . ?term wdt:P279 wd:Q16707842. ?ps pq:P582 ?end.
      # find all terms of office and their end date
      filter not exists { ?ps pq:P1534 wd:Q741182 . 
                          # omit any terms which end at dissolution
                          ?mp p:P39 ?ps2 . ?ps2 ps:P39 ?term2 . ?term2 wdt:P155 ?term . 
                          ?ps2 pq:P2715 ?elec . ?elec wdt:P31 wd:Q15283424 . }
                          # and where the MP comes back at the next general election
      filter not exists { ?ps pq:P1534 wd:Q50393121 } # omit any double-return seats which were not taken up
      filter not exists { ?mp p:P39 ?ps2 . ?ps2 ps:P39 ?term . ?ps2 pq:P580 ?date . ?ps pq:P582 ?date }
                          # omit any where a later term started on the same date - ie party switch
  } ORDER BY (?mp) ?end }
  # now take our starts as the key, and match each to its appropriate end - the next one along
  # this is the *smallest* end date which is still *larger* than the start date
  # so filter by larger here, and smallest using min in the SELECT clause
  filter(?end > ?start) . # note > not >=
  # add Wikipedia link

  SERVICE wikibase:label { bd:serviceParam wikibase:language "[AUTO_LANGUAGE],en". }
} group by ?mp ?mpLabel ?start
order by ?start  """

queryB = query3 + member + query4

rB = requests.get(url, params = {'format': 'json', 'query': queryB})
wdqsB = rB.json()

print(wdqsB)

# dump to check we got it all

with open("wdqsB.json", "w") as write_file:
    json.dump(wdqsB, write_file)

# now to break it down

for item in wdqsA['results']['bindings']:
    mp = item['mp']['value']
    name = item['mpLabel']['value']
    born = item['birthyear']['value']
    if 'deathyear' in item:
        died = item['deathyear']['value']
        slug = name + " (" + born + "-" + died + ") was a"
    else:
        slug = name + " (born " + born + ") is a former"
    parties = item['parties']['value']
    seats = item['seats']['value']
    partyword = word(parties)
    seatword = word(seats)
    party = item['party']['value']
    seat = item['seat']['value']
    if parties == '1':
        if seats == '1':
            slug = slug + " " + party + " Member of Parliament for " + seat + ", "
            # one party, one seat - "Con MP for Wessex"
        else:
            slug = slug + " " + party + " Member of Parliament for " + seatword.lower() + " seats, "
            # one party, multiple seats - "Con MP for various seats"
    else:
        if seats == '1':
            slug = slug + " Member of Parliament for " + seat + " for " + partyword.lower() + " parties, "
            # one party, one seat - "MP for Wessex for various parties"
        else:
            slug = slug + " Member of Parliament for " + seatword.lower() + " seats and " + partyword.lower() + " parties, "
            # one party, multiple seats - "MP for various seats and parties"
    # the bit below writes to "links"
    # so we can add the term dates in between the slug and the links
    if 'wikipedia' in item:
        wikilink = item['wikipedia']['value']
        links = " | Wikipedia: " + wikilink
    else:
        links = " | Wikidata: " + mp
    if 'hansard' in item:
        hansard = item['hansard']['value']
        links = links + ' | Hansard: https://api.parliament.uk/historic-hansard/people/' + hansard
        # nb this only takes ONE hansard link if TWO exist, so may be odd
    if 'odnb' in item:
        odnb = item['odnb']['value']
        links = links + ' | ODNB: https://doi.org/10.1093/ref:odnb/' + odnb
    else:
        if 'whoswho' in item:
            whoswho = item['whoswho']['value']
            links = links + ' | Who\'s Who: https://www.ukwhoswho.com/view/article/oupww/whoswho/' + whoswho
    if 'rush' in item:
        rush = item['rush']['value']
        links = links + ' | Rush: https://membersafter1832.historyofparliamentonline.org/members/' + rush
    if 'image' in item:
        image = item['image']['value']
        imagelink = image + '?width=640'
        if image.find('/'):
          imagetype = image.rsplit('.', 1)[1]
        
# now we break down the terms in query B

terms = ''
for item in wdqsB['results']['bindings']:
    period = item['period']['value']
    terms = terms + ", " + period

termsclean = terms[2:]

# trim off the leading comma on terms

links = links.replace(' |', '\n*')

# turn the links into a pretty multi-line element

print(slug)
print(terms)
print(termsclean)
print(links)

tweet = slug + termsclean + "." +"\n" + links

# set up the tweet content

print(tweet)

with open("nexttweet.txt", "w") as candidates:
    candidates.write(tweet + "\n")

# drop the tweet coment into a clean file

# but wait, we forgot our images!

if 'imagelink' in globals():
    print(imagelink)
    print(imagetype)
    img = requests.get(imagelink, allow_redirects=True, headers=headers)
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
