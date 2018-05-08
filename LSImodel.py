import pandas as pd
from gensim import corpora, models, similarities
from gensim.corpora import Dictionary
from nltk.corpus import stopwords
import pymorphy2
import re
import json
from gensim.test.utilsgensim.te  import common_corpus, common_dictionary
from gensim.similarities import MatrixSimilarity

def make_data(csv_path):
    df = pd.read_csv(csv_path)

    documents = []
    for col in df.columns:
        documents.append(df[col].dropna().tolist())
    dct = corpora.Dictionary(documents)
    dct.save('deerwester.dict')
    corpus = [dct.doc2bow(doc) for doc in documents]
    corpora.MmCorpus.serialize('deerwester.mm', corpus)  # store to disk, for later use
    return corpus, dct

def tokenize_text(text):
    #tokens = text.rstrip()
    tokens = re.sub("[^\w]", " ", text).split()
    tokens = [t.lower() for t in tokens]
    tokens = [morph.parse(word)[0].normal_form for word in tokens]
    #tokens = [i for i in tokens if (i not in stop_words)]
    return ' '.join(tokens)

def make_doc(doc):
    prog = re.compile('[А-Яа-я]+')
    doc = prog.findall(doc.lower())
    doc = [morph.parse(token)[0].normal_form for token in doc]
    return doc

def make_query(query_path):
    with open(query_path, 'r', encoding='utf8') as file:
        query = json.load(file)
    doc = query['text']
    doc = tokenize_text(doc)
    doc = make_doc(doc)
    return doc

if __name__ == '__main__':

    corpus, dct = make_data('value.csv')
    number_of_topics = 2

    lsi = models.LsiModel(corpus, id2word = dct, num_topics = number_of_topics)
    morph = pymorphy2.MorphAnalyzer()

    doc = make_query('query.json')

    vec_bow = dct.doc2bow(doc)
    vec_lsi = lsi[vec_bow]  # convert the query to LSI space
    print(vec_lsi)
    index = similarities.MatrixSimilarity(lsi[corpus])
    sims = index[vec_lsi]  # perform a similarity query against the corpus
    print(list(enumerate(sims)))  # print (document_number, document_similarity) 2-tuples
    sims = sorted(enumerate(sims), key=lambda item: -item[1])
    print(sims)  # print sorted (document number, similarity score) 2-tuples