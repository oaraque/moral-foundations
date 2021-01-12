import os
import numpy as np
import pandas as pd
from glob import glob
from gsitk.preprocess import pprocess_twitter, simple, Preprocesser
from sklearn.pipeline import Pipeline

## Read dataset
def read_tw_csv(path, split):
    df = pd.read_csv(path, sep='\t', header=None, names=['label', 'text_raw'])
    df['split'] = split
    return df

def read_dataset():
    tw_train = read_tw_csv('data/twitter/train/shuffled_dataset_LSTM.csv', 'train')
    tw_test = read_tw_csv('data/twitter/test/shuffled_dataset_LSTM.csv', 'test')
    dataset = pd.concat([tw_train, tw_test], axis=0).reset_index()

    pp_pipe = Pipeline([
        ('twitter', Preprocesser(pprocess_twitter)),
        ('simple', Preprocesser(simple)),
    ])

    dataset['text'] = pp_pipe.fit_transform(dataset['text_raw'])
    return dataset

## Study 1 dataset
def read_study1_dataset():
    df = pd.read_csv('data/new_dataset/moral_values_and_charitable_donation/study_1/dfProcessed',
            sep='\t', error_bad_lines=False)
    df = df[df['PostShare']=='post']
    df = df[df['Action']=='True']

    floats = ['HarmVirtue', 'HarmVice', 'FairnessVirtue', 'FairnessVice','IngroupVirtue', 'IngroupVice',
     'AuthorityVirtue', 'AuthorityVice', 'PurityVirtue', 'PurityVice', 'Morality']
    df[floats] = df[floats].astype(float)

    morality_mean = df['Morality'].mean()

    morals = ['harm', 'fairness', 'ingroup', 'authority', 'purity']
    for moral in morals:
        df[moral] = df[[col for col in floats if col.lower().startswith(moral)]].sum(axis=1)

    df['moral'] = df[morals].idxmax(axis=1)[df['Morality'] > morality_mean]
    df['moral'] = df['moral'].apply(lambda x: x if x in morals else 'non-moral')
    df['moral'] = df['moral'].apply(lambda x: x if x != 'ingroup' else 'loyalty')
    df['moral'] = df['moral'].apply(lambda x: x if x != 'harm' else 'care')
    df['text_raw'] = df['Tweet']
    df['label'] = df['moral']
    dataset = df[['text_raw', 'label']]

    pp_pipe = Pipeline([
        ('twitter', Preprocesser(pprocess_twitter)),
        ('simple', Preprocesser(simple)),
    ])

    dataset['text'] = pp_pipe.fit_transform(dataset['text_raw'])
    return dataset

    return df

## Read Lexicon
moral_label = {'fairness': 'FC', 'loyalty': 'LB', 'care': 'CH', 'purity': 'PD', 'authority': 'AS', 'non-moral': 'NM'}

def _read_moral_lex(moral_df, moral_dict, version):
    moral_lex = dict()
    for moral, df in moral_df.items():
        if version == 'original':
            moral_lex[moral] = df.set_index('LEMMA')
        else:
            moral_lex[moral] = df.set_index('WORD')
        moral_lex[moral] = moral_lex[moral].to_dict()['EXPRESSED_MORAL']
    return moral_lex

def read_moral_lex(version):

    if version == 'original':
        folder_path = 'annotations'
    else:
        folder_path = 'annotations/v{}'.format(version)

    annotations_path = os.path.join(os.path.dirname(__file__), folder_path)
    morals = [os.path.splitext(os.path.basename(file))[0] for file in glob(os.path.join(annotations_path, '*.tsv'))]

    moral_df = dict()
    moral_dict = dict()

    for moral in morals:
        tsv_path = os.path.join(annotations_path, "{}.tsv".format(moral))
        df = pd.read_csv(tsv_path, sep='\t', index_col=False)
        moral_df[moral] = df
        if version == 'original':
            moral_dict[moral] = df['LEMMA'].values
        else:
            moral_dict[moral] = df.index.values

    moral_lex = _read_moral_lex(moral_df, moral_dict, version)

    return moral_lex
