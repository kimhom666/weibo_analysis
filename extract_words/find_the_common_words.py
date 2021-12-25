from sql.sql_tools import pg_tools
import jieba
from collections import Counter
import codecs
db = pg_tools()


def get_stopwords():
    with codecs.open("chineseStopWords.txt", 'rb', 'GB2312') as file:
        word_list = file.read().splitlines()
    # print(word_list)
    return word_list


def get_the_phrase(sql):
    rows = db.select(sql)
    result = ''
    for row in rows:
        result += row[0]
    return result


sql = "select text from comment where weibo_id = '4464733140773077'"
common_words = [x for x in jieba.cut(get_the_phrase(sql)) if (len(x) >= 2 and x not in get_stopwords())] #将全文分割，并将大于两个字的词语放入列表
c=Counter(common_words).most_common(20) #取最多的10组
print(c)