# everympbot

This is a Python script to assemble tweets for the [@everympbot](https://twitter.com/everympbot) account on Twitter. It pulls data from the [Wikidata British Politicians dataset](https://www.wikidata.org/wiki/Wikidata:WikiProject_British_Politicians) to generate a short summary for a given MP.

The main script is `twitterbot.sh`. This calls `assembly.py`, which randomly selects an entry from a pre-selected list of candidate items in `sourceids.txt`. It then runs two queries to get data about the entry, and assembles a tweet, plus optionally an image if one is present on Wikidata. It logs the generated tweet and some metadata in `generatedlog.txt`.

The second script,`tweeting.py`, pulls credentials from `config.txt` and then uses the [twython](https://github.com/ryanmcgrath/twython) framework to post the tweet plus, if it exists, an image. It then logs this in `tweetedlog.txt`.

The shell script can be run manually or set to run on a regular basis.

A second pair of scripts, `twitterbot-1386.sh` and `assembly-1386.py`, generate a simplified tweet for medieval MPs (currently only using the 1386-1421 HoP volume), using a seperate candidates file (`sourceids-1386.txt`)

**Version log**

* 0.1 - minimal one-line tweet using [everywordbot](https://github.com/aparrish/everywordbot)
* 0.2 - adds Wikidata link
* 0.3 - adds Wikipedia or Wikidata link, plus optional ODNB, Hansard, Rush links.
* 0.4 - adds a check to make sure that there was continuous service (otherwise it would only tweet one half of it)
* 0.5 - rewritten to cope with multiple distinct periods of office, seats, or parties.
* 0.6 - tweaked to add a number of parties or seats where appropriate
* 1.0 - changed to a multi-line tweet posted with [twython](https://github.com/ryanmcgrath/twython) 
* 1.1 - adds support for images
* 1.2 - logs image correctly

**Generating sourceids.txt:**

Candidate lists are a plain text file of Wikidata QIDs, of the form Q123456 - no prefixes or suffixes.

* [MPs who have full seat and party data, with only one seat and party affiliation through their careers; no sitting MPs](https://query.wikidata.org/#%23%20query%20to%20find%20ONLY%20simple%20cases%20where%20the%20MP%20did%20not%20change%20seat%20or%20party%3B%20seatLabel%20is%20used%20to%20catch%20renames.%0A%0Aselect%20distinct%20%3Fmp%20%3FmpLabel%20%3Fterms%20%3Fterms_with_parties%20%3Fterms_with_seats%20%3Fparties%20%3Fseats%20where%0A%7B%0A%20%20filter%28%3Fterms%20%3D%20%3Fterms_with_parties%29%0A%20%20filter%28%3Fterms%20%3D%20%3Fterms_with_seats%29%0A%20%20filter%28%3Fseats%20%3D%201%29%0A%20%20filter%28%3Fparties%20%3D%201%29%0A%20%20filter%20not%20exists%20%7B%20%3Fmp%20p%3AP39%20%3Fps%20.%20%3Fps%20ps%3AP39%20wd%3AQ77685926%20%7D%20%23%20no%20current%20MPs%0A%20%20%7B%20select%20distinct%20%3Fmp%20%3FmpLabel%20%3Fterms%20%3Fterms_with_parties%20%3Fterms_with_seats%0A%20%20%20%20%28count%28distinct%20%3Fparty%29%20as%20%3Fparties%29%20%0A%20%20%20%20%28count%28distinct%20%3Fseatname%29%20as%20%3Fseats%29%20%0A%20%20%20%20%20%20WHERE%20%7B%0A%20%20%20%20%20%20%20%20%3Fmp%20wdt%3AP31%20wd%3AQ5%20.%20%3Fmp%20p%3AP39%20%3Fps%20.%20%3Fps%20ps%3AP39%20%3Fposition%20.%20%3Fposition%20wdt%3AP279%20wd%3AQ16707842.%0A%20%20%20%20%20%20%20%20optional%20%7B%20%3Fps%20pq%3AP4100%20%3Fparty%20%7D%20optional%20%7B%20%3Fps%20pq%3AP768%20%3Fseat%20.%20%3Fseat%20rdfs%3Alabel%20%3Fseatname%20.%20filter%28lang%28%3Fseatname%29%20%3D%20%22en%22%29%20%7D%0A%20%20%20%20%20%20%20%20%7B%20select%20%3Fmp%20%28count%28distinct%20%3Fps%29%20as%20%3Fterms%29%20where%0A%20%20%20%20%20%20%20%20%20%20%20%20%20%7B%20%3Fmp%20p%3AP39%20%3Fps%20.%20%3Fps%20ps%3AP39%20%3Fposition%20.%20%3Fposition%20wdt%3AP279%20wd%3AQ16707842.%20%7D%20group%20by%20%3Fmp%20%7D%0A%20%20%20%20%20%20%20%20optional%20%7B%20select%20%3Fmp%20%28count%28distinct%20%3Fps%29%20as%20%3Fterms_with_parties%29%20where%0A%20%20%20%20%20%20%20%20%20%20%20%20%20%7B%20%3Fmp%20p%3AP39%20%3Fps%20.%20%3Fps%20ps%3AP39%20%3Fposition%20.%20%3Fposition%20wdt%3AP279%20wd%3AQ16707842.%20%3Fps%20pq%3AP4100%20%3Fparty%20%7D%20group%20by%20%3Fmp%20%7D%0A%20%20%20%20%20%20%20%20optional%20%7B%20select%20%3Fmp%20%28count%28distinct%20%3Fps%29%20as%20%3Fterms_with_seats%29%20where%0A%20%20%20%20%20%20%20%20%20%20%20%20%20%7B%20%3Fmp%20p%3AP39%20%3Fps%20.%20%3Fps%20ps%3AP39%20%3Fposition%20.%20%3Fposition%20wdt%3AP279%20wd%3AQ16707842.%20%3Fps%20pq%3AP768%20%3Fseat%20%7D%20group%20by%20%3Fmp%20%7D%0A%20%20%20%20%20%20%20%20filter%20not%20exists%20%7B%20%3Fps%20ps%3AP39%20wd%3AQ77685926%20%7D%20%23%20no%20current%20MPs%0A%20%20%20%20SERVICE%20wikibase%3Alabel%20%7B%20bd%3AserviceParam%20wikibase%3Alanguage%20%22%5BAUTO_LANGUAGE%5D%2Cen%22.%20%7D%0A%20%20%7D%20group%20by%20%3Fmp%20%3FmpLabel%20%3Fterms%20%3Fterms_with_parties%20%3Fterms_with_seats%20%7D%0A%7D) - needed for earliest versions
* [MPs who have full seat and party data, including those with multiple seats and party affiliations; no sitting MPs](https://query.wikidata.org/#SELECT%20distinct%20%3Fmp%20%3FmpLabel%20%3Fparties%20%3Fseats%0A%28sample%28%3Fseatname%29%20as%20%3Fseat%29%20%28sample%28%3Fpartyname%29%20as%20%3Fparty%29%0Awhere%7B%0A%23%20find%20all%20seat-party-start%20pairs%20%20%0A%20%20filter%28%3Fterms%20%3D%20%3Fterms_with_parties%29%0A%20%20filter%28%3Fterms%20%3D%20%3Fterms_with_seats%29%0A%20%20%3Fmp%20wdt%3AP31%20wd%3AQ5%20.%20%3Fmp%20p%3AP39%20%3Fps%20.%20%3Fps%20ps%3AP39%20%3Fposition%20.%20%3Fposition%20wdt%3AP279%20wd%3AQ16707842.%20%0A%20%20%3Fps%20pq%3AP4100%20%3Faffil%20.%20%3Faffil%20rdfs%3Alabel%20%3Fpartyname%20.%20filter%28lang%28%3Fpartyname%29%20%3D%20%22en%22%29%20%0A%20%20%3Fps%20pq%3AP768%20%3Fconst%20.%20%3Fconst%20rdfs%3Alabel%20%3Fseatname%20.%20filter%28lang%28%3Fseatname%29%20%3D%20%22en%22%29%20%0A%20%20filter%20not%20exists%20%7B%20%3Fps%20pq%3AP1534%20wd%3AQ50393121%20%7D%0A%20%20filter%20not%20exists%20%7B%20%3Fmp%20p%3AP39%20%3Fps2%20.%20%3Fps2%20ps%3AP39%20wd%3AQ77685926%20%7D%20%23%20no%20current%20MPs%0A%20%20%3Fmp%20wdt%3AP569%20%3Fborn%20.%20%0A%20%20%20%20SERVICE%20wikibase%3Alabel%20%7B%20bd%3AserviceParam%20wikibase%3Alanguage%20%22%5BAUTO_LANGUAGE%5D%2Cen%22.%20%7D%0A%20%20%7B%20select%20distinct%20%3Fmp%20%3FmpLabel%20%3Fterms%20%3Fterms_with_parties%20%3Fterms_with_seats%0A%20%20%20%20%28count%28distinct%20%3Fparty%29%20as%20%3Fparties%29%20%0A%20%20%20%20%28count%28distinct%20%3Fseatname%29%20as%20%3Fseats%29%20%0A%20%20%20%20%20%20WHERE%20%7B%0A%20%20%20%20%20%20%20%20%3Fmp%20wdt%3AP31%20wd%3AQ5%20.%20%3Fmp%20p%3AP39%20%3Fps%20.%20%3Fps%20ps%3AP39%20%3Fposition%20.%20%3Fposition%20wdt%3AP279%20wd%3AQ16707842.%0A%20%20%20%20%20%20%20%20filter%20not%20exists%20%7B%20%3Fps%20ps%3AP39%20wd%3AQ77685926%20%7D%0A%20%20%20%20%20%20%20%20filter%20not%20exists%20%7B%20%3Fps%20pq%3AP1534%20wd%3AQ50393121%20%7D%20%23%20omit%20any%20where%20it%20was%20turned%20down%0A%20%20%20%20%20%20%20%20optional%20%7B%20%3Fps%20pq%3AP4100%20%3Fparty%20%7D%20optional%20%7B%20%3Fps%20pq%3AP768%20%3Fseat%20.%20%3Fseat%20rdfs%3Alabel%20%3Fseatname%20.%20filter%28lang%28%3Fseatname%29%20%3D%20%22en%22%29%20%7D%0A%20%20%20%20%20%20%20%20%7B%20select%20%3Fmp%20%28count%28distinct%20%3Fps%29%20as%20%3Fterms%29%20where%0A%20%20%20%20%20%20%20%20%20%20%20%20%20%7B%20%3Fmp%20p%3AP39%20%3Fps%20.%20%3Fps%20ps%3AP39%20%3Fposition%20.%20%3Fposition%20wdt%3AP279%20wd%3AQ16707842.%20%0A%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20filter%20not%20exists%20%7B%20%3Fps%20pq%3AP1534%20wd%3AQ50393121%20%7D%20%7D%20group%20by%20%3Fmp%20%7D%0A%20%20%20%20%20%20%20%20optional%20%7B%20select%20%3Fmp%20%28count%28distinct%20%3Fps%29%20as%20%3Fterms_with_parties%29%20where%0A%20%20%20%20%20%20%20%20%20%20%20%20%20%7B%20%3Fmp%20p%3AP39%20%3Fps%20.%20%3Fps%20ps%3AP39%20%3Fposition%20.%20%3Fposition%20wdt%3AP279%20wd%3AQ16707842.%20%3Fps%20pq%3AP4100%20%3Fparty%20.%0A%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20filter%20not%20exists%20%7B%20%3Fps%20pq%3AP1534%20wd%3AQ50393121%20%7D%7D%20group%20by%20%3Fmp%20%7D%0A%20%20%20%20%20%20%20%20optional%20%7B%20select%20%3Fmp%20%28count%28distinct%20%3Fps%29%20as%20%3Fterms_with_seats%29%20where%0A%20%20%20%20%20%20%20%20%20%20%20%20%20%7B%20%3Fmp%20p%3AP39%20%3Fps%20.%20%3Fps%20ps%3AP39%20%3Fposition%20.%20%3Fposition%20wdt%3AP279%20wd%3AQ16707842.%20%3Fps%20pq%3AP768%20%3Fseat%20.%0A%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20filter%20not%20exists%20%7B%20%3Fps%20pq%3AP1534%20wd%3AQ50393121%20%7D%7D%20group%20by%20%3Fmp%20%7D%0A%20%20%20%20SERVICE%20wikibase%3Alabel%20%7B%20bd%3AserviceParam%20wikibase%3Alanguage%20%22%5BAUTO_LANGUAGE%5D%2Cen%22.%20%7D%0A%20%20%7D%20group%20by%20%3Fmp%20%3FmpLabel%20%3Fterms%20%3Fterms_with_parties%20%3Fterms_with_seats%20%7D%0A%0A%7D%20group%20by%20%3Fmp%20%3FmpLabel%20%3Fparties%20%3Fseats) - usable from 0.5 onwards
* [As above but filtered to only those with images](https://query.wikidata.org/#SELECT%20distinct%20%3Fmp%20%3FmpLabel%20%3Fparties%20%3Fseats%0A%28sample%28%3Fseatname%29%20as%20%3Fseat%29%20%28sample%28%3Fpartyname%29%20as%20%3Fparty%29%0Awhere%7B%0A%23%20find%20all%20seat-party-start%20pairs%20%20%0A%20%20filter%28%3Fterms%20%3D%20%3Fterms_with_parties%29%0A%20%20filter%28%3Fterms%20%3D%20%3Fterms_with_seats%29%0A%20%20%3Fmp%20wdt%3AP31%20wd%3AQ5%20.%20%3Fmp%20p%3AP39%20%3Fps%20.%20%3Fps%20ps%3AP39%20%3Fposition%20.%20%3Fposition%20wdt%3AP279%20wd%3AQ16707842.%20%0A%20%20%3Fps%20pq%3AP4100%20%3Faffil%20.%20%3Faffil%20rdfs%3Alabel%20%3Fpartyname%20.%20filter%28lang%28%3Fpartyname%29%20%3D%20%22en%22%29%20%0A%20%20%3Fps%20pq%3AP768%20%3Fconst%20.%20%3Fconst%20rdfs%3Alabel%20%3Fseatname%20.%20filter%28lang%28%3Fseatname%29%20%3D%20%22en%22%29%20%0A%20%20filter%20not%20exists%20%7B%20%3Fps%20pq%3AP1534%20wd%3AQ50393121%20%7D%0A%20%20filter%20not%20exists%20%7B%20%3Fmp%20p%3AP39%20%3Fps2%20.%20%3Fps2%20ps%3AP39%20wd%3AQ77685926%20%7D%20%23%20no%20current%20MPs%0A%20%20%3Fmp%20wdt%3AP569%20%3Fborn%20.%20%3Fmp%20wdt%3AP18%20%3Fimage%20.%0A%20%20%20%20SERVICE%20wikibase%3Alabel%20%7B%20bd%3AserviceParam%20wikibase%3Alanguage%20%22%5BAUTO_LANGUAGE%5D%2Cen%22.%20%7D%0A%20%20%7B%20select%20distinct%20%3Fmp%20%3FmpLabel%20%3Fterms%20%3Fterms_with_parties%20%3Fterms_with_seats%0A%20%20%20%20%28count%28distinct%20%3Fparty%29%20as%20%3Fparties%29%20%0A%20%20%20%20%28count%28distinct%20%3Fseatname%29%20as%20%3Fseats%29%20%0A%20%20%20%20%20%20WHERE%20%7B%0A%20%20%20%20%20%20%20%20%3Fmp%20wdt%3AP31%20wd%3AQ5%20.%20%3Fmp%20p%3AP39%20%3Fps%20.%20%3Fps%20ps%3AP39%20%3Fposition%20.%20%3Fposition%20wdt%3AP279%20wd%3AQ16707842.%0A%20%20%20%20%20%20%20%20filter%20not%20exists%20%7B%20%3Fps%20ps%3AP39%20wd%3AQ77685926%20%7D%0A%20%20%20%20%20%20%20%20filter%20not%20exists%20%7B%20%3Fps%20pq%3AP1534%20wd%3AQ50393121%20%7D%20%23%20omit%20any%20where%20it%20was%20turned%20down%0A%20%20%20%20%20%20%20%20optional%20%7B%20%3Fps%20pq%3AP4100%20%3Fparty%20%7D%20optional%20%7B%20%3Fps%20pq%3AP768%20%3Fseat%20.%20%3Fseat%20rdfs%3Alabel%20%3Fseatname%20.%20filter%28lang%28%3Fseatname%29%20%3D%20%22en%22%29%20%7D%0A%20%20%20%20%20%20%20%20%7B%20select%20%3Fmp%20%28count%28distinct%20%3Fps%29%20as%20%3Fterms%29%20where%0A%20%20%20%20%20%20%20%20%20%20%20%20%20%7B%20%3Fmp%20p%3AP39%20%3Fps%20.%20%3Fps%20ps%3AP39%20%3Fposition%20.%20%3Fposition%20wdt%3AP279%20wd%3AQ16707842.%20%0A%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20filter%20not%20exists%20%7B%20%3Fps%20pq%3AP1534%20wd%3AQ50393121%20%7D%20%7D%20group%20by%20%3Fmp%20%7D%0A%20%20%20%20%20%20%20%20optional%20%7B%20select%20%3Fmp%20%28count%28distinct%20%3Fps%29%20as%20%3Fterms_with_parties%29%20where%0A%20%20%20%20%20%20%20%20%20%20%20%20%20%7B%20%3Fmp%20p%3AP39%20%3Fps%20.%20%3Fps%20ps%3AP39%20%3Fposition%20.%20%3Fposition%20wdt%3AP279%20wd%3AQ16707842.%20%3Fps%20pq%3AP4100%20%3Fparty%20.%0A%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20filter%20not%20exists%20%7B%20%3Fps%20pq%3AP1534%20wd%3AQ50393121%20%7D%7D%20group%20by%20%3Fmp%20%7D%0A%20%20%20%20%20%20%20%20optional%20%7B%20select%20%3Fmp%20%28count%28distinct%20%3Fps%29%20as%20%3Fterms_with_seats%29%20where%0A%20%20%20%20%20%20%20%20%20%20%20%20%20%7B%20%3Fmp%20p%3AP39%20%3Fps%20.%20%3Fps%20ps%3AP39%20%3Fposition%20.%20%3Fposition%20wdt%3AP279%20wd%3AQ16707842.%20%3Fps%20pq%3AP768%20%3Fseat%20.%0A%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20filter%20not%20exists%20%7B%20%3Fps%20pq%3AP1534%20wd%3AQ50393121%20%7D%7D%20group%20by%20%3Fmp%20%7D%0A%20%20%20%20SERVICE%20wikibase%3Alabel%20%7B%20bd%3AserviceParam%20wikibase%3Alanguage%20%22%5BAUTO_LANGUAGE%5D%2Cen%22.%20%7D%0A%20%20%7D%20group%20by%20%3Fmp%20%3FmpLabel%20%3Fterms%20%3Fterms_with_parties%20%3Fterms_with_seats%20%7D%0A%0A%7D%20group%20by%20%3Fmp%20%3FmpLabel%20%3Fparties%20%3Fseats)
* [1386-1421 MPs only](https://query.wikidata.org/#SELECT%20DISTINCT%20%3Fitem%20%7B%0A%20%3Fitem%20p%3AP39%20%3FpositionStatement%20.%20%0A%20%3FpositionStatement%20ps%3AP39%20%3Fterm%20.%20%3Fterm%20wdt%3AP279%20wd%3AQ18018860%20.%20%0A%20%3FpositionStatement%20prov%3AwasDerivedFrom%20%3Fref%20.%20%3Fref%20pr%3AP1614%20%3Frefhop%20.%0A%20%20%20%20%20%20%20%20%20%20%20%20%3Fref%20pr%3AP248%20wd%3AQ7739799%20.%20filter%20%28%3Frefhop%20%3D%20%3Fmainhop%20%29%20.%0A%20%3Fitem%20wdt%3AP1614%20%3Fmainhop%20.%20FILTER%28STRSTARTS%28%3Fmainhop%2C%20%221386%22%29%29.%0A%7D%20%0A)
