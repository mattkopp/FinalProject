#Matt Koppelman
#GIS 501
#December 11, 2014
#Final Project

from TwitterSearch import *
from geopy import geocoders
import arcpy
from arcpy import env
import csv



#load geocoder
def geo(location):
    g = geocoders.GoogleV3()
    loc = g.geocode(location)
    return loc.latitude, loc.longitude

#Create empty array variable.
point = arcpy.Point()
#be able to overwrite data
arcpy.env.overwriteOutput = True

#WHERE YOU WANT YOUR NEW FILE
filelocation = "C:/Users/Matt/Documents/UWTacoma/GIS501/GitHub/FinalProject/Results/"
#place to put new feature class
fc = "C:/Users/Matt/Documents/UWTacoma/GIS501/GitHub/FinalProject/Results/TweetOutput.shp"
#set spatial reference for shapefile you will create
spatialref = arcpy.SpatialReference ('WGS 1984')

#Create point feature class
arcpy.management.CreateFeatureclass(filelocation, "TweetOutput.shp", "POINT","","","",spatialref)
arcpy.management.AddField(fc, "LAT", "FLOAT","","",20,"","NULLABLE")
arcpy.management.AddField(fc, "LNG", "FLOAT", "","",20,"","NULLABLE")
arcpy.management.AddField(fc, "USER_NAME", "TEXT","","",40,"","NULLABLE")
arcpy.management.AddField(fc, "TWEET", "TEXT","","",140,"","NULLABLE")
arcpy.management.AddField(fc, "TWEET_DATE", "TEXT","","",40,"","NULLABLE")
arcpy.management.AddField(fc, "KEYWORD", "TEXT","","",140,"","NULLABLE")


#USE THE SHAPE@XY TOKEN TO ADD POINTS TO A POINT FC
cursIns = arcpy.da.InsertCursor(fc, ("SHAPE@XY", "LAT", "LNG", "USER_NAME", "TWEET","TWEET_DATE", "KEYWORD"))
HashtagList = ["#MLSPlayoffs", "#LAGalaxy", "#FirstToFive", "#SportingKC", "#DefendTogether", "#Crew96", "#CrewSC", "#ForColumbus",  "#Revs", "#STAND", "#FCDallas", "#FCD", "#RedForGlory","#DCU", "#WeWantFive", "#RSL", "#AsOne", "#Sounders", "#ebfg", "#WhitecapsFC", "#StrengthInNumbers", "#NYRB", "#RunWithUs"]


try:
	for Hashtag in HashtagList:
		tso = TwitterSearchOrder() # create a TwitterSearchOrder object
		tso.set_keywords([Hashtag])
		
		tso.set_include_entities(False) # and don't give us all those entity information

		#object creation with secret token. Twitter API crap.
		ts = TwitterSearch(
			consumer_key = 'KmjqQQkZDmlXVh7JTCsWhUT3u',
			consumer_secret = '2Y6ZTj4wfLl3FtzVnqGYOGQPl7ZYnIfH9vhbqYqqINtKSV7SVt',
			access_token = '361007642-rJRndwoXv09DZ8Olh9ooyG5Wv0dXPPy0bIW6MoQM',
			access_token_secret = 'BgSOv1PBGJfk1qjLAIFvss1IeEfuGBSvpdhXmWOnhX8fa'
		 )

		 # this is where the fun actually starts :)
		for tweet in ts.search_tweets_iterable(tso):
			if tweet['coordinates'] is not None: #check to see if tweet geotagged. If not, [0.0, 0.0] or None will be there.
				print ( '@%s tweeted: %s, on %s' % ( tweet['user']['screen_name'], tweet['text'], tweet['created_at'] ) )
				C = (tweet['coordinates']) #grab the dictionary containing coordinates
				C = C.get('coordinates') #get only the coordinates
				lat = C[1]  #lat is the second one
				lng = C[0]  #Lng is the first
				print "from geot-tagged location: {}, {}".format(lat, lng)

			elif tweet['place'] is not None:
				(lat, lng)= geo(tweet['place']['full_name'])
				print '(place) And they said it from (' + str(lat) +', ' +str(lng)+')'

			elif tweet['user']['location'] is not None:
				try:
					(lat, lng) = geo(tweet['user']['location'])
					print ( '@%s tweeted: %s, on %s' % ( tweet['user']['screen_name'], tweet['text'], tweet['created_at'] ) )
				except:
					continue

			try:
				#setup text to put into shapefile or CSV
				text = (str(tweet['text'])) #this gave me a ascii error, look at the four lines below to see how you can use the encode functioni on  a string to make it utf-8 which is better for web data
			except UnicodeEncodeError as e:
				#continue #this is like a skip command. comment it out to make the code beneath it run. this is just to show you how the .encode function works
				print "Error : ", e
				print "Error Text : ", tweet['text']
				print "Converted to Unicode : ", tweet['text'].encode("utf-8")
				print "take two : ", str(tweet['text'].encode("utf-8")), str(tweet['created_at'].encode("utf-8")) #shoud work every time
				text = str(tweet['text'].encode("utf-8"))
			username = tweet['user']['screen_name']
			created_at = str(tweet['created_at'])
			point = arcpy.Point(lng, lat)
			
			if lat == 0:
				continue
			else:
				cursIns.insertRow((point, lat, lng, username, text, created_at, Hashtag))


except TwitterSearchException as e: # take care of all those ugly errors if there are some
    print(e)

del cursIns


