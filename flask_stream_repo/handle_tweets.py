import pandas as pd
import numpy as np
import text_clean as tc
import pickle
import sklearn
import glob
import datetime
import time

#return list of filenames with latest file at top  of list.
def give_latest_tweets():

 while True:
  lstfile = glob.glob('data/tweets_latest_subset*.csv')
  print('\n\t**lstfile = ',lstfile)
  #when app is launched it takes sometime for streaming tweets to be processed.
  if lstfile:
   break
  time.sleep(60)

 #extract the datetime
 lstfnm = []
 lstdtg = []
 for fnm in lstfile:
  substr=fnm[26:45]
  dt = datetime.datetime.strptime(substr, '%Y-%m-%d_%H-%M-%S')
  lstdtg.append(dt)
  lstfnm.append(fnm)
  #print('\t\t\t  ',dt)

 z = [x for _,x in sorted(zip(lstdtg,lstfnm))]

 return(z[::-1])


#Clean and predict sentiment of tweets 
def process_tweets(dftw):
 print('\tvik : In process tweets')
 
#---drop some tweets---
 kywrds = ['tsla', 'tesla', 'elon', 'musk']
 badwords = ['nigga','nigger','gay','pussy','pussc','cunt','fuck','dick','cock','suck','whore','pimp','wtf','asshole','bitch']
 
 #Get rid of any tweets which do not contain relevant keywords. Even though the API uses keywords to search
 #some tweets do not contain these keywords (like tsla, tesla) since the user name might contain these keywords. 
 #Get rid of any tweets which are replies.

 for index,row in dftw.iterrows():
  txt = row['tweet']
  ctxt =  tc.p.clean(txt)
  if (not any(wrd in ctxt.lower() for wrd in kywrds)) or (any(wrd in ctxt.lower() for wrd in badwords)) or (ctxt[0] == '@'):  
   dftw.drop(index,axis=0,inplace=True) 


 #Get rid of tweets with too many cashtags
 for index,row in dftw.iterrows():
  txt = row['tweet']
  ctxt =  tc.p.clean(txt)
  if tc.count_cashtags(ctxt)>0:
   dftw.drop(index,axis=0,inplace=True) 

 #Get rid of tweets with zero words.
 for index,row in dftw.iterrows():
  txt = row['tweet']
  ctxt = tc.p.clean(txt)
  ctxt = tc.remove_mention(ctxt)
  ctxt = tc.remove_hashtag(ctxt)  
  ctxt = tc.remove_cashtag(ctxt)
  if len(ctxt.split())<1:   
   dftw.drop(index,axis=0,inplace=True)
   
 nrows = dftw.shape[0]
 
 dftw.reset_index(inplace=True,drop=True)

 if nrows>0:
  dftw = predict_label(dftw)

 return dftw 



#Label each tweet using trained model (inference) and identify strong sentiment tweets.
def predict_label(dftw):  

 dftw['tidy_tweet'] = dftw['tweet'].apply(lambda x : tc.p.clean(x))
 dftw['tidy_tweet'] = dftw['tidy_tweet'].apply(lambda x : tc.remove_hashtag(x))
 dftw['tidy_tweet'] = dftw['tidy_tweet'].apply(lambda x : tc.replace_tesla(x))
 dftw['tidy_tweet'] = dftw['tidy_tweet'].apply(lambda x : tc.remove_mention(x))
 dftw['tidy_tweet'] = dftw['tidy_tweet'].apply(lambda x : tc.replace_chars(x))
 dftw['tidy_tweet'] = dftw['tidy_tweet'].apply(lambda x : tc.normalize_doc(x))

 nrows = dftw.shape[0]

 load_model = pickle.load(open('save_model/bayes_count.sav','rb'))
 count_vect = pickle.load(open('save_model/count_vect.sav','rb'))

 ser = dftw['tidy_tweet']
 ser_count =  count_vect.transform(ser)
 
 predictions = load_model.predict(ser_count)
 proba = load_model.predict_proba(ser_count)

 ii=0
 kk=0
 for index,row in dftw.iterrows():
  if (proba[ii][0]>0.8 or proba[ii][1]>0.8):
   kk += 1
  else: 
   dftw.drop(index,axis=0,inplace=True) 
  ii += 1 
    
# print('\n\tii,kk = ',ii,kk)    
# print('\n\tdftw.shape = ',dftw.shape)

 return dftw
