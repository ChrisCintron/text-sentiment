import sqlite3
import os
import sys
from collections import Counter
from .tests.fixtures.constants import *

class FileAnalyzer(object):
    """Prepares data for SentimentAnalyzer"""
    def __init__(self,file_path=None):
        #Variables for methods
        self.file_path = file_path

    def _openfile(self):
        """Opens file and generates lines
        Args:
            file_path = Path to text file
        Notes:
            Accepts plain text files
        """
        with open(self.file_path, 'r') as infile:
            for line in infile:
                line = line.strip('\n')
                yield line

    def makechunk(self,line_generator,chunk_size):
        """Package lines in file into specific chunk size, return the chunk
        Args:
            line_gen = String Generator of lines of file
            chunk_size = Number of lines from file wanted in each chunk
        """
        lines = []
        try:
            while True:
                for i in range(0,chunk_size):
                    lines.append(next(line_generator))
                text_chunk = ' '.join(lines)
                yield text_chunk
                lines = []
        except StopIteration as e:
            if lines:
                text_chunk = ''.join(lines)
                yield text_chunk

    def clean(self,chunk_generator):
        """Cleans chunk to only contain valid characters
        Notes:
            Possible for valid words in parsed words that
            were not intended by original author.
            Example:
                word = self2*fish
                returns: 'self', 'fish'
        """
        for chunk in chunk_generator:
            #Find bad characters
            bad_chars = filter(lambda char: not char.isalpha(),chunk)
            bad_chars = set(bad_chars) #Removes duplicate bad characters
            bad_chars.discard(' ')

            #Alter, replace, and format chunk
            chunk = chunk.lower()
            clean_chunk = list(map(lambda char: chunk.replace(char, ' '), bad_chars))
            clean_chunk = ''.join(clean_chunk)

            #Gets rid of double spaces and makes tuple
            clean_chunk = tuple(clean_chunk.split())
            yield clean_chunk

    def countwords(self,chunk_generator):
        """Counts number of words in text, return word counts"""
        for chunk in chunk_generator:
            yield Counter(chunk)

class DBLookup(object):
    """Connects the wordbank.db"""
    def __init__(self,path_to_db=None):
        #Initiate database connection
        self.connection = sqlite3.connect(path_to_db)
        self.c = self.connection.cursor() #Used for interacting with DB

        #Variables for methods
        self.tables = None
        self.indices = None

    def loadtables(self):
        """Grab tables from DB, returns Tuple of tables"""
        self.tables = self.c.execute("""SELECT name FROM sqlite_master WHERE type='table'""")
        self.tables = tuple(table[0] for table in self.tables)
        return self.tables

    def loadindices(self):
        """Grab indices from DB, returns Tuple of indices"""
        self.indices = self.c.execute("""SELECT name FROM sqlite_master WHERE type='index'""")
        self.indices = tuple(index[0] for index in self.indices)
        return self.indices

    #Optimization for doing our word searches
    def createindex(self):
        """Index connected to table for faster searches"""
        for tablename in self.tables:
            try:
                index_name = '{}_idx'.format(tablename)
                string = """CREATE INDEX '{}' ON '{}'({});""".format(index_name,tablename,'word')
                self.c.execute(string)
                self.connection.commit()
            except sqlite3.OperationalError as e:
                print(e)

    #Two binary searches because of our index tables from createindex()
    def wordsearch(self,word):
        """Queries Database for word"""
        try:
            string = """SELECT value FROM 'Warriner-English' WHERE word='{}';""".format(word)
            self.c.execute(string)
            value = self.c.fetchone()
            print(value)
            return value
        except:
            print("Error: wordsearch failed")

    def main(self):
        self.loadtables()
        self.loadindices()
        self.createindex()
        self.wordsearch('freezing')
        self.connection.close()

class SentimentAnalyzer(object):
    """Finds the sentiment value of objects"""
    def __init__(self):
        pass

    def totalvalue(self):
        """Multiply count by the db's word value"""
        pass

if __name__ == '__main__':
    pass
