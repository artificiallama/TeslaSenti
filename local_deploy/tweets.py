import os
import tweepy as tw
from tweepy.streaming import StreamListener
import pandas as pd
import numpy as np
import preprocessor as p
import json
import csv
#import datetime
import time
#import time_helper
#import handle_tweets
import pickle



# Write streaming tweets to csv file
class StdOutListener(StreamListener):
    
  def on_data(self, data):

    p.set_options(p.OPT.EMOJI,p.OPT.SMILEY)
  
    if not 'retweeted_status' in data:
      decoded = json.loads(data)
      if (not decoded['is_quote_status'])  and (decoded['in_reply_to_status_id'] is None)  :
        if 'extended_tweet' in data:
          write_txt = p.clean(decoded['extended_tweet']['full_text'])
        else:
          write_txt = p.clean(decoded['text'])
        with open('data_tweets/streaming_tweets_save.csv','a',encoding='utf-8',newline='') as file:
          csvwriter = csv.writer(file)   
          csvwriter.writerow([decoded['id'],decoded['created_at'],write_txt,
                        decoded['retweet_count'],decoded['favorite_count'], decoded['user']['screen_name'], 
                        decoded['user']['name'], decoded['user']['verified'], decoded['user']['followers_count'],
                        decoded['user']['friends_count'],decoded['source'],decoded['user']['url']])
          
    #print('\nDone writing : on_data')      
    return True

  def on_error(self, status):
    print('\nERROR status = ',status)
    #self.disconnect()
        

#Append a csv file with latest tweets
def live_stream(): 
  print('\nEntered live_stream' )  
  consumer_key        = os.getenv('consumer_key')
  consumer_secret     = os.getenv('consumer_secret')
  access_token        = os.getenv('access_token')
  access_token_secret = os.getenv('access_token_secret')

  #print('\n\taccess_token_secret  = ',access_token_secret)

  if access_token_secret is None:
   raise NameError('access_token_secret is not set')
   
  auth = tw.OAuthHandler(consumer_key, consumer_secret)
  auth.set_access_token(access_token, access_token_secret)    
     
  l = StdOutListener()
  stream = tw.Stream(auth,l)
  print('Called stream.filter')
  stream.filter(track=['tesla','tsla','elon','musk'],languages=['en'])
 


#Clean the tweets  
#Run the model on each tweet and write sentiment index to csv file  
def sentiment_tweets():
  
  print('\n\t\tEntered sentiment_tweets')   

  with open('data/bayes_fit.pkl', 'rb') as f:
   count_vect,model = pickle.load(f)
  
  skiprows = 0
  while True:
   if os.path.exists('data_tweets/streaming_tweets_save.csv'):
    break
   else:
    print('\t\tsentiment_tweets() : Sleeping')   
    time.sleep(20)   

  print('\t\tlatest_tweets() : streaming tweets file exists')
  
  dftw_senti = pd.DataFrame(columns=['id','date','tweet','senti','screen_name'])
  
  while True:
   dftw_senti.drop(dftw_senti.index,inplace=True)
   dftw = pd.read_csv('data_tweets/streaming_tweets_save.csv',names = ['id','date','tweet','retweet_count','favorite_count',
                                        'screen_name','name','verified','followers_count','friends_count',
                                                                       'source','user_url'],skiprows=skiprows)
   shp = dftw.shape
   #print('\n\tskiprows = ',skiprows)  
   if shp[0] != 0:
    print('\n\tdftw.shape = ',shp)
    #print('\tFirst = ',dftw.iloc[0,2])
    #print('\tLast = ',dftw.iloc[shp[0]-1,2])
    dftw_senti[['id','date','tweet','screen_name']] =  dftw[['id','date','tweet','screen_name']].copy()
    #dftw_senti.loc[:,'senti'] = 0.5
    #print('\tFirst = ',dftw_senti.iloc[0,2])
    #print('\tLast = ',dftw_senti.iloc[shp[0]-1,2])
    #print('\tdftw_senti.shape = ',dftw_senti.shape)
    for indx,row in dftw_senti.iterrows():     
     senti_index = model.predict(count_vect.transform([row['tweet']]))
     #print('\ttweet : {} |  senti  = {} '.format(row['tweet'],senti_index))
     dftw_senti.loc[indx,'senti'] = senti_index
    dftw_senti.to_csv('data_tweets/senti_tweets.csv',mode='a',header=False,index=False)
    #dftmp = pd.read_csv('data_tweets/senti_tweets.csv')
    #print('\tid = ',dftmp.iloc[0,0])
    #print('\tdate = ',dftmp.iloc[0,1])
    #print('\ttweet = ',dftmp.iloc[0,2])
    #print('\tsenti = ',dftmp.iloc[0,3])
    #print('\tsenti = ',dftmp.iloc[0,4])
   #else:
    #print('\thsp[0] = ',shp[0])
   skiprows += shp[0]  
   time.sleep(20)
