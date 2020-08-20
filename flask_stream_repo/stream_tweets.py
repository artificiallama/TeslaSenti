#write to file and manage files
import os
import tweepy as tw
from tweepy.streaming import StreamListener
import pandas as pd
import numpy as np
import preprocessor as p
import json
import csv
import datetime
import time
import time_helper
import handle_tweets
#import multiprocessing as mp
import os


class StdOutListener(StreamListener):
    
 def on_data(self, data):

    p.set_options(p.OPT.EMOJI,p.OPT.SMILEY)
    #print('\ncurrent_process = ',mp.current_process())
  
    if not 'retweeted_status' in data:
     decoded = json.loads(data)
     write_txt = p.clean(decoded['text'])
     if 'extended_tweet' in data:
       try:
        write_txt = p.clean(decoded['extended_tweet']['full_text'])
       except:
        pass      
        
     with open('data/streaming_tweets_save.csv','a',encoding='utf-8',newline='') as file:
      csvwriter = csv.writer(file)   
      csvwriter.writerow([decoded['id'],decoded['created_at'],write_txt,
                        decoded['retweet_count'],decoded['favorite_count'], decoded['user']['screen_name'], 
                        decoded['user']['name'], decoded['user']['verified'], decoded['user']['followers_count'],
                        decoded['user']['friends_count'],decoded['source'],decoded['user']['url']]) 
        
    return True

    def on_error(self, status):
        print('\nERROR status = ',status)
        #self.disconnect()
        

#Append a csv file with latest tweets
def live_stream(): 

 consumer_key = ''
 consumer_secret = ''
 access_token = ''
 access_token_secret = ''

 auth = tw.OAuthHandler(consumer_key, consumer_secret)
 auth.set_access_token(access_token, access_token_secret)    
     
 l = StdOutListener()
 stream = tw.Stream(auth,l)
 stream.filter(track=['tesla','tsla'],languages=['en'])


#write csv files containing cleaned, significant sentiment tweets in the last somany minutes
def latest_tweets():

  time_horizon = 5  #minutes (this can be adjsuted to something convenient like ~30 minutes)
    
  print('\n\t\tEntered latest_tweets')   
    
  while True:
   if os.path.exists('data/streaming_tweets_save.csv'):
    break
   else:
    print('\t\tlatest_tweets() : Sleeping')   
    time.sleep(20)   

  print('\t\tlatest_tweets() : streaming tweets file exists')


  while True:
      
      #Read the latest chunk of rows.
      dftw = pd.read_csv('data/streaming_tweets_save.csv',names = ['id','date','tweet','retweet_count','favorite_count',
                                        'screen_name','name','verified','followers_count','friends_count',
                                                                   'source','user_url'])
      print('\n\tchunkshape = ',dftw.shape)
      
      dt2 = time_helper.current_time()
      dt1 = time_helper.lag_time(dt2,time_horizon)
         
      for index,row in dftw.iterrows():
          if not time_helper.time_between(dt1,dt2,time_helper.dstr_obj(row['date'])): 
              dftw.drop(index,axis=0,inplace=True)
      else:
          dftw.reset_index(inplace=True,drop=True)
          print('\n\t\tlatest : dftw.shape = ',dftw.shape)
#          dftw.to_csv('data/tweets_latest_'+dt1.strftime('%Y-%m-%d_%H-%M-%S')+'_to_'+dt2.strftime('%Y-%m-%d_%H-%M-%S')+'.csv',index=False)

      #Return a subset of only strong sentiment tweets
      if dftw.shape[0] > 3:
       dftw = handle_tweets.process_tweets(dftw)
       print('\n\t\tafter process : dftw.shape = ',dftw.shape)
       #print('\n\tcolumns = = ',dftw.columns)

      if dftw.shape[0] > 3:
       print('\n\t\tWrite out subset : dftw.shape = ',dftw.shape)   
       dftw.to_csv('data/tweets_latest_subset_'+dt1.strftime('%Y-%m-%d_%H-%M-%S')+'_to_'+dt2.strftime('%Y-%m-%d_%H-%M-%S')+'.csv',index=False)
      
      time.sleep(60*time_horizon) 
