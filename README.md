# MoralStrenght lexicon

This repository contains the MoralStrenght lexicon, which enables researchers to extract the moral valence from a variety of lemmas.
An example of use of the lexicon with Python is:

```
>>> import lexicon_use

>>> lexicon_use.moral_value(word='care', moral='care')
8.8
```


# Moral Foundations Theory predictor

Additionally, this repository contains code and trained models corresponding to the paper "MoralStrength: Exploiting a Moral Lexicon and Embedding Similarity for Moral Foundations Prediction".
Run `Predictor.ipynb` to see a functioning version of the moral foundations predictor.