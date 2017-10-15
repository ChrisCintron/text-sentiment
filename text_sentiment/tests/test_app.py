from text_sentiment.app import *
from text_sentiment.tests.fixtures.constants import *
import pytest
import copy


@pytest.fixture(scope="module")
def f():
    f = FileAnalyzer(file_path=TEST_DOC)
    yield f

@pytest.fixture(scope="module")
def db():
    db = DBLookup(path_to_db=DB_PATH)
    yield db

def test_openfile(f):
    line_generator = f._openfile()
    output = list(line_generator)
    assert len(output) == 7
    assert output[0] == 'This is line one.'

def test_makechunk(f):
    f.chunk_size = 3
    line_generator = f._openfile()
    dirty_chunks = f.makechunk(line_generator,f.chunk_size)
    output = list(dirty_chunks)
    assert len(output) == 3
    assert output[0] == 'This is line one. My second line. Third line is the charm.'

def test_clean(f):
    line_generator = f._openfile()
    dirty_chunks = f.makechunk(line_generator,f.chunk_size)
    clean_chunk = f.clean(dirty_chunks)
    assert clean_chunk

def test_loadtables(db):
    expectedresults = ('Warriner-English', 'labMTwords-English')
    db.tables = db.loadtables()
    #print(db.tables)
    assert db.tables == expectedresults

def test_createindex(db):
    #print('\n__createindex__')
    string = ["CREATE INDEX 'Warriner-English_idx' ON 'Warriner-English'(word);",
              "CREATE INDEX 'labMTwords-English_idx' ON 'labMTwords-English'(word);"]
    try:
        assert string == list(db.createindex())
        print("Index Created")
    except:
        print("Indices Present")
        assert [None,None] == list(db.createindex())

def test_loadindices(db):
    #print("__loadindices__")
    db.indices = ('Warriner-English_idx', 'labMTwords-English_idx')
    assert db.indices == db.loadindices()

def test_wordsearch(db):
    dbs = ('Warriner-English_idx', 'labMTwords-English_idx')
    #db.wordsearch()
def test_chunksearch(db,f):
    line_generator = f._openfile()
    dirty_chunks = f.makechunk(line_generator,f.chunk_size)
    clean_chunk = f.clean(dirty_chunks)

    r = db.chunksearch(db.tables,clean_chunk)
