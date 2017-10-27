#!/usr/bin/python3
from constants import *
from sqlalchemy import Integer, Column, Numeric, String
from sqlalchemy import create_engine, MetaData, Table
from sqlalchemy.orm import mapper, sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from collections import Counter
import argparse
import os

class Filters(object):
    """Contain filters used to filter the contents from textfile"""
    def __init__(self):
        self.order = ['lowercase','split','badchars','whitespace']

    def filter(self,chunk):
        """Filter chunk in specified order of filter layers"""
        for name in self.order:
            func = getattr(self,name)
            chunk = func(chunk)
        return chunk

    def split(self,chunk):
        """Parse chunk into list"""
        return chunk.split(' ')

    def badchars(self,chunk):
        """Remove non-alphabetical characters"""
        return [''.join(filter(str.isalpha,word)) for word in chunk]

    def lowercase(self,chunk):
        """Lowercase all characters"""
        return chunk.lower()

    def whitespace(self,chunk):
        """Remove whitespace and blanks"""
        space,nothing = ' ',''
        while space in chunk:
            chunk.remove(space)
        while nothing in chunk:
            chunk.remove(nothing)
        return chunk

class FileObj(object):
    """Read in textfile and create content generator"""
    def __init__(self,file_path=None,chunk_size=1):
        self.file_path = file_path
        self.chunk_size = chunk_size
        self.pipeline = self.chunk(self.openfile())
        self.filters = Filters()

    def openfile(self,*kwargs):
        """Opens file and generates lines
        Args:
            file_path = Path to text file
        Notes:
            Accepts plain text files
        """
        with open(self.file_path, 'r') as infile:
            for line in infile:
                line_generator = line.rstrip('\n')
                yield line_generator

    def chunk(self,line_generator):
        """Package lines in file into specific chunk size, return the chunk
        Args:
            line_gen = String Generator of lines of file
            chunk_size = Number of lines from file wanted in each chunk
        """
        lines = []
        try:
            while True:
                for i in range(0,self.chunk_size):
                    lines.append(next(line_generator))
                dirty_chunk = ' '.join(lines)
                yield dirty_chunk
                lines = []
        except StopIteration as e:
            if lines:
                dirty_chunk = ' '.join(lines)
                yield dirty_chunk

    def filter(self):
        """Filter content in textfile"""
        for chunk in self.pipeline:
            yield self.filters.filter(chunk)

Base = declarative_base()
class WordBank(Base):
    __tablename__ = 'Warriner-English'
    word = Column(String, primary_key=True)
    value = Column(Integer)

class Database(object):
    def __init__(self,db_path=None):
        """Temp Fix regarding path constants"""
        PROJECT_ROOT = os.path.abspath(os.path.dirname(__file__))
        DEFINITIONS_ROOT = os.path.join(PROJECT_ROOT,'wordbank.db')
        db_path = DEFINITIONS_ROOT
        engine = create_engine('sqlite:///%s' % db_path, echo=False)
        metadata = MetaData(engine)
        Warriner_English = Table('Warriner-English', metadata, autoload=True)
        Session = sessionmaker(bind=engine)
        self.session = Session()

    def query(self,content):
        found = {}
        notfound = {}
        for word in content:
            row = self.session.query(WordBank).filter_by(word=word).first()
            try:
                found.update({row.word:row.value})
            except AttributeError:
                notfound.update({word:None})
        return found, notfound

class Data(object):
    def __init__(self):
        self.content = None
        self.wordcount = Counter()
        self.wordsfound = Counter()
        self.wordsnotfound = {}

    def __call__(self):
        return self.__dict__

class TextSentiment(object):
    def __init__(self,file_path,chunk_size):
        self.content = FileObj(file_path=file_path,
                               chunk_size=chunk_size).filter()
        self.db = Database(db_path=DB_PATH)
        self.data = Data()
        self.data.content = self.content

    def wordcountcalc(self):
        for chunk in self.content:
            self.data.wordcount.update(Counter(chunk))

    def query(self):
        keys = self.data.wordcount.keys()
        self.data.wordsfound, self.data.wordsnotfound = self.db.query(keys)

    def sentimentvalue(self):
        totalvalue, totalfrequency = 0, 0
        for key, value in self.data.wordsfound.items():
            wordfrequency = self.data.wordcount[key]
            totalfrequency += wordfrequency
            totalvalue += wordfrequency * value
        sv = totalvalue / totalfrequency
        return round(sv,4)

    def __getitem__(self,key):
        return self.data.__dict__[key]

    def __call__(self):
        return self.data.__dict__

def myparser():
    parser = argparse.ArgumentParser()
    parser.add_argument('--file_path','--file','-f', default=None, help='File path to file for analysis')
    parser.add_argument('--chunk_size','--chunk','-ch', default=1, help='Lines to read at a time')
    args = parser.parse_args()
    if not args.file_path:
        parser.error("A file path path is not specified. Use -h for help")
    return(args)

def main():
    args = myparser()
    if args.file_path:
        ts = TextSentiment(args.file_path,args.chunk_size)
    ts.wordcountcalc() #Count each word
    ts.query() #Split words into wordsfound and wordsnotfound
    sv = ts.sentimentvalue() #Calculate the average sentiment value
    print("Sentiment Value: ",sv)

if __name__ == '__main__':
    main()
