# report script for everympbot on the total number of MPs
# 
# 1.0 is barebones
# 1.1 adds a count for MPs in the pool of candidates
# 1.2 generates the list of items anew to ensure both
#     fresh data + a recent count

version = 'report-1.2' # set version here for logging

import requests
import json
import pandas as pd
from num2word import word
from datetime import datetime

# now the SPARQL query

url = 'https://query.wikidata.org/sparql'
queryA = """# script to generate items for @everympbot - andrew@generalist.org.uk
# periodic reporting script
SELECT ?total ?eng_count ?gb_count ?uk_count
WHERE {
 { select (count (distinct ?person) as ?total) where
   { ?person wdt:P31 wd:Q5 ; p:P39 ?ps . ?ps ps:P39 ?term .
     {?term wdt:P279* wd:Q16707842 } UNION { ?term wdt:P279* wd:Q18015642 } UNION { ?term wdt:P279* wd:Q18018860 } } }
 { select (count (distinct ?person) as ?eng_count) where
   { ?person wdt:P31 wd:Q5 ; p:P39 ?ps . ?ps ps:P39 ?term . ?term wdt:P279* wd:Q18018860 } }
 { select (count (distinct ?person) as ?gb_count) where
   { ?person wdt:P31 wd:Q5 ; p:P39 ?ps . ?ps ps:P39 ?term . ?term wdt:P279* wd:Q18015642 } }
 { select (count (distinct ?person) as ?uk_count) where
   { ?person wdt:P31 wd:Q5 ; p:P39 ?ps . ?ps ps:P39 ?term . ?term wdt:P279* wd:Q16707842 } }
} """

rA = requests.get(url, params = {'format': 'json', 'query': queryA})
wdqsA = rA.json()

print(wdqsA)

# dump to check we got it all

with open("wdqsA.json", "w") as write_file:
    json.dump(wdqsA, write_file)

# now to break it down

for item in wdqsA['results']['bindings']:
    total = item['total']['value']
    uk = item['uk_count']['value']
    gb = item['gb_count']['value']
    eng = item['eng_count']['value']

# now regenerate the local counts

# first early data (1386-1421, 1509-1604 - 3 vol total)

queryB = """# script to generate worklists for @everympbot - andrew@generalist.org.uk
SELECT DISTINCT ?item {
 ?item p:P39 ?positionStatement . 
 ?positionStatement ps:P39 ?term . ?term wdt:P279 wd:Q18018860 . 
 ?positionStatement prov:wasDerivedFrom ?ref . ?ref pr:P1614 ?refhop .
            ?ref pr:P248 wd:Q7739799 . filter (?refhop = ?mainhop ) .
 { ?item wdt:P1614 ?mainhop . FILTER(STRSTARTS(?mainhop, "1386")) } union
 { ?item wdt:P1614 ?mainhop . FILTER(STRSTARTS(?mainhop, "1509")) } union
 { ?item wdt:P1614 ?mainhop . FILTER(STRSTARTS(?mainhop, "1558")) }
 filter not exists { ?item wdt:P1614 ?hop . FILTER(STRSTARTS(?hop, "1604")) }
  # get all MPs who served in the 1386-1421, 1509-1604 periods, but omit any who served after 1604
  # this avoids potentially bringing in members from the 1640s where data is less complete
} """

rB = requests.get(url, params = {'format': 'json', 'query': queryB})
wdqsB = rB.json()

print(wdqsB)

with open("wdqsB.json", "w") as write_file:
    json.dump(wdqsB, write_file)

list1 = []
for item in wdqsB['results']['bindings']:
    entry = item['item']['value']
    string = str(entry)
    string = entry.replace("http://www.wikidata.org/entity/", "")
    list1.append(str(string))
    list1.append("\n")
    
with open("sourceids-1386.txt", "w") as output:
    output.writelines(list1)

# now modern data (MPs with full party data only)

queryC = """# script to generate worklists for @everympbot - andrew@generalist.org.uk
SELECT distinct ?mp
where{
# find all seat-party-start pairs  
  filter(?terms = ?terms_with_parties)
  filter(?terms = ?terms_with_seats)
  ?mp wdt:P31 wd:Q5 . ?mp p:P39 ?ps . ?ps ps:P39 ?position . ?position wdt:P279 wd:Q16707842. 
  ?ps pq:P4100 ?affil .
  ?ps pq:P768 ?const . 
  filter not exists { ?ps pq:P1534 wd:Q50393121 }
  filter not exists { ?mp p:P39 ?ps2 . ?ps2 ps:P39 wd:Q77685926 } # no current MPs
  ?mp wdt:P569 ?born . 
  { select distinct ?mp ?terms ?terms_with_parties ?terms_with_seats
      WHERE {
        ?mp wdt:P31 wd:Q5 . ?mp p:P39 ?ps . ?ps ps:P39 ?position . ?position wdt:P279 wd:Q16707842.
        filter not exists { ?ps ps:P39 wd:Q77685926 }
        filter not exists { ?ps pq:P1534 wd:Q50393121 } # omit any where it was turned down
        { select ?mp (count(distinct ?ps) as ?terms) where
             { ?mp p:P39 ?ps . ?ps ps:P39 ?position . ?position wdt:P279 wd:Q16707842. 
               filter not exists { ?ps pq:P1534 wd:Q50393121 } } group by ?mp }
        optional { select ?mp (count(distinct ?ps) as ?terms_with_parties) where
             { ?mp p:P39 ?ps . ?ps ps:P39 ?position . ?position wdt:P279 wd:Q16707842. ?ps pq:P4100 ?party .
               filter not exists { ?ps pq:P1534 wd:Q50393121 }} group by ?mp }
        optional { select ?mp (count(distinct ?ps) as ?terms_with_seats) where
             { ?mp p:P39 ?ps . ?ps ps:P39 ?position . ?position wdt:P279 wd:Q16707842. ?ps pq:P768 ?seat .
               filter not exists { ?ps pq:P1534 wd:Q50393121 }} group by ?mp }
  } group by ?mp ?terms ?terms_with_parties ?terms_with_seats }
} group by ?mp"""

rC = requests.get(url, params = {'format': 'json', 'query': queryC})
wdqsC = rC.json()

print(wdqsC)

with open("wdqsC.json", "w") as write_file:
    json.dump(wdqsC, write_file)

list2 = []
for item in wdqsC['results']['bindings']:
    entry = item['mp']['value']
    string = str(entry)
    string = entry.replace("http://www.wikidata.org/entity/", "")
    list2.append(str(string))
    list2.append("\n")
    
with open("sourceids.txt", "w") as output:
    output.writelines(list2)


# now find how many local options there are

count1 = len(open("sourceids.txt").readlines(  ))
count2 = len(open("sourceids-1386.txt").readlines(  ))
count = count1 + count2

# now write the tweet

tweet = "There are currently " + total + " individual MPs in the database: \n* " + uk + " served in the modern UK parliament;\n* " + gb + " in the 1707-1801 British parliament; and\n* " + eng + " in the pre-1707 English parliament.\n\n" + str(count) + " are in the pool to be tweeted."

print(tweet)

with open("nexttweet.txt", "w") as candidates:
    candidates.write(tweet + "\n")

with open("generatedlog.txt", "a") as logfile:
    logfile.write("REPORT\t" + str(datetime.now()) + "\t" + version + "\t" + tweet.replace('\n', ' | ') + "\tno image\n")
