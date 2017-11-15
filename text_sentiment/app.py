from fixtures.constants import *
from sqlalchemy import Integer, Column, Numeric, String
from sqlalchemy import create_engine, MetaData, Table
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from collections import Counter, defaultdict
import argparse
import os
import json

class Filters(object):
    """Contain filters used to filter the contents from textfile"""
    def __init__(self):
        self.order = ['remove_badchars','make_lowercase','split']

    def filter(self,line):
        """Filter line in specified order of filter layers"""
        for name in self.order:
            func = getattr(self,name)
            line = func(line)
        return line

    def remove_badchars(self,line):
        """Remove non-alphabetical characters"""
        return ''.join(filter(lambda char: char.isalpha() or char.isspace(), line))

    def make_lowercase(self,line):
        """Lowercase all characters"""
        return line.lower()

    def split(self,line):
        """Parse words in line into list
        Notes:
            Make sure this is the last filter in the order
        """
        return [word for word in line.split(' ') if word]

class Database(object):
    def __init__(self,db_path=None):
        """Create Database to perform queries"""
        engine = create_engine('sqlite:///%s' % db_path, echo=False)
        self.metadata = MetaData()
        self.metadata.reflect(bind=engine)
        Session = sessionmaker(bind=engine)
        self.session = Session()

    def query(self, table=None, word=None):
        """Query individual word for value in specified table"""
        table_schema = self.metadata.tables[table]
        row = self.session.query(table_schema).filter_by(word=word).first()
        try:
            return (table,word,row.value)
        except AttributeError:
            return (table,word,0)

class TextSentiment(object):
    def __init__(self,file_path=None,content=None,db_path=None):
        self.file_path = file_path
        self.content = [content]
        self.db_path = db_path

        self.filters = Filters()
        self.db = Database(db_path=db_path) #Compose database connection

        self.data = {} #Data container for export
        #self.metrics = {}
        #self.tables = self.db.metadata.tables
        #self.metrics['totalwords'] = 0
        #self.metrics['sentimentvalue'] = 0
        #self.metrics['foundwords'] = 0

        if file_path:
            self.content = self._openfile(file_path)
        self.content = self._filter(self.content)

    def _openfile(self,file_path):
        """Open plain text file and generate lines"""
        with open(file_path, 'r') as infile:
            for line in infile:
                yield line.rstrip('\n')

    def _filter(self,content):
        """Filter content in textfile into shared data structure"""
        for line in content:
            filtered_line = self.filters.filter(line)
            yield filtered_line

    def _query(self,table=None,word=None):
        """Search db table for word"""
        return self.db.query(table=table,word=word)

    def wordcount(self, content):
        """Counts words in iterable"""
        totalcount = Counter()
        for line in content:
            count = Counter(line)
            totalcount.update(count)
        return totalcount

    

    def run(self):
        pass
        #self.wordcounts = self.wo
        #for word in




        #print(json.dumps(self.shared_dict, indent=4))
        #return json.dumps(self.shared_dict)


def myparser():
    parser = argparse.ArgumentParser()
    parser.add_argument('--file_path','--file','-f', default=None, help='File path to file for analysis')
    parser.add_argument('--chunk_size','--chunk','-ch', default=1, help='Lines to read at a time')
    parser.add_argument('--verbose', '-v', action='count', default=0, help='Show all data')
    args = parser.parse_args()
    if not args.file_path:
        parser.error("A file path path is not specified. Use -h for help")
    return(args)

def main():
    args = myparser()
    ts = TextSentiment(args.file_path,args.chunk_size)
    ts.wordcountcalc()
    ts.query()
    ts.mapvalues(ts.data.wordcount,ts.data.wordsfound)
    ts.sentimentvalue()

    if args.verbose >= 0:
        print("Sentiment Value: ",ts.data.sentimentvalue)
    if args.verbose >= 1:
        print("\n__Text Sentiment Data Collections__")
        print("-FinalValues-")
        print("Sentiment Value: ",ts.data.sentimentvalue)
        print("Total number of words: ",sum(ts.data.wordcount.values()))
        print("Number of unique Parsed Words: ",len(ts.data.wordcount))
        print("Number of unique found words: ",len(ts.data.wordsfound))
        print("Number of unique notfound words:",len(ts.data.wordsnotfound))
        print("Most Common Words: ",ts.data.wordcount.most_common(3))
        print("Highest Count*DBValue Words: ",ts.data.totalwordvalues.most_common(3))
    if args.verbose >= 2:
        print("\nWordFrequency: ",ts.data.wordcount)
        print("\nFoundInDB: ",ts.data.wordsfound)
        print("\nnotFoundinDB: ",ts.data.wordsnotfound)

if __name__ == '__main__':
    #Run pytest for now.
    main()
