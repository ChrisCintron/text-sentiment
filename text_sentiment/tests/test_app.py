from text_sentiment.app import *
from text_sentiment.tests.fixtures.constants import *
import pytest
import copy

@pytest.fixture(scope="session")
def f():
    print("SetupClass:          FileFilter")
    f = FileFilter(file_path=TEST_DOC,chunk_size=3)
    yield f
    print("TeardownClass:          FileFilter")

@pytest.fixture()
def fprint(f):
    print("\n.FF: Setup Method")
    yield #Initiate Method

    print("Pipeline:                    ",f.pipeline)
    if f.pipeline:
        print("    \n___Pipeline Content[Start]___")
        for content in f.pipeline:
            print("    [Content]")
            print("    ",content,"\n")
        print("    ___Pipeline Content[Finish]___")
    print("FF: Teardown Method")

@pytest.fixture(scope="session")
def db(f):
    print("SetupClass:          DBLookup")
    print("Check__init__:       ",)
    f.addfilter(f.openfile)
    f.addfilter(f.makechunk)
    f.addfilter(f.clean)
    f.process()

    db = DBLookup(path_to_db=DB_PATH)
    yield db
    print("TeardownClass:          DBLookup")

@pytest.fixture()
def dbprint(db,f):
    print("\n.DB: Setup Method")
    yield #Initiate Method
    print("DB: Teardown Method")

class TestFileFilter:
    def test_openfile(self,f,fprint):
        print("_openfile()")
        f.addfilter(f.openfile)
        f.process()

    def test_makechunk(self,f,fprint):
        print("_makechunk()")
        f.addfilter(f.openfile)
        f.addfilter(f.makechunk)
        f.process()
        assert next(f.pipeline) == 'This- is line one. My second line. Third line is the charm.'

    def test_clean(self,f,fprint):
        print("clean()")
        f.addfilter(f.openfile)
        f.addfilter(f.makechunk)
        f.addfilter(f.clean)
        f.process()
        assert next(f.pipeline)[0] == 'this'

class TestDBLookup:
    def test_loadtables(self,db,dbprint):
        expectedresults = {('Warriner-English'): {},('labMTwords-English'):{}}
        db.tables = db.loadtables()
        assert db.tables == expectedresults

    def test_loadindices(self,db,dbprint):
        #print("__loadindices__")
        db.indices = (('labMTwords-English_idx',), ('Warriner-English_idx',))
        assert db.indices == db.loadindices()

    def test_createindex(self,db,dbprint):
        string = ["CREATE INDEX 'Warriner-English_idx' ON 'Warriner-English'(word);",
                  "CREATE INDEX 'labMTwords-English_idx' ON 'labMTwords-English'(word);"]
        try:
            assert string == list(db.createindex())
            print("Index Created")
        except:
            print("Indices Present")
            assert [None,None] == list(db.createindex())

    def test_wordsearch(self,db,dbprint):
        dbs = ('Warriner-English_idx', 'labMTwords-English_idx')

    def test_chunksearch(self,f,db,dbprint):
        print("================================================")
        print('table:           ',db.tables)

        for chunk in f.pipeline:
            print('\nchunk:           ',chunk)
            data_tables = db.chunksearch(db.tables,chunk)
            print('wordvalues:        ')
            for table in data_tables:
                print("                 ",table)
                print("                 ",data_tables[table],'\n')

        print("================================================")
