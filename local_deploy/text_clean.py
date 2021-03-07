"""Functions to clean and normalize text.

   Remove irrelevant text. Eg. For tweets mentions,hashtags
   cashtags, embedded graphs/smileys are noise and should be
   removed before performing feature extraction using BOW
   or tf-idf,etc. These functions can be used for text including
   newspaper headlines which usually do not contain mentions,
   cashtags etc.
"""

import re
from nltk.stem.porter import PorterStemmer
from nltk.stem import WordNetLemmatizer
import nltk
from nltk.tokenize import word_tokenize
import preprocessor as p

nltk.download('stopwords')

lemmatizer = WordNetLemmatizer()
stemmer = PorterStemmer()

stop_words = nltk.corpus.stopwords.words('english')

# these words should not be part of stop_words since these are relevant
# for stocks.
remove_words = ['above', 'below', 'up',  'down', 'off',  'over', 'under']
more_stop_words = ['would', 'get', 'also']


for w in remove_words:
    stop_words.remove(w)

for w in more_stop_words:
    stop_words.append(w)

p.set_options(p.OPT.EMOJI, p.OPT.SMILEY,  p.OPT.URL)


def clean_emoji_url(x):
    """Remove emoji, smileys and urls."""

    return p.clean(x)


def remove_mention(input_txt):
    """Remove @tokens."""

    return re.sub("@[\w]*", '', input_txt)


def remove_hashtag(input_txt):
    """Remove #tokens."""

    return re.sub("#[\w]*", '', input_txt)


def remove_cashtag(input_txt):
    """Remove $tokens."""

    return re.sub("[$][\w]*", '', input_txt)


def count_cashtags(input_txt):
    """Count cashtags which are not ($TSLA, $TSLAQ) """

    ff = re.findall('[$][a-zA-Z]+', input_txt)

    return len([tk for tk in ff if tk.lower() not in ['$tsla', '$tslaq']])


def replace_chars(input_txt):
    """Replace &amp and embedded pictures/graphs."""

    input_txt = input_txt.replace("&amp", " and ")

    input_txt = input_txt.replace('\U0001f4c8', " ")

    return input_txt


def normalize_doc(txt):
    """Remove everything except text.

    Stop words are removed.
    All punctuation is removed.
    """

    txt = re.sub('[^a-zA-Z]', ' ', txt)
    txt = txt.lower()
    tok_list = word_tokenize(txt)
    filtered_tok_list = [token for token in tok_list if token not in
                         stop_words]
    filtered_tok_list = [stemmer.stem(w) for w in filtered_tok_list]
    return ' '.join(filtered_tok_list)


def count_toks(txt):
    """Return number of words."""

    return len(word_tokenize(txt))
