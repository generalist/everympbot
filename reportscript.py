# report script for everympbot on the total number of MPs
# 
# 1.0 is barebones
# 1.1 adds a count for MPs in the pool of candidates

version = 'report-1.0' # set version here for logging

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
