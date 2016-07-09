import sys
from nltk import *
import codecs
reload(sys)
sys.setdefaultencoding('utf-8')
from PreProcessing import *
from nltk.tag import StanfordNERTagger
from MongoDB import getCollection

# Get the entity count for Persons in the tweet 
def getEntityCount(tweet):
    # Use the Stanford NER Tagger
    st = StanfordNERTagger('english.all.3class.distsim.crf.ser.gz') 
    # tokenize the tweet
    tokenized_text = word_tokenize(tweet)
    classified_text = st.tag(tokenized_text)
    countPerson =0
    for text in classified_text:
        if "PERSON" in text[1]:
            countPerson+=1 
    return countPerson


# get the Length of the tweet
def getLength(tweet):  
    return len(tweet)

# Set containing the List of Positive words 
listPositive = set()
# Set containing the List of Negative words 
listNegative = set()


# Get the word list for the positive and negative words
def getWordList():
    global listNegative
    global listPositive
    if len(listNegative)> 0 and len(listPositive)> 0:
        return
    # Open the Regular Lexicon
    regularLexicon = open("sentimentUnigram/RegularLexicon.txt",'r')
    for line in regularLexicon:
        tokens = line.split()
        # Get the score of word in the file
        if int(tokens[len(tokens) -1]) > 0:
            listPositive.add(" ".join(tokens[:-1]))
        else:
            listNegative.add(" ".join(tokens[:-1]))
    regularLexicon.close()

    # open Twitter Lexicon
    twitterLexicon = open("sentimentUnigram/TwitterLexicon.txt",'r')
    for line in twitterLexicon:
        tokens = line.split()
        # Get the score of word in the file
        if float(tokens[0]) > 0:
            listPositive.add(" ".join(tokens[1:]))
        else:
            listNegative.add(" ".join(tokens[1:]))
    twitterLexicon.close()

# Get the count of positive words in the tweet
def getCountPositiveWords(tweet):
    getWordList()
    tokens = word_tokenize(tweet.lower())
    count = 0
    for token in tokens:
        if token in listPositive:
            count+=1
    return count

# Get the count of negative words in the tweet
def getCountNegativeWords(tweet):
    getWordList()
    tokens = word_tokenize(tweet.lower())
    count = 0
    for token in tokens:
        if token in listNegative:
            count+=1
    return count

# Get the count of emoticons in the tweet
def getCountEmoticons(tweet):
    emoticons = [":-)",":-*",":-(",":-|"]
    tokens = tweet.split()
    count =0
    for token in tokens:
        if token in emoticons:
            count+=1
    return count
