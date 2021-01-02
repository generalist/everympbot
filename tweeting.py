# tweeting script 1.2 - take multiline file and tweet it
# works with assembly.py 1.2

version = '1.2' # set version here for logging

from twython import Twython
from datetime import datetime
import config

cfg = config.Config('config.txt')

APP_KEY = cfg['APP_KEY']
APP_SECRET = cfg['APP_SECRET']
OAUTH_TOKEN = cfg['OAUTH_TOKEN']
OAUTH_TOKEN_SECRET = cfg['OAUTH_TOKEN_SECRET']

# config.txt should have these four variables

twitter = Twython(APP_KEY, APP_SECRET, OAUTH_TOKEN, OAUTH_TOKEN_SECRET)

with open ("nexttweet.txt", "r") as myfile:
    tweetsource=myfile.read()

print(tweetsource)

# check what it looks like

# now the workflow to find out if image is possible
# the wrapper script deletes nextimage.txt each time around
# so if it exists, it's because assembly.py has put it there
# and it will only do that if there is actually an image

try:
    with open('nextimage.txt') as i:
        image = str(i.read())
        print (image)
        print ('image present')
        with open("tweetedlog.txt", "a") as logfile:
            logfile.write(str(datetime.now()) + "\t" + version + "\t" + tweetsource.replace('\n', ' | ') + "\twith image\n")
        # log that we have an image
        photo = open(image, 'rb')
        response = twitter.upload_media(media=photo)
        twitter.update_status(status=tweetsource, media_ids=[response['media_id']])
        # fancy tweet if we have the image!
except IOError: # ie nextimage.txt does not exist
    print("no image present")
    with open("tweetedlog.txt", "a") as logfile:
        logfile.write(str(datetime.now()) + "\t" + version + "\t" + tweetsource.replace('\n', ' | ') + "\tno image\n")
        # log that we don't have an image
    twitter.update_status(status=tweetsource)
    # standard tweet if no source file present

