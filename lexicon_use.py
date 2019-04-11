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
        v = -1
    if isinstance(v, pd.Series):
        return v.values[0]
    return v

def bucketize(x):
    if x == -1 :
        return np.array([0, 0])
    if x > 5:
        return np.array([0, 1])
    elif x <= 5:
        return np.array([1, 0])
    
def form_word_vector(word, bucketize_=None):
    v = []
    for moral in moral_lex.keys():
        v_m = moral_value(word, moral)
        if bucketize_ is not None:
            v_m = bucketize_(v_m)
        v.append(v_m)

    if bucketize_ is not None:
        return np.concatenate(v)

    v = np.array(v)
    return v
    
def form_text_vector(text, model='count'):
    '''
    model: count of freq
    '''
    if model == 'count':
        bucketize_ = bucketize
    elif model == 'freq':
        bucketize_ = None

    v = []
    for word in text:
        v.append(form_word_vector(word, bucketize_=bucketize_))
    if model == 'count':
        return np.sum(v, axis=0)
    elif model == 'freq':
        return np.concatenate(
            (
                np.average(v, axis=0),
                np.std(v, axis=0),
                np.median(v, axis=0),
                np.max(v, axis=0),
        ))

