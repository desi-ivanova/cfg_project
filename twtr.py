from datetime import datetime
import tweepy
from tweepy import OAuthHandler, API, Stream, OAuthHandler
from tweepy.streaming import StreamListener
from nltk.sentiment.vader import SentimentIntensityAnalyzer

import nltk
nltk.downloader.download('vader_lexicon')

import json
import time
import sys

class SListener(StreamListener):
    def __init__(self, api = None, fprefix = 'streamer', time_limit = 60):
        self.api = api or API()
        self.start_time = time.time()
        self.limit = time_limit
        self.counter = 0
        self.fprefix = fprefix
        self.output  = open('%s_%s.json' % (self.fprefix, 'listened'), 'w')


    def on_data(self, data):
        if (time.time() - self.start_time) > self.limit:
            return False
        elif  'in_reply_to_status' in data:
            self.on_status(data)
        elif 'delete' in data:
            delete = json.loads(data)['delete']['status']
            if self.on_delete(delete['id'], delete['user_id']) is False:
                return False
        elif 'limit' in data:
            if self.on_limit(json.loads(data)['limit']['track']) is False:
                return False
        elif 'warning' in data:
            warning = json.loads(data)['warnings']
            print("WARNING: %s" % warning['message'])
            return


    def on_status(self, status):
        self.output.write(status)
        self.counter += 1
        if self.counter >= 20000:
            self.output.close()
            self.output  = open('%s_%s.json' % (self.fprefix, time.strftime('%Y%m%d-%H%M%S')), 'w')
            self.counter = 0
        return


    def on_delete(self, status_id, user_id):
        print("Delete notice")
        return


    def on_limit(self, track):
        print("WARNING: Limitation notice received, tweets missed: %d" % track)
        return


    def on_error(self, status_code):
        print('Encountered error with status code:', status_code)
        return 


    def on_timeout(self):
        print("Timeout, sleeping for 60 seconds...")
        time.sleep(60)
        return 

# Consumer key authentication
auth = OAuthHandler('POtvWDXl74vOtKxgK00oJZGWx', 'L1ASG7vlTwTWTbVHxgdkNgNoeejYPhT7tDu8H5LuELO0fae8IW')
# Access key authentication
auth.set_access_token('2909167113-et0k0ZVAxEalFyP9BRoJPKD2S9sIQqyGXcClRcC', 'A19IdhhZLEEhv0mj3dWPMp6G8RRxHZXUw01jDlpVHhmYl')
# Set up the API with the authentication handler
api = API(auth)


def get_live(kwd, time_limit = 20): 
    """
    Params:
    -------
        kwd: keywords
        time_limit: time limit to listen in seconds
    
    Output:
    -------
        streamer_listened.json file containing tweets
    """
    # Instantiate the SListener object 
    listen = SListener(api, time_limit=time_limit)
    # Instantiate the Stream object
    stream = Stream(auth, listen)
    
    # Begin collecting data
    stream.filter(track = kwd)
    return

def get_historical(kwd, result_type='popular'):
    """
    Params:
    -------
        kwd: keywords
        result_type: type of result, passsed to tweepy.Cursor; default <popular>    
    Output:
    -------
        cursor_historical.json file containing tweets
    """
    out_text = []
    out_favcount = []
    out_file = open('cursor_historical.json', 'w')
    with open('cursor_historical.json', 'w') as out_file:
        for tweet in tweepy.Cursor(api.search, q=kwd, count=100, lang="en", result_type = result_type).items(100):
        
            out_file.write(json.dumps(tweet._json))
            out_file.write('\n')
            out_text.append(tweet.text)
            out_favcount.append(tweet.favorite_count)
    
    return # (out_text, out_favcount) 


### helpers
def flatten_tweets(tweets_json):
    """ Flattens out tweet dictionaries so relevant JSON
        is in a top-level dictionary."""
    
    tweets_list = []
    
    for line in open(tweets_json, 'r'):
        # tweet_obj = json.loads(tweet)
        tweet = json.loads(line)
        # Store the user screen name in 'user-screen_name'
        tweet['user-screen_name'] = tweet['user']['screen_name']
    
        # Check if this is a 140+ character tweet
        if 'extended_tweet' in tweet:
            # Store the extended tweet text in 'extended_tweet-full_text'
            tweet['tweet_text'] = tweet['extended_tweet']['full_text']
        else:
            tweet['tweet_text'] = tweet['text']
    
        if 'retweeted_status' in tweet:
            # Store the retweet user screen name in 'retweeted_status-user-screen_name'
            tweet['retweeted_status-user-screen_name'] = tweet['retweeted_status']['user']['screen_name']

            # Store the retweet text in 'retweeted_status-text'
            tweet['retweeted_status-text'] = tweet['retweeted_status']['text']
            
            if 'extended_tweet' in tweet['retweeted_status']:
            # Store the extended tweet text in 'extended_tweet-full_text'
                tweet['tweet_text'] = tweet['retweeted_status']['extended_tweet']['full_text']
        
            
        tweets_list.append(tweet)
    return tweets_list



def check_word_in_tweet(word, data):
    """Checks if a word is in a Twitter dataset's text. 
    Checks text and extended tweet (140+ character tweets) for tweets,
    retweets and quoted tweets.
    Returns a logical pandas Series.
    """
    contains_column = data['text'].str.contains(word, case = False)
    contains_column |= data['extended_tweet-full_text'].str.contains(word, case = False)
    contains_column |= data['quoted_status-text'].str.contains(word, case = False)
    contains_column |= data['quoted_status-extended_tweet-full_text'].str.contains(word, case = False)
    contains_column |= data['retweeted_status-text'].str.contains(word, case = False)
    contains_column |= data['retweeted_status-extended_tweet-full_text'].str.contains(word, case = False)
    return contains_column



def compute_sentiment(flattended_tweets, return_all = False):
    sid = SentimentIntensityAnalyzer()

    # Generate sentiment scores
    sentiment_scores = flattended_tweets['text'].apply(lambda x: sid.polarity_scores(x))
    
    if return_all:
        return sentiment_scores
    else:
        return [s['compound'] for s in sentiment_scores]
    
    
    
def clean_and_analyse(json_file):
    tweets = pd.DataFrame(twtr.flatten_tweets(json_file))
    
    tweets['sentiment'] = twtr.compute_sentiment(tweets)
    
    tweets=tweets.sort_values('sentiment')
    
    show_tweets = pd.concat([tweets.tail(2), tweets.head(2)])
    