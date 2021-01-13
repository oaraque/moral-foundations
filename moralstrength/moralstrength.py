from moralstrength import lexicon_use
from moralstrength.estimators import estimate,models
from moralstrength.moral_list import moral_options_lexicon, moral_options_predictions
import math
import numpy as np
import pandas as pd
import spacy

try:
    nlp = spacy.load("en_core_web_sm")
    nlp_reduced = spacy.load("en_core_web_sm", disable=["tagger", "parser", "ner"])
except OSError as error:
    if "Can't find model 'en_core_web_sm'" in error.args[0]:
        print('Downloading files required by the Spacy language processing library (this is only required once)')
        spacy.cli.download('en_core_web_sm')
    nlp = spacy.load("en_core_web_sm")
    nlp_reduced = spacy.load("en_core_web_sm", disable=["tagger", "parser", "ner"])


def word_moral_value(word, moral, normalized=False):
    """Returns the association strength between word and moral trait,
       as rated by annotators. Value ranges from 1 to 9.
       1: words closely associated to vices: harm, cheating, betrayal, subversion, degradation
       9: words closely associated to virtues: care, fairness, loyalty, authority, sanctity
       normalized=True will normalize each annotation in the range -1 (vice) to +1 (virtue)
       If the word is not in the lexicon of that moral trait, returns NaN.
       For a list of available traits, get_available_lexicon_traits()
       """

    if moral not in moral_options_lexicon:
        raise ValueError('Invalid moral trait "{}" specified. Valid traits are: {}'.format(moral,moral_options_lexicon))
    return lexicon_use.moral_value(word=word, moral=moral, normalized=normalized)


def word_moral_annotations(word, normalized=False):
    """Returns a dict that gives the association strength between word and every
       moral trait, as rated by annotators. Value ranges from 1 to 9.
       1: words closely associated to harm, cheating, betrayal, subversion, degradation
       9: words closely associated to care, fairness, loyalty, authority, purity/sanctity
       normalized=True will normalize each annotation in the range -1 (vice) to +1 (virtue)
       If the word is not in the lexicon of that moral trait, returns NaN."""

    return {moral: lexicon_use.moral_value(word=word, moral=moral, normalized=normalized) for moral in moral_options_lexicon}


def string_average_moral(text,moral):
    """Returns the average of the annotations for the words in the sentence (for one moral).
       If no word is recognized/found in the lexicon, returns -1.
       Words are lemmatized using spacy.
       """

    # TODO: add new metric

    sum = 0
    recognized_words_no = 0
    for token in nlp(text):
        lemma = token.lemma_
        value = word_moral_value(lemma,moral)
        #print("lemma: {}".format(lemma))
        if value>-1:
            sum += value
            recognized_words_no += 1
    if recognized_words_no == 0:
        return float('NaN')
    else:
        return sum/recognized_words_no


def string_vader_moral(text,moral,alpha=15):
    """Returns a normalized annotation score for the words in the sentence (for one moral).
       Score ranges from -1 (vices) to 1 (virtues) and is calculated as in VADER (Hutto and Gilbert, 2014).
       The optional alpha parameter defines how quickly the score maxes out (to 1 or -1),
       and can be tweaked (e.g. for very long texts it *might* be more sensible to set it to 150; 15 is the default taken from VADER).
       If no word is recognized/found in the lexicon, returns NaN.
       Text is lemmatized using spacy.
       """
    score = 0
    recognized_words_no = 0
    for token in nlp(text):
        lemma = token.lemma_
        value = word_moral_value(lemma,moral,normalized=True)
        if not math.isnan(value):
            score += value
            recognized_words_no += 1
    if recognized_words_no == 0:
        return float('NaN')
    else:
        return score/math.sqrt((score*score) + alpha)

def texts_moral(texts, moral, process=False):
    """Estimates the moral value of the selected moral trait
       for a list of documents. The list could contain only one
       document, or many. The process parameter (by default False)
       controls whether each document is processed with spacy,
       performing the lemmatization. If no moral value is found,
       the document is estimated a NaN value. Estimation is done
       using the lexicon annotations, with no learning whatsoever.
    """
    Sums = []
    if process:
        docs = list(nlp_reduced.pipe(texts))
    else:
        docs = texts
    for doc in docs:
        result = None
        summ = 0
        recognized_words_no = 0
        for token in doc:
            lemma = token.lemma_
            value = word_moral_value(lemma, moral)
            if value>-1:
                summ += value
                recognized_words_no += 1
            if recognized_words_no == 0:
                result = float('NaN')
            else:
                result = summ/recognized_words_no
        Sums.append(result)

    return Sums

