import pandas as pd
import text_clean as tc
from sklearn.model_selection import GridSearchCV,StratifiedKFold
import numpy as np
from sklearn.feature_extraction.text import CountVectorizer
from sklearn import naive_bayes, metrics
import cvars
#import ML_methods as ML
import matplotlib.pyplot as plt
from sklearn.pipeline import Pipeline
from sklearn.feature_selection import SelectKBest,chi2


if __name__ == '__main__':
    """
     Calculate scores for differet subsets of features within CV using
     Chi2.
    """

    fname = 'train_data/all_tweets_headlines_17844.csv'

    df = pd.read_csv(fname)

    print('\n\tdf.shape = ', df.shape)

    df.dropna(axis=0, how='any', inplace=True)

    print('\n\tdf.shape = ', df.shape)

    # Non-unique indices messes up the drop indices call below.
    print('\n\tAre indices unique ? ', df.index.is_unique)

    if not df.index.is_unique:
        df.reset_index(drop=True, inplace=True)

    # print(df[df.index.duplicated(keep=False)])

    df['senti'] = df['senti'].astype('category')

    # --------Clean text-----------

    # Delete tweets with more than 10 cashtags
    cond10 = df['text'].apply(lambda x:
                              tc.count_cashtags(x) > cvars.cash_thresh)
    df.drop(index=df[cond10].index, inplace=True)
    print('\n\tdf.shape = ', df.shape)

    df['tidy_text'] = df['text'].apply(lambda x: tc.clean_emoji_url(x))
    df['tidy_text'] = df['tidy_text'].apply(lambda x: tc.remove_hashtag(x))
    df['tidy_text'] = df['tidy_text'].apply(lambda x: tc.remove_cashtag(x))
    df['tidy_text'] = df['tidy_text'].apply(lambda x: tc.remove_mention(x))
    df['tidy_text'] = df['tidy_text'].apply(lambda x: tc.replace_chars(x))
    df['tidy_text'] = df['tidy_text'].apply(lambda x: tc.normalize_doc(x))

    # Drop rows with empty tidy_text. After cleaning it is possible that all
    # the tokens in tidy_text get deleted. For example, the following tweet
    # after cleaning contains zero tokens.
    # $CUBE $EXR $HOG $KO $LSI $PSA $IRM https://t.co/GFZTPvIifx

    cond = df['tidy_text'].apply(lambda x: tc.count_toks(x) == 0)

    print('\n\tcond.shape = ', cond.shape)
    print('\n\tcond.value_counts = ', cond.value_counts())

    df.drop(index=df[cond].index, inplace=True)

    print('\n\t', df['senti'].value_counts())
    print('\n\tnrows = ', df.shape[0])

	# Extract features
    count_vect = CountVectorizer()
    count_vect.fit(df['tidy_text'])

    xtrain_count = count_vect.transform(df['tidy_text'])
	
    
    pipeline = Pipeline([('selector',SelectKBest(chi2)),('model',naive_bayes.MultinomialNB())])

	
    topn = [100, 1000, 2000, 4000, 8000, 12000]
    alpha_vals = [0.1, 0.5, 1.0, 1.25, 1.5, 1.75, 2.0, 3.0, 4.0, 5.0, 10.0, 20.0,50.0,100.0,500.0] 

    nf = len(topn)
    npar = len(alpha_vals)

    check_params = {'selector__k':topn,'model__alpha': alpha_vals}

    refit_score = 'accuracy_score'

    clf = GridSearchCV(estimator=pipeline, param_grid = check_params,\
                    refit=refit_score, \
                    cv=StratifiedKFold(shuffle=True,n_splits=5), \
                    return_train_score=True)

    clf.fit(xtrain_count, df['senti'])


    res = pd.DataFrame(clf.cv_results_)
    res_acc = res[["param_model__alpha","param_selector__k","mean_test_score","mean_train_score"]]
    arr = res_acc[["mean_test_score","mean_train_score"]].to_numpy()

	
    acc2d = np.empty([nf,npar,2])

    l = len(arr[:,0])

    for i in range(nf):
     acc2d[i,:,0:2] = arr[i:l:nf,0:2]
    
    print('\nnf, npar = ',nf, npar)    
    
    traincl = ['y','c','b','g','r','k']

    hd=[]

    plt.figure(1)
    plt.style.use('fivethirtyeight')
    for i in np.arange(nf):
     h1,=plt.plot(alpha_vals,acc2d[i,:,1], color=traincl[i], lw=1.5); hd.append(h1)
     plt.plot(alpha_vals,acc2d[i,:,0], color=traincl[i],linestyle='--',lw=1.5)
    plt.legend(hd,topn,fontsize=15,bbox_to_anchor=(0.95,1.0))
    plt.grid(True); plt.xticks(fontsize=15); plt.yticks(fontsize=15); plt.ylim([0.5,0.8])
    plt.title('Accuracy (Chi2 : inCV feature selection)',fontsize=15)
    plt.xlabel('Laplace smoothing parameter',fontsize=15)    
    #plt.savefig('figs/chi2_featureselect_laplace.png', bbox_inches = 'tight')


    plt.figure(2)
    plt.style.use('fivethirtyeight')
    for i in np.arange(nf):
     h1,=plt.plot(alpha_vals[0:8],acc2d[i,0:8,1], color=traincl[i], lw=1.5); hd.append(h1)
     plt.plot(alpha_vals[0:8],acc2d[i,0:8,0], color=traincl[i],linestyle='--',lw=1.5)
    plt.legend(hd,topn,fontsize=15,bbox_to_anchor=(0.95,1.0))
    plt.grid(True); plt.xticks(fontsize=15); plt.yticks(fontsize=15); plt.ylim([0.5,0.8])
    plt.title('Accuracy (Chi2 : inCV feature selection)',fontsize=15)
    plt.xlabel('Laplace smoothing parameter',fontsize=15)   
    #plt.savefig('figs/chi2_featureselect_laplace_few.png', bbox_inches = 'tight')

    plt.show()
