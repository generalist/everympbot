# this is the overall script to make a tweet with the twitterbot
# version 1.2
# uses assembly.py and tweeting.py

# set working directory - change as needed

cd ~/scripts/everymp

# clean up old data to prevent retweeting if the query fails

rm nexttweet.txt
rm nextimage.txt
rm twitterimage.*

# first generate a new link

python3 assembly.py

# then run the tweet script

python3 tweeting.py

# and you're done!
