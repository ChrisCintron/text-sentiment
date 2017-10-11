import sqlite3
import os


class FileAnalyzer(object):
    """Prepares data for SentimentAnalyzer"""
    def __init__(self,file_path=None):
        self.file_path = file_path
        self.textfile = None

    def line_generator(self):
        """Opens file and generates lines"""
        with open(self.file_path, 'r') as f:
            for line in f:
                line = line.strip('\n')
                yield line

    def parse_words(self,file):
        """Finds individual words from text"""
        pass

    def count_words(self,listofwords):
        """Counts the number of words in text"""
        pass

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
    result = f.line_generator()

if __name__ == '__main__':
    main()
