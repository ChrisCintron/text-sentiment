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
    """Analyzes the sentiment score of a given file or text

    Basic usage:
        As a Module:
            from text_sentiment.app import TextSentiment
            ts = TextSentiment(file_path="absolute/path/to/file")
            data = ts.process()

        From the command line:
            python3 text_sentiment/app.py -f absolute/path/to/file
            or
            python3 text_sentiment/app.py -c "My string I want analyzed"
    """
    def __init__(self,file_path=None,content=None,db_path=DB_PATH):
        self.file_path = file_path
        self.content = [content]
        self.db_path = db_path

        self.filters = Filters()
        self.db = Database(db_path=db_path) #Compose database connection

        if file_path:
            self.content = self._openfile(file_path)
        self.content = self._wordcount(self._filter(self.content))
        self.populate_datalabels()

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

    def populate_datalabels(self):
        """Initial function to add labels to the main data container"""
        self.data = {}
        self.data.update(table_metrics={})
        self.data.update(words={})
        self.tables = self.db.metadata.tables
        for table in self.tables:
            self.data['table_metrics'].update({table:{}})
            self.data['table_metrics'][table].update(total_frequency=0,
                                                     total_db_value=0,
                                                     sentimentvalue=0)
    def _wordcount(self, content):
        """Counts words in iterable"""
        totalcount = Counter()
        for line in content:
            count = Counter(line)
            totalcount.update(count)
        return totalcount

    def _updateTotalValues(self,frequency,table,value):
        """Update values needed to calculate sentiment value for each table"""
        table_data = self.data['table_metrics'][table]
        if value:
            table_data['total_db_value'] += value * frequency
            table_data['total_frequency'] += frequency
            tdbval,tfreq = table_data['total_db_value'], table_data['total_frequency']
            table_data['sentimentvalue'] =  round((tdbval / tfreq),2)
            return table_data['sentimentvalue']

    def process(self, wordset=None,tables=None,format=None):
        """Process words in wordset and update the main data container with data"""
        if not wordset:
            wordset = self.content
        if not tables:
            tables = self.tables

        for word,frequency in wordset.items():
            word_labels = {word:{'frequency':frequency,'table_value':{}}}
            self.data['words'].update(word_labels)

            for table in tables:
                table,row,value = self._query(table=table,word=word)
                self.data['words'][word]['table_value'].update({table:value})
                self._updateTotalValues(frequency,table,value)

        if format == 'json':
            return json.dumps(self.data,indent=4,sort_keys=True)
        return self.data


def parser():
    parser = argparse.ArgumentParser()
    parser.add_argument('--file_path','--file','-f', default=None, help='File (absolute)path to file for analysis')
    parser.add_argument('--content', '-c', default=None, help='Use with raw strings')
    parser.add_argument('--database', '-db', default=DB_PATH, help='Database (absolute)path to sqlite database.')
    parser.add_argument('--json', action='store_true', default=False, help='Show data with JSON formatting')
    parser.add_argument('--verbose', '-v', action='count', default=0, help='Show all data')
    args = parser.parse_args()
    if not args.file_path and not args.content:
        parser.error("A file path or content is not specified. Use -h for help")
    return(args)

def main():
    args = parser()
    ts = TextSentiment(file_path=args.file_path,content=args.content,db_path=args.database)

    if args.json:
        data = ts.process(format='json')
        print(data)
        return data
    else:
        data = ts.process()

    if args.verbose <= 0:
        print("\nSentiment_Value: ")
        for table in ts.tables:
            print(table,": ",data['table_metrics'][table]['sentimentvalue'])
        print()
        return None
    if args.verbose == 1:
        print("\n___Table_Metrics___")
        for table in ts.tables:
            print('Table:',table)
            print("sentimentvalue: ",data['table_metrics'][table]['sentimentvalue'])
            print('total_frequency: ',data['table_metrics'][table]['total_frequency'])
            print('total_db_value: ',data['table_metrics'][table]['total_db_value'],'\n')
        return None
    if args.verbose >= 2:
        print("\nALL DATA")
        print(data)
    return data

if __name__ == '__main__':
    main()
