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
        table = self.metadata.tables[table]
        row = self.session.query(table).filter_by(word=word).first()
        try:
            return {word:row.value}
        except AttributeError:
            return {word:0}

class NumberCruncher:
    """Helper that contains analysis tools"""
    def wordcount(content):
        """Counts words in list or generator"""
        totalcount = Counter()
        if isinstance(content,list): #Catches one liners to work with loop
            content = [content]
        for line in content:
            count = Counter(line)
            totalcount.update(count)
        return totalcount

class TextSentiment(object):
    def __init__(self,file_path=None,content=None,db_path=None):
        self.data = defaultdict(dict) #Data container for export
        self.metrics = {}
        self.metrics['totaluniquewordcount'] = 0

        self.content = content
        self.db_path = db_path

        self.db = Database(db_path=db_path) #Compose database connection
        self.filters = Filters()

        if file_path:
            self.content = self._openfile(file_path)

        self.filtered_content = self._filter(self.content)

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

    def _createlabels(self,labels,value=None):
        """Populate metric container with labels"""
        for label in labels:
            self.metrics[label] = value

    def query(self,table=None,word=None):
        """Search db table for word"""
        return self.db.query(table=table,word=word)

    def _updateWord(self,word,count):
        """Updates that occur on every word iteration"""
        self.data[word] = {}
        self.data[word].update(frequency=count,tables={})
        self.metrics['totaluniquewordcount'] += 1

    def _updateTable(self,word,count,table):
        """Updates that occur on every table iteration"""
        query = self.query(table=table,word=word)
        self.data[word]['tables'].update({table: {}})
        self.data[word]['tables'][table].update({'value': query[word]})
        self.data[word]['tables'][table].update({'total_value': count*query[word]})

    def run(self):
        tables = [table for table in self.db.metadata.tables]
        wordcount = NumberCruncher.wordcount(self.filtered_content)
        for word,count in wordcount.items():
            self._updateWord(word,count)
            for table in tables:
                self._updateTable(word,count,table)
    """
    def set_uniquewordcount(self):
        results = len(self.shared_dict['words'])
        self.shared_dict['metrics']['uniquewordcount'] = results
        return results
    """
    """
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
    """
    """
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
    """

def main():
    pass

if __name__ == '__main__':
    #Run pytest for now.
    main()
