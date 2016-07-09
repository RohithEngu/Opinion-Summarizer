import sys
import pymongo
from pymongo import MongoClient

# client connection to MongoDB
client = ""

# Connect to MongoDB
def getConnection():
    global client
    try:
        if client == "":
         client = MongoClient()
    except:
        print ("ERROR: Connection to MongoDb Failed")
        sys.exit()

  
# Get the Database "OpinionSummarizer". Exit the system if there is an error
def getDatabase():   
    db = ""
    try:
        # get connection before connecting to database
        getConnection()
        db = client.OpinionSummarizer
    except:
        print ("ERROR: Connection to Database "+ dbName+ "Failed")
        sys.exit()
    return db

# Get the collection in the database
def getCollection(collectionName):   
    coll = ""
    try:
        # get the database first and then the collection
        coll = getDatabase()[collectionName]
    except:
        print ("ERROR: Connection to Collection "+ collectionName+ "Failed")
        sys.exit()
    return coll

# Close the MongoDB client
def closeConnection():
    try:
      if client != "":
         client.close()
         client = ""
    except:
        print ("WARNING: Unable to close MongoConnection")
