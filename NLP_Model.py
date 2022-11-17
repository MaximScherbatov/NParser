import pickle
import string
import re
from nltk.stem import *
from nltk.corpus import stopwords
from nltk.stem.snowball import SnowballStemmer
from nltk import word_tokenize
from pymystem3 import Mystem
from string import punctuation
from sklearn.linear_model import LogisticRegression

mystem = Mystem()
with open('LogRegModel_sw.nlp', 'rb') as f:
    LogRegModel_tags = pickle.load(f)

russian_stopwords = ['и','в', 'во', 'не', 'что', 'он', 'на', 'я', 'с', 'со', 'как', 'а',
                     'то', 'все', 'она', 'так', 'его', 'но', 'да', 'ты', 'к', 'у', 'же',
                     'вы', 'за', 'бы', 'по', 'только', 'ее', 'мне', 'было', 'вот', 'от',
                     'меня', 'еще', 'нет', 'о', 'из', 'ему', 'теперь', 'когда', 'даже',
                     'ну', 'вдруг', 'ли', 'если', 'уже', 'или', 'ни', 'быть', 'был', 'него',
                     'до', 'вас', 'нибудь', 'опять', 'уж', 'вам', 'ведь', 'там', 'потом',
                     'себя', 'ничего', 'ей', 'может', 'они', 'тут', 'где', 'есть', 'надо', 'ней',
                     'для', 'мы', 'тебя', 'их', 'чем', 'была', 'сам', 'чтоб', 'без', 'будто',
                     'чего', 'раз', 'тоже', 'себе', 'под', 'будет', 'ж', 'тогда', 'кто', 'этот',
                     'того', 'потому', 'этого', 'какой', 'совсем', 'ним', 'здесь', 'этом', 'один',
                     'почти', 'мой', 'тем', 'чтобы', 'нее', 'сейчас', 'были', 'куда', 'зачем', 'всех',
                     'никогда', 'можно', 'при', 'наконец', 'два', 'об', 'другой', 'хоть', 'после', 'над',
                     'больше', 'тот', 'через', 'эти', 'нас', 'про', 'всего', 'них', 'какая', 'много', 'разве',
                     'три', 'эту', 'моя', 'впрочем', 'хорошо', 'свою', 'этой', 'перед', 'иногда', 'лучше', 'чуть',
                     'том', 'нельзя', 'такой', 'им', 'более', 'всегда', 'конечно', 'всю', 'между', '…', '«', '»',
                     '...', '<br/>', 'br ']


def remove_punctuation(text):
    return "".join([ch if ch not in '!"#$%&\'()*+,-./:;<=>?@[\\]^_`{|}~' else ' ' for ch in text])

def remove_numbers(text):
    return ''.join([i if not i.isdigit() else ' ' for i in text])

def remove_multiple_spaces(text):
    return re.sub(r'\s+', ' ', text, flags=re.I)


def lemmatize_text(text):
    tokens = mystem.lemmatize(text.lower())
    tokens = [token for token in tokens if token not in russian_stopwords and token != " "]
    text = " ".join(tokens)
    return text

def remove_stop_words(text):
    tokens = word_tokenize(text)
    tokens = [token for token in tokens if token not in russian_stopwords and token != ' ']
    return " ".join(tokens)

def tag_prediction(text):
    x = remove_stop_words(remove_multiple_spaces(remove_numbers(remove_punctuation(text.lower()))))
    tag = LogRegModel_tags.predict([x])[0]
    return tag