def texts_morals(texts):
    """An useful wrapper for the texts_moral function. Estimates
       all available moral values for a list of text. Returns a numpy
       array with 2 dimensions (number of documents x number of moral traits).
       The order of moral traits is found by executing the method lexicon_morals.
    """
    S = []
    docs = list(nlp_reduced.pipe(texts))
    for moral in lexicon_morals():
        sums = texts_moral(docs, moral, process=False)
        S.append(sums)
    return np.array(S).T

def estimate_morals(texts):
    """Wrapper of the texts_morals function. It returns the moral estimation in a
    Pandas DataFrame, being the columns the morals, and the rows the different documents.
    This should be the method used analyzing text without using any machine learning. It uses
    only the annotations of the lexicon.
    """
    estimation = texts_morals(texts)
    estimation = pd.DataFrame(columns=lexicon_morals(), data=estimation)
    return estimation


def get_available_models():
    """Returns a list of available models for predicting texts.
       Short explanation of names:
       unigram: simple unigram-based model
       count: number of words that are rated as closer to moral extremes
       freq: distribution of moral ratings across the text
       simon: SIMilarity-based sentiment projectiON
       or a combination of these.
       For a comprehensive explanation of what each model does and how it performs on
       different datasets, see https://arxiv.org/abs/1904.08314
       (published at Knowledge-Based Systems)."""

    return models

def get_available_lexicon_traits():
    """Returns a list of traits that were annotated and can be queried
       by word_moral_value().
       care: Care/Harm
       fairness: Fairness/Cheating
       loyalty: Loyalty/Betrayal
       authority: Authority/Subversion
       purity: Purity/Degradation
       """

    return moral_options_lexicon

def lexicon_morals():
    """Syntactic sugar call to get_available_lexicon_traits.
       """

    return get_available_lexicon_traits()


def get_available_prediction_traits():
    """Returns a list of traits that can be predicted by string_moral_value()
       or file_moral_value().
       care: Care/Harm
       fairness: Fairness/Cheating
       loyalty: Loyalty/Betrayal
       authority: Authority/Subversion
       purity: Purity/Degradation
       non-moral: Tweet/text is non-moral
       """

    return moral_options_predictions

def string_moral_value(text,moral,model='unigram+freq'):
    """Returns the estimated probability that the text is relevant to either a vice or
       virtue of the corresponding moral trait.
       The default model is unigram+freq, the best performing (on average) across all
       dataset, according to our work.
       For a list of available models, see get_available_models().
       For a list of traits, get_available_prediction_traits().
    """

    if model not in models:
        raise ValueError('Invalid model "{}" specified. Valid models are: {}'.format(model,models))
    if moral not in moral_options_predictions:
        raise ValueError('Invalid moral trait "{}" specified. Valid traits are: {}'.format(moral,moral_options_predictions))
    return estimate(text, moral=moral, model=model)[0]

def string_moral_values(text,model='unigram+freq'):
    """Returns the estimated probability that the text is relevant to vices or virtues
       of all moral traits, as a dict.
       The default model is unigram+freq, the best performing (on average) across all
       dataset, according to our work.
       For a list of available models, see get_available_models().
       For a list of traits, get_available_prediction_traits().
    """

    if model not in models:
        raise ValueError('Invalid model "{}" specified. Valid models are: {}'.format(moral,models))
    return {moral: estimate(text=text, moral=moral, model=model)[0] for moral in moral_options_predictions}

# def file_moral_value(filename,trait,model):
#   if model not in models:
#       raise ValueError('Invalid model "{}" specified. Valid models are: {}'.format(model,models))
#   if moral not in moral_options_predictions:
#       raise ValueError('Invalid moral trait "{}" specified. Valid traits are: {}'.format(moral,moral_options_predictions))
#
#   return
#
# def file_moral_values(filename,model):
#   if model not in models:
#       raise ValueError('Invalid model "{}" specified. Valid models are: {}'.format(model,models))
#   return
