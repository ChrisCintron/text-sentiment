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
    def __init__(self,file_path=None,chunk_size=1):
        self.file_path = file_path
        self.chunk_size = chunk_size
        self.textfile = None

        #Generators
        self.line_gen = self.line_generator()
        self.chunk_gen = self.read_in_chunks(self.line_gen,self.chunk_size)



    def line_generator(self):
        """Opens file and generates lines"""
        with open(self.file_path, 'r') as infile:
            for line in infile:
                line = line.strip('\n')
                yield line

    def read_in_chunks(self,line_gen=None,chunk_size=None):
        """Read file by specified number of lines"""
        i,text_chunk = 0,str()
        for line in line_gen:
            i += 1
            text_chunk += line
            if i >= chunk_size:
                yield text_chunk
                i,text_chunk = 0,str()
        if text_chunk:
            yield text_chunk

    def word_parsing_generator(self,chunk_gen=None):
        """Finds individual words from text
        Checks if all chars in word are alphabetical.

        line in line_gen = "Test I am1 a line"
        words = ('Test', 'I', 'am', 'a', 'line')
        accepted_list = ('Test', 'I', 'a', 'line')
        rejected_list = ('am1',)

        Possibly another way of doing it..
        #filtered_list = tuple(filter(str.isalpha,words))
        """
        for line in chunk_gen:

            line = line.lower()
            line = line.replace('.', '')
            line = line.replace('\'', ' ')

            words = tuple(line.split(' '))
            accepted_list = tuple(word for word in words if str.isalpha(word))
            rejected_list = tuple(word for word in words if not str.isalpha(word))

            yield accepted_list

    def word_count_generator(self,filtered_list=None,chunk_size=None):
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
            if i >= chunk_size:
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
        self.line_gen = self.line_generator()
        #p = self.word_parsing_generator(l)
        #c = self.word_count_generator(p,lines_at_a_time=10)
        #t = self.tally_word_count(c)
        self.read_in_chunks()

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
    print("Main Starting")
    testdoc = './text_sentiment/tests/fixtures/testfile.txt'
    f = FileAnalyzer(file_path=testdoc,chunk_size=2)

if __name__ == '__main__':
    main()
