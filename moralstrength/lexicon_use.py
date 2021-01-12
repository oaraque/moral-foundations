import numpy as np
import pandas as pd
from moralstrength import data 
from moralstrength.moral_list import moral_options_lexicon

moral_lex = data.read_moral_lex('original')
new_moral_lex = data.read_moral_lex('1.1')
current_moral_lex = new_moral_lex

def select_version(version):
    global current_moral_lex
    if version == 'original':
        current_moral_lex = moral_lex
    elif version == 'latest':
        current_moral_lex = new_moral_lex

def moral_value(word, moral, normalized=False):
    value = __private_moral_value(word, moral)
    if value==-1:
        return float('NaN')
    #annotation is between 1 and 9
    if normalized:
        value = (value-1)/8
    return value

def __private_moral_value(word, moral):
    v = moral_lex[moral].get(word, -1)
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
    for moral in moral_options_lexicon:
        v_m = __private_moral_value(word, moral)
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

