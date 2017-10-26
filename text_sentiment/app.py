
from tests.fixtures.constants import *
from sqlalchemy import Integer, Column, Numeric, String
from sqlalchemy import create_engine, MetaData, Table
from sqlalchemy.orm import mapper, sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from collections import Counter

class Filters(object):
    def __init__(self):
        self.order = ['lowercase','split','badchars','whitespace']

    def filter(self,chunk):
        for name in self.order:
            func = getattr(self,name)
            chunk = func(chunk)
        return chunk

    def split(self,chunk):
        return chunk.split(' ')

    def badchars(self,chunk):
        return [''.join(filter(str.isalpha,word)) for word in chunk]

    def lowercase(self,chunk):
        return chunk.lower()

    def whitespace(self,chunk):
        space,nothing = ' ',''
        while space in chunk:
            chunk.remove(space)
        while nothing in chunk:
            chunk.remove(nothing)
        return chunk

class FileObj(object):
    """Read in file"""
    def __init__(self,file_path,chunk_size=1):
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
        for chunk in self.pipeline:
            yield self.filters.filter(chunk)

class Data(object):
    def __init__(self,content=None):
        #Object with word and word values
        self.content = content
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

class TextSentiment(object):
    def __init__(self,file_path=None,chunk_size=3):
        #Create content genenerator
        self.content = FileObj(file_path=file_path,
                               chunk_size=chunk_size).filter()
        #Create database connection
        self.db = Database(db_path=DB_PATH)
        #Create Data Object that holds working information
        self.data = Data(content=self.content)

    def countwords(self):
        try:
            self.data.countwords()
        except Exception as e:
            print("Error: ",e)
        finally:
            return self.data.counted_words

    def query(self,word):
        return self.db.query(word)

    def queryall(self,dictobj):
        return self.db.queryall(dictobj)

    def updatedbvalues(self,values):
        return self.data.updatedbvalues(values)

    def rejectwords(self):
        return self.data.rejectwords()

    def cleanvalues(self):
        return self.data.cleanvalues()

    def sentimentvalue(self):
        return self.data.sentimentvalue()

def main():
    ts = TextSentiment(file_path=TEST_DOC,chunk_size=10)
    data = ts.countwords()
    dbvalues = ts.queryall(data)
    ts.updatedbvalues(dbvalues)
    ts.rejectwords()
    ts.cleanvalues()
    sv = ts.sentimentvalue()
    print("Sentiment Value: ",sv)

if __name__ == '__main__':
    main()
