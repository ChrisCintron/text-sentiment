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
def db():
    yield Database(db_path=DB_PATH)

class Test_Database:
    def test_init(self,db):
        expected_output = ['Warriner-English','labMTwords-English']
        output = [table for table in db.metadata.tables]
        assert set(expected_output).issubset(output)

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
        expected_output = ['my','second','line']
        output = ts._filter(content)
        assert next(output) == expected_output

    #@pytest.mark.skip
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

    def test_wordcount(self,ts):
        """Tests specific wordcount and actually returned data structure"""
        word = 'is'
        value = 1
        content = [['my','second','line',
                    'third','line','is','the','charm',
                    'fourth','one','fits','the','bill',]]
        expected_output = value
        output = ts.wordcount(content)[word]
        assert output == expected_output

        content = [['one','two','two','three','three','three']]
        expected_output = Counter({'one':1,'two':2,'three':3})
        output = ts.wordcount(content)
        assert output == expected_output

    def test_pipe(self,ts):
        """Test methods appending to pipeline attribute"""
        print("Also working")
        expected_output = [ts.wordcount]
        output = ts._pipe('wordcount') #test the output of _pipe function
        assert output == expected_output

        ts._pipe('_query')
        output = ts.pipeline #test the actual pipeline attribute
        expected_output = [ts.wordcount,ts._query]
        assert output == expected_output

        with pytest.raises(AttributeError, match=r'.* object has no attribute .*'):
            ts._pipe('fakemethod')

    def test_package(self,ts):
        word = 'one'
        frequency = 1
        table_data = (('Warriner-English',word,6.09),('labMTwords-English',word,5.4))
        output = ts._package(word=word,frequency=frequency,table_data=table_data)
        expected_output = {
                            word: {
                              "frequency":frequency,
                              "tables": {'Warriner-English':6.09,
                                         'labMTwords-English':5.4}
                            }
                          }
        assert output == expected_output
        #print("\nItem: ",json.dumps(output, indent=4,sort_keys=True))

    def test_process(self,ts):
        tables = ts.tables
        wordset = Counter(['one','two','two','three','three','three'])
        output = ts._process(wordset=wordset, tables=tables)
        one = {'one': {'frequency': 1, 'tables': {'Warriner-English': 6.09, 'labMTwords-English':5.4}}}
        two = {'two': {'frequency': 2, 'tables': {'Warriner-English': 6.3, 'labMTwords-English': 5.4}}}
        three = {'three': {'frequency': 3, 'tables': {'Warriner-English': 5.43, 'labMTwords-English': 5.72}}}
        expected_output = dict()
        expected_output.update(one)
        expected_output.update(two)
        expected_output.update(three)
        assert output == expected_output

    #@pytest.mark.skip()
    def test_main(self):
        """Testing arbitrary functionality"""
        string = 'What can you tell me about the brothers that went missing last night? I always wondered what hapens to folks that can break or swim underwater! #Bananaface'
        ts = TextSentiment(content=string,db_path=DB_PATH)
