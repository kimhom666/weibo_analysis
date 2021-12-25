from gensim.models import KeyedVectors
import warnings
# from sql.language_processing import get_sentence_scores, get_data
warnings.filterwarnings('ignore')


def load_pre_trained_models():
    path = '/Users/kimhom/Downloads/news_12g_baidubaike_20g_novel_90g_embedding_64.bin'
    cn_model = KeyedVectors.load_word2vec_format(path, binary=True)
    print("成功载入模型")
    return cn_model


cn_model = load_pre_trained_models()
print(cn_model['医生'])
print(cn_model.most_similar('医生'))