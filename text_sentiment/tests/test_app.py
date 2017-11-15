import pytest
import types
from context import app #context file adjust our working directory in order to access app
from app import *

class Test_Filters:
    @pytest.fixture(autouse=True)
    def filterobj(self):
        self.line = 'Cont1ain filt2ers us1ed to filter th103e con*tents from textfile'
        yield Filters()

    def test_init(self,filterobj):
        """Split has to be the last function to be called"""
        assert filterobj.order.pop() == 'split'

    def test_remove_badchars(self,filterobj):
        line = 'Cont1ain filt2ers us1ed to filter th103e con*tents from textfile'
        output_correct = 'Contain filters used to filter the contents from textfile'
        output = filterobj.remove_badchars(line)
        assert output == output_correct

    def test_make_lowercase(self,filterobj):
        line = 'ContAiN fIlterS uSeD to fiLTer thE contenTS fRom texTFILE'
        output_correct = 'contain filters used to filter the contents from textfile'
        output = filterobj.make_lowercase(line)
        assert output == output_correct

    def test_split(self,filterobj):
        line = 'Contain filters used to filter the contents'
        output_correct = ['Contain','filters','used','to','filter','the','contents']
        output = filterobj.split(line)
        assert output == output_correct

    def test_filter(self,filterobj):
        line = 'Cont1*7ain f@#9ILTErs us9]ed TO fIltER the+ ContenTS'
        output_correct = ['contain','filters','used','to','filter','the','contents']
        output = filterobj.filter(line)
        assert output == output_correct

@pytest.fixture()
def db():
    yield Database(db_path=DB_PATH)

class Test_Database:
    def test_init(self,db):
        output_correct = ['Warriner-English','labMTwords-English']
        output = [table for table in db.metadata.tables]
        assert set(output_correct).issubset(output)

    def test_query(self,db):
        table = 'Warriner-English'
        assert db.query(table=table, word='love') == (table, 'love', 8)
        assert db.query(table=table, word='rest') == (table, 'rest', 7.86)
        assert db.query(table=table, word='grave') == (table, 'grave', 2.4)
        assert db.query(table=table, word='132s') == (table, '132s', 0)
        assert db.query(table=table, word='x2') == (table, 'x2', 0)
        assert db.query(table=table, word='yelack') == (table, 'yelack', 0)

        table = 'labMTwords-English'
        assert db.query(table=table, word='love') == (table, 'love', 8.42)
        assert db.query(table=table, word='rest') == (table, 'rest', 7.18)
        assert db.query(table=table, word='grave') == (table, 'grave', 2.56)
        assert db.query(table=table, word='132s') == (table, '132s', 0)
        assert db.query(table=table, word='x2') == (table, 'x2', 0)
        assert db.query(table=table, word='yelack') == (table, 'yelack', 0)


@pytest.fixture()
def ts():
    yield TextSentiment(file_path=TEST_DOC,db_path=DB_PATH)

class Test_TextSentiment:
    #@pytest.mark.skip()
    def test_init(self,ts):
        pass

    #@pytest.mark.skip()
    def test_openfile(self,ts):
        file_path = TEST_DOC
        output_1_correct = 'My second line.'
        output_2_correct = 'Third line is the charm.'
        output_3_correct = 'Fourth one fits the bill.'
        output = ts._openfile(file_path)
        assert next(output) == output_1_correct
        assert next(output) == output_2_correct
        assert next(output) == output_3_correct

    #@pytest.mark.skip()
    def test_filter(self,ts):
        content = ['My Second Line']
        output_correct = ['my','second','line']
        output = ts._filter(content)
        assert next(output) == output_correct

    #@pytest.mark.skip
    def test_query(self,ts):
        """Test single word query on both tables"""
        tables = ['Warriner-English','labMTwords-English']
        word = 'love'
        output_correct = (tables[0], 'love', 8)
        output = ts._query(table=tables[0], word=word)
        assert output == output_correct

        output_correct = (tables[1], 'love', 8.42)
        output = ts._query(table=tables[1], word=word)
        assert output == output_correct

    def test_wordcount(self,ts):
        """Tests specific wordcount and actually returned data structure"""
        word = 'is'
        value = 1
        content = [['my','second','line',
                    'third','line','is','the','charm',
                    'fourth','one','fits','the','bill',]]
        output_correct = value
        output = ts.wordcount(content)[word]
        assert output == output_correct

        content = [['one','two','two','three','three','three']]
        output_correct = Counter({'one':1,'two':2,'three':3})
        output = ts.wordcount(content)
        assert output == output_correct
