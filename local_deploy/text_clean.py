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
remove_words = ['above', 'below', 'up',  'down', 'off',  'over',
                'under',  'few',  'more',  'most', 'own', 'against',
                'during', 'out', 'in',
                'no', 'nor', 'not', 'too', 'very']

for w in remove_words:
    stop_words.remove(w)


def normalize_doc(txt):
    txt = re.sub('[^a-zA-Z]', ' ', txt)  # Remove punctuation
    txt = txt.lower()
    tok_list = word_tokenize(txt)
    filtered_tok_list = [token for token in tok_list if token not in
                         stop_words]
    filtered_tok_list = [stemmer.stem(w) for w in filtered_tok_list]
    return ' '.join(filtered_tok_list)


# Important for tweets/posts
def clean_emoji_url(x):
    p.set_options(p.OPT.EMOJI)
    p.set_options(p.OPT.SMILEY)
    p.set_options(p.OPT.URL)
    return p.clean(x)


def remove_mention(input_txt):
    pattern = "@[\w]*"
    r = re.findall(pattern, input_txt)
    for tok in r:
        input_txt = re.sub(tok, '', input_txt)

    return input_txt


def remove_hashtag(input_txt):
    pattern = "#[\w]*"
    r = re.findall(pattern, input_txt)
    for tok in r:
        input_txt = re.sub(tok, '', input_txt)
    return input_txt


def remove_cashtag(input_txt):
    pattern = "[$][\w]*"
    r = re.findall(pattern, input_txt)
    for tok in r:
        input_txt = input_txt.replace(tok, '')

    return input_txt
