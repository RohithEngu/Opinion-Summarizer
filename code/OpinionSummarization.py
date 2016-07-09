from MongoDB import getCollection
from PreProcessing import *
import operator

# dictionary contating global word probability distribution of entire input
probWords = {}

# list containing the threshold of relevant tweets
listRelevantTweet=[]

# Calcuate the initial Sum Basic score
def calculateSumBasic(collectionName,personName):
    collection = getCollection(collectionName)
   
    dictWords = {}            # dictionary to hold thw word counts
    listSentiment0 =[]        # list conatting the positive sentiment tweets with relevance 1
    listSentiment1 =[]        # list conatting the negative sentiment tweets with relevance 1
    global probWords
    tweets = []
    for document in collection.find({},no_cursor_timeout=False).batch_size(100):
        tweet = document['Tweet']
        tweet = process(tweet)                      # basic processing of tweet
        tweet = removePerson(tweet,personName)      # remove the person name from tweet
        tweet = stemming(tweet)                     # stem the tweet
        tweet = removeStopWords(tweet)              # remove stop words
        # eliminate the tweet with length less than 2
        if len(tweet) < 2:
            continue
        tweets.append((document['_id'],tweet,document['Sentiment'],document['Relevance']))
        tweetWords = tweet.split()
        # count the frequency of words in the tweet
        for word in tweetWords:
            if dictWords.has_key(word):
                value = dictWords[word]
                dictWords[word] = value + 1
            else:
                dictWords[word] = 1

    totalWordsCount = len(dictWords)  # total number of words in input set

    # get the probability distribution of every word in input
    for key in dictWords.keys():
         probWords[key] = dictWords[key]/float(totalWordsCount)

    # Calculate the sumbasic score and upadte in DB
    for id,tweet,sentiment,relevance in tweets:
        tweetWords = tweet.split()
        numberOfWordsinTweet= len(tweetWords)
        probability = 0
        for word in tweetWords:
            count = tweetWords.count(word)
            probability += (probWords[word]/float(count))
        
        prob = probability
        collection.update_one({"_id":id},{'$set': {'sumBasic': prob}})
        if sentiment == 0 and relevance == 1:
            listSentiment0.append((id,tweet,prob))
        elif sentiment == 1 and relevance == 1: 
            listSentiment1.append((id,tweet,prob))


    del tweets[:]   # free the list of tweetss
    return listSentiment0,listSentiment1


# Update the word probbaility of words in tweet and return the updated dictionary
def fixWordProbability(sorted_probability,tweet):
    for word in tweet.split():
        sorted_probability[word] *= sorted_probability[word]
    return sorted_probability


# Fix the sentence sum basic score for tweets
def fixSentenceProbability(listTweet,sorted_probability):
    newProbList = []
    for id,tweet,probability in listTweet:
        tweetWords = tweet.split()
        probability = 0
        for word in tweetWords:
            count = tweetWords.count(word)
            probability += (sorted_probability[word]/float(count))
        
        prob = probability
        newProbList.append((id,tweet,prob))

    return newProbList

          

# Retrieve the relevant tweets from the list of tweets
def getRelevantPositiveTweets(collectionName,listTweet,countTweets):
    global listRelevantTweet
    global probWords
    collection =getCollection(collectionName)
    sorted_probability = probWords
    wordPresent = True      # bool to check if the word is present in the list of tweets or not
    word = ""
    while(countTweets > 0):
          #sort the list of Tweets based on sentence score
          sortedList = sorted(listTweet,key=lambda x: x[2], reverse=True)
          if not wordPresent:
              sorted_probability[word] *= sorted_probability[word]  # fix the probability of word if none of the tweets contains it
              if sorted_probability[word] <= 0 :   # delete the word if the probabilty of it becomes zero
                  del sorted_probability[word]

          if not sorted_probability:        # return if all the words in the dictionary are deleted beacuse of 0 probability
              return  

          # sort the probabilities and return the highest probability word
          word = (sorted(sorted_probability.items(), key=operator.itemgetter(1),reverse = True))[0][0]
          wordPresent = False
          for id,tweet,probability in sortedList:
              if word in tweet.split():
                  docs = collection.find({"_id":id})
                  for doc in docs:
                    listRelevantTweet.append((doc['Tweet'],doc['Sentiment']))       # Append the relevant tweet to the list
                    break
                  sorted_probability = fixWordProbability(sorted_probability,tweet) # Fix the word probabilities
                  listTweet.remove((id,tweet,probability))                          # Remove that tweet form list of Tweets
                  listTweet = fixSentenceProbability(listTweet,sorted_probability)  # Fix the sentence probability of all the other tweets
                  countTweets-=1
                  wordPresent =True
                  break

# Fetch all teh relevant Tweets having relevance as 1
def fetchAllTheRelevant(collectionName):
    listRelevance = []
    collection = getCollection(collectionName)
    for document in collection.find({'Relevance':1},no_cursor_timeout=False):
        listRelevance.append((document['Tweet'],document['Sentiment'])) 
    return listRelevance


# Get the relevat tweets based on the percentage    
def getTheRelevantTweets(collectionName,percentage,personName):
    global listRelevantTweet
    collection = getCollection(collectionName)
    totalTweets = collection.find({}).count()                                   # Total number of Tweets collected for personName
    totalRelevant1 = collection.find({'Relevance':1}).count()                   # Number of relevant tweets
    totalPositive = collection.find({'Relevance':1,'Sentiment':0}).count()      # Number of positive tweets which are relevant
    totalNegative = collection.find({'Relevance':1,'Sentiment':1}).count()      # Number of negative tweets which are relevant

    print("Relevance 1 Sentiment 0",str(totalPositive))
    print("Relevance 1 Sentiment 1",str(totalNegative))

    totalTwetsToFind = int(percentage*totalTweets)      # total number of tweets to find for summarization                            

    # If the number of relevant tweets are less than the percentage of tweets to find return all the relevant tweets 
    if totalRelevant1 <= totalTwetsToFind:
        print("Relevant Tweets are less than the percentage of Tweets to find")
        return fetchAllTheRelevant(collectionName)


    ratioPositiveNegative = totalPositive/totalNegative     # ratio of positive to negative tweets
    print ("Total tweets to find:",str(totalTwetsToFind))   

    postiveToFind = int((ratioPositiveNegative*totalTwetsToFind)/float(ratioPositiveNegative+1))    # Number of positive tweets to find
    negativeToFind = int(totalTwetsToFind-postiveToFind)                                            # Number of negative tweets to find

    print("Positive to find:",str(postiveToFind))
    print("Negative to find:",str(negativeToFind))

    listTweets = calculateSumBasic(collectionName,personName)   # call to calculate initial sumbasic score

    # get the relevant positive and negative tweets
    for listTweet in listTweets:
        getRelevantPositiveTweets(collectionName,listTweet,postiveToFind)
        postiveToFind = negativeToFind


    print ("Number of tweets Found:"+str(len(listRelevantTweet)))

    return listRelevantTweet
            