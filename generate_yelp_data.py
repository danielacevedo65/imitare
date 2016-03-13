# Generates a .txt file containing Yelp review text.

"""
Yelp Data Format

Review
{
    'type': 'review',
    'business_id': (encrypted business id),
    'user_id': (encrypted user id),
    'stars': (star rating, rounded to half-stars),
    'text': (review text),
    'date': (date, formatted like '2012-03-14'),
    'votes': {(vote type): (count)},
}

Relevant keys: business_id, user_id, stars, text, date
"""

import json
import urllib.request as ur
import matplotlib.pyplot as plt
from nltk import FreqDist

class Yelp_Data:

    LOCAL_YELP_FILE = "yelp_data/yelp_academic_dataset_review.json"
    YELP_FILE_LINK = "http://www.ics.uci.edu/~changsm1/data/yelp_academic_dataset_review.json"

    def __init__(self, n_reviews=100, min_review_length=50, criteria_key=None, criteria_value=None):
        self.n_reviews = n_reviews                      # number of reviews to search through for criteria
        self.min_review_length = min_review_length      # length (number of tokens) of reviews
        self.criteria_key = criteria_key                # business_id, user_id, stars, text, date
        self.criteria_value = criteria_value
        self.reviews = []
        self.review_texts = []
        self.review_lengths = []
        self.fetch_reviews()
        self.fetch_review_text()

    def fetch_reviews(self):
        """Fetches JSON review with all info"""
        data_file = ur.urlopen(self.YELP_FILE_LINK)
        #with open(self.YELP_FILE) as data_file:                # USED LOCALLY
            #while len(self.reviews) < self.n_reviews:          # search through all reviews to get right number (may error out)
        for i in range(self.n_reviews):                         # go through set number of reviews
            #review_json = json.loads(data_file.readline())     # USED LOCALLY
            review_json = json.loads(data_file.readline().decode("utf-8"))
            if self.criteria_key != None:
                if review_json[self.criteria_key] != self.criteria_value:
                    continue
            self.reviews.append(review_json)

    def fetch_review_text(self):
        """Retrieves text of review"""
        for review in self.reviews:
            review_length = len(review["text"])
            if review_length > self.min_review_length:
                self.review_texts.append(review["text"])
                self.review_lengths.append(review_length)
        return self.review_texts

    def write_review_text(self, filepath="yelp_data.txt"):
        with open(filepath, 'w') as f:
            for review in self.review_texts:
                f.write(review)

    def print_reviews(self):
        for review in self.reviews:
            print(review)

    def print_review_text(self):
        review_texts = self.fetch_review_text()
        for review in review_texts:
            print(review)

    def avg_review_length(self):
        return (sum(self.review_lengths) / len(self.review_lengths))

    def review_length_histogram(self):
        fdist = FreqDist(len(r) for r in self.review_texts)        # get review length data for histogram
        max_review_length = max(fdist.keys())

        print("Max review length: " + str(max_review_length))
        review_lengths, number_of_reviews = [], []

        for sample in fdist:
            review_lengths.append(sample)
            number_of_reviews.append(fdist[sample])

        fig, axes = plt.subplots()
        axes.set_title('Review Length Histogram for Yelp Data')
        axes.set_xlabel('Review Length')
        axes.set_ylabel('Number of Reviews')
        axes.set_xlim(1, max_review_length)
        axes.bar(review_lengths, number_of_reviews)
        fig.savefig("Yelp Data Histogram")

def get_Yelp_data():
    n_reviews = input("Number of reviews to retrieve (default is 1000): ") or 1000
    min_review_length = input("Minimum review length (default is 50): ") or 50
    criteria_key = input("Search by criteria [business_id, user_id, stars, date] (default is None): ") or None
    if criteria_key != None:
        criteria_value = input("Set criteria value [stars=4]: ")
    criteria_value = None
    print("\tFetching Yelp data...")
    return Yelp_Data(int(n_reviews), int(min_review_length), criteria_key, criteria_value)

if __name__ == '__main__':
    yelp_data = get_Yelp_data()
    print("\nGenerating Yelp data file...")
    yelp_data.print_review_text()
    yelp_data.write_review_text()
    print("Average review length: " + str(yelp_data.avg_review_length()))
    #yelp_data.review_length_histogram()
    print("\nFinished writing data file 'yelp_data.txt'.")