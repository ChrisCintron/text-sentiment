from text_sentiment.app import *
from text_sentiment.tests.fixtures.constants import *
import pytest

#For later use
"""
@pytest.fixture(scope="class")
def file_class(): #FileAnalyzer class
    fa = FileAnalyzer(file_path=TEST_DOC)
    yield fa
"""
"""
@pytest.fixture(scope="module")
def db(): #DBLookup class
    pass #Initiate
    v = 0
    yield v
    pass #close
"""

class TestFileAnalyzer():
    @pytest.mark.skip
    def test_general(self):
        f = FileAnalyzer(file_path=TEST_DOC)
        line_gen = f._openfile()
        gen1 = f.makechunk(line_generator=line_gen,chunk_size=2)
        gen2 = f.clean(gen1)
        for i in f.countwords(gen2):
            print(i)

    def test_openfile(self):
        f = FileAnalyzer(file_path=TEST_DOC)
        line_gen = f._openfile()
        output = list(line_gen)
        assert len(output) == 7
        assert output[0] == 'This is line one.'

    def test_makechunk(self):
        f = FileAnalyzer(file_path=TEST_DOC)
        line_gen = f._openfile()
        dirtychunks = f.makechunk(line_gen,3)
        output = list(dirtychunks)
        assert len(output) == 3
        assert output[0] == 'This is line one. My second line. Third line is the charm.'

    
