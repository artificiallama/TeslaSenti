#Code taken from,
#https://blog.heptanalytics.com/flask-plotly-dashboard/
#https://github.com/yvonnegitau/flask-Dashboard
import stream_tweets
import multiprocessing as mp
from multiprocessing import Process
import time
from flask import Flask,render_template,request,jsonify #,g
import requests
import pandas as pd
import numpy as np
import json
import text_clean as tc
import handle_tweets
import time_helper

app = Flask(__name__)

#https://github.com/fhaque/nlp-mlops-workshop-group-2/blob/master/server/twitter_service.py
def get_tweet_embed_html(screenname,id_str):
 try:
  getrequest = requests.get(
            'http://publish.twitter.com/oembed',
            params={
                "url": create_tweet_url(screenname,id_str),
            },
        ).json()['html']
 except:
  print('\trequests.get failed')
  getrequest = "tweet page not found"
  pass
 
 return getrequest

 
def create_tweet_url(screen_name,id_str):
 twiturl = "https://twitter.com/{}/status/{}".format(screen_name, id_str)
 return twiturl


@app.route('/',methods=['GET'])
def home():

  print('\n----Entered home : request.method = ',request.method)
# print('\n\trequest.args = ',request.args)
  params = request.args.to_dict()

  fnms = handle_tweets.give_latest_tweets()
  print('\tparams = ',params)
  
#  print('\n\t^^fnms[-1]    = ',fnms[-1])
#  print('\n\t^^fnms[0] = ',fnms[0])
  print('\n\tfnms[0][26:45] = ',fnms[0][26:45])

  df_latest = pd.read_csv(fnms[0])
  
  print('\n\t^^df_latest.shape = ',df_latest.shape) 

  if not params:
   cc = 0
  else:
   cc = int(params['ccount'])
   lastdtg = str(params['dtg'])
   print('\n\tcc = ',cc)
   print('\tlastdtg = ',lastdtg)
   if fnms[0][26:45] != lastdtg:   #newer file is available
    cc = 0
    print('\tnewer file is available')
   else:
    print('\tuse same file')
    if cc*4+4 >= df_latest.shape[0]: #Remaining entries in file are fewer than 4
     cc = 0                          #go back to beginning of file

  print('\n\tcc = ',cc) 
  tweet_embed = []

  for kk in np.arange(cc*4,cc*4+4):
#   print('\t = ',dftw.iloc[kk]['tweet'])
   #print('\t',kk)   
   #print('\t',df_latest.iloc[kk]['date'])   
   htmlcode = get_tweet_embed_html(df_latest.iloc[kk]['screen_name'],str(df_latest.iloc[kk]['id']))
   tweet_embed.append(htmlcode)

  cc += 1  
  
  return render_template('home.html', embed_tweet1 = tweet_embed[0], embed_tweet2 = tweet_embed[1], embed_tweet3 = tweet_embed[2], embed_tweet4 = tweet_embed[3],mycc=cc,dtgtime=fnms[0][26:45],utc=time_helper.current_time().strftime('%Y-%m-%d %H:%M:%S')+' UTC')



if __name__=='__main__':

  print('\n\tStarting :')

  print("\n\tNumber of cpus = ",mp.cpu_count())
  
  p1 = Process(target = stream_tweets.live_stream,args=())  #fetch tweets and write to csv
  p1.start()
  
  p2 = Process(target = stream_tweets.latest_tweets,args=()) #make smaller csv files with latest tweets
                                                             #after cleaning, labeling etc.
  p2.start()

  p3 = Process(target = app.run,args=())  #serve requests
  p3.start()
  
  p1.join()
  p2.join()
  p3.join()


