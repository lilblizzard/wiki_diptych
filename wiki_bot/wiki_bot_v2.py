import wikipedia
import tweepy
import random
import urllib.request
from PIL import Image
import os

def twitter_api():

    twitter_consumer_key = 'zYVvznaEaHaQacUnR4pdEivPm'
    twitter_consumer_secret = '0m4XDM4Wa0d9ytTtKCVqN9PgLJBZP3rKpPvVGFdRlrH79AFyow'

    twitter_access_token = '1162470665091506177-TeUsm94IPzCN6SJTYuqjByKPloXfRR'
    twitter_access_secret = 'Ed2avQwgob4bZEDIY2SpjYcBfBOEfvKYChmDbG6cjzbrV'

    auth = tweepy.OAuthHandler(twitter_consumer_key, twitter_consumer_secret)
    auth.set_access_token(twitter_access_token, twitter_access_secret)
    api = tweepy.API(auth)
    return api


def get_page_with_at_least_two_jpegs():

    count_of_jpegs = 0
    while count_of_jpegs < 2:
        try:
            #getting one random wiki page
            random_page = wikipedia.page(wikipedia.random(1))
            image_count = len(random_page.images)
            if image_count > 3:
                image_urls = random_page.images
            else:
                image_urls = []

            count_of_jpegs = 0
            for url in image_urls:
                if url[-4:] == '.jpg':
                    count_of_jpegs+=1
                    # download image
                    #urllib.request.urlretrieve(url, random_page.title + '.jpg')
                    jpeg_url = url
        except wikipedia.exceptions.DisambiguationError:
            print('DisambiguationError')
            continue
        except wikipedia.exceptions.PageError:
            print('PageError')
            continue

    #return the page with more than 2 jpegs
    return random_page.title, jpeg_url


def assemble_tweet(first_pair, second_pair):

    success = False
    while not success:
        try:
            urllib.request.urlretrieve(first_pair[1], '/home/pi/wiki_diptych/wiki_bot/first_image.jpg')
            urllib.request.urlretrieve(second_pair[1], '/home/pi/wiki_diptych/wiki_bot/second_image.jpg')

            filenames = ['/home/pi/wiki_diptych/wiki_bot/first_image.jpg','/home/pi/wiki_diptych/wiki_bot/second_image.jpg']
            media_ids = []
            for filename in filenames:
                #test size of images, return appropraite file
                test_image_and_downscale_if_too_large(filename)
                try:
                    res = twitter_api().media_upload(filename)
                    media_ids.append(res.media_id)
                except tweepy.error.TweepError:
                    print(tweepy.error.TweepError)
                    continue
            twitter_api().update_status(status = first_pair[0] + ', ' + second_pair[0], media_ids=media_ids)
            success = True
        except tweepy.error.TweepError:
            print(tweepy.error.TweepError)


#test function
def test_image_and_downscale_if_too_large(filepath):

    #if the image is < 2000kb, return image
    image_size = os.stat(filepath).st_size
    success = False
    while not success:
        if image_size < 2000000:
            success = True
            return filepath
        #if the image is > 2000kb, return resized image and replace file
        else:
            original_image = Image.open(filepath)
            original_image.save(filepath, quality=20, optimized=True)
            return filepath


first_pair = get_page_with_at_least_two_jpegs()
second_pair = get_page_with_at_least_two_jpegs()
print(first_pair)
print(second_pair)
assemble_tweet(first_pair,second_pair)

