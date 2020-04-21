
import tweepy
from tweepy import OAuthHandler
import csv
import json
import re
from textblob import TextBlob

# Create a json file with the twitter credentials by replacing * with your own credentials

twitter_cred = dict()

twitter_cred['CONSUMER_KEY'] = '**************'
twitter_cred['CONSUMER_SECRET'] = '**************'
twitter_cred['ACCESS_KEY'] = '*********************'
twitter_cred['ACCESS_SECRET'] = '*****************'

# Twitter API credentials

with open('twitter_credentials.json', 'w') as secret_info:

    json.dump(twitter_cred, secret_info, indent=4, sort_keys=True)
with open('twitter_credentials.json') as cred_data:
    info = json.load(cred_data)
    consumer_key = info['CONSUMER_KEY']
    consumer_secret = info['CONSUMER_SECRET']
    access_key = info['ACCESS_KEY']
    access_secret = info['ACCESS_SECRET']

# Create the api endpoint

auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
api = tweepy.API(auth)


def get_world_trends(num_of_trends):

    WORLD_WOE_ID = 1
    world_trends = api.trends_place(WORLD_WOE_ID)

    print("\n The Top %02d Global Trends on Twitter are:" %num_of_trends)

    trend_num = 1
    for location in world_trends:
        for trend in location["trends"][:num_of_trends]:
            print(" %02d- %s" % (trend_num, trend["name"]))
            trend_num += 1

def get_us_trends(num_of_trends):

    US_WOE_ID = 23424977
    us_trends = api.trends_place(US_WOE_ID)

    print("\n The Top %02d Trends on Twitter in the United States of America are:" %num_of_trends)

    trend_num = 1
    for location in us_trends:
        for trend in location["trends"][:num_of_trends]:
            print(" %02d- %s" % (trend_num, trend["name"]))
            trend_num += 1

def get_trends():

    print("Do you want to see the Global trends or the trends only in United States?"
          "\n For Global trending topics - Enter '1':"
          "\n For Trending Topics in United States - Enter '2'")

    response = int(input(">>>>"))
    num_of_trends = int(input("Enter the number of top trending topics you wish to see:"))


    if response == 1:
        get_world_trends(num_of_trends)
    if response == 2:
        get_us_trends(num_of_trends)

def tweet_scraper_with_RT(trend_entered):

    maximum_number_of_tweets_to_be_extracted = int(input('Enter the number of tweets that you want to extract- '))

    with open("Tweets_with_trend_" + trend_entered + ".csv", 'w', newline='') as csvfile:
        csvWriter = csv.writer(csvfile)
        csvWriter.writerow(['User_name', 'Created_at', 'Tweet_Posted'])

        for tweet in tweepy.Cursor(api.search, q="'#'+ hashtag", lang='en').items(2000):

                csvWriter.writerow([tweet.user.screen_name, tweet.created_at, tweet.text.encode('utf-8')])


    print('Extracted ' + str(maximum_number_of_tweets_to_be_extracted)\
          + ' tweets with the keyword ' + trend_entered)

    print('A CSV file is created with the same name in the Current Working Folder')


def tweet_scraper_without_RT(trend_entered):

    maximum_number_of_tweets_to_be_extracted = int(input('Enter the number of tweets that you want to extract- '))

    with open("Tweets_with_trend_" + trend_entered + ".csv", 'w', newline='') as csvfile:
        csvWriter = csv.writer(csvfile)
        csvWriter.writerow(['User_name', 'Created_at', 'Tweet_Posted'])

        for tweet in tweepy.Cursor(api.search, q="'#'+ hashtag", lang='en').items(2000):

            if (not tweet.retweeted) and ('RT @' not in tweet.text):
                csvWriter.writerow([tweet.user.screen_name, tweet.created_at, tweet.text.encode('utf-8')])


    print('Extracted ' + str(maximum_number_of_tweets_to_be_extracted)\
          + ' tweets with the keyword ' + trend_entered)

    print('A CSV file is created with the same name in the Current Working Folder')


# Class for analysing tweets

