import pickle
import numpy as np
import pandas as pd
import data 

moral_df, moral_dict = data.read_moral_lex()

moral_lex = dict()
for moral, df in moral_df.items():
    moral_lex[moral] = df.set_index('LEMMA')

moral_list = list(moral_lex.keys())

def moral_value(word, moral):
    try:
        v = moral_lex[moral].loc[word]['EXPRESSED_MORAL']
    except KeyError:
        v = None
    if isinstance(v, pd.Series):
        return v.values[0]
    return v

def bucketize(x):
    if x is None:
        return np.array([0, 0])
    if x > 5:
        return np.array([0, 1])
    elif x <= 5:
        return np.array([1, 0])
    
def form_word_vector(word):
    v = []
    for moral in moral_lex.keys():
        v_m = bucketize(moral_value(word, moral))
        v.append(v_m)
    return np.concatenate(v)
    
def form_text_vector(text):
    v = []
    for word in text:
        v.append(form_word_vector(word))
    return np.sum(v, axis=0)

def load_models():
    lrs, ngrams = {}, {}
    moral_options = ('care', 'fairness', 'loyalty', 'authority', 'purity', 'non-moral')

    for moral in moral_options:
        with open('export/{}_lr.pck'.format(moral), 'rb') as f:
            lr = pickle.load(f)
        lrs[moral] = lr

        with open('export/{}_ngram.pck'.format(moral), 'rb') as f:
            ngram = pickle.load(f)
        ngrams[moral] = ngram
        
    return lrs, ngrams