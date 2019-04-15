# Moral Foundations Theory predictor

Additionally, this repository contains code and trained models corresponding to the paper "MoralStrength: Exploiting a Moral Lexicon and Embedding Similarity for Moral Foundations Prediction".
Run `Predictor.ipynb` to see a functioning version of the moral foundations predictor.

# MoralStrength lexicon

## MoralStrength processed lexicon

This repository contains the MoralStrength lexicon, which enables researchers to extract the moral valence from a variety of lemmas.
It is available under the directory `moralstrength`.
An example of use of the lexicon with Python is:

```python
>>> import lexicon_use

>>> lexicon_use.moral_value(word='care', moral='care')
8.8
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


