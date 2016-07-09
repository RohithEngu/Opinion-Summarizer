from nltk import *
from nltk.stem.snowball import EnglishStemmer
from nltk.corpus import stopwords
import random
from random import shuffle, sample
import numpy
import nltk.classify
import sklearn
from sklearn import svm
from sklearn.svm import SVC
from MongoDB import getCollection


#holds the data from the training file
train=[]
test =[]
#classlabel=[]
word_features=[]


#get all the words in the training data
def get_words_in_training(train):
    all_words = []
    for (words, sentiment) in train:
        all_words += words
    return all_words

#get the most common 1000 words
def get_word_features(wordlist):
    wordlist = FreqDist(wordlist)
    word_features = [w for (w, c) in wordlist.most_common(1000) if len(w)>2] #remove words whose length is less than 2
    #print word_features
    print("Total word features: "+str(len(word_features)))
    return word_features

#extract the features for the tweet
def extract_features(document):
    document_words = set(document)
    features = {}
    for word in word_features:
        features['contains(%s)' % word] = (word in document_words)
    return features

# method creates and builds classifiers
def trainClassifier():
     training_set = [(extract_features(d), c) for (d,c) in train]
     
     classifierNaive = NaiveBayesClassifier.train(training_set)

     classifierSVM = nltk.classify.SklearnClassifier(SVC(kernel='linear')).train(training_set)

     clasifierMaxEntropy=nltk.classify.MaxentClassifier.train(training_set, max_iter=10)

     #classifierSVM_ = nltk.classify.SklearnClassifier(SVC(kernel='poly')).train(training_set)

     del training_set[:]
     return classifierNaive,classifierSVM,clasifierMaxEntropy#,classifierSVM_


#perform cross validation by spliiting training set into training and test set
#based on number of folds for ex: for data 1,2,...20 and numFolds=10
# 1st split: 1,2 ->test_set and 3,4...20->training_set
# 2nd split: 3,4 ->test_set and 1,2,5,6...20->training_set.

def crossvalidation(num_folds,classifiers):
    subset_size = len(train)/num_folds
    accuracy = 0
    accuracy_1 = 0
    accuracy_2 = 0
    #accuracy_3 = 0

    classifierNaive =classifiers[0]
    classifierSVM = classifiers[1]
    clasifierMaxEntropy = classifiers[2]
    #classifierSVM_=classifiers[3]

    for i in range(num_folds):
        print 
        print("Cross Validation #"+str(i))
        #get the training set
        training_set = [(extract_features(d), c) for (d,c) in train[:i*subset_size] + train[i*subset_size+subset_size:]]

        #get the test set
        test_set=[(extract_features(d), c) for (d,c) in train[i*subset_size:i*subset_size+subset_size]]
        
        #Naive Bayes Classifier
        classifierNaive = NaiveBayesClassifier.train(training_set)

        accuracy_=classify.accuracy(classifierNaive, test_set)
        print ("Naive Bayes Accuracy: "+str(classify.accuracy(classifierNaive, test_set)))

        accuracy +=accuracy_
        
        classifierSVM.train(training_set)
        accuracy_1+=classify.accuracy(classifierSVM, test_set)
        print ("SVM Accuracy: "+str(classify.accuracy(classifierSVM, test_set)))


        clasifierMaxEntropy.train(training_set,  max_iter=10, trace=0)
        accuracy_2+=classify.accuracy(clasifierMaxEntropy, test_set)
        print ("MaxEntropy Accuracy: "+str(classify.accuracy(clasifierMaxEntropy, test_set)))

        #classifierSVM_.train(training_set)
        #accuracy_3+=classify.accuracy(classifierSVM_, test_set)
        #print ("SVM_ Accuracy: "+str(classify.accuracy(classifierSVM_, test_set)))

        #classifierDT = nltk.classify.DecisionTreeClassifier.train(training_set, entropy_cutoff=0,support_cutoff=0)
        #print ("DT Accuracy: "+str(classify.accuracy(classifierDT, test_set)))

        del training_set[:]
        del test_set[:]       

    print ("Accuracy of Naive Bayes: "+str(accuracy/num_folds))
    print ("Accuracy of SVC Linear: "+str(accuracy_1/num_folds))
    print ("Accuracy of Maximum Entropy: "+str(accuracy_2/num_folds))
    #print (str(accuracy_3/num_folds))

# method to predict the class label by taking votes
def pefromVotingAndLabelOnTest(classifiers,collectionName):
    #classify the data in the test Instance
    collection = getCollection(collectionName)
    for tweet,documentId in test:
        countPositive = 0
        countNegative = 0
        #print tweet
        for classifier in classifiers:
            sentiment = classifier.classify(extract_features(tweet))
            #print (str(sentiment))
            if sentiment == 0:
                countPositive+=1
            else:
                countNegative+=1

        if countNegative > countPositive:
           collection.update_one({"_id":documentId },{'$set': {'Sentiment': 1}})
        else:
           collection.update_one({"_id":documentId },{'$set': {'Sentiment': 0}})

# Main method to perform sentiment analysis
def sentimentAnalysis(training,testing,collectionName):
    global train
    global test
    global word_features
    #global classlabel
    train = training
    test = testing
    #classlabel =label

    all_words = get_words_in_training(train)
    word_features = get_word_features(all_words)
    del all_words[:]
    #number of folds for crosss validation
    num_folds = 10
    #Randomize the list of training data
    train=random.sample(train, len(train))  

    classifiers = trainClassifier()
    #crossvalidation(num_folds,classifiers)
    pefromVotingAndLabelOnTest(classifiers,collectionName)

    del train[:]
    del test[:]
    del word_features[:]
