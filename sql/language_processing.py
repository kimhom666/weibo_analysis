import jieba
from sql.sql_tools import pg_tools
from snownlp import SnowNLP

db = pg_tools()
handled = db.select("select distinct comments_id from text_score")
handled_list = []
for item in handled:
    handled_list.append(handled[0][0])

def get_words_count(word_list):
    word_counts = {}
    for word in word_list:
        if len(word) == 1:
            continue
        else:
            word_counts[word] = word_counts.get(word, 0) + 1
    items = list(word_counts.items())  # 将键值对转换成列表
    items.sort(key=lambda x: x[1], reverse=True)  # 根据词语出现的次数进行从大到小排序
    return items


def get_sentence_scores(sentence_list):
    for sentence in sentence_list:
        if len(sentence) == 0:
            continue
        print(sentence)
        sentence_score = SnowNLP(sentence)
        print(sentence_score.sentiments)


def get_data():
    sql_tools = pg_tools()
    rows = sql_tools.select("select * from comment where weibo_id = '4462503775931329'")
    all_text = ''
    for item in rows:
        all_text += str(item[0]) + ';\n'
    return all_text


def get_sentences(sql):
    sql_tools = pg_tools()
    rows = sql_tools.select(sql)
    return rows


def main_function(label):
    sql = "select comments_id,text from comment where weibo_id in " \
          "(select a.weibo_id from weibo_item a where a.type like '%{type}%') and text != ''".format(type=label)
    sentence_list = get_sentences(sql)
    for item in sentence_list:
        id = item[0]
        if id in handled_list:
            print("已经处理")
            continue
        text = item[1]
        sentence_score = SnowNLP(text)
        db.insert("insert into text_score(comments_id, score, type) values('{comments_id}','{score}', '{type}')"
                  .format(comments_id=item[0], score=sentence_score.sentiments,  type=label))


if __name__ == '__main__':
    labels = []
    for item in db.select("select distinct type from weibo_item where type is not null"):
        labels.append(item[0])
    for label in labels:
        main_function(label)
