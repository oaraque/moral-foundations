import pytest
import numpy as np
import pandas as pd

from moralstrength import (
    get_available_models, get_available_lexicon_traits, get_available_prediction_traits, lexicon_morals, string_moral_values, string_moral_value, word_moral_value, word_moral_annotations, string_vader_moral, string_average_moral, texts_moral, texts_morals, estimate_morals
)


@pytest.fixture
def example_texts():
    with open('tests/test_examples.txt') as f:
        text = f.readlines()
    text = [t.strip() for t in text]
    return text

def check_prediction(value):
    assert value is not None
    assert isinstance(value, float)
    assert value >= 0
    assert value <= 1

def check_moral_value(value):
    assert value is not None
    assert isinstance(value, float) or isinstance(value, int)
    assert ((value >= 0) and (value <= 9) ) or np.isnan(value)

def check_moral_polarity(value):
    assert value is not None
    assert isinstance(value, float) or isinstance(value, int)
    assert ((value >= -1) and (value <= 1) ) or np.isnan(value)

def check_trait_list(result):
    assert result is not None
    assert isinstance(result, list)
    assert len(result) > 0
    for element in result:
        assert element is not None
        assert isinstance(element, str)

def check_estimation_matrix(result, size):
    assert result.shape[0] > 0
    assert result.shape[0] == size[0]
    assert result.shape[1] > 0
    assert result.shape[1] == size[1]

def test_get_available_models():
    result = get_available_models()
    assert result is not None
    assert isinstance(result, tuple)
    assert len(result) > 0
    for element in result:
        assert element is not None
        assert isinstance(element, str)

def test_get_available_lexicon_traits():
    result = get_available_lexicon_traits()
    check_trait_list(result)

def test_get_available_prediction_traits():
    result = get_available_prediction_traits()
    check_trait_list(result)

def test_lexicon_morals():
    result = lexicon_morals()
    check_trait_list(result)

def test_string_moral_value():
    mytext = "My cat is loyal only to me."
    for moral_trait in get_available_prediction_traits():
        result = string_moral_value(mytext, moral_trait)
        check_prediction(result)

def test_string_moral_values():
    mytext = "My cat is loyal only to me."
    result = string_moral_values(mytext)
    assert isinstance(result, dict)
    for key, value in result.items():
        assert key is not None
        assert isinstance(key, str)
        check_prediction(value)

def test_word_moral_value():
    words = ('loyalty', 'cat', 'dog', 'happiness', 'asdfg')
    for word in words:
        for moral_trait in get_available_lexicon_traits():
            result = word_moral_value(word, moral_trait)
            check_moral_value(result)

def test_word_moral_annotations():
    words = ('loyalty', 'cat', 'dog', 'happiness', 'asdfg')
    for word in words:
        result = word_moral_annotations(word)
        assert isinstance(result, dict)
        for key, value in result.items():
            assert key is not None
            assert isinstance(key, str)
            check_moral_value(value)

def test_string_average_moral():
    text = "My cat is loyal only to me."
    for moral_trait in get_available_lexicon_traits():
        result = string_average_moral(text, moral_trait)
        assert isinstance(result, float)

def test_string_vader_moral():
    text = "My cat is loyal only to me."
    for moral_trait in get_available_lexicon_traits():
        result = string_vader_moral(text, moral_trait)
        assert isinstance(result, float)

def test_texts_moral(example_texts):
    for moral_trait in lexicon_morals():
        result = texts_moral(example_texts, moral_trait, process=True)
        assert len(result) is not 0
        assert len(result) == len(example_texts)
        for moral_trait_estimation in result:
            check_moral_value(moral_trait_estimation)

def test_texts_morals(example_texts):
    result = texts_morals(example_texts)
    assert isinstance(result, np.ndarray)
    check_estimation_matrix(result, (len(example_texts), len(lexicon_morals())))
    for doc in result:
        for doc_pred in doc:
            check_moral_value(doc_pred)

def test_estimate_morals(example_texts):
    result = estimate_morals(example_texts)
    assert isinstance(result, pd.DataFrame)
    check_estimation_matrix(result, (len(example_texts), len(lexicon_morals())))
    for doc in result[lexicon_morals()].values:
        for doc_pred in doc:
            check_moral_value(doc_pred)
