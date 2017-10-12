import sqlite3
import os


class FileAnalyzer(object):
    """Prepares data for SentimentAnalyzer"""
    def __init__(self,file_path=None):
        self.file_path = file_path
        self.textfile = None


    def line_generator(self):
        """Opens file and generates lines"""
        with open(self.file_path, 'r') as f:
            for line in f:
                line = line.strip('\n')
                yield line

    def word_parsing_generator(self,line_gen):
        """Finds individual words from text
        Checks if all chars in word are alphabetical.

        line in line_gen = "Test I am1 a line"
        words = ('Test', 'I', 'am', 'a', 'line')
        accepted_list = ('Test', 'I', 'a', 'line')
        rejected_list = ('am1',)

        Possibly another way of doing it..
        #filtered_list = tuple(filter(str.isalpha,words))


        """
        for line in line_gen:

            words = tuple(line.split(' '))
            accepted_list = tuple(word for word in words if str.isalpha(word))
            rejected_list = tuple(word for word in words if not str.isalpha(word))

            yield accepted_list,rejected_list

    def count_words(self,listofwords):
        """Counts the number of words in text"""
        pass

    def run(self):
        l = self.line_generator()
        p = self.word_parsing_generator(l)

        #print(next(p))
        #print(next(p))




class DBLookup(object):
    """Connects the wordbank.db"""
    def __init__(self,path_to_local_db):
        pass

    def query(self,word):
        """Queries Database for word"""
        pass

class SentimentAnalyzer(object):
    """Finds the sentiment value of objects"""
    def __init__(self):
        pass

    def word_totalvalue(self):
        """Multiply count by the db's word value"""
        pass

def main():
    testdoc = './text_sentiment/tests/fixtures/testfile.txt'
    f = FileAnalyzer(file_path=testdoc)
    f.run()
    #line_gen = f.line_generator()
    #print(next(line))
    #f.parse_words(line_gen)
    #f.parse_words(line_gen)
    #f.parse_words(line_gen)
    #f.parse_words(line_gen)

    #print(next(line))


if __name__ == '__main__':
    main()
