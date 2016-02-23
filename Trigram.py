import Twitter_data
import random
import nltk

class Trigram:
    
    def __init__(self, file):
        self.database = {}
        self.file = file
        self.contents = self.convert()
        self.trigram = self.getTrigramInfo()
        self.data()
    
    def convert(self):
        return self.file.read()
        
    def getTrigramInfo(self):
        return nltk.ngrams(nltk.word_tokenize(self.contents), 3)
        
    def data(self):
        for i, j, h in self.trigram:
            key = (i, j)
            if key in self.database:
                self.database[key].append(h)
            else:
                self.database[key] = [h]
    
    def generationLength(self):
        n = int(input("Please enter length of generated tweet: "))
        if type(n) == int:
            return n
        else:
            print("Must enter an integer value. Please try again.")
            return self.generationLength()
    
    def generate(self):
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
