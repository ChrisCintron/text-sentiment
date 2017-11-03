#!/usr/bin/python3
from constants import *
from sqlalchemy import Integer, Column, Numeric, String
from sqlalchemy import create_engine, MetaData, Table
from sqlalchemy.orm import mapper, sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from collections import Counter, defaultdict
import argparse
import os

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

    def split(self,line):
        """Parse words in line into list
        Notes:
            Make sure this is the last filter in the order
        """
        return [word for word in line.split(' ') if word]

    def remove_badchars(self,line):
        """Remove non-alphabetical characters"""
        return ''.join(filter(lambda char: char.isalpha() or char.isspace(), line))

    def make_lowercase(self,line):
        """Lowercase all characters"""
        return line.lower()

class FileObj(object):
    """Read in textfile and create content generator"""
    def __init__(self,file_path=None,):
        self.file_path = file_path
        self.filters = Filters()

    def openfile(self,*kwargs):
        """Opens file and generates lines
        Notes:
            Accepts plain text files
        """
        with open(self.file_path, 'r') as infile:
            for line in infile:
                yield line.rstrip('\n')

    def filter(self,content):
        """Filter content in textfile into shared data structure"""
        for line in content:
            filtered_line = self.filters.filter(line)
            yield filtered_line

    def run(self):
        content = self.filter(self.openfile())
        return content


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
        nan = float("NaN")
        for word in content:
            row = self.session.query(WordBank).filter_by(word=word).first()
            try:
                found.update({row.word:row.value})
            except AttributeError:
                notfound.update({word:nan})
        return found, notfound

class Data(object):
    def __init__(self):
        self.content = None
        self.wordcount = Counter()
        self.wordsfound = Counter()
        self.wordsnotfound = {}
        self.totalwordvalues = Counter()

    def __call__(self):
        return self.__dict__

class TextSentiment(object):
    def __init__(self,file_path):
        self.shared_dict = {}
        self.metrics = ['total_word_count','words']
        self.content = FileObj(file_path=file_path).run()
        self.db = Database(db_path=DB_PATH)
        self.data = Data()
        self.data.content = self.content

    def create_data_structure(self,metrics,shared_dict):
        for item in metrics:
            shared_dict[item] = {}
        return shared_dict

    def extractcontent(self,content,shared_dict):
        wordcounts = Counter()
        for line in content:
            unique_line = set(line)
            for item in unique_line:
                wordcounts.update({item:line.count(item)})
        for key,value in wordcounts.items():
            shared_dict['words'][key] = {'frequency':value}
        return shared_dict

    def query(self,keys):
        wordsfound, wordsnotfound = self.db.query(keys)
        combined_dict = {}
        combined_dict.update(wordsfound)
        combined_dict.update(wordsnotfound)
        return combined_dict

    def sentimentvalue(self):
        totalvalue, totalfrequency = 0, 0
        for key, value in self.data.wordsfound.items():
            wordfrequency = self.data.wordcount[key]
            totalfrequency += wordfrequency
            totalvalue += wordfrequency * value
        sv = round(totalvalue / totalfrequency,5)
        self.data.sentimentvalue = sv
        return sv

    def set_totalwordcount(self):
            self.shared_dict['total_word_count'] = len(self.shared_dict['words'])

    def set_totalvalue(self):
        for key,value in self.shared_dict['words'].items():
            frequency = self.shared_dict['words'][key]['frequency']
            db_value = self.shared_dict['words'][key]['db_value']
            self.shared_dict['words'][key].update({"totalvalue":frequency*db_value})

    def set_highlowratings(self,metric):
        highest_rating,lowest_rating = 0,10
        for key,value in self.shared_dict['words'].items():
            value = value[metric]
            if value > highest_rating:
                highest_word = {}
                highest_rating = value
                highest_word[key] = highest_rating
            if value < lowest_rating:
                lowest_word = {}
                lowest_rating = value
                lowest_word[key] = lowest_rating
        results = {metric:{'highest_pair':highest_word, 'lowest_pair':lowest_word}}
        self.shared_dict.update(results)
        return results

    def run(self):
        self.create_data_structure(self.metrics,self.shared_dict)
        self.extractcontent(self.content,self.shared_dict)
        combined_dict = self.query(self.shared_dict['words'].keys())

        for key,value in combined_dict.items():
            self.shared_dict['words'][key].update({"db_value":value})

        self.set_totalwordcount()
        self.set_totalvalue()
        self.set_highlowratings('db_value')
        print(self.shared_dict)


    def __getitem__(self,key):
        return self.data.__dict__[key]

    def __call__(self):
        return self.data.__dict__

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

def main_test():
     ts = TextSentiment(TEST_DOC)
     ts.run()
     #print(ts.shared_dict)
    # print(ts.shared_dict)







if __name__ == '__main__':
    #main()
    main_test()
    pass
