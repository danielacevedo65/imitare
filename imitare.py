"""
Imitare - A Versatile Text Generator
-------
Main Program

CS175 Winter 2016
    Daniel Acevedo, 20406712, daceved1@uci.edu
    Priyank Patel, 40093954, pnpatel2@uci.edu
    Stephanie Chang, 33865312, changsm1@uci.edu
"""

import csv
import os
from stanford import StanfordTagger, StanfordDetokenizer
from generator import LVGNgramGenerator
from generate_yelp_data import get_Yelp_data
from Twitter_data import TwitterData

class Imitare:
    def __init__(self):
        self.ROOT_PATH = os.path.dirname(os.path.abspath(__file__))
        self.WORK_PATH = self.ROOT_PATH
        self.data_type = None
        self.data_set = None
        self.data = None
        self.tagged_data = None
        self.n_gram = 5
        self.save_tagged_data = False

    def get_working_directory(self):
        path  = input("Please enter a name for a working directory for generated files: ")
        if not os.path.exists(path):
            print("\tMaking working directory...")
            os.mkdir(path)
        else:
            print("\tWorking directory already exists.")
        self.WORK_PATH = os.path.join(self.ROOT_PATH, path)

    def set_data_set(self, data_set):
        self.data_set = data_set

    def get_ngram(self):
        self.n_gram = int(input("\nWhat n-gram length would you like to use? "))
        print("\tYou have chosen to use n_grams of length " + str(self.n_gram) + ".")
        if self.n_gram > 10:
            print("\tPlease note that the larger the n_gram length, the longer it will take to analyze the data.")

    def show_intro(self):
        print()
        print("Welcome to Imitare - a versatile text generator!")
        print("------------------------------------------------")
        print("CS175 Winter 2016 Project")
        print("\tDaniel Acevedo\n\tPriyank Patel\n\tStephanie Chang")
        print()

    def get_data_type(self):
        print("\nData Set Types:")
        print("\tNew Data Set: Generate and tag a new data set.")
        print("\tExisting Data Set: Use a tagged file to generate text (faster).")
        print("\t\t- Twitter: Barack Obama, Bernie Sanders, CNN, Donald Trump, Jimmy Fallon, Kanye West, NASA")
        print("\t\t- Project Gutenberg: Harry Potter Books")
        print("\t\t- Yelp: 1000 Reviews (Min-Length: 50 words), 1000 Reviews (Min-Length: 50 words, Stars: 1), 1000 Reviews (Min-Length: 50 words, Stars: 5")
        self.data_type = input("Would you like to generate a [n]ew data set or use an [e]xisting data set?: ").lower()
        while self.data_type not in ['n', 'e',]:
            print("\tPlease type [n, e].")
            self.data_type = input("Would you like to generate a [n]ew data set or use an [e]xisting data set?: ").lower()

    def get_existing_data(self):
        print("\nExisting Data Sets")
        print("\t- [T]witter: Barack Obama, Bernie Sanders, CNN, Donald Trump, Jimmy Fallon, Kanye West, NASA")
        print("\t- [P]roject Gutenberg: Harry Potter Books")
        print("\t- [Y]elp: 1000 Reviews (Length: 50 words)\n")
        self.data_set = input("Please choose a data set: ").upper()
        while self.data_set not in ['T', 'P', 'Y']:
            print("\tPlease type [T, P, Y].")
            self.data_set = input("Please choose a data set: ").upper()
        if self.data_set == 'T':
            twitter_accounts = ["barackobama", "berniesanders", "cnn", "donaldtrump", "jimmyyfallon", "kanyewest", "nasa"]
            print("\nTwitter Data:")
            print("\t[1] Barack Obama\n\t[2] Bernie Sanders\n\t[3] CNN\n\t[4] Donald Trump\n\t[5] Jimmy Fallon\n\t[6] Kanye West\n\t[7] NASA")
            data = int(input("\nPlease enter the number of the account you would like to use: "))
            print()
            self.tagged_data = os.path.join(os.path.join(self.ROOT_PATH, "data"), twitter_accounts[data-1] + ".tags")
        elif self.data_set == 'P':
            pg_data = ["hp_and_the_ss", "hp_and_the_gof"]
            print("\tProject Gutenberg Data:")
            print("\t[1] Harry Potter and the Sorceror's Stone\n\t[2] Harry Potter and the Goblet of File")
            data = int(input("\nPlease enter the number of the book you would like to use: "))
            print()
            self.tagged_data = os.path.join(os.path.join(self.ROOT_PATH, "data"), pg_data[data-1] + ".tags")
        elif self.data_set == 'Y':
            yelp_data = ["yelp_1000r_50l", "yelp_1000r_50l_1s", "yelp_1000r_50l_5s"]
            print("\tYelp Data:")
            print("\t[1] 1000 Reviews, Length 50\n\t[2] 1000 Reviews, Length 50, 1 Star\n\t[3] 1000 Reviews, Length 50, 5 Stars")
            data = int(input("\nPlease enter the number of the review set you would like to use: "))
            print()
            self.tagged_data = os.path.join(os.path.join(self.ROOT_PATH, "data"), yelp_data[data-1] + ".tags")
        else:
            print("Error in choosing existing data set.")

    def get_data_set(self):
        print("\nData Sets")
        print("\t[C]ustom")
        print("\t[T]witter")
        print("\t[Y]elp\n")
        self.data_set = input("Please choose a data set: ").upper()
        while self.data_set not in ['C', 'T', 'Y']:
            print("\tPlease type [C, T, Y].")
            self.data_set = input("Please choose a data set: ").upper()
        self.fetch_data()
        save_data = input("\nWould you like to save a tagged version of this data {y: yes, n: no}?: ").lower()
        while not save_data in ['y', 'n']:
            print("Please enter [y] for yes or [n] for no.")
            save_data = input("\nWould you like to save a tagged version of this data {y: yes, n: no}?: ").lower()
        if save_data == 'y':
            self.save_tagged_data = True

    def fetch_data(self):
        if self.data_set == 'C':
            print("\tYou have chosen to work with custom data.")
            print()
            self.get_custom_data()
        elif self.data_set == 'T':
            print("\tYou have chosen to work with Twitter data.")
            print()
            self.get_twitter_data()
        elif self.data_set == 'Y':
            print("\tYou have chosen to work with Yelp data.")
            print()
            self.get_yelp_data()
        else:
            print("\tData set is not valid.")
            self.get_data_set()

    def get_custom_data(self):
        print("Please place a .txt file containing your data in the following directory: " + str(self.WORK_PATH))
        data_path = input("What is the name of your text file?: ")
        while not os.path.exists(os.path.join(self.WORK_PATH, data_path)):
            print("\tCould not locate file.")
            data_path = input("What is the name of your text file?: ")
        self.data = os.path.join(self.WORK_PATH, data_path)

    def get_twitter_data(self):
        os.chdir(self.WORK_PATH) # change to data save directory
        self.data = TwitterData().execute()
        os.chdir(self.ROOT_PATH) # change back to main path

    def get_yelp_data(self):
        data = get_Yelp_data()
        print("\tGenerating Yelp data file (yelp_data.txt)...")
        self.data = os.path.join(self.WORK_PATH, "yelp_data.txt")
        data.write_review_text(os.path.join(self.data))
        print("\tYelp data file created.")

    def generate(self):
        if self.data is not None:
            with open(self.data, 'r') as data_file:
                text = data_file.read()
                tagged = StanfordTagger(verbose=True).tag(text)
            if self.save_tagged_data:
                save_file = self.data + ".tags"
                with open(self.data + ".tags", 'w') as save_file:
                    save = csv.writer(save_file)
                    save.writerows(tagged)
        elif self.tagged_data is not None:
            with open(self.tagged_data, 'r') as data_file:
                tagged = csv.reader(data_file)
                tagged = [tuple(row) for row in tagged]
        detok = StanfordDetokenizer()
        model = LVGNgramGenerator(tagged, self.n_gram)
        methods = {'b': model.generate_without_pos, 'n': model.generate, 't': model.generate_alternative}
        while True:
            num_words = input('\nEnter the length in words to generate (or "q" to exit): ')
            if num_words.isdigit():
                method = input('Enter a generation method {b: baseline, n: normal, t: tuned}: ')
                if method in methods:
                    print("\n\t" + detok.detokenize(' '.join(methods[method](int(num_words)))))
            elif num_words == 'q':
                break

def main():
    imitare = Imitare()
    imitare.show_intro()
    imitare.get_working_directory()
    imitare.get_data_type()
    if imitare.data_type == 'n':
        imitare.get_data_set()
    else:
        imitare.get_existing_data()
    imitare.get_ngram()
    print("\nSetup complete. Please note the following:")
    print("\t- If you are using a new data set, the tagging process may take some time.")
    print("\t- If you want to use another data set, you must re-run the program.\n")
    print("Let's start generating text!\n")
    imitare.generate()
    print("\nExiting Imitare...Goodbye!")

if __name__ == '__main__':
    main()
