from text_sentiment.app import *
from text_sentiment.tests.fixtures.constants import *
import pytest

#For later use
"""
@pytest.fixture(scope="module")
def specific_func_needed():
    pass #Initiate
    v = 0
    yield v
    pass #close

@pytest.make.parametrize("test_input, text_output",
                        [
                            (),
                            (),
                            (),
                        ])
"""

class TestFileAnalyzer(object):
    def test_general(self):
        f = FileAnalyzer(file_path=TEST_DOC,chunk_size=2)
        line_gen = f._openfile()
        gen1 = f.makechunk(line_generator=line_gen,chunk_size=2)
        gen2 = f.clean(gen1)
        for i in f.countwords(gen2):
            print(i)
