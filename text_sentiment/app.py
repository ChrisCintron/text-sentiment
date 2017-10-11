import sqlite3
import os


class FileAnalyzer(object):
    """Prepares data for SentimentAnalyzer"""
    def __init__(self,file_path=None):
        self.file_path = file_path

        self.textfile = None


    def open(self):
        pass

    def parse_words(self):
        pass

    def count_words(self,listofwords):
        pass


class DBLookup(object):
    """Connects the wordbank.db"""
    def __init__(self,path_to_local_db):
        pass

    def query(self,word):
        pass


class SentimentAnalyzer(object):
    """Finds the sentiment value of objects"""
    def __init__(self):
        pass

    def word_totalvalue(self):
        """Multiply count by the db's word value"""
        pass

def main():
    pass


if __name__ == '__main__':
    main()
