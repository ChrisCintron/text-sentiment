import sqlite3
import os
from collections import Counter

"""
TODO:
1.Maybe start lines_at_a_time variable at line_generator method
This would insure the object stay roughly the same size
while being passed through methods. Would possbily mean less generators.

2.Does not properly tally the number of words in testfile when lines_at_a_time
is set to = 1. Edit: Wrongly assumed dict.update() adds values together. Adding
Counters is the right way to add them.
"""
class FileAnalyzer(object):
    """Prepares data for SentimentAnalyzer"""
    def __init__(self,file_path=None):
        self.file_path = file_path
        self.textfile = None

        self.main()

    def line_generator(self):
        """Opens file and generates lines"""
        with open(self.file_path, 'r') as f:
            for line in f:
                line = line.strip('\n')
                yield line

    def word_parsing_generator(self,line_gen):
        """Finds individual words from text
        Checks if all chars in word are alphabetical.

        line in line_gen = "Test I am1 a line"
        words = ('Test', 'I', 'am', 'a', 'line')
        accepted_list = ('Test', 'I', 'a', 'line')
        rejected_list = ('am1',)

        Possibly another way of doing it..
        #filtered_list = tuple(filter(str.isalpha,words))
        """
        for line in line_gen:

            line = line.lower()
            line = line.replace('.', '')
            line = line.replace('\'', ' ')

            words = tuple(line.split(' '))
            accepted_list = tuple(word for word in words if str.isalpha(word))
            rejected_list = tuple(word for word in words if not str.isalpha(word))

            yield accepted_list

    def word_count_generator(self,filtered_list,lines_at_a_time=1):
        """Counts the number of words in text
        lines_at_a_time = Number of lines you want handled at one time
        Iterate through each line and yield the maximum lines specified
        """
        word_counter = 0
        bulk_words = ()
        i = 0
        for line in filtered_list:
            i += 1
            bulk_words += line
            if i >= lines_at_a_time:
                c = Counter(bulk_words)
                yield c
                bulk_words = ()
                i = 0

        if bulk_words:
            c = Counter(bulk_words)
            yield c

    def tally_word_count(self,wordcounts):
        word_bulk = Counter()
        for wordcount in wordcounts:
            word_bulk += wordcount
        print(word_bulk)

    def main(self):
        l = self.line_generator()
        p = self.word_parsing_generator(l)
        c = self.word_count_generator(p,lines_at_a_time=10)
        t = self.tally_word_count(c)

class DBLookup(object):
    """Connects the wordbank.db"""
    def __init__(self,path_to_local_db):
        pass

    def query(self,word):
        """Queries Database for word"""
        pass

class SentimentAnalyzer(object):
    """Finds the sentiment value of objects"""
    def __init__(self):
        pass

    def word_totalvalue(self):
        """Multiply count by the db's word value"""
        pass

def main():
    testdoc = './text_sentiment/tests/fixtures/testfile.txt'
    f = FileAnalyzer(file_path=testdoc)

if __name__ == '__main__':
    main()
