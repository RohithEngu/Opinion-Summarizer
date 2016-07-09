# coding: utf-8 
import sys
import codecs
import re 
import nltk
from nltk.stem import wordnet
from nltk.stem.wordnet import WordNetLemmatizer
from nltk.stem.snowball import EnglishStemmer
from nltk.corpus import stopwords
reload(sys)
sys.setdefaultencoding('utf-8')

# removing URL's from the tweet
def removeHttps(tweet):
   tweet = re.sub(r"http\S+",'',tweet)
   tweet = re.sub(r"https\S+",'',tweet)
   return tweet

# word Stemming using EnglishStemmer
def stemming(tweet):
    tweets = tweet.split()
    wrdStemmer = EnglishStemmer()
    stemTweet =[]
    try:
        for tweet in tweets:
            tweet = wrdStemmer.stem(tweet)
            stemTweet.append(tweet)
    except:
        print("Error: Stemming")
    return " ".join(stemTweet)

# Pre processing : case folding ,numeric numbers removal and RT removal
def process(tweet):
    #Convert to lower case
    tweet = tweet.lower()
    #Convert @username to ''
    tweet = re.sub('@[^\s]+','',tweet)
    #remove everythong except '
    tweet = re.sub("[^\w']",' ',tweet)

    #remove rt from tweet
    tweet =re.sub("^(rt)",'',tweet)

    #Remove additional white spaces
    tweet = re.sub('[\s]+', ' ', tweet)
    #remove number
    tweet = re.sub(r'([0-9]*)',"",tweet)
    #trim
    tweet = tweet.strip('\'"')

    tweet = tweet.strip()

    return tweet

# removing stop words
def removeStopWords(tweet):
     stopwords_ = stopwords.words('english')
     stopwords_.remove("not")
     tweet = ' '.join([word for word in tweet.lower().split() if word not in stopwords_])
     return tweet

# removing person entity 
def removePersonEntity(tweet,listPerson):
    tweet=tweet.split()
    tweetEnriched =[]
    for token in tweet:
        if token not in listPerson:
            tweetEnriched.append(token)
    return " ".join(tweetEnriched)

# remove a particular person form tweet
def removePerson(tweet,personName):
    persons = personName.lower().split()
    listPerson=[]
    listPerson.append("".join(persons))
    for person in persons:
        name = person.lower()
        listPerson.append(person)
        listPerson.append(person+"'s")
    return removePersonEntity(tweet.lower(),listPerson)

# case folding
def lowerCaseFolding(tweet):
    return tweet.lower()

def upperCaseFolding(tweet):
    return tweet.upper()
