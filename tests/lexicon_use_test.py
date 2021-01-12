import pytest
from moralstrength import lexicon_use

def _check_lexicon_size(lex):
    return [len(lex[moral].keys()) for moral in lex.keys()]

original_sizes = _check_lexicon_size(lexicon_use.moral_lex)
new_sizes = _check_lexicon_size(lexicon_use.new_moral_lex)

def test_default_lexicon_selected():
    # default lexicon is latest version
    assert new_sizes == _check_lexicon_size(lexicon_use.current_moral_lex)

def test_select_version():
    # change to original lexicon
    lexicon_use.select_version('original')
    assert original_sizes == _check_lexicon_size(lexicon_use.current_moral_lex)


    # change back to latest version
    lexicon_use.select_version('latest')
    assert new_sizes == _check_lexicon_size(lexicon_use.current_moral_lex)

    # and again to original, just to be sure
    lexicon_use.select_version('original')
    assert original_sizes == _check_lexicon_size(lexicon_use.current_moral_lex)
