# Moral Foundations Theory predictor and lexicon

This repository contains code and trained models corresponding to the paper "MoralStrength: Exploiting a Moral Lexicon and Embedding Similarity for Moral Foundations Prediction".
Run `Predictor.ipynb` to see a functioning version of the moral foundations predictor. Keep reading for some examples of use below.

## Install

The software is written in Python 3. For installing, please use `pip`:

```
pip install moralstrength
```

## GUI

This repository is intended for users that are willing to use the software through Python.
Alternatively, we have published a Graphical Interface that works on Linux, MacOS, and Windows. Please visit [this repository](https://github.com/oaraque/moral-foundations-gui).

# MoralStrength lexicon

## MoralStrength processed lexicon

This repository contains the MoralStrength lexicon, which enables researchers to extract the moral valence from a variety of lemmas.
It is available under the directory `moralstrength_annotations`.
An example of use of the lexicon with Python is:

```python
>>> import moralstrength

>>> moralstrength.word_moral_values('care')
{'care': 8.8, 'fairness': -1, 'loyalty': -1, 'authority': -1, 'purity': -1}
```

## MoralStrength presence

Also, this repository contains several already-trained models that predict the presence of a certain moral trait.
That is, whether the analyzed text is relevant for a moral trait, or not.
A minimal example of use:

```python
import moralstregnth

text = "PLS help #HASHTAG's family. No one prepares for this. They are in need of any assistance you can offer"  

moralstrength.string_moral_value(text, moral='care')
```
         
You can check the available moral traits using the `moralstrength.get_available_prediction_traits` method.
The complete list of methods that can be used is shown in the next section.
         
## List of methods to use

The methods that are under `moralstrength.moralstrength` are the following:
```
get_available_lexicon_traits()
    Returns a list of traits that were annotated and can be queried
    by word_moral_value().
    care: Care/Harm
    fairness: Fairness/Cheating
    loyalty: Loyalty/Betrayal
    authority: Authority/Subversion
    purity: Purity/Degradation

get_available_models()
    Returns a list of available models for predicting texts.
    Short explanation of names:
    unigram: simple unigram-based model
    count: number of words that are rated as closer to moral extremes
    freq: distribution of moral ratings across the text
    simon: SIMilarity-based sentiment projectiON
    or a combination of these.
    For a comprehensive explanation of what each model does and how it performs on
    different datasets, see https://arxiv.org/abs/1904.08314
    (published at Knowledge-Based Systems).

get_available_prediction_traits()
    Returns a list of traits that can be predicted by string_moral_value()
    or file_moral_value().
    care: Care/Harm
    fairness: Fairness/Cheating
    loyalty: Loyalty/Betrayal
    authority: Authority/Subversion
    purity: Purity/Degradation
    non-moral: Tweet/text is non-moral

string_average_moral(text, moral)
    Returns the average of the annotations for the words in the sentence (for one moral).
    If no word is recognized/found in the lexicon, returns -1.
    Words are lemmatized using spacy.

string_moral_value(text, moral, model='unigram+freq')
    Returns the estimated probability that the text is relevant to either a vice or
    virtue of the corresponding moral trait.
    The default model is unigram+freq, the best performing (on average) across all
    dataset, according to our work.
    For a list of available models, see get_available_models().
    For a list of traits, get_available_prediction_traits().

string_moral_values(text, model='unigram+freq')
    Returns the estimated probability that the text is relevant to vices or virtues
    of all moral traits, as a dict.
    The default model is unigram+freq, the best performing (on average) across all
    dataset, according to our work.
    For a list of available models, see get_available_models().
    For a list of traits, get_available_prediction_traits().

word_moral_value(word, moral)
    Returns the association strength between word and moral trait,
    as rated by annotators. Value ranges from 1 to 9.
    1: words closely associated to harm, cheating, betrayal, subversion, degradation
    9: words closely associated to care, fairness, loyalty, authority, sanctity
    If the word is not in the lexicon of that moral trait, returns -1.
    For a list of available traits, get_available_lexicon_traits()

word_moral_values(word)
    Returns a dict that gives the association strength between word and every
    moral trait, as rated by annotators. Value ranges from 1 to 9.
    1: words closely associated to harm, cheating, betrayal, subversion, degradation
    9: words closely associated to care, fairness, loyalty, authority, purity/sanctity
    If the word is not in the lexicon of that moral trait, returns -1.
```
## MoralStrength raw lexicon

The `moralstrength_raw` folder contains the raw annotations collected from figure-eight.
The folder all_annotators_except_failed contains all the annotations collected, except for the annotators that failed the task (see the paper for details on the control questions, which were based on valence ratings from Warriner et al.).
The folder filtered_annotators contains the annotations after the annotators with low inter-annotator agreement were removed.

The filename is `RAW_ANNOTATIONS_[MORAL]`, where MORAL is the moral trait considered and can either be AUTHORITY, CARE, FAIRNESS, LOYALTY or PURITY.

The fields in each file are:
- WORD	the word to be annotated
- ANNOTATOR_ID	the unique ID of each annotator
- VALENCE	the valence rating of WORD, on a scale from 1 (low) to 9 (high)
- AROUSAL	the arousal rating of WORD, on a scale from 1 (low) to 9 (high)
- RELEVANCE	whether WORD is related to the MORAL
- EXPRESSED_MORAL	the moral strength of WORD, i.e. whether it is closer to one or the other extremes pertaining the MORAL trait.

The numbers for EXPRESSED_MORAL range from 1 to 9, and the extremes of the scales are:
- 1=Subversion, 9=Authority for AUTHORITY
- 1=Harm, 9=Care for CARE
- 1=Proportionality, 9=Fairness for FAIRNESS
- 1=Disloyalty, 9=Loyalty for LOYALTY
- 1=Degradation, 9=Purity for PURITY

For privacy reason, the annotator ID has been salted and hashed, so that going back to the original annotator ID is not possible, but it is still possible to track each annotator's ratings across the different morals.

## MoralStrength annotation task descriptions

In the folder `moralstrength/tasks` we also include the original description of the annotation tasks for the crowdsourcing process.
The interested reader can consult the instructions given to the human annotators.