class TwitterClient(object):
    '''
    Generic Twitter Class for sentiment analysis.
    '''

    def __init__(self):
        '''
        Class constructor or initialization method.
        '''
        # keys and tokens from the Twitter Dev Console
        consumer_key = '************'
        consumer_secret = '************'
        access_token = '****************'
        access_token_secret = '************'

        # attempt authentication
        try:
            # create OAuthHandler object
            self.auth = OAuthHandler(consumer_key, consumer_secret)
            # set access token and secret
            self.auth.set_access_token(access_token, access_token_secret)
            # create tweepy API object to fetch tweets
            self.api = tweepy.API(self.auth)
        except:
            print("Error: Authentication Failed")

    def clean_tweet(self, tweet):
        '''
        Utility function to clean tweet text by removing links, special characters
        using simple regex statements.
        '''
        return ' '.join(re.sub("(@[A-Za-z0-9]+)|([^0-9A-Za-z \t])| (\w+:\ / \ / \S+)", " ", tweet).split())



    def get_tweet_sentiment(self, tweet):
        '''
        Utility function to classify sentiment of passed tweet
        using textblob's sentiment method
        '''
        # create TextBlob object of passed tweet text
        analysis = TextBlob(self.clean_tweet(tweet))
        # set sentiment
        if analysis.sentiment.polarity > 0:
            return 'positive'
        elif analysis.sentiment.polarity == 0:
            return 'neutral'
        else:
            return 'negative'

    def get_tweets(self, query, count=10):
        '''
        Main function to fetch tweets and parse them.
        '''
        # empty list to store parsed tweets
        tweets = []

        try:
            # call twitter api to fetch tweets
            fetched_tweets = self.api.search(q=query, count=count)

            # parsing tweets one by one
            for tweet in fetched_tweets:
                # empty dictionary to store required params of a tweet
                parsed_tweet = {}

                # saving text of tweet
                parsed_tweet['text'] = tweet.text
                # saving sentiment of tweet
                parsed_tweet['sentiment'] = self.get_tweet_sentiment(tweet.text)

                # appending parsed tweet to tweets list
                if tweet.retweet_count > 0:
                    # if tweet has retweets, ensure that it is appended only once
                    if parsed_tweet not in tweets:
                        tweets.append(parsed_tweet)
                else:
                    tweets.append(parsed_tweet)

                    # return parsed tweets
            return tweets

        except tweepy.TweepError as e:
            # print error (if any)
            print("Error : " + str(e))


def main():

    print("Do you want to see the Trending Topics on Twitter ?"
          "\n Enter Yes or No")

    see_trends = input(">>>>")


    if see_trends == "Yes" or see_trends == "yes":
        get_trends()
        trend_entered = input("\nEnter the trend or keyword you want to scrape -")

        retweet_considered = input('\nDo you want to consider the Re-tweets ?(yes/no)')

        if retweet_considered == "Yes" or retweet_considered == "yes":
            tweet_scraper_with_RT(trend_entered)

        if retweet_considered == "No" or retweet_considered == "no":
            tweet_scraper_without_RT(trend_entered)

        analyzer = input('\nDo you want to further analyze the tweets? (yes/no)')

        if analyzer == 'Yes' or analyzer == 'yes':

            api_1 = TwitterClient()

            count_of_tweets = int(input('Enter the count of tweets to be analyzed:'))

            tweets = api_1.get_tweets(query=trend_entered, count=count_of_tweets)


            # picking positive tweets from tweets
            ptweets = [tweet for tweet in tweets if tweet['sentiment'] == 'positive']
            # percentage of positive tweets
            print("\nPositive tweets percentage: {} %".format(100 * len(ptweets) / len(tweets)))

            # picking negative tweets from tweets
            ntweets = [tweet for tweet in tweets if tweet['sentiment'] == 'negative']
            # percentage of negative tweets
            print("Negative tweets percentage: {} %".format(100 * len(ntweets) / len(tweets)))

            # percentage of neutral tweets
            print("Neutral tweets percentage: {} % ".format(
                100 * (len(tweets) - len(ntweets) - len(ptweets)) / len(tweets)))

            # printing first 5 positive tweets
            print("\n\nPositive tweets:")
            for tweet in ptweets[:10]:
                print(tweet['text'])

            # printing first 5 negative tweets
            print("\n\nNegative tweets:")
            for tweet in ntweets[:10]:
                print(tweet['text'])

        if analyzer == 'No' or analyzer == 'no':
            print("Fine! Thank You!!")


    if see_trends == "No" or see_trends == "no":

        key_word = input('\nEnter the Hashtag or Key word you want to scrape-')

        retweet_considered = input('\nDo you want to consider the Re-tweets ?(yes/no)')

        if retweet_considered == "Yes" or retweet_considered == "yes":
            tweet_scraper_with_RT(key_word)

        if retweet_considered == "No" or retweet_considered == "no":
            tweet_scraper_without_RT(key_word)

        analyzer = input('\nDo you want to further analyze the tweets? (yes/no)')

        if analyzer == 'Yes' or analyzer == 'yes':

            api_1 = TwitterClient()

            count_of_tweets = int(input('\nEnter the count of tweets to be analyzed:'))

            tweets = api_1.get_tweets(query=key_word, count=count_of_tweets)

            # picking positive tweets from tweets
            ptweets = [tweet for tweet in tweets if tweet['sentiment'] == 'positive']
            # percentage of positive tweets
            print("\nPositive tweets percentage: {} %".format(100 * len(ptweets) / len(tweets)))

            # picking negative tweets from tweets
            ntweets = [tweet for tweet in tweets if tweet['sentiment'] == 'negative']
            # percentage of negative tweets
            print("Negative tweets percentage: {} %".format(100 * len(ntweets) / len(tweets)))

            # percentage of neutral tweets
            print("Neutral tweets percentage: {} % ".format(
                100 * (len(tweets) - len(ntweets) - len(ptweets)) / len(tweets)))

            # printing first 5 positive tweets
            print("\n\nPositive tweets:")
            for tweet in ptweets[:10]:
                print(tweet['text'])

            # printing first 5 negative tweets
            print("\n\nNegative tweets:")
            for tweet in ntweets[:10]:
                print(tweet['text'])

        if analyzer == 'No' or analyzer == 'no':
            print("Fine! Thank You!!")



main()