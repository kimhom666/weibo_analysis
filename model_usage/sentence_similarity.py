from model_usage.load_model import load_pre_trained_models
import jieba
import numpy as np
from scipy.linalg import norm
from sql.sql_tools import pg_tools

db = pg_tools()

cn_model = load_pre_trained_models()


def sentence_vector(s):
    words = jieba.lcut(s)
    v = np.zeros(64)
    for word in words:
        try:
            v += cn_model[word]
        except Exception as e:
            pass
    v /= len(words)
    return v


def vector_similarity(s1, s2):
    v1, v2 = sentence_vector(s1), sentence_vector(s2)
    return np.dot(v1, v2) / (norm(v1) * norm(v2))
#

def main_function(label):
    print(label)
    key_word = db.select("select key_word from key_word_of_comment where type = '{label}'"
                         " group by key_word having count(key_word) > 20".format(label=label))
    text_sql = "select comments_id, text from comment " \
               "where comments_id in (select distinct comments_id from key_word_of_comment " \
               "where key_word = '{key}' and type = '{label}') order by like_counts desc limit 10"
    another_text_sql = "select comments_id, text from comment " \
                       "where comments_id in (select distinct comments_id from key_word_of_comment " \
                       "where key_word = '{key}' and type = '{label}')"
    for key in key_word:
        target_text_list = db.select(text_sql.format(key=key[0], label=label))  # 10 items
        another_target_text_list = db.select(another_text_sql.format(key=key[0], label=label))  # all items
        for target_text in target_text_list:  # 0 id, 1 text
            # print(target_text)
            for text in another_target_text_list:
                similarity = vector_similarity(target_text[1], text[1])
                if similarity > 0.6 and similarity != 1:
                    try:
                        db.insert("insert into text_similarity(comments_id_1, comments_id_2, similarity)"
                              " values('{comments_id_1}','{comments_id_2}',{similarity})"
                              .format(comments_id_1=target_text[0], comments_id_2=text[0], similarity=similarity))

                    except Exception as e:
                        print(e)
                        pass


def text_similarity(label):
    print(label)
    # another_text_sql = "select comments_id, text from comment where comments_id in (select comments_id from weibo_item " \
    #            "where type = '{label}')".format(label=label)
    weibo_id_sql = "select weibo_id from weibo_item where type = '{label}'".format(label=label)
    weibo_list = db.select(weibo_id_sql)
    handled_list = []
    print(len(weibo_list))
    for weibo_id in weibo_list:
        top_10_sql = "select comments_id, text from comment where weibo_id = '{weibo_id}' " \
                     "order by like_counts desc limit 10".format(weibo_id=weibo_id[0])
        text_list_sql = "select comments_id, text from comment where weibo_id = '{weibo_id}'".format(weibo_id=weibo_id[0])
        text_list = db.select(text_list_sql)
        top_10_comment = db.select(top_10_sql)
        for comment_item in top_10_comment:
            for index in range(len(text_list)):
                try:
                    similarity = vector_similarity(comment_item[1], text_list[index][1])
                except Exception as e:
                    similarity = 0
                if similarity>0.8 and similarity != 1:
                    try:
                        db.insert("insert into text_similarity(comments_id_1, comments_id_2, similarity)"
                                  " values('{comments_id_1}','{comments_id_2}',{similarity})"
                                  .format(comments_id_1=comment_item[0],
                                          comments_id_2=text_list[index][0],
                                          similarity=similarity))

                    except Exception as e:
                        print(e)
                        pass

def gaokao_main():
    info = db.select("select comments_id, text from comment where comment.weibo_id in (select distinct weibo_item.weibo_id from "
                     "weibo_item where type like '%教育%' and content like '%高考%' )")
    handled_list = []
    category = 0
    for index_1 in range(len(info)):
        category += 1
        if index_1 in handled_list:
            continue

        for index_2 in range(index_1+1, len(info)):
            if index_2 in handled_list:
                continue
            try:
                similarity = vector_similarity(info[index_1][1], info[index_2][1])
            except Exception as e:
                print(e)
                continue
            if similarity > 0.9:
                db.insert("insert into gaokao_attitudes(comments_id, text, category) "
                          "values('{comments_id}','{text}','{category}')".format(comments_id=info[index_1][0],
                                                                                 text=info[index_1][1],
                                                                                 category=str(category)))
                db.insert("insert into gaokao_attitudes(comments_id, text, category) "
                          "values('{comments_id}','{text}','{category}')".format(comments_id=info[index_2][0],
                                                                                 text=info[index_2][1],
                                                                                 category=str(category)))
                handled_list.append(index_2)


if __name__ == '__main__':
    labels = []
    for item in db.select("select distinct type from weibo_item where type is not null and type != '肺炎疫情'"):
        labels.append(item[0])
    for label in labels:
        text_similarity(label)
