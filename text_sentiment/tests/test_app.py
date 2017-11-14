import pytest
import types

#context file adjust our working directory in order to access app
from context import app
from app import *


@pytest.fixture()
def fileobj():
    yield FileObj(file_path=TEST_DOC,)

class Test_FileObj:
    def test_init(self):
        fileobj = FileObj(file_path=TEST_DOC,)
        assert fileobj

    def test_openfile(self,fileobj):
        content = fileobj.openfile()
        assert isinstance(content,types.GeneratorType)

    def test_filter(self,fileobj):
        content = fileobj.openfile()
        content = fileobj.filter(content)
        assert isinstance(content,types.GeneratorType)

    def test_run(self,fileobj):
        fileobj.run()
        assert isinstance(fileobj.content,types.GeneratorType)

@pytest.fixture()
def db():
    yield Database(db_path=DB_PATH)

class Test_Database:
    def test_init(self):
        db = Database(db_path=DB_PATH)

    def test_query(self,db):
        table = 'Warriner-English'
        #table = db.metadata.tables[table_name]
        #type(db.metadata.tables['Warriner-English'])
        assert db.query(table=table, word='love') == {'love': 8}
        assert db.query(table=table, word='rest') == {'rest': 7.86}
        assert db.query(table=table, word='brute') == {'brute': 3.48}

        assert db.query(table=table, word='132s') == {'132s': 0}
        assert db.query(table=table, word='x2') == {'x2': 0}
        assert db.query(table=table, word='a') == {'a': 0}

@pytest.fixture()
def ts():
    yield TextSentiment(file_path=TEST_DOC,db_path=DB_PATH)

class Test_TextSentiment:
    def test_init(self):
        labels = ['metrics','words']
        ts = TextSentiment(file_path=TEST_DOC,db_path=DB_PATH)
        assert ts.data == {}

    @pytest.mark.skip
    def test_createlabels(self,ts):
        data = {}
        labels = {'metrics','words'}
        results = ts._createlabels(labels,value={})
        print(results)

    def test_run(self,ts,db):
        ts.run()
        print(ts.data)

class Test_NumberCruncher:

    @pytest.fixture(autouse=True)
    def nc(self):
        self.line = "My word My word does not equal one".split(' ')
        yield NumberCruncher

    def test_wordcount(self,nc,ts):
        wordcounts = nc.wordcount(ts.filtered_content)
        #assert wordcounts['i'] == 30

@pytest.mark.skip
def test_main():
    string = "I love having fun!"
    data = TextSentiment(db_path=DB_PATH, content=string)

    path = TEST_DOC
    data = TextSentiment(db_path=DB_PATH, file_path=TEST_DOC)
    data.sentimentvalue
