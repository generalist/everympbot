# version 0.2
# assembles a very minimal data line from a set of probably-OK sample IDs
# adds a Wikidata link

import requests
import json
import pandas as pd

# first let us find a member - list of suitable IDs is in sourceids.txt

with open("sourceids.txt", "r") as read_file:
    identifiers = pd.read_csv(read_file)

member = identifiers.sample().to_string(index=False, header=False)

# extract our sample ID as a *string*

print(member)

# now run the analysis on that member via SPARQL


url = 'https://query.wikidata.org/sparql'
query1 = """# script to generate items for @everympbot - andrew@generalist.org.uk
#

SELECT distinct ?mp ?mpLabel ?partyLabel ?seatLabel ?start (min(?end) as ?end2) (round(?end2 - ?start) as ?days) 
((round(?days/36.525)/10) as ?years)
(concat(?mpLabel, " (",str(year(?born)),"-",str(year(?died)),") was a ", ?partyLabel, " MP for ",
        ?seatLabel, ", serving ", str(?years), " years, ",      
        str(year(?start)), "-", str(year(?end2)), ".") as ?string)
(concat(?mpLabel, " (born ",str(year(?born)),") is a former ", ?partyLabel, " MP for ",
        ?seatLabel, ", serving ", str(?years), " years, ",      
        str(year(?start)), "-", str(year(?end2)), ".") as ?string2)
where { VALUES ?mp { wd:"""
query2 = """ } # set MP here
  ?mp wdt:P569 ?born . optional { ?mp wdt:P570 ?died }
  # find all seat-party-start pairs for each continuing period of office
  { SELECT distinct ?mp ?mpLabel ?partyLabel ?seatLabel ?start
    WHERE {
      ?mp p:P39 ?ps. ?ps ps:P39 ?term . ?term wdt:P279 wd:Q16707842. 
      ?ps pq:P768 ?seat . ?ps pq:P4100 ?party . ?ps pq:P580 ?start. 
      # find all terms of office with seat and party, and their start date
      filter not exists { ?ps pq:P2715 ?elec . ?elec wdt:P31 wd:Q15283424 . 
                          # omit any terms which started at a general election
                          ?mp p:P39 ?ps0 . ?ps0 ps:P39 ?term0 . ?term0 wdt:P156 ?term .
                          ?ps0 pq:P4100 ?party . ?ps0 pq:P768 ?seat . ?ps0 pq:P1534 wd:Q741182 . }
                          # and where the MP served for the same party & seat at dissolution in the previous term
      filter not exists { ?ps pq:P1534 wd:Q50393121 } # omit any double-return seats which were not taken up
      SERVICE wikibase:label { bd:serviceParam wikibase:language "[AUTO_LANGUAGE],en". }
      # labels inside the queries to catch any oddities where seat item changes, but name does not  
  } ORDER BY (?mp) ?start }
  # and all corresponding seat-party-end pairs
  { SELECT distinct ?mp ?mpLabel ?partyLabel ?seatLabel ?end
    WHERE {
      ?mp p:P39 ?ps. ?ps ps:P39 ?term . ?term wdt:P279 wd:Q16707842.
      ?ps pq:P768 ?seat . ?ps pq:P4100 ?party . ?ps pq:P582 ?end.
      # find all terms of office with seat and party, and their end date
      filter not exists { ?ps pq:P1534 wd:Q741182 . 
                          # omit any terms which end at dissolution
                          ?mp p:P39 ?ps2 . ?ps2 ps:P39 ?term2 . ?term2 wdt:P155 ?term . 
                          ?ps2 pq:P4100 ?party . ?ps2 pq:P768 ?seat . 
                          ?ps2 pq:P2715 ?elec . ?elec wdt:P31 wd:Q15283424 . }
                          # and where the MP comes back for the same party & seat at the next general election
      filter not exists { ?ps pq:P1534 wd:Q50393121 } # omit any double-return seats which were not taken up
      SERVICE wikibase:label { bd:serviceParam wikibase:language "[AUTO_LANGUAGE],en". }
      # labels inside the queries to catch any oddities where seat item changes, but name does not  
  } ORDER BY (?mp) ?end }
  # now take our starts as the key, and match each to its appropriate end - the next one along
  # this is the *smallest* end date which is still *larger* than the start date
  # so filter by larger here, and smallest using min in the SELECT clause
  filter(?end > ?start) . # note > not >= 
} group by ?mp ?mpLabel ?partyLabel ?seatLabel ?start ?born ?died order by ?start """

query = query1 + member + query2

# this mess patches all the sparql bits together

r = requests.get(url, params = {'format': 'json', 'query': query})
servicejson = r.json()

print(servicejson)

# dump to check we got it all

with open("service_file.json", "w") as write_file:
    json.dump(servicejson, write_file)

# now to analyse it

for item in servicejson['results']['bindings']:
    mp = item['mp']['value']
    if 'string' in item:
        slug = item['string']['value'] 
    if not 'string' in item:
        slug = item['string2']['value']

print(slug)
print(mp)

newslug = slug + " | WD: " + mp

print(newslug)

with open("candidates.txt", "a") as candidates:
    candidates.write(member + "\t" + newslug + "\n")

# we now have the tweetable one-liner as a slug

quit ()

