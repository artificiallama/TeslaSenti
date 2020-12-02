import pandas as pd
import text_clean as tc
from sklearn import model_selection
import numpy as np
from sklearn.feature_extraction.text import CountVectorizer
from sklearn import naive_bayes,metrics
import pickle

if __name__=='__main__':

 fname = 'train_data/all_tweets_headlines_11844_stocktwit_balance.csv'  

 df = pd.read_csv(fname)

 print('\n\tdf.shape = ',df.shape)

# print(df.head())

 df = df.sample(frac=1,random_state=333)

# print(df.head())

 print('',df['senti'].value_counts())
 nrows = df.shape[0]
 print('\nnrows = ',nrows)

 #Clean text
 df['tidy_text'] = df['text'].apply(lambda x : tc.clean_emoji_url(x))
 df['tidy_text'] = df['tidy_text'].apply(lambda x : tc.remove_hashtag(x))
 df['tidy_text'] = df['tidy_text'].apply(lambda x : tc.remove_cashtag(x))
 df['tidy_text'] = df['tidy_text'].apply(lambda x : tc.remove_mention(x))
 df['tidy_text'] = df['tidy_text'].apply(lambda x : tc.normalize_doc(x))

# print(df.head())
 print('')
 x_train, x_test, y_train, y_test = model_selection.train_test_split(df['tidy_text'], \
                                    df['senti'],test_size=0.2,random_state=123,stratify=df['senti'])

 #print('\n',isinstance(train_x,list))
 print('\nshape = ',np.shape(x_train),np.shape(x_test))
 print('shape = ',np.shape(y_train),np.shape(y_test))

 print('\n',x_train.iloc[0],y_train.iloc[0])
 print('\n',x_test.iloc[3],y_test.iloc[3])

 count_vect = CountVectorizer(analyzer='word', token_pattern=r'\w{1,}')
 count_vect.fit(x_train)

 xtrain_count =  count_vect.transform(x_train)
 xtest_count  =  count_vect.transform(x_test)

 
 model = naive_bayes.MultinomialNB() 
 model.fit(xtrain_count, y_train)

 predictions = model.predict(xtrain_count)
 print('\nTrain accuracy = ',metrics.accuracy_score(y_train, predictions))
 
 predictions = model.predict(xtest_count)
 print('Test  accuracy = ',metrics.accuracy_score(y_test, predictions))

 with open('save_model/bayes_fit.pkl', 'wb') as fout:
  pickle.dump((count_vect,model), fout)

 print('') 
