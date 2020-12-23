
all_cols = ['id','date','tweet','retweet_count','favorite_count',
            'screen_name','name','verified','followers_count','friends_count',
            'source','user_url']

cols_display = ['id', 'date', 'tweet', 'senti', 'screen_name', 'tidy_tweet']

# any tweets with more than cash_thresh cashtags are removed.
cash_thresh = 10
nsecs=20

# sentiment index for how many minutes before current time should be shown in the graph ?
time_horizon1=600
time_horizon2=60

# Tick interval on xaxis of the plotly graph. The unit of tick_step is minutes. The unit expected by plotly
# is milliseconds.
tick_step1=60
tick_step2=5
