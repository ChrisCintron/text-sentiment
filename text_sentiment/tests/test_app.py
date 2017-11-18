import pytest
import types
from context import app #context file adjust our working directory in order to access app
from app import *
from fixtures.constants import *

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
        expected_output = 'Contain filters used to filter the contents from textfile'
        output = filterobj.remove_badchars(line)
        assert output == expected_output

    def test_make_lowercase(self,filterobj):
        line = 'ContAiN fIlterS uSeD to fiLTer thE contenTS fRom texTFILE'
        expected_output = 'contain filters used to filter the contents from textfile'
        output = filterobj.make_lowercase(line)
        assert output == expected_output

    def test_split(self,filterobj):
        line = 'Contain filters used to filter the contents'
        expected_output = ['Contain','filters','used','to','filter','the','contents']
        output = filterobj.split(line)
        assert output == expected_output

    def test_filter(self,filterobj):
        line = 'Cont1*7ain f@#9ILTErs us9]ed TO fIltER the+ ContenTS'
        expected_output = ['contain','filters','used','to','filter','the','contents']
        output = filterobj.filter(line)
        assert output == expected_output

@pytest.fixture()
def database():
    yield Database(db_path=DB_PATH)

class Test_Database:
    def test_init(self,database):
        expected_output = ['Warriner-English','labMTwords-English']
        output = [table for table in database.metadata.tables]
        assert set(expected_output).issubset(output)

    def test_query(self,database):
        table = 'Warriner-English'
        assert database.query(table=table, word='love') == (table, 'love', 8)
        assert database.query(table=table, word='rest') == (table, 'rest', 7.86)
        assert database.query(table=table, word='grave') == (table, 'grave', 2.4)
        assert database.query(table=table, word='132s') == (table, '132s', 0)
        assert database.query(table=table, word='x2') == (table, 'x2', 0)
        assert database.query(table=table, word='yelack') == (table, 'yelack', 0)

        table = 'labMTwords-English'
        assert database.query(table=table, word='love') == (table, 'love', 8.42)
        assert database.query(table=table, word='rest') == (table, 'rest', 7.18)
        assert database.query(table=table, word='grave') == (table, 'grave', 2.56)
        assert database.query(table=table, word='132s') == (table, '132s', 0)
        assert database.query(table=table, word='x2') == (table, 'x2', 0)
        assert database.query(table=table, word='yelack') == (table, 'yelack', 0)


@pytest.fixture()
def ts():
    yield TextSentiment(file_path=TEST_DOC,db_path=DB_PATH)

class Test_TextSentiment:
    def test_openfile(self,ts):
        file_path = TEST_DOC
        output_1_correct = 'My second line.'
        output_2_correct = 'Third line is the charm.'
        output_3_correct = 'Fourth one fits the bill.'
        output = ts._openfile(file_path)
        assert next(output) == output_1_correct
        assert next(output) == output_2_correct
        assert next(output) == output_3_correct

    def test_filter(self,ts):
        content = ['My Second Line']
        expected_output = ['my','second','line']
        output = ts._filter(content)
        assert next(output) == expected_output

    def test_query(self,ts):
        """Test single word query on both tables"""
        tables = ['Warriner-English','labMTwords-English']
        word = 'love'
        expected_output = (tables[0], 'love', 8)
        output = ts._query(table=tables[0], word=word)
        assert output == expected_output

        expected_output = (tables[1], 'love', 8.42)
        output = ts._query(table=tables[1], word=word)
        assert output == expected_output

    def populate_datalabels(self,ts):
        ts.populate_datalabels

    def test_wordcount(self,ts):
        """Tests specific wordcount and actually returned data structure"""
        word = 'is'
        value = 1
        content = [['my','second','line',
                    'third','line','is','the','charm',
                    'fourth','one','fits','the','bill',]]
        expected_output = value
        output = ts._wordcount(content)[word]
        assert output == expected_output

        content = [['one','two','two','three','three','three']]
        expected_output = Counter({'one':1,'two':2,'three':3})
        output = ts._wordcount(content)
        assert output == expected_output

    def test_process(self,ts):
        tables = ts.tables
        wordset = Counter(['one','two','two','three','three','three'])
        #output = ts.process(wordset=wordset, tables=tables,formatter='json')
        output = ts.process(wordset=wordset, tables=tables)
        #output = json.loads(output)
        assert output['table_metrics']['Warriner-English']['sentimentvalue'] == 5.83
        assert round(output['table_metrics']['Warriner-English']['total_db_value'],2) == 34.98
        assert output['table_metrics']['Warriner-English']['total_frequency'] == 6
        assert output['table_metrics']['labMTwords-English']['sentimentvalue'] == 5.56
        assert output['table_metrics']['labMTwords-English']['total_db_value'] == 33.36
        assert output['table_metrics']['labMTwords-English']['total_frequency'] == 6
        assert output['words']['one']['frequency'] == 1
        assert output['words']['one']['table_value']['Warriner-English'] == 6.09
        assert output['words']['one']['table_value']['labMTwords-English'] == 5.4
        assert output['words']['two']['frequency'] == 2
        assert output['words']['two']['table_value']['Warriner-English'] == 6.3
        assert output['words']['two']['table_value']['labMTwords-English'] == 5.4
        assert output['words']['three']['frequency'] == 3
        assert output['words']['three']['table_value']['Warriner-English'] == 5.43
        assert output['words']['three']['table_value']['labMTwords-English'] == 5.72

    def test_updatetotalvalues(self,ts):
        table = 'Warriner-English'
        frequency,table_value = 1, 6.04
        output = ts._updatetotalvalues(frequency,table,table_value)
        expected_output = 6.04
        assert output == expected_output

        frequency,table_value = 2, 3
        output = ts._updatetotalvalues(frequency,table,table_value)
        expected_output = 4.01
        assert output == expected_output

    def test_main(self,ts):
        """Test overall functionality"""
        string = "What can you tell me about the brother that went missing last night? I always wondered what hapens to folks that can't swim underwater! #Bananaface"
        ts = TextSentiment(file_path=TEST_DOC)
        data = ts.process(formatter='json')
        print(data)
