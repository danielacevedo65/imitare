### TO DOWNLOAD TWYTHON, OPEN A COMMAND SHELL AND TYPE: pip install twython ###
from twython import Twython
import os
  
class TwitterData:
    
    def __init__(self):
        self.app_key = "0jQVXOQwtgWwpMQDKW4j2RATp"
        self.app_secret = "ULkoBdUbd5v66AiTyJV854pTtC3y41plzERvAql6ePkiTwK2KM"
        self.oauth_token = "4890112186-uQdAncc22l4hcUVVOzk9B6tNAt2t2GyVMleJYju"
        self.oauth_token_secret = "UGuZ9uFObsDdOyALCdVAjhgobl4s13AxlxiZUibnSGJM3"
        
        self.twitterAuth = self.getTwitterAuth()
        self.user = ''
        self.uID = ''
        while True:
            try:
                self.user = self.getUser()
                self.uID = self.getUserID()
                break
            except:
                print("Invalid user. Please try again. An example is 'barackobama'")
        self.fields = self.getFields()

    def getTwitterAuth(self) -> "twitter info":
        return Twython(app_key=self.app_key, app_secret=self.app_secret, oauth_token=self.oauth_token, oauth_token_secret=self.oauth_token_secret)
       
    def getUser(self) -> str:
        user = str(input("Which User would you like to use? "))
        return user
        
    def getUserID(self) -> dict:
        return self.twitterAuth.lookup_user(screen_name=self.user)[0]
        
    def getFields(self) -> list:
        return "name screen_name id followers_count friends_count description location".split()
    
    def getInfo(self, userData: "file", userTweets: "file") -> None:
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

        for f in self.fields:
            try:
                userData.write(str(f) + " " + str(info[f]) + "\n")
            except:
                pass
        
        tweets = self.twitterAuth.get_user_timeline(screen_name=self.user, count=200, exclude_replies=1, include_rts=0)
        for i in tweets:
            try:
                userTweets.write(i['text'] + "\n")
            except:
                pass
        
        '''
        ### TEST PRINT ###
        print("\n" + self.user + "'s Data\n")
        for i in info:
            print('    ' + str(i) + ' -> ' + str(info[i]))
        print("\n" + self.user + "'s Latest Tweets\n")
        for i in range(len(tweets)):
            print(str(i+1) + ": " + tweets[i]['text'] + '\n')
        ### END TEST ###
        '''
    
    def execute(self):
        user_data = "%s_data.txt" % (self.user)
        user_tweets = "%s_tweets.txt" % (self.user)
    
        userData = open(user_data, "w")        
        userTweets = open(user_tweets, "w")
    
        self.getInfo(userData, userTweets)
        
        userData.close()
        userTweets.close()
        
        return os.path.abspath(user_tweets)