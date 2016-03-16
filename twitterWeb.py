### TO DOWNLOAD TWYTHON, OPEN A COMMAND SHELL AND TYPE: pip install twython ###
from twython import Twython
import os
  
class TwitterData:
    """ Retrieves data to be used for the Web User Interface """
    
    def __init__(self, user=None):
        """ Initializes information to grab Twitter authorization and information """
        self.app_key = "0jQVXOQwtgWwpMQDKW4j2RATp"
        self.app_secret = "ULkoBdUbd5v66AiTyJV854pTtC3y41plzERvAql6ePkiTwK2KM"
        self.oauth_token = "4890112186-uQdAncc22l4hcUVVOzk9B6tNAt2t2GyVMleJYju"
        self.oauth_token_secret = "UGuZ9uFObsDdOyALCdVAjhgobl4s13AxlxiZUibnSGJM3"
        
        self.twitterAuth = self.getTwitterAuth()
        self.user = user
        self.uID = ''
        while True:
            try:
                self.user = user
                self.uID = self.getUserID()
                break
            except:
                print("Invalid user. Please try again. An example is 'barackobama'")
        self.fields = self.getFields()

    def getTwitterAuth(self) -> "twitter info":
        """ Returns the Twitter Authorization"""
        return Twython(app_key=self.app_key, app_secret=self.app_secret, oauth_token=self.oauth_token, oauth_token_secret=self.oauth_token_secret)
       
    def getUser(self) -> str:
        """ Return the username to use """
        user = str(input("Which User would you like to use? "))
        return user
        
    def getUserID(self) -> dict:
        """ Grabs the user ID of the entered username """
        return self.twitterAuth.lookup_user(screen_name=self.user)[0]
        
    def getFields(self) -> list:
        return "name screen_name id followers_count friends_count description location".split()
    
    def getInfo(self, userTweets: "file") -> None:
        """ Grabs the necessary information to obtain a user's tweets """
        info = {}
        for f in self.fields:
            info[f] = ""
        info['name'] = self.uID['name']
        info['screen_name'] = self.uID['screen_name']
        info['id'] = self.uID['id'] 
        info['followers_count'] = self.uID['followers_count']
        info['friends_count'] = self.uID['friends_count']
        info['description'] = self.uID['description']
        info['location'] = self.uID['location']    
        
        maxTweet = self.twitterAuth.get_user_timeline(screen_name=self.user, count=1)[0]['id']
        for h in range(20): 
            tweets = self.twitterAuth.get_user_timeline(screen_name=self.user, count=200, exclude_replies=1, include_rts=0, max_id=maxTweet)
            for i in tweets:
                if h > 0 and i['id'] == maxTweet:
                    pass
                else:
                    temp = []
                    for j in str(i['text']).split():
                        if j[0:4] != "http":
                            temp.append(j)
                    temp = ' '.join(temp)

                    try:
                        userTweets.write(temp + "\n")
                    except:
                        pass
                    maxTweet = i['id']
    
    def execute(self):
        """ Returns the path to a file containing, at most, the most recent 4000 tweets from a user """
        user_tweets = "%s_tweets.txt" % (self.user)
    
        userTweets = open(user_tweets, "w")
    
        self.getInfo(userTweets)
        
        userTweets.close()
        
        return os.path.abspath(user_tweets)
