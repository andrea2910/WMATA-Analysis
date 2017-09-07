import pandas as pd
from pandas.io.json import json_normalize 
import requests, json
from requests_oauthlib import OAuth1
import nltk
from nltk.sentiment.vader import SentimentIntensityAnalyzer as SIA
import re

auth = OAuth1('',
			  '',
			  '',
			  '')
			  

def create_searches(since, until):
	"""
	Create the parameters for twitter searches. The since and until dates
	should be in the format of 'YYYY-MM-DD.
	
	This code will be used to create only weekday searches
	"""
	searches = {
			'h_wmata': {'q': '%23wmata','result_type': 'recent',
						'count': '100', 'since':since,'until':until},
			'a_wmata': {'q': '%40wmata', 'until':until,
						'result_type': 'recent',
						'count': '100'},
			'h_unsuckdcmetro': {'q': '%23unsuckdcmetro','since':since, 'until':until,
								'result_type': 'recent', 'count': '100'},
			'a_unsuckdcmetro': {'q': '%40unsuckdcmetro','since':since, 'until':until,
								'result_type': 'recent', 'count': '100'},
			'a_fixwmata': {'q': '%40fixwmata', 'since':since, 'until':until,
						   'result_type': 'recent',
						   'count': '100'},
			'a_dcmetrosucks': {'q': '%40dcmetrosucks','since':since, 'until':until,
							   'result_type': 'recent', 'count': '100'},
			'a_metrorage': {'q': '%40metrorage','since':since, 'until':until,
							'result_type': 'recent',
							'count': '100'},
			'a_overhaulmetro': {'q': '%40overhaulmetro','since':since, 'until':until,
								'result_type': 'recent', 'count': '100'},
			'h_metrorailinfo': {'q': '%23metrorailinfo','since':since, 'until':until,
								'result_type': 'recent', 'count': '100'},
			'a_metrorailinfo': {'q': '%40metrorailinfo','since':since, 'until':until,
								'result_type': 'recent', 'count': '100'},
			'h_metrofailinfo': {'q': '%23metrofailinfo','since':since, 'until':until,
								'result_type': 'recent', 'count': '100'},
			'a_metrofailinfo': {'q': '%40metrofailinfo','since':since, 'until':until,
								'result_type': 'recent', 'count': '100'},
			'a_drgridlock': {'q': '%40drgridlock','since':since, 'until':until,
							 'result_type': 'recent',
							 'count': '100'}}
	return searches
	
def make_first_request(request_info):
	"""
	Make the twitter request
	"""
	url_base = 'https://api.twitter.com/1.1/search/tweets.json'
	r = requests.get(url_base, auth=auth, params=request_info)
	tweets = json.loads(r.text)
	return tweets

def make_url_request(request_url):
	"""
	Iterate through a twitter result
	"""
	r = requests.get(request_url, auth=auth)
	tweets = json.loads(r.text)
	return tweets


def tweet_search(since, until):
	"""
	Code to return all twitter search results from our searches
	"""
	all_search_results = []
	url_base = 'https://api.twitter.com/1.1/search/tweets.json'
	searches = create_searches(since,until)
	for search_term in searches:
		search_results = make_first_request(searches[search_term])
		if len(search_results) == 0:
			pass
		elif 'errors' in search_results.keys():
			pass
		elif len(search_results['statuses']) == 0:
			pass
		elif 'next_results' not in search_results['search_metadata'].keys():
			all_search_results.append(search_results['statuses'])
			pass
		else:
			all_search_results.append(search_results['statuses'])
			while ('next_results' in search_results['search_metadata'].keys()):
				next_search_url = search_results['search_metadata']['next_results']
				search_results = make_url_request(url_base + next_search_url)
				all_search_results.append(search_results['statuses'])
	return all_search_results

def weekday_searches(since,until):
	"""
	Code to search between dates
	"""
	all_results = tweet_search(since,until)
	if len(search_results)==0:
		return None
	else:
		tweets0 = json_normalize(all_results[0])
		tweets1 = tweets0[['id','created_at','text','favorite_count','retweet_count']]
		tweets_final = tweets1.drop_duplicates()
		tweets_final.index = range(tweets_final.shape[0])
		tweets_final['created'] = [pd.Timestamp(t).tz_convert('US/Eastern') for t in tweets_final['created_at']]
		return tweets_final[['id','created','text','favorite_count','retweet_count']]
	