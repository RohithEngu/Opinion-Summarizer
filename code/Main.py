import sys
from nltk import *
import csv
import MongoDB
from MongoDB import *
import codecs
from Attributes import getCountNegativeWords, getCountPositiveWords,getCountEmoticons,getEntityCount
from PreProcessing import stemming, removeStopWords,process, removePersonEntity
from SentimentAnalyzer import sentimentAnalysis
from SearchApiCollectTweets import collectTweets
from sklearn import linear_model
from sklearn.cross_validation import train_test_split
from sklearn import metrics
import numpy
from OpinionSummarization import getTheRelevantTweets
reload(sys)
sys.setdefaultencoding('utf-8')


# Name of the person 
namePerson= "Barrack Obama"
# Number of tweets to collect
numberTweets=50

threshold = 0.3                                         # Percentage of tweets you want for summary
testCollection = namePerson                             # Collection name for test data of Mongo DB 
testTweetsFile = testCollection+".csv"                  # File contating the collected tweets and its attributes 
testSummaryFileName = testCollection+" Summary.txt"     # File containing the summary of the proposed system
trainingCollection = "Tweets"                           # Collection containing the Training Tweets
trainTweetsFile = "TrainingTweets.csv"                  # File containing the Training Tweets 


# Holds the list of person in Training Tweets
listPerson=["Donald Trump","Bill Gates","Katy Perry","Justin Bieber","JK Rowling","Adolf Hitler","Miley Cyrus","Charlie Sheen","Russell Crowe"]


# Get the count of Positive, Negative and emoticons in the tweet
def getCountOfPositveAndNegative(collectionName):
    collection = getCollection(collectionName)
    for document in collection.find({},no_cursor_timeout=False).batch_size(100):
        positiveCount = getCountPositiveWords(document['Tweet']) 
        negativeCount = getCountNegativeWords(document['Tweet'])
        emoticons = getCountEmoticons(document['Tweet'])
        # update the attribute in MongoDB
        collection.update_one({"_id":document['_id'] },{'$set': {'positiveNegative': positiveCount+negativeCount+emoticons}})


# Permutation of all the names in the list Person
def getEnrichedListOfPeople():
    listPeople=[]
    listPerson.append(namePerson)
    for person in listPerson:
        names=person.lower().split()
        listPeople.append("".join(names))
        for name in names:
            listPeople.append(name)
            listPeople.append(name+"'s")
    
    return listPeople


# Perform the Sentiment Analysis
def performSentimentAnalysis(collectionTraining,collectionTesting):
    # holds the tweets of the tarining data
    train =[]
    # holds the tweets of the test data 
    test=[]
    listPeople = getEnrichedListOfPeople()
    collection = getCollection(collectionTraining)
    for document in collection.find({},no_cursor_timeout=False).batch_size(100): # retrieve data in batches of 100
        tweet = document['Tweet']
        tweet = process(tweet)                                  # perform basic processing on the tweet
        tweet = removePersonEntity(tweet,listPeople)            # remove named entities 
        tweet = removeStopWords(tweet)                          # remove stop words
        tweet = stemming(tweet)                                 # perform stemming
        train.append((tweet.split(), document['Sentiment']))
    collection = getCollection(collectionTesting)
    for document in collection.find({},no_cursor_timeout=False).batch_size(100):
        tweet = document['Tweet']
        tweet = process(tweet) 
        tweet = removePersonEntity(tweet,listPeople)
        tweet = removeStopWords(tweet)
        tweet = stemming(tweet)
        test.append((tweet.split(), document['_id']))
    
    sentimentAnalysis(train,test,collectionTesting)


# Get the training tweets attributes and Relevance class label
def getTrainingDataAndClass(collectionName):
    collection = getCollection(collectionName)
    data =[]
    classLabel = []
    for document in collection.find({},no_cursor_timeout=False).batch_size(100):
        data.append((document['NEREntityCount'],document['LengthOfTweet'],document['positiveNegative']))
        classLabel.append(document['Relevance'])
    return data,classLabel

# Get the test data i.e data collected about the person you wnat to summarize
def getTestdata(collectionName):
    collection = getCollection(collectionName)
    data =[]
    documentId = []
    for document in collection.find({},no_cursor_timeout=False):
        data.append((document['NEREntityCount'],document['LengthOfTweet'],document['positiveNegative']))
        documentId.append(document['_id'])
    return data,documentId

# Perform Logistic Regression and return the labels for the test set
def logisticRegression(trainCollection,testCollection):
    logreg = linear_model.LogisticRegression()
    training = getTrainingDataAndClass(trainCollection)
    test = getTestdata(testCollection)
    accuracy_ = 0
    for i in range(0,10): 
        train,test1,trainLabel,testLabel = train_test_split(training[0],training[1],test_size=0.25)
        logreg.fit(train, trainLabel)
        y_predi_class = logreg.predict(test1)

        accuracy = metrics.accuracy_score(testLabel,y_predi_class)
        accuracy_+=accuracy

    print("Accuracy after cross validation is:"+str(accuracy_/float(10)))

    X = numpy.array(training[0])
    logreg.fit(X, training[1])
    Y = numpy.array(test[0])
    Z= logreg.predict(Y)
    dictionary = dict(zip(test[1],Z))
    return dictionary

# Insert the relevance label for the testset
def insertIntoDB(relevanceScore,collectionName):
    collection =getCollection(collectionName)
    for id,score in relevanceScore.items():
        collection.update_one({"_id":id },{'$set': {'Relevance':score}})


# Retuens the list of relevant Tweets from the Opinion Summarizer
def getRelevantTweets(collectionName,percentRelevant):
    return getTheRelevantTweets(collectionName,percentRelevant,namePerson)

# write the test set and its attributes to the output file
def writeTestSet(fileName,collectionName):
    csvfile= open(fileName, 'wb')
    collection = getCollection(collectionName)
    # Header Attributes of the CSV File, NEREntityCount is the number of entity the Stanford NER system found
    fieldnames = ['Tweet','NEREntityCount','LengthOfTweet','Sentiment','Relevance']
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    # write the header
    writer.writeheader()
    for document in collection.find({},no_cursor_timeout=False):
        writer.writerow({'Tweet':document['Tweet'], 'NEREntityCount':document['NEREntityCount'],"LengthOfTweet": document['LengthOfTweet'],"Sentiment":document['Sentiment'],"Relevance":document['Relevance']})

    csvfile.close()

# Write the Opinion Summarizer summary to the Sumamry file
def writeSummaryIntoFile(filename,relevantTweets):
    file = open (filename,'w') 
    for tweet,sentiment in relevantTweets:
        if sentiment == 0:
            file.write("\nPositive: "+str(tweet))
        else:
            file.write("\nNegative: "+str(tweet))

    file.close()



# collect the tweets for namePerson
collectTweets(testTweetsFile,namePerson,testCollection,numberTweets)

# perfom sentiment analysis
performSentimentAnalysis(trainingCollection,testCollection)

# count of positive, negative and emoticons for tarining collection
getCountOfPositveAndNegative(trainingCollection)

# count of positive, negative and emoticons for tarining collection
getCountOfPositveAndNegative(testCollection)

# perform logistic regression and get the relevence prediction
relevanceData = logisticRegression(trainingCollection,testCollection)
insertIntoDB(relevanceData,testCollection)

# retrieve relevant tweets from the tests set
relevantTweets = getRelevantTweets(testCollection,threshold)
# write summary to file
writeSummaryIntoFile(testSummaryFileName,relevantTweets)
# write test set to file
writeTestSet(testTweetsFile,testCollection)

print ("Completed Execution!")