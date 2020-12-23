from multiprocessing import Process
import time
from flask import Flask, render_template, request
import requests
import pandas as pd
import numpy as np
import time_helper
import plotly.graph_objs as go
import plotly
from plotly import subplots as sp
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

    tweet_embed = []

    for kk in np.arange(nrows-4,nrows):  
        #print('\n\t** kk = ',kk, df_senti.iloc[kk]['id'])
        #print('\t** screenname = ',df_senti.iloc[kk]['screen_name'])
        #print('\t** tweet = ',df_senti.iloc[kk]['tweet'])    
        #print('\t** senti = ',df_senti.iloc[kk]['senti'])   
        htmlcode = get_tweet_embed_html(df_senti.iloc[kk]['screen_name'],str(df_senti.iloc[kk]['id']))
        tweet_embed.append(htmlcode)

    cc += 1   
    fnms='tweets_latest_subset_2020-07-13_17-14-17_to_2020-07-13_17-19-17.csv'

    dt2 = time_helper.current_time()
    dt1 = time_helper.lag_time(dt2,cvars.time_horizon1)

    print('\n\tdt2 = ',dt2)
	
    cond =  df_senti['date'].apply(lambda x : time_helper.time_between(dt1,dt2,time_helper.dstr_obj(x)))

    df_senti.drop(index=df_senti[~cond].index,inplace=True)

    print('\n\tdf_senti.shape = ',df_senti.shape)

    if not df_senti.empty:
        df_senti['dtobj'] = df_senti['date'].apply(lambda x : time_helper.dstr_obj(x))
        dates1 = df_senti['dtobj'].tolist()
        arr1   =  df_senti['senti'].to_numpy()			

        dt1 = time_helper.lag_time(dt2,cvars.time_horizon2)
        cond =  df_senti['date'].apply(lambda x : time_helper.time_between(dt1,dt2,time_helper.dstr_obj(x)))
        df_senti.drop(index=df_senti[~cond].index,inplace=True)

        dates2 = df_senti['dtobj'].tolist()
        arr2   =  df_senti['senti'].to_numpy()			
		
        graphJSON = give_graph(dates1,arr1,dates2,arr2)
    else:
        print('&&&&&Calling')
        graphJSON = {} 

		
    return render_template('home.html',plot=graphJSON,embed_tweet1 = tweet_embed[0], embed_tweet2 = tweet_embed[1], embed_tweet3 = tweet_embed[2], embed_tweet4 = tweet_embed[3],mycc=cc,dtgtime=fnms[26:45],utc=time_helper.current_time().strftime('%Y-%m-%d %H:%M:%S')+' UTC')


 
def give_graph(xdates1,senti_index1,xdates2,senti_index2):

    l1 = len(xdates1)
    l2 = len(xdates2)	
    print('\n\tlen(dates) = ',l1,l2)
    print('\tlen(dates) = ',len(senti_index1),len(senti_index2))
    
    ymd = xdates1[0].strftime('%Y-%b-%d')

    #for ii in range(43,0,-1):
    # print('\n^^xdates1 = ',xdates1[l1-ii], senti_index1[l1-ii])
    # print('  xdates2 = ',xdates2[l2-ii],senti_index2[l2-ii])

    print('')
	
    fig = sp.make_subplots(rows=1,cols=2)

    dt1 = go.Scatter(x=xdates1, y=senti_index1, mode='markers', marker=dict(color='Red'))	
    dt2 = go.Scatter(x=xdates2, y=senti_index2, mode='markers', marker=dict(color='MediumPurple'))
	
    fig.add_trace(dt1,row=1,col=1)	
    fig.add_trace(dt2,row=1,col=2)
	
    fig.update_layout(xaxis1={'type':'date',
                            'tickmode':'linear',
                             'dtick': cvars.tick_step1*60*1000,
                            },
		             xaxis2={'type':'date',
                            'tickmode':'linear',
                             'dtick': cvars.tick_step2*60*1000,
                            },
                     yaxis1={'range':[-5,5],
                            'title' : { 'text':'Sentiment', 'font' : {'size':30} },
                           },
                     yaxis2={'range':[-5,5]},					                       					  
                     margin=dict(l=20, r=20, t=20, b=20),
                     paper_bgcolor="LightSteelBlue")
	
    fig.update_layout(height=400,width=1000)
    fig.update(layout_showlegend=False)
	
    graph = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder) 

    return graph

   
 
if __name__=='__main__':

    print('\n\tStarting in app.py main :')
#  print("\n\tNumber of cpus = ",mp.cpu_count())
    app.run(debug=True)
#  tweets.live_stream()

#    p1 = Process(target = tweets.live_stream,args=())  #fetch tweets and write to csv
#    p1.start()

#    p2 = Process(target = tweets.sentiment_tweets,args=())  #label and write to csv
#    p2.start()

#    p3 = Process(target = app.run,args=())  #serve requests
#    p3.start()
  
#    p1.join()
#    p2.join()
#    p3.join()
