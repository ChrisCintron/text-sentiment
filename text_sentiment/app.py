
from tests.fixtures.constants import *
from sqlalchemy import Integer, Column, Numeric, String
from sqlalchemy import create_engine, MetaData, Table
from sqlalchemy.orm import mapper, sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from collections import Counter


class Filters(object):
    def __init__(self):
        self.filters = []

    def addfilter(self,method):
        if callable(method):
            self.filters.append(method)

    def split(self,chunks):
        for chunk in chunks:
            chunk = chunk.split(' ')
            yield chunk

    def badchars(self,chunks):
        from itertools import groupby
        for chunk in chunks:
            chunk = [''.join(filter(str.isalpha,word)) for word in chunk]
            yield chunk

    def lowercase(self,chunks):
        for chunk in chunks:
            chunk = chunk.lower()
            yield chunk

    def whitespace(self,chunks):
        for chunk in chunks:
            w = ' '
            n = ''
            while w in chunk:
                chunk.remove(w)

            while n in chunk:
                chunk.remove(n)

            yield chunk

    def process(self,pipeline):
        for f in self.filters:
            pipeline = f(pipeline)
        return pipeline

class FileObj(object):
    """Read in file"""
    def __init__(self,file_path):
        self.file_path = file_path
        self.pipeline = file_path

        self.chunk_size = 3
        self.process_methods = []

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

    def addprocessmethod(self,method):
        if callable(method):
            self.process_methods.append(method)

    def process(self):
        for f in self.process_methods:
            self.pipeline = f(self.pipeline)
        return self.pipeline

class Data(object):
    def __init__(self):
        #Object with word and word values
        self.content = None
        self.counted_words = Counter()
        self.dbvalues = {}

    def countwords(self):
        for chunk in self.content:
            self.counted_words.update(Counter(chunk))

    def updatedbvalues(self,dbvalues):
        for value in dbvalues:
            self.dbvalues.update(value)

    def rejectwords(self):
        self.rejectedwords = {key for key,value in self.dbvalues.items() if not value}

    def cleanvalues(self):
        for word in self.rejectedwords:
            self.dbvalues.pop(word,None)
            self.counted_words.pop(word,None)

        self.dbvalues = Counter(self.dbvalues)
        return self.dbvalues

    def sentimentvalue(self):
        totalvalue = 0
        frequency = sum(self.counted_words.values())
        for key,value in self.counted_words.items():
            totalvalue += value * self.dbvalues[key]

        sv = totalvalue/ frequency
        return round(sv,4)

Base = declarative_base()
class WordBank(Base):
    __tablename__ = 'Warriner-English'
    word = Column(String, primary_key=True)
    value = Column(Integer)

class Database(object):
    def __init__(self,db_path=None):
        engine = create_engine('sqlite:///%s' % db_path, echo=False)
        metadata = MetaData(engine)
        Warriner_English = Table('Warriner-English', metadata, autoload=True)
        Session = sessionmaker(bind=engine)
        self.session = Session()

    def query(self,word):
        row = self.session.query(WordBank).filter_by(word=word).first()
        return row

    def queryall(self,dictobj):
        for word in dictobj:
            row = self.session.query(WordBank).filter_by(word=word).first()
            if row:
                yield {row.word:row.value}
            elif not row:
                yield {word:None}

class App(object):
    def __init__(self):
        self.c = FileObj(file_path=TEST_DOC)
        self.db = Database(db_path=DB_PATH)
        self.f = Filters()
        self.data = Data()

    def setup_FileObj(self):
        self.c.addprocessmethod(self.c.openfile)
        self.c.addprocessmethod(self.c.chunk)

    def setup_Filters(self):
        self.f.addfilter(self.f.lowercase)
        self.f.addfilter(self.f.split)
        self.f.addfilter(self.f.badchars)
        self.f.addfilter(self.f.whitespace)

    def setup(self):
        self.setup_FileObj()
        self.setup_Filters()

    def run(self):
        chunks = self.c.process()
        self.data.content = self.f.process(chunks)


def main():
    app = App()
    app.setup()
    app.run()

    app.data.countwords()
    data = app.data.counted_words
    dbvalues = app.db.queryall(data)
    app.data.updatedbvalues(dbvalues)

    app.data.rejectwords()
    app.data.cleanvalues()
    sv = app.data.sentimentvalue()
    print(sv)
main()
