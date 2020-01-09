import pytest
import numpy as np

from moralstrength import (
    get_available_models, get_available_lexicon_traits, get_available_prediction_traits, string_moral_values, string_moral_value, word_moral_value, word_moral_annotations
)


def check_prediction(value):
    assert value is not None
    assert isinstance(value, float)
    assert value >= 0
    assert value <= 1

def check_moral_value(value):
    assert value is not None
    assert isinstance(value, float) or isinstance(value, int)
    assert ((value >= 0) and (value <= 9) ) or np.isnan(value)

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
    assert result is not None
    assert isinstance(result, list)
    assert len(result) > 0
    for element in result:
        assert element is not None
        assert isinstance(element, str)

def test_get_available_prediction_traits():
    result = get_available_prediction_traits()
    assert result is not None
    assert isinstance(result, list)
    assert len(result) > 0
    for element in result:
        assert element is not None
        assert isinstance(element, str)

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
