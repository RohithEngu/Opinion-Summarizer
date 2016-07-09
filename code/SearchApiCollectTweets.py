# coding: utf-8 
import sys
from TwitterSearch import *
import MongoDB
from MongoDB import *
from Attributes import *
from PreProcessing import *
import csv
import codecs
reload(sys)
sys.setdefaultencoding('utf-8')


# holds number of tweets found
count = 0
setTweets=set()

# writing header of csv file with various columns
def writeHeader(csvfile,header):
     # Header Attributes of the CSV File, NEREntityCount is the number of entity the NER system found
    fieldnames = ['Person', 'Tweet','NEREntityCount','LengthOfTweet']
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    if not header:
        writer.writeheader()
    return writer

# inserting the collected tweet to DB.
def insertIntoDB(collectionName,tweet,writer,person):
    global count
    global setTweets
    processedTweet = process(tweet)

    training = getCollection(collectionName)
    if processedTweet in setTweets:
        return

    setTweets.add(processedTweet)
    print tweet
    numberOfEntity = getEntityCount(tweet)
    lengthOfTweet = getLength(tweet)
    count+=1
	# Save the tweet in MongoDB
    training.save({"Person":person,"Tweet":tweet,"NEREntityCount":numberOfEntity,"LengthOfTweet":lengthOfTweet})
    # Write in CSV file   
    writer.writerow({'Person':person,'Tweet': tweet, 'NEREntityCount':str(numberOfEntity),"LengthOfTweet":lengthOfTweet})
   
# method for collecting and writing tweets to csv file.
def collectTweets(file,keywords,collection,numTweets):
    header = False
    if os.path.exists(file):
        header = True

    #open a csv file for writing
    if "Test" in file:
        csvfile= open(file, 'wb')
    else:
        csvfile= open(file, 'ab')

    writer = writeHeader(csvfile,header)
    names = keywords.split()
    entity =[]
    for keyowrd in names:
        entity.append(keyowrd.lower())    
    try:
        tso = TwitterSearchOrder() # create a TwitterSearchOrder object
        tso.set_keywords(entity)
        tso.set_language('en') 
        tso.set_include_entities(False) # don't give all the entity information

        # create a TwitterSearch object with our secret tokens
        ts = TwitterSearch(
            consumer_key = 'Hvq33CfuafOFrbDJOrSAKNkLg',
            consumer_secret = '3u37qtXeNQF60C0npQeG4rMeZOCFPlmRwHn97akWFVdk6sabBJ',
            access_token = '33020840-hDoKHyIfU4PobFpZifignmJHOXZoY22FxBOG95swf',
            access_token_secret = 'smjekhIny8IePpvC1ZQoDp9Bh20lOgeMie255BHy1kxI5'
         )
        global count 
        for tweet in ts.search_tweets_iterable(tso):
            tweetText = tweet['text']
            tweetText = removeHttps(tweetText.encode('ascii','ignore'))
            insertIntoDB(collection,tweetText,writer,keywords)
            if count == numTweets:
                break;
    
        print("Total tweets collected for "+keywords+ " are "+ str(count))
    except TwitterSearchException as e: # handle errors if there are some
        print(e)

    finally:
        csvfile.close()