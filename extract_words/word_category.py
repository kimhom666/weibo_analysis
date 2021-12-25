from sql.sql_tools import pg_tools
from model_usage.load_model import load_pre_trained_models
import jieba.analyse

db = pg_tools()


def contains_same_item(l1, l2):
    for item in l1:
        if item in l2:
            print("contains")
            return True
    return False


def main_function(label, cn_model):

    key_word_list = db.select("select distinct key_word from key_word_of_comment "
                              "where type = '{type}'".format(type=label))
    category = 0
    category_list = []
    handled_list = []
    for index in range(len(key_word_list)):
        if index in handled_list:
            continue
        temp_list = []
        try:
            cn_model.get_vector(key_word_list[index][0])
        except Exception as e:
            continue
        temp_list.append(key_word_list[index][0])
        db.update("update key_word_of_comment set category = '{index}'"
                  " where key_word = '{keyword}' and type='{type}'".format(index=index,
                                                                           keyword=key_word_list[index][0],
                                                                           type=label))
        for index_2 in range(index+1, len(key_word_list)):
            try:
                similarity = cn_model.similarity(key_word_list[index][0], key_word_list[index_2][0])
            except Exception as e:
                continue
            if similarity > 0.6:
                db.update("update key_word_of_comment set category = '{index}'"
                          " where key_word = '{keyword}' and type = '{type}'".format(index=index,
                                                                                    keyword=key_word_list[index_2][0],
                                                                                    type=label))
                temp_list.append(key_word_list[index_2][0])
                handled_list.append(index_2)

        category_list.append(temp_list)
labels = []
for item in db.select("select distinct type from weibo_item where type is not null and type != '肺炎疫情'"):
    labels.append(item[0])
cn_model = load_pre_trained_models()
for label in labels:
    main_function(label, cn_model)