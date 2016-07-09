##################################
REQUIRED SOFTWARES
#################################

Download MongoDB (3.0.X) :
		https://www.mongodb.org/dr/fastdl.mongodb.org/win32/mongodb-win32-i386-3.0.11-signed.msi/download
(Optional) Download RoboMongo (for DB UI):
		https://robomongo.org/download
Download Stanford NER Package:
		http://nlp.stanford.edu/software/stanford-ner-2015-04-20.zip
Add Environment Variables (System Variables) for the Stanford packages as:
		CLASSPATH : 
			A:\College\Softwares\stanford-ner-2015-04-20\stanford-ner-2015-04-20\stanford-ner.jar
			A:\College\Softwares\stanford-ner-2015-04-20\stanford-ner-2015-04-20\lib\
		PATH :      
			A:\College\Softwares\stanford-ner-2015-04-20\stanford-ner-2015-04-20\lib\
		STANFORD_MODELS: 
			A:\College\Softwares\stanford-ner-2015-04-20\stanford-ner-2015-04-20\classifiers\


##################################
FILES
#################################

Training file: TrainingTweets.csv

For each of the new person when you will run the system, 2 files will be generated:
	1. PersonName.csv - Contains the tweets and the attributes 
	2. PersonName Sumamry.txt - COnatins the summary prodiced by the proposed system

Go to "Results" directory you will see directory of all the people we have analyzed.
For the readibilty we have created a PersonName.xlsx file for each of the person we have analyzed the system on. It contains 3 wordbooks:
	1. PersonName - Conatins tweets and attributes
	2. Manual Summary - Conatins Manual summary and statistics like precision, recall
	3. Summarizer Summary - Conatins the summary of the summarizer


##################################
SETUP
##################################

Note: You will need MongoDB system running to execute code.

A) Running MongoDB Server
	1. Open the command prompt and go the directory where Mongo DB is installed:
		cd "..\..\Program Files\MongoDB\Server\3.0\bin"

	2. create a new data directory in any other directory except C:\\ drive and name it "MongoData"
	
	3. Now run the command:
		mongod.exe --dbpath=H:\MongoData

   You should be able to see the "[initandlisten] waiting for connections on port 27017".


B) Unzip the Project.zip file 


C) Import the TrainingTweets.csv into MongoDB
	1. Open the command prompt and go the directory where Mongo DB is installed:
		cd "..\..\Program Files\MongoDB\Server\3.0\bin"
	2. Execute the command below:
		mongoimport --db OpinionSummarizer --type csv --collection Tweets --headerline --file "PATH TO FILE TrainingTweets.csv"
	
   You should be able to see :
	 connected to: localhost
	 imported 1114 documents

Your setup is complete.

##################################
HOW TO USE THE SYSTEM
##################################

A) In order to use the system go the "code" directory inside the unzipped project.

B) In the python File "Main.py" you will see 2 variables like below. 
   1. namePerson - The name of the person you want to summarize the tweets for. For ex: namePerson = "Nicki Minaj"
   2. numberTweets - the numner of tweets you want to collect for the person. For ex: numberTweets = 100

C) Run the Main.py

OUTPUT:

For the output you will see 2 files:
	1. namePerson.csv - Conatins tweets and attributes
	2. namePerson Summary.txt - Contains the summary from the proposed system









