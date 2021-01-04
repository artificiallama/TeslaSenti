import os
import tweepy as tw
from tweepy.streaming import StreamListener
import pandas as pd
import numpy as np
import preprocessor as p
import json
import csv
import time
import pickle
import cvars
import text_clean as tc


# Write streaming tweets to csv file
class StdOutListener(StreamListener):

    def on_data(self, data):

        p.set_options(p.OPT.EMOJI, p.OPT.SMILEY)

        if 'retweeted_status' not in data:
            decoded = json.loads(data)
            if (not decoded['is_quote_status'])  and (decoded['in_reply_to_status_id'] is None):
                if 'extended_tweet' in data:
                    write_txt = p.clean(decoded['extended_tweet']['full_text'])
                else:
                    write_txt = p.clean(decoded['text'])

                with open('data_tweets/streaming_tweets_save.csv', 'a', encoding='utf-8', newline='') as file:
                    csvwriter = csv.writer(file)
                    csvwriter.writerow([decoded['id'], decoded['created_at'], write_txt,
                        decoded['retweet_count'], decoded['favorite_count'], decoded['user']['screen_name'],
                        decoded['user']['name'], decoded['user']['verified'], decoded['user']['followers_count'],
                        decoded['user']['friends_count'], decoded['source'], decoded['user']['url']])

        # print('\nDone writing : on_data')
        return True

    def on_error(self, status):
        print('\nERROR status = ', status)
    # self.disconnect()


# Append a csv file with latest tweets
def live_stream():
    print('\nEntered live_stream')
    consumer_key = os.getenv('consumer_key')
    consumer_secret = os.getenv('consumer_secret')
    access_token = os.getenv('access_token')
    access_token_secret = os.getenv('access_token_secret')

    # print('\n\taccess_token_secret  = ',access_token_secret)

    if consumer_key is None:
        raise NameError(' consumer_key is not set')
    if consumer_secret is None:
        raise NameError('consumer_secret is not set')
    if access_token is None:
        raise NameError('access_token is not set')
    if access_token_secret is None:
        raise NameError('access_token_secret is not set')

    auth = tw.OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_token, access_token_secret)

    l = StdOutListener()
    stream = tw.Stream(auth, l)
    print('\n\tCalled stream.filter')
    stream.filter(track=['tesla', 'tsla'], languages=['en'])


# Clean the tweets
# Run the model on each tweet and write the weighted sentiment index to csv file
def sentiment_tweets():

    print('\n\t\tEntered sentiment_tweets : ')

    # Deserialize the model
    with open('data/bayes_fit.pkl', 'rb') as f:
        count_vect, model = pickle.load(f)

    # On entry (very first time the app is launched), make sure the file exists
    while True:
        if os.path.exists('data_tweets/streaming_tweets_save.csv'):
            break
        else:
            print('\t\tsentiment_tweets() : Sleeping')
            time.sleep(20)

  
    dftw = pd.DataFrame(columns=cvars.cols_senti)

    skiprows = 0	
    while True:
        # Empty out dataframe, to be sure
        dftw.drop(dftw.index, inplace=True)

		# Read in only the latest tweets (Within last nsecs) using skiprows.
        dftw = pd.read_csv('data_tweets/streaming_tweets_save.csv', names=cvars.cols , skiprows=skiprows)

        shp = dftw.shape
		
        cond_cash =  dftw['tweet'].apply(lambda x : tc.count_cashtags(x) > cvars.cash_thresh)
        dftw.drop(index=dftw[cond_cash].index,inplace=True)
	
        print('\n\t^^ skiprows = ',skiprows)
        print('\n^^ shape = ',dftw.shape)

        if not dftw.empty:
            print('\n\tIN dftw.shape = ',shp)

            dftw['tidy_tweet'] = dftw['tweet'].apply(lambda x : tc.clean_emoji_url(x))
            dftw['tidy_tweet'] = dftw['tidy_tweet'].apply(lambda x : tc.remove_hashtag(x))
            dftw['tidy_tweet'] = dftw['tidy_tweet'].apply(lambda x : tc.remove_cashtag(x))
            dftw['tidy_tweet'] = dftw['tidy_tweet'].apply(lambda x : tc.remove_mention(x))
            dftw['tidy_tweet'] = dftw['tidy_tweet'].apply(lambda x : tc.replace_chars(x))
            dftw['tidy_tweet'] = dftw['tidy_tweet'].apply(lambda x : tc.normalize_doc(x))

            cond = dftw['tidy_tweet'].apply(lambda x : tc.count_toks(x) == 0)
            dftw.drop(index = dftw[cond].index,inplace=True)
            print('\t^^ ',dftw.shape)
			
            if not dftw.empty:
                print('\t** ',dftw.shape)
                for indx,row in dftw.iterrows():
                    dftw.loc[indx,'senti'] =  model.predict(count_vect.transform([row['tidy_tweet']]))
                dftw['wt_senti'] = dftw.apply(lambda x : weighted_senti(x['senti'],x['retweet_count']+x['favorite_count'],x['verified'],x['followers_count']+x['friends_count']), axis=1)	
                dftw[cvars.cols_display].to_csv('data_tweets/senti_tweets.csv', mode='a', header=False, index=False)

        print('\t!! ',dftw.shape)
        skiprows += shp[0]
        time.sleep(cvars.nsecs)
        # wait for the streaming to bring in new tweets.
		# skiprows defines the boundary between old and new tweets.

		
# Neutral tweets are unaffected.
def weighted_senti(wt_senti,fav_retweet,verifyuser,foll_friend):

 # In real-time it is unusual to find a favorited or retweeted tweet.	
 if fav_retweet > 0 :
  wt_senti = wt_senti * 5.0 * fav_retweet

 # foll_friend can be a huge number for some users. 
 if foll_friend > 10 :
  wt_senti = wt_senti * np.log10(foll_friend)

 # Double the impact for verified users. 
 if verifyuser:
  wt_senti = wt_senti * 2

 return wt_senti 
	
	
