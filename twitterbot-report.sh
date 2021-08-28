# this is the overall script to make a tweet with the twitterbot

# set working directory

cd ~/scripts/everymp

# clean up old data to prevent retweeting if the query fails

rm nexttweet.txt
rm nextimage.txt
rm twitterimage.*

# first generate a new lin

python3 reportscript.py

# then run the tweet script

python3 tweeting.py
