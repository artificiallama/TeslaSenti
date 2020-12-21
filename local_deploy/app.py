from multiprocessing import Process
import time
from flask import Flask, render_template, request
import requests
import pandas as pd
import numpy as np
import time_helper
import plotly.graph_objs as go
import plotly
import json
import tweets
import os
import cvars


app = Flask(__name__)


def get_tweet_embed_html(screenname, id_str):

    try:
        getrequest = requests.get(
            'http://publish.twitter.com/oembed',
            params={
                "url": create_tweet_url(screenname, id_str),
            },
        ).json()['html']
    except:
        print('\trequests.get failed : ', screenname, id_str)
        getrequest = "tweet page not found"
        pass

    return getrequest

 
def create_tweet_url(screen_name,id_str):
    twiturl = "https://twitter.com/{}/status/{}".format(screen_name, id_str)
    return twiturl


@app.route('/',methods=['GET'])
def home():

    print('\n----Entered home : request.method = ',request.method)
    params = request.args.to_dict()
    # print('\tparams = ',params)

    while True:
        if os.path.exists('data_tweets/senti_tweets.csv'):
            break
        else:
            print('\t\thome() : Sleeping')   
            time.sleep(5)   

    df_senti = pd.read_csv('data_tweets/senti_tweets.csv', names = cvars.cols_display)
    nrows = df_senti.shape[0]
  
    if not params:
        cc = 0
    else:
        cc = int(params['ccount'])

    print('\tnrows = ',nrows)
#  print('\n\tsenti = ',df_senti['senti'])
#  print('\n\tsenti_array = ',df_senti['senti'].to_numpy())
  
  #print('\tTime        = ',datetime.datetime.now())
  #print('\tTime UTC = ',datetime.datetime.utcnow())

    tweet_embed = []

#  for kk in np.arange(cc*4,cc*4+4):
    for kk in np.arange(nrows-4,nrows):  
        print('\n\t** kk = ',kk, df_senti.iloc[kk]['id'])
        print('\t** screenname = ',df_senti.iloc[kk]['screen_name'])
        print('\t** tweet = ',df_senti.iloc[kk]['tweet'])    
        print('\t** senti = ',df_senti.iloc[kk]['senti'])   
        htmlcode = get_tweet_embed_html(df_senti.iloc[kk]['screen_name'],str(df_senti.iloc[kk]['id']))
        tweet_embed.append(htmlcode)
  #  if kk > nrows-1 :
  #  break

    cc += 1   
    fnms='tweets_latest_subset_2020-07-13_17-14-17_to_2020-07-13_17-19-17.csv'

    dates = []
    for indx,row in df_senti.iterrows():
        dates.append(time_helper.dstr_obj(row['date']))

    graphJSON =  give_graph(dates, df_senti['senti'].to_numpy())
   
    return render_template('home.html',plot=graphJSON,embed_tweet1 = tweet_embed[0], embed_tweet2 = tweet_embed[1], embed_tweet3 = tweet_embed[2], embed_tweet4 = tweet_embed[3],mycc=cc,dtgtime=fnms[26:45],utc=time_helper.current_time().strftime('%Y-%m-%d %H:%M:%S')+' UTC')


 
def give_graph(xdates,senti_index):

    data = [go.Scatter(
             x = xdates,
             y = senti_index,
            mode = 'markers'
        )]

    #print('\n\tlen = ',len(xdates))
    #print('\tlen = ',len(senti_index))
    
    ymd = xdates[0].strftime('%Y-%b-%d')
    #print('\tymd = ',ymd)
    #print('\tday = ', xdates[0].strftime('%A'))
    
    layout = go.Layout(xaxis={'type':'date',
                            'tickmode':'linear',
                             'dtick': 5*60*1000,
                            },
                     yaxis={'range':[-5,5],
                            'title' : { 'text':'Sentiment', 'font' : {'size':30} },
                           } ,
                     title={ 'text' : ymd + ' (Time is in UTC)', 'x': 0.5,'font' : {'size':30}  },
                     margin=dict(l=20, r=20, t=20, b=20),
                     paper_bgcolor="LightSteelBlue")

    fig = go.Figure(data=data,layout=layout)
    graph = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder) 

    return graph
    

   
 
if __name__=='__main__':

    print('\n\tStarting in app.py main :')
#  print("\n\tNumber of cpus = ",mp.cpu_count())
#  app.run(debug=True)
#  tweets.live_stream()

    p1 = Process(target = tweets.live_stream,args=())  #fetch tweets and write to csv
    p1.start()

    p2 = Process(target = tweets.sentiment_tweets,args=())  #serve requests
    p2.start()

    p3 = Process(target = app.run,args=())  #serve requests
    p3.start()
  
    p1.join()
    p2.join()
    p3.join()
