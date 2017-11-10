#!/usr/bin/python3
from constants import *
from sqlalchemy import Integer, Column, Numeric, String
from sqlalchemy import create_engine, MetaData, Table
from sqlalchemy.orm import mapper, sessionmaker
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
    def __init__(self,file_path=None,file_upload=None):
        self.file_path = file_path
        self.file_upload = file_upload
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
        if self.file_path:
            file = self.openfile()
        elif self.file_upload:
            file = self.file_upload
        content = self.filter(file)
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
        #print(Warriner_English['word'])
        #exit()
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
                notfound.update({word:0})
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
    def __init__(self,file_path=None,file_upload=None,db_path=None):
        self.shared_dict = {}
        self.metrics = ['metrics','words']
        if file_path:
            fileobj = FileObj(file_path=file_path)
        elif file_upload:
            fileobj = FileObj(file_upload=file_upload)
        self.content = fileobj.run()
        self.db = Database(db_path=db_path)
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

    def set_wordcount(self):
        results = 0
        for value in self.shared_dict['words'].values():
            results += value['frequency']
        self.shared_dict['metrics']['wordcount'] = results
        return results

    def set_uniquewordcount(self):
        results = len(self.shared_dict['words'])
        self.shared_dict['metrics']['uniquewordcount'] = results
        return results

    def set_acceptedwordcount(self):
        results = 0
        for value in self.shared_dict['words'].values():
            if value['db_value']:
                results += value['frequency']
        self.shared_dict['metrics']['acceptedwordcount'] = results
        return results

    def set_accepteduniquewordcount(self):
        results = 0
        for value in self.shared_dict['words'].values():
            if value['db_value']:
                results += 1
        self.shared_dict['metrics']['accepteduniquewordcount'] = results
        return results

    def set_rejecteduniquewordcount(self):
        results = 0
        for value in self.shared_dict['words'].values():
            if not value['db_value']:
                results += 1
        self.shared_dict['metrics']['rejecteduniquewordcount'] = results
        return results

    def set_rejectedwordcount(self):
        results = 0
        for value in self.shared_dict['words'].values():
            if not value['db_value']:
                results += value['frequency']
        self.shared_dict['metrics']['rejectedwordcount'] = results
        return results

    def set_highlowratings(self,metric):
        highest_rating,lowest_rating = 0,10
        for key,value in self.shared_dict['words'].items():
            value = value[metric]
            if value:
                if value > highest_rating:
                    highest_word = key
                    highest_rating = value
                if value < lowest_rating:
                    lowest_word = key
                    lowest_rating = value

        self.shared_dict['metrics']['highest_pair'] = (highest_word,highest_rating)
        self.shared_dict['metrics']['lowest_pair'] = (lowest_word,lowest_rating)

    def set_word_totalvalue(self):
        for key,value in self.shared_dict['words'].items():
            frequency = self.shared_dict['words'][key]['frequency']
            db_value = self.shared_dict['words'][key]['db_value']
            results = {"totalvalue":frequency*db_value}
            self.shared_dict['words'][key].update(results)
        return results

    def set_word_dbvalue(self):
        combined_dict = self.query(self.shared_dict['words'].keys())
        for key,value in combined_dict.items():
            self.shared_dict['words'][key].update({"db_value":value})

    def set_sentimentvalue(self):
        totalvalue = 0
        totalfrequency = self.shared_dict['metrics']['acceptedwordcount']
        for value in self.shared_dict['words'].values():
            totalvalue += value['totalvalue']
        sv = round(totalvalue / totalfrequency,5)
        self.shared_dict['metrics'].update({'sentimentvalue':sv})
        return sv

    def run(self):
        self.create_data_structure(self.metrics,self.shared_dict)
        self.extractcontent(self.content,self.shared_dict)
        self.set_word_dbvalue()
        self.set_word_totalvalue()

        self.set_wordcount()
        self.set_uniquewordcount()
        self.set_acceptedwordcount()
        self.set_accepteduniquewordcount()
        self.set_rejectedwordcount()
        self.set_rejecteduniquewordcount()
        self.set_highlowratings('db_value')
        self.set_sentimentvalue()
        print(json.dumps(self.shared_dict, indent=4))
        return json.dumps(self.shared_dict)

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
    ts = TextSentiment(TEST_DOC,DB_PATH)
    ts.run()


if __name__ == '__main__':
    #main()
    main_test()
