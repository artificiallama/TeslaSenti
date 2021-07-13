import pandas as pd
import text_clean as tc
from sklearn import model_selection
import numpy as np
from sklearn.feature_extraction.text import CountVectorizer
from sklearn import naive_bayes, metrics
import pickle
import cvars
import ML_methods as ML
import matplotlib.pyplot as plt

if __name__ == '__main__':
    """Train a classifier to label tweets with sentiments.

    The labelled tweets are first cleaned, then features
    are extracted using BOW and then a naive Bayes model
    is fit. The best value of Laplace smoothing parameter
    is identified using grid search. The best model is saved.
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

    x_train, x_test, y_train, y_test = model_selection.train_test_split(
                       df['tidy_text'], df['senti'], test_size=0.33,
                       random_state=123, stratify=df['senti'])

    print('\n\tshape = ', np.shape(x_train), np.shape(x_test))
    print('\tshape = ', np.shape(y_train), np.shape(y_test))

    # print('\n\t', x_train.iloc[0], y_train.iloc[0])
    # print('\n\t', x_test.iloc[3], y_test.iloc[3])

    # Extract features
    count_vect = CountVectorizer()
    count_vect.fit(x_train)

    xtrain_count = count_vect.transform(x_train)
    xtest_count = count_vect.transform(x_test)

    check_params = {'alpha': [0.1, 0.5, 1.0, 3.0, 5.0,
                              10.0, 50.0, 1e2, 1e3, 1e4]}

    refit_score = 'accuracy_score'

    # Identify best value of alpha
    bestmodel, res = ML.grid_search_wrapper(naive_bayes.MultinomialNB(),
                                            xtrain_count, y_train,
                                            check_params, refit_score)

    print(res[['mean_test_score', 'mean_train_score', 'std_test_score',
               'std_train_score']])

    predictions = bestmodel.predict(xtrain_count)
    print('\n\tTrain accuracy = ', metrics.accuracy_score(y_train,
                                                          predictions))

    predictions = bestmodel.predict(xtest_count)
    print('\tTest  accuracy = ', metrics.accuracy_score(y_test, predictions))

    # print('\nConfusion matrix = ', metrics.confusion_matrix(y_test,
    #                                                        predictions))

    print('\n\tClassification report = \n')
    print(metrics.classification_report(y_test, predictions))


    arr = list(*check_params.values())

    hd = []
    plt.figure(1)
    h1,=plt.plot(arr, res[['mean_train_score']], 'b-o'); hd.append(h1)
    h1,=plt.plot(arr, res[['mean_test_score']],  'r-o'); hd.append(h1)
    plt.legend(hd,['train','test'],fontsize=15)
    plt.grid(True)
    plt.title('Mean accuracy K-fold crossvalidation',fontsize=15)
    plt.xlabel('Laplace smoothing parameter')
    #plt.savefig('figs/CV_accuracy_laplace.png', bbox_inches = 'tight')

    hd=[]
    plt.figure(2)
    h1,=plt.plot(arr[0:6], res.loc['0':'5','mean_test_score'],  'r-o');
    hd.append(h1)
    h1,=plt.plot(arr[0:6], res.loc['0':'5','mean_train_score'], 'b-o');
    hd.append(h1)
    plt.legend(hd,['train','test'],fontsize=15)
    plt.xlabel('Laplace smoothing parameter')
    plt.title('Mean accuracy K-fold crossvalidation (only showing alpha<=10)')
    plt.grid(True)
    #plt.savefig('figs/CV_accuracy_laplace_10.png', bbox_inches = 'tight')
    plt.show()


    with open('save_model/bayes_fit.pkl', 'wb') as fout:
        pickle.dump((count_vect, bestmodel), fout)

    print('')
