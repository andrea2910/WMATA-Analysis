import nltk
from nltk.sentiment.vader import SentimentIntensityAnalyzer as SIA
import re
import pandas as pd

delay_words = ['delay','delays','delayed','dual','tracking','single', 'minute',
               'minutes', 'min', 'mins', 'midday', 'mid-day', 'wait', 'waiting', 'service']
line_words = ['red','orange','blue','silver','yellow','green','line','station','train', 'RL', 'OL', 'BL', 'SL', 'YL', 'GL']
angry_words = ['rt','@wmata','@unsuckdcmetro','@metrorailinfo',
               '@metrofailinfo', '@fixwmata', '@dcmetrosucks','@fixmetro', '@drgridlock',
               '#wmata', '#unsuckdcmetro', '#fixwmata']
ok_words = ['normal', 'resume', 'resuming']
irrelevant_words = ['bus', 'route']

# remove usernames, hyperlinks, numbers, etc.
def clean_tweet(tweet):
    """
    remove usernames, hyperlinks, numbers, etc.
    """
    tweet = re.sub('[@][A-Za-z0-9]+','', tweet)
    tweet = re.sub('http://[A-Za-z\.\/0-9]+', '', tweet)
    tweet = re.sub('https://[A-Za-z\.\/0-9]+', '', tweet)
    tweet = re.sub('[0-9]+', '', tweet)
    tweet = tweet.replace('\'', '')
    return tweet.lower()

def is_rt(tweet):
    """
    Find whether the word rt occurs
    """
    if len(re.findall('\brt\b', tweet.lower()))>0:
        return True
    else:
        return False

def is_delay(tweet):
    """
    determine whether a tweet has a delay word in it
    """
    if any(word in delay_words for word in tweet.lower().split()):
        return True
    else:
        return False

def is_angry(tweet):
    """
    determine whether a tweet has a angry word in it
    """
    if any(word in angry_words for word in tweet.lower().split()):
        return True
    else:
        return False 

def is_ok(tweet):
    """
    determine whether a tweet has an ok in it
    """
    if any(word in ok_words for word in tweet.lower().split()):
        return True
    else:
        return False 

def is_irrelevant(tweet):
    """
    determine whether a tweet has an irrelevant word in it
    """
    if any(word in irrelevant_words for word in tweet.lower().split()):
        return True
    else:
        return False

def get_sentiment_score(tweet):
    """
    return total score of a tweet based on twitter's own package
    """
    sia = SIA()
    return sia.polarity_scores(tweet)['compound']

def add_variables(data):
    """
    Create new columns: cleaned tweet, is a RT, delay, angry, ok, irrelevant,
        own score, sentiment score from python
    """
    data['cleaned_tweet'] = data['text'].apply(clean_tweet)
    data['is_rt'] = data['text'].apply(is_rt)
    data['is_angry'] = data['text'].apply(is_angry)
    data['is_delay'] = data['text'].apply(is_delay)
    data['is_ok'] = data['text'].apply(is_ok)
    data['is_irrelevant'] = data['text'].apply(is_irrelevant)
    data['tweet_score'] = data['cleaned_tweet'].apply(get_sentiment_score)
    unhappy_scores = [0]*data.shape[0]
    #for each row generate a score
    for index, row in data.iterrows():
        score = 0
        if row['is_angry']:
            score = score + row['favorite_count'] + row['retweet_count'] + 1
        if row['is_delay']:
            score = score + row['favorite_count'] + row['retweet_count'] + 1
        unhappy_scores[index] = score
    data['unhappy_score'] = unhappy_scores
    return data
	
tweets = pd.read_csv("tweets.csv")
tweets2 = add_variables(tweets)
tweets2.to_csv("tweets_cleaned.csv",index=False)
