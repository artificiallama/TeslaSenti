from multiprocessing import Process
import time
from flask import Flask, render_template  # request
import requests
import pandas as pd
import numpy as np
import time_helper as tm
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
        response = requests.get(
            'http://publish.twitter.com/oembed',
            params={
                "url": create_tweet_url(screenname, id_str),
            },
        )
    except requests.exceptions.RequestException as e:
        print('\trequests.get failed : ', screenname, id_str)
        print('\t', e)
        getrequest = "tweet page not found"
    else:
        try:
            getrequest = response.json()['html']
        except Exception as e:
            print('\tVIK : JSON json() failed : ', screenname, id_str)
            print('\tVIK : ', e)
            getrequest = "tweet page not found"

    return getrequest


def create_tweet_url(screen_name, id_str):
    twiturl = "https://twitter.com/{}/status/{}".format(screen_name, id_str)
    return twiturl


@app.route('/', methods=['GET'])
def home():

    while True:
        if os.path.exists('data_tweets/senti_tweets.csv'):
            break
        else:
            time.sleep(5)

    df = pd.read_csv('data_tweets/senti_tweets.csv', names=cvars.cols_display)
    nrows = df.shape[0]

    tweet_embed = []

    for kk in np.arange(nrows-4, nrows):
        htmlcode = get_tweet_embed_html(df.iloc[kk]['screen_name'],
                                        str(df.iloc[kk]['id']))
        tweet_embed.append(htmlcode)

    timenow = tm.current_time()
    tminus = pd.Series(tm.lag_time(timenow,
                       cvars.time_horizon1)).dt.floor('60min')[0]

    cond = df['date'].apply(lambda x:
                            tm.isin_window(tminus, timenow, tm.dstr_obj(x)))
    df.drop(index=df[~cond].index, inplace=True)
    print('\n\t', df.shape)

    if not df.empty:
        df['dtobj'] = df['date'].apply(lambda x: tm.dstr_obj(x))
        graphJSON = give_graph(df, timenow)
    else:
        graphJSON = {}

    return render_template(
           'home.html', plot=graphJSON,
           embed_tweet1=tweet_embed[0], embed_tweet2=tweet_embed[1],
           embed_tweet3=tweet_embed[2], embed_tweet4=tweet_embed[3],
           utc=tm.current_time().strftime('%Y-%m-%d %H:%M:%S')+' UTC')


# Return graph of sentiment index against time. The left subplot goes
#  back for a longer time (24 hours) and the
# right subplot goes back for a shorter time (1 hour).
def give_graph(dfin, tnow):

    fig = sp.make_subplots(rows=1, cols=2)

    # longser = go.Scatter(x=dfin['dtobj'].tolist(),
    # y=dfin['wt_senti'].to_numpy(), mode='markers',
    # marker=dict(color='Blue'))

    # Use a 60 min bucket to average sentiment index.
    # If data is not available mean for that particular hour is NaN.
    dfavg1 = dfin.resample("60min", kind='timestamp', on='dtobj').mean()

    sentiarr = dfavg1['wt_senti'].to_numpy()
    bound_senti = np.clip(sentiarr, a_min=-1.0, a_max=1.0)
    # longavg2 = go.Scatter(x=dfavg1.index.tolist(), y=sentiarr,
    # mode='lines+markers', marker=dict(color='Red'))
    longavg = go.Scatter(x=dfavg1.index.tolist(), y=bound_senti,
                         mode='lines+markers', marker=dict(color='green'))

    # fig.add_trace(longser,row=1,col=1)
    # fig.add_trace(longavg2,row=1,col=1)
    fig.add_trace(longavg, row=1, col=1)

    tminus = pd.Series(tm.lag_time(tnow,
                       cvars.time_horizon2)).dt.floor('5min')[0]

    cond = dfin['dtobj'].apply(lambda x: tm.isin_window(tminus, tnow, x))
    dfin.drop(index=dfin[~cond].index, inplace=True)

    if not dfin.empty:
        # shortser = go.Scatter(x=dfin['dtobj'].tolist(),
        # y=dfin['wt_senti'].to_numpy(), mode='markers',
        # marker=dict(color='Blue'))
        # Use a 5 min bucket to average sentiment index.
        dfavg2 = dfin.resample("5min", kind='timestamp', on='dtobj').mean()

        sentiarr = dfavg2['wt_senti'].to_numpy()
        bound_senti = np.clip(sentiarr, a_min=-1.0, a_max=1.0)

        # shortavg2 = go.Scatter(x=dfavg2.index.tolist(), y=sentiarr,
        # mode='markers+lines', marker=dict(color='Red'))
        shortavg = go.Scatter(x=dfavg2.index.tolist(), y=bound_senti,
                              mode='markers+lines', marker=dict(color='green'))

        # fig.add_trace(shortser,row=1,col=2)
        # fig.add_trace(shortavg2,row=1,col=2)
        fig.add_trace(shortavg, row=1, col=2)

    fig.update_layout(xaxis1={'type': 'date', 'tickmode': 'linear',
                             'dtick': cvars.tick_step1*3*60*1000,
                             },
                     xaxis2={'type': 'date', 'tickmode': 'linear',
                             'dtick': cvars.tick_step2*60*1000,
                            },
                     yaxis1={'range': [-1,1],
                             'title': { 'text': 'Sentiment', 'font' : {'size': 30} },
                             'tickfont': {'size' : 18},
					        },
                     yaxis2={'range': [-1,1], 'tickfont': {'size': 18}},
                     margin=dict(l=20, r=20, t=20, b=20),
                            paper_bgcolor="LightSteelBlue")

    fig.update_layout(height=400, width=1000)
    fig.update(layout_showlegend=False)

    graph = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)

    return graph


if __name__ == '__main__':

    print('\n\tStarting in app.py main :')
    # print("\n\tNumber of cpus = ",mp.cpu_count())
    # app.run(debug=True)
    # tweets.live_stream()

    # fetch tweets and write to csv
    p1 = Process(target=tweets.live_stream, args=())
    p1.start()

    # label and write to csv
    p2 = Process(target=tweets.sentiment_tweets, args=())
    p2.start()

    # serve requests
    p3 = Process(target=app.run, args=())
    p3.start()

    p1.join()
    p2.join()
    p3.join()
