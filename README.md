# TeslaSenti
Near real-time sentiment analysis of Tesla tweets.

This is a capstone project for a workshop conducted by AISC. This project was executed by a team of two members (including myself).


The objective of this project is to fetch tweets about TESLA in real time, analyse them for sentiment and generate a buy/sell signal every hour.

A multiprocessing approach is employed because fetching the tweets, preprocessing/analysing them and serving the requests has to be done
simultaneously. Process p1 fetches the tweets and writes them to a csv file. Process p2 cleans the tweets, runs the sentiment predictor and writes only
the strong sentiment tweets to csv files. Each file contains latest tweets in 30 minutes intervals.  Process p3 serves the incoming requests. Every time the user
clicks next a set of 4 latest tweets are shown. With every click the older tweets are shown going back to 30 minutes. After that the tweets are recycled. Therefore
the tweets displayed are always within the last 30 minutes.

The user interface is very basic. There is a TESLA logo and a next button. The main body of the page shows 4 tweets. These are clickable. The user can click and visit the respective twitter page.

We could not achieve the ultimate objective of generating a buy and sell signal based on the sentiment. A positive sentiment about TESLA is a buy signal while a negative
sentiment is a sell signal. The idea was to calculate a sentiment index for each tweet, weigh it by the number of followers/likes and average over an hour to generate a buy or sell signal. However we found that the trained sentiment model performed poorly on identifying the sentiment of many of the tweets.

We trained a Naive Bayes model to identify sentiment of financial headlines. For this we used 4845 financial phrase bank Kaggle dataset and 1100 FiQA financial tweets and headlines dataset. These are labelled datasets (Negative, Neutral and Positive). We trained the Naive Bayes model on 80% of the dataset. It performed well on the test dataset (85% accuracy). However we found that it did not perform well on the actual tweets about Tesla. The model mislabelled many positive tweets as negative and vice versa. This is because the tweets about Tesla were about varied topics like energy, battery, cars and also politics. This can be improved only if labeled tweets (about Tesla) can be used to train the model. 

Therefore we could not generate a buy/sell signal reliably. Hence we only identify tweets with intense sentiment (either positive or negative) and display them in near-real time.
 
<p align="left">
<img width="400" height="300" src="images/FiQA_headline_sentiment.png">
<img width="400" height="300" src="images/FiQA_post_sentiment.png">
</p>


References :

Malo, P., Sinha, A., Korhonen, P., Wallenius, J., & Takala, P. (2014). Good debt or bad debt: Detecting semantic orientations in economic texts. Journal of the Association for Information Science and Technology, 65(4), 782-796.
https://www.kaggle.com/ankurzing/sentiment-analysis-for-financial-news
