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

    def main():
        line_generator = self._openfile()
        dirty_chunks = self.makechunk(line_generator,self.chunk_size)
        clean_chunks = self.clean(dirty_chunks)
        counted_chunks = self.countwords(clean_chunks)

    def _openfile(self):
        """Opens file and generates lines
        Args:
            file_path = Path to text file
        Notes:
            Accepts plain text files
        """
        with open(self.file_path, 'r') as infile:
            for line in infile:
                line_generator = line.strip('\n')
                yield line_generator

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
                dirty_chunk = ' '.join(lines)
                yield dirty_chunk
                lines = []
        except StopIteration as e:
            if lines:
                dirty_chunk = ''.join(lines)
                yield dirty_chunk

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

        #Holds dict of dict of word:value
        self.data_tables = None


    def loadtables(self):
        """Grab tables from DB, returns Tuple of tables"""
        self.tables = self.c.execute("""SELECT name FROM sqlite_master WHERE type='table'""")
        self.tables = tuple(table[0] for table in self.tables)
        self.data_tables = {table: {} for table in self.tables}
        return self.data_tables

    def loadindices(self):
        """Grab indices from DB, returns Tuple of indices"""
        self.indices = self.c.execute("""SELECT name FROM sqlite_master WHERE type='index'""")
        self.indices = tuple(index[0] for index in self.indices)
        #print(list(self.indices))
        return self.indices

    #Optimization for doing our word searches
    def createindex(self):
        """Index connected to table for faster searches"""
        for tablename in self.tables:
            try:
                index_name = '{}_idx'.format(tablename)
                string = """CREATE INDEX '{}' ON '{}'({});""".format(index_name,tablename,'word')
                #print(string)
                self.c.execute(string)
                self.connection.commit()
                yield string
            except sqlite3.OperationalError as e:
                yield

    #Two binary searches because of our index tables from createindex()
    def wordsearch(self,table,word):
        """SINGLE word search of the value of word from db"""
        try:
            string = """SELECT value FROM '{}' WHERE word='{}';""".format(table,word)
            self.c.execute(string)
            value = self.c.fetchone()
            return value
        except:
            print("Error: wordsearch fail: [{}]".format(word))

    def chunksearch(self,tables,chunk):
        """Takes in chunk and returns chunk containing dict of {word,value}"""
        for word in chunk:
            for table in tables:
                value = self.wordsearch(table,word)
                self.data_tables[table].update({word:value})
        return self.data_tables


class SentimentAnalyzer(object):
    """Finds the sentiment value of objects"""
    def __init__(self):
        pass

    def totalvalue(self):
        """Multiply count by the db's word value"""
        pass

if __name__ == '__main__':
    pass
