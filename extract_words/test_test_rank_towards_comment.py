from sql.sql_tools import pg_tools
import jieba
from jieba.analyse import textrank,extract_tags
import codecs
import collections
sql_tools = pg_tools()


def get_stopwords():
    with codecs.open("chineseStopWords.txt", 'rb', 'GB2312') as file:
        word_list = file.read().splitlines()
    # print(word_list)
    return word_list


def get_sentences(sql):

    rows = sql_tools.select(sql)
    return rows


def main_function(label):
    print(label)
    sentence_list = get_sentences("select text, comments_id from comment where weibo_id in "
                                  "(select weibo_id from weibo_item where type = '{type}')".format(type=label))
    stopwords = get_stopwords()
    sentence_key_word_dict = {}
    key_word_list = []
    for sentence in sentence_list:
        keywords = textrank(sentence=sentence[0], topK=1, withWeight=True)
        for word in keywords:
            if word[0] not in stopwords:
                sentence_key_word_dict[sentence] = word[0]
                key_word_list.append(word[0])
                insert_sql = "insert into key_word_of_comment(comments_id, key_word, type) " \
                             "values('{comments_id}', '{key_word}', '{type}')".format(key_word=word[0],
                                                                                      comments_id=sentence[1],
                                                                                      type=label)
                sql_tools.insert(insert_sql)

def key_word_of_weibo():
    weibo_item = sql_tools.select("select comments_id, text"
                                  " from comment where comment.weibo_id in "
                                  "(select weibo_id from weibo_item where type "
                                  "='肺炎疫情')")
    print(len(weibo_item))
    word_counts_dict = collections.defaultdict(int)
    for item in weibo_item:
        keywords = textrank(sentence=item[1], topK=1, withWeight=False)
        key_word_list = textrank(sentence=item[1], topK=5, withWeight=False)

        try:
            insert_sql = "insert into summary_key_word (comments_id, key_word, key_word_list) " \
                             "values('{comments_id}', '{key_word}', '{key_word_list}')"\
                            .format(comments_id=item[0], key_word=keywords[0], key_word_list=str(key_word_list).
                                    replace("'","").replace("[","").replace("]",""))

            sql_tools.insert(insert_sql)

        except Exception as e:
            insert_sql = "insert into summary_key_word (comments_id, key_word, key_word_list) " \
                         "values('{comments_id}', '{key_word}', '{key_word_list}')" \
                .format(comments_id=item[0], key_word='', key_word_list='')
            sql_tools.insert(insert_sql)

    #     for word in key_word_list:
    #         word_counts_dict[word] +=1
    # words_list = word_counts_dict.keys()
    # stop_words = get_stopwords()
    # for word in words_list:
    #     if word not in stop_words:
    #         print(word, word_counts_dict[word])
    #         try:
    #             insert_sql = "insert into transportation_cross_key_counts (key_word, counts) " \
    #                              "values('{key_word}','{counts}')"\
    #                             .format(key_word=word, counts=str(word_counts_dict[word]))
    #
    #             sql_tools.insert(insert_sql)
    #
    #         except Exception as e:
    #             print(e)
    #             pass
keywords = textrank(sentence="【#武汉医院视频连线意大利医院#分享新冠肺炎治疗经验】3月4日，武汉同济医院光谷院区内多位专家通过视频向意大利尼瓜尔达医院专家分享同济救治新冠肺炎患者经验。据了解，尼瓜尔达医院已收治200余名新冠肺炎患者。连线中，意方专家详细询问了新冠肺炎疫情防控经验和患者的同济救治方案等。新京报我们视频的秒拍视频@新京报我们视频#武汉医院视频连线意大利医院#分享新冠肺炎治疗经验】3月4日，武汉同济医院光谷院区内多位专家通过视频向意大利尼瓜尔达医院专家分享同济救治新冠肺炎患者经验。"
                             "据了解，尼瓜尔达医院已收治200余名新冠肺炎患者。连线中，意方专家详细询问了新冠肺炎疫情防控经验和患者的同济救治方案等。新京报我们视频的秒拍视频@新京报我们视频",
                    topK=5, withWeight=True)
print(keywords)