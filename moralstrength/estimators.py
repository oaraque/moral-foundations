import os
import numpy as np
import pickle
from sklearn.pipeline import Pipeline
from gsitk.preprocess import pprocess_twitter, simple, Preprocesser

from moralstrength.lexicon_use import form_text_vector

moral_options = ('care', 'fairness', 'loyalty', 'authority', 'purity', 'non-moral')
models = (
    'simon', 'unigram', 'count', 'freq',
    'simon+count', 'simon+freq', 'simon+count+freq',
    'unigram+count', 'unigram+freq', 'unigram+count+freq',
    'simon+unigram+count', 'simon+unigram+freq', 'simon+unigram+count+freq',
)

sorter = {'simon': 0, 'unigram': 1, 'count': 2, 'freq': 3}

pp_pipe = Pipeline([
        ('twitter', Preprocesser(pprocess_twitter)),
        ('simple', Preprocesser(simple)),
])

def generate_model_name(names):
    names = sorted(zip(names, [sorter[i] for i in names]), key=lambda x: x[1])
    return '+'.join([n[0] for n in names])

def pck_name(model_name, moral, transformer=False, transformer_name='unigram'):
    if not transformer:
        return "{}_{}_lr".format(model_name, moral)
    if transformer_name == 'unigram':
        return "ngram"
    elif transformer_name == 'simon':
        return "simon_{}".format(moral)

def load_model(model_name):
    dir_path = os.path.dirname(os.path.realpath(__file__))
    model_path = 'export/{}.pck'.format(model_name)
    full_path = os.path.join(dir_path, model_path)
    with open(full_path, 'rb') as f:
        m = pickle.load(f)
    return m

def load_models(estimators, transformers, moral):
    model_name = generate_model_name(estimators)
    lr = load_model(pck_name(model_name, moral))

    trans = {}
    for transformer in transformers:
        if transformer == 'unigram' or transformer == 'simon':
            name_tmp = pck_name(
                transformer, moral,
                transformer=True, transformer_name=transformer
                )
            trans[transformer] = load_model(name_tmp)
        else:
            trans[transformer] = None

    return lr, trans

def get_estimators(estimator_name):
    return estimator_name.split('+')

def select_processes(process_names, moral):
    estimators = get_estimators(process_names)
    transformers = []
    for estimator in estimators:
        transformers.append(estimator)
        #if estimator == 'simon':
        #    transformers.append('simon')
        #elif estimator == 'unigram':
        #    transformers.append('unigram')
    return estimators, transformers



def estimate(text, moral, model='count', from_file=False):
    if not from_file:
        text_processed = pp_pipe.transform([text])
    else:
        with open('lines.txt', 'r') as f:
            lines = f.readlines()
        lines = [line.strip() for line in lines]
        text_processed = pp_pipe.transform(lines)

    estimators, transformers = select_processes(model, moral)
    lr, transformers = load_models(estimators, transformers, moral)

    X = []
    for transformer in transformers.keys():
        if transformer == 'unigram':
            X_tmp = transformers[transformer].transform([' '.join(t) for t in text_processed])
            X_tmp = X_tmp.toarray()
            X.append(X_tmp)
        elif transformer == 'simon':
            X_tmp = transformers[transformer].transform(text_processed)
            X.append(X_tmp)
        else: 
            X_tmp = [form_text_vector(t, model=transformer) for t in text_processed]    
            X.append(X_tmp)
    X = np.hstack(X)

    return lr.predict_proba(X)[:, 1]
