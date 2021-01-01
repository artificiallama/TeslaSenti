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
more_stop_words = ['would','get','also']


for w in remove_words:
    stop_words.remove(w)

for w in more_stop_words:
 stop_words.append(w)	

p.set_options(p.OPT.EMOJI, p.OPT.SMILEY,  p.OPT.URL)


# Important for tweets/posts
def clean_emoji_url(x):
    return p.clean(x)


def remove_mention(input_txt):
    return re.sub("@[\w]*", '', input_txt)


def remove_hashtag(input_txt):
    return re.sub("#[\w]*", '', input_txt)


def remove_cashtag(input_txt):
    return re.sub("[$][\w]*", '', input_txt)


# Count cashtags which are not ($TSLA, $TSLAQ)
def count_cashtags(input_txt):
    ff = re.findall('[$][a-zA-Z]+', input_txt)
    return len([tk for tk in ff if tk.lower() not in ['$tsla', '$tslaq']])


def replace_chars(input_txt):
    input_txt = input_txt.replace("&amp", " and ")
# Replace embedded pictures/graphs in tweets
    input_txt = input_txt.replace('\U0001f4c8', " ")
    return input_txt


def normalize_doc(txt):
    txt = re.sub('[^a-zA-Z]', ' ', txt)  # Remove everything except text.
    txt = txt.lower()
    tok_list = word_tokenize(txt)
    filtered_tok_list = [token for token in tok_list if token not in
                         stop_words]
    filtered_tok_list = [stemmer.stem(w) for w in filtered_tok_list]
    return ' '.join(filtered_tok_list)


def count_toks(txt):
    return len(word_tokenize(txt))
