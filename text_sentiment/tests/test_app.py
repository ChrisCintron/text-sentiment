from text_sentiment.app import *
from text_sentiment.tests.fixtures.constants import *
import pytest

"""Fixtures"""
@pytest.fixture(scope="module")
def f():
    return FileAnalyzer(file_path=TEST_DOC)

@pytest.fixture(scope="module")
def db():
    yield DBLookup(path_to_db=DB_PATH)

"""FileAnalyzer class"""
def test_openfile(f):
    line_gen = f._openfile()
    output = list(line_gen)
    assert len(output) == 7
    assert output[0] == 'This is line one.'

def test_makechunk(f):
    line_gen = f._openfile()
    dirtychunks = f.makechunk(line_gen,3)
    output = list(dirtychunks)
    assert len(output) == 3
    assert output[0] == 'This is line one. My second line. Third line is the charm.'

"""DBLookup class"""
def test_loadtables(db):
    expectedresults = ('Warriner-English', 'labMTwords-English')
    tables = db.loadtables()
    print(tables)
    assert tables == expectedresults

def test_createindex(db):
    print('\n__createindex__')
    string = ["CREATE INDEX 'Warriner-English_idx' ON 'Warriner-English'(word);",
              "CREATE INDEX 'labMTwords-English_idx' ON 'labMTwords-English'(word);"]
    try:
        assert string == list(db.createindex())
        print("Index Created")
    except:
        print("Indices Present")
        assert [None,None] == list(db.createindex())

def test_loadindices(db):
    print("__loadindices__")
    eresults = ('Warriner-English_idx', 'labMTwords-English_idx')
    assert eresults == db.loadindices()

def test_wordsearch(db):
    dbs = ('Warriner-English_idx', 'labMTwords-English_idx')
    #db.wordsearch()
