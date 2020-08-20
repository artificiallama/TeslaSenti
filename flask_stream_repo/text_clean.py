import re
from nltk.stem.porter import PorterStemmer
from nltk.stem import WordNetLemmatizer
import nltk
from nltk.tokenize import word_tokenize
import preprocessor as p

#nltk.download()

lemmatizer = WordNetLemmatizer()
stemmer = PorterStemmer()

stop_words = nltk.corpus.stopwords.words('english')

#print(stop_words)

remove_words = ['above','below','up', 'down','off', 'over', 'under', 'few', 'more', 
                'most','own','against','during','out','in','no','nor','not','too','very']
for w in remove_words:
 stop_words.remove(w)

#print('\n',stop_words)

def normalize_doc(txt):
 txt = re.sub('[^a-zA-Z]', ' ',txt)  #Remove punctuation
 txt = txt.lower()
 tok_list = word_tokenize(txt)
 filtered_tok_list = [token for token in tok_list if token not in stop_words]  
 filtered_tok_list = [stemmer.stem(w) for w in filtered_tok_list]   
# return filtered_tok_list
 return ' '.join(filtered_tok_list)

#-----------------Important for tweets/posts
p.set_options(p.OPT.EMOJI)
p.set_options(p.OPT.SMILEY)
p.set_options(p.OPT.URL)

#Remove "dollar amounts" ie.e remove pattern $dddd
#Eg. input = Do $you agree $5.5 with @Tesla $NKLA solar $3000-$400 powered $TSLA  $200...'
#    output= Do $you agree .5 with @Tesla $NKLA solar - powered $TSLA  ...
def remove_dollar(input_txt):
 r = re.findall(r'[$][\d]*',input_txt)
 #eg. r = ['$', '$5', '$', '$3000', '$400', '$', '$200'] 
 for tok in r:
  if len(tok)>1:
   input_txt = input_txt.replace(tok, '')     
 return input_txt

#Count cashtags which are not one of those below
#eg. @GerberKawasaki @elonmusk Is morning star valuation of $731 for $TSLA right? What about $TTD, $ROKU ?
#kk = 2
def count_cashtags(input_txt):
 ff = re.findall(r'[$][a-zA-Z]*',input_txt)
 kk=0
 for tok in ff:
  #print(tok.lower())   
  if len(tok)>1 and tok.lower() not in ('$tsla','$tslaq','$googl','$goog','aapl'):
   kk += 1  
 return kk
   
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

def replace_chars(input_txt):
 input_txt = input_txt.replace("|"," ")   
 input_txt = input_txt.replace("#"," ")     
 input_txt = input_txt.replace("$"," ")  
 input_txt = input_txt.replace("\""," ")  
 input_txt = input_txt.replace("&amp"," and ") 
 input_txt = input_txt.replace('\U0001f4c8'," ")   #Replace embedded pictures/graphs in tweets
 #input_txt = input_txt.replace('\U0001f6a8'," ")
 return input_txt   

#anonymize tokens related to tesla
def replace_tesla(input_txt):
 input_txt = input_txt.replace("tesla","THECOMP")
 input_txt = input_txt.replace("$tsla","THECOMP")
 input_txt = input_txt.replace("@tesla","THECOMP")
 input_txt = input_txt.replace("@elonmusk","THEGUY")
 input_txt = input_txt.replace("$tslaq","THECOMPQ")   
 return input_txt
