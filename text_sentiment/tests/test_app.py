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
    assert len(output)
    assert output[0] == 'This is line one.'

def test_makechunk(f):
    f.chunk_size = 3
    line_generator = f._openfile()
    dirty_chunks = f.makechunk(line_generator,f.chunk_size)
    output = list(dirty_chunks)
    assert len(output)
    assert output[0] == 'This is line one. My second line. Third line is the charm.'

def test_clean(f):
    line_generator = f._openfile()
    dirty_chunks = f.makechunk(line_generator,f.chunk_size)
    clean_chunk = f.clean(dirty_chunks)
    assert clean_chunk

def test_loadtables(db):
    expectedresults = {('Warriner-English'): {},('labMTwords-English'):{}}
    db.tables = db.loadtables()
    assert db.tables == expectedresults

def test_createindex(db):
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
    db.indices = (('labMTwords-English_idx',), ('Warriner-English_idx',))
    assert db.indices == db.loadindices()

@pytest.mark.skip
def test_wordsearch(db):
    dbs = ('Warriner-English_idx', 'labMTwords-English_idx')
    #db.wordsearch()

def test_chunksearch(db,f):
    line_generator = f._openfile()
    dirty_chunks = f.makechunk(line_generator,f.chunk_size)
    clean_chunks = f.clean(dirty_chunks)
    print("================================================")
    print('table:           ',db.tables)
    for chunk in clean_chunks:
        print('\nchunk:           ',chunk)
        data_tables = db.chunksearch(db.tables,chunk)
        print('wordvalues:        ')
        for table in data_tables:
            print("                 ",table)
            print("                 ",data_tables[table],'\n')

    print("================================================")



@pytest.mark.skip
def test_db_main(db):
    db.loadtables()
    db.loadindices()
    db.createindex()
    print(self.chunksearch(self.tables,self.chunk))
    self.connection.close()
