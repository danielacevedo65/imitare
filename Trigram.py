import Twitter_data
import random
import nltk

class Trigram:
    """ A very rough Trigram text generator, used only to test the initial small Twitter set.
        Not used in any way for our main program.
    """
    
    def __init__(self, file):
        self.database = {}
        self.file = file
        self.contents = self.convert()
        self.trigram = self.getTrigramInfo()
        self.data()
    
    def convert(self):
        """ Return the file as a string """
        return self.file.read()
        
    def getTrigramInfo(self):
        """ Obtain Trigram information from NLTK library """
        return nltk.ngrams(nltk.word_tokenize(self.contents), 3)
        
    def data(self):
        """ Assign data into a dictionary """
        for i, j, h in self.trigram:
            key = (i, j)
            if key in self.database:
                self.database[key].append(h)
            else:
                self.database[key] = [h]
    
    def generationLength(self):
        """ Obtain desired length of the tweet """
        n = int(input("Please enter length of generated tweet: "))
        if type(n) == int:
            return n
        else:
            print("Must enter an integer value. Please try again.")
            return self.generationLength()
    
    def generate(self):
        """ Generate tweets """
        n = self.generationLength()
        contents = self.contents.split()
        startPoint = random.randint(0, len(contents)-3)
        start, follow = contents[startPoint], contents[startPoint+1]
        i, j = start, follow
        generated = []
        for h in range(n):
            try:
                generated.append(i)
                i, j = j, random.choice(self.database[(i, j)])
            except:
                pass
        generated.append(j)
        return ' '.join(generated)
    
if __name__ == '__main__':
    tweets = Twitter_data.TwitterData().execute()
    user = open(tweets,"r")
    trigram = Trigram(user)

    print(trigram.generate())

    user.close()
