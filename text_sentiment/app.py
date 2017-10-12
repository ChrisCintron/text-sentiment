import sqlite3
import os
from collections import Counter

"""
TODO:

"""
class FileAnalyzer(object):
    """Prepares data for SentimentAnalyzer"""
    def __init__(self,file_path=None,chunk_size=1):
        #Variables for methods
        self.file_path = file_path
        self.chunk_size = chunk_size
        self.textfile = None

    def open_file(self,file_path=None):
        """Opens file and generates lines
        Type:
            Generator
        Args:
            file_path = Path to text file
        Notes:
            Accepts plain text files
        """
        with open(file_path, 'r') as infile:
            for line in infile:
                line = line.strip('\n')
                yield line

    def read_in_chunks(self,line_gen=None,chunk_size=None):
        """Package lines in file into specific chunk size, return the chunk
        Type:
            Generator
        Args:
            line_gen = String Generator of lines of file
            chunk_size = Number of lines from file wanted in each chunk
        """
        i,text_chunk = 0,str()
        for line in line_gen:
            i += 1
            text_chunk += line
            if i >= chunk_size:
                yield text_chunk
                i,text_chunk = 0,str()
        if text_chunk:
            yield text_chunk

    def parse_words(self,chunk_gen=None):
        """Parse words in chunk, return the accepted words
        Type:
            Generator
        Args:
            chunk_gen = Tuple Generator of chunks from file
        Notes:
            Possibly another way of doing it >>
            filtered_list = tuple(filter(str.isalpha,words))
        """
        for line in chunk_gen:

            line = line.lower()
            line = line.replace('.', '')
            line = line.replace('\'', ' ')

            words = tuple(line.split(' '))
            accepted_list = tuple(word for word in words if str.isalpha(word))
            rejected_list = tuple(word for word in words if not str.isalpha(word))

            yield accepted_list

    def count_words(self,parsed_chunks=None):
        """Counts number of words in text, return word counts
        Type:
            Generator
        Args:
            parsed_chunks = Tuple Generator of parsed words
            Example:
                parsed_chunks = ('aword','bword','cword')
        """
        text_count = Counter()
        for chunk in parsed_chunks:
            text_count += Counter(chunk)
        #DEBUG
        print(text_count)

    def main(self):
        """Executes analysis of file"""
        f = self.open_file(file_path=self.file_path)
        chunks = self.read_in_chunks(line_gen=f,chunk_size=self.chunk_size)
        parsed_chunks = self.parse_words(chunk_gen=chunks)
        counts = self.count_words(parsed_chunks=parsed_chunks)


class DBLookup(object):
    """Connects the wordbank.db"""
    def __init__(self,path_to_db=None):
        #Initiate database connection
        self.connection = sqlite3.connect(path_to_db)
        self.c = self.connection.cursor() #Used for interacting with DB

        #Variables for methods
        self.tables = None
        self.indices = None

    def loadin_tables(self):
        """Grab tables from DB, returns Tuple of tables"""
        self.tables = self.c.execute("""SELECT name FROM sqlite_master WHERE type='table'""")
        self.tables = tuple(table[0] for table in self.tables)
        return self.tables

    def loadin_indices(self):
        """Grab indices from DB, returns Tuple of indices"""
        self.indices = self.c.execute("""SELECT name FROM sqlite_master WHERE type='index'""")
        self.indices = tuple(index[0] for index in self.indices)
        return self.indices

    #Optimization for doing our word searches
    def create_index(self):
        """Index connected to table for faster searches"""
        for tablename in self.tables:
            try:
                index_name = '{}_idx'.format(tablename)
                string = """CREATE INDEX '{}' ON '{}'({});""".format(index_name,tablename,'word')
                self.c.execute(string)
                self.connection.commit()
            except sqlite3.OperationalError as e:
                print(e)

    #Two binary searches because of our index tables from create_index()
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
        self.loadin_tables()
        self.loadin_indices()
        self.create_index()
        self.wordsearch('freezing')
        self.connection.close()

class SentimentAnalyzer(object):
    """Finds the sentiment value of objects"""
    def __init__(self):
        pass

    def word_totalvalue(self):
        """Multiply count by the db's word value"""
        pass

def main():
    print("Main Starting")
    #testdoc = './text_sentiment/tests/fixtures/testfile.txt'
    db_path = './text_sentiment/models/wordbank.db'
    #f = FileAnalyzer(file_path=testdoc,chunk_size=2)
    #f.main()
    db = DBLookup(db_path)
    db.main()


if __name__ == '__main__':
    main()
