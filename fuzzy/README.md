Fuzzy String Zendo
========================================================================

An inductive logic game inspired by [Zendo](https://en.wikipedia.org/wiki/Zendo_%28game%29). The computer devises a fuzzy rule which accepts or rejects strings; for instance "accepted strings tend to be long but contain few vowels". (This is implemented as a SVC on some features of the word.)

Then you ask the computer to classify some strings. Once you think you roughly understand the rule, the computer tests your understanding by asking you how strongly you believe that it'll accept each of several strings. Your score is the [Bayes score](https://en.wikipedia.org/wiki/Scoring_rule#Logarithmic_scoring_rule) of your beliefs, considered together with the difficulty and the number of strings you asked the computer to classify.


How to run
----------

Ensure that you've [installed Python](https://www.python.org/downloads/), and that you've [installed Scikit-Learn](http://scikit-learn.org/stable/install.html), then run fuzzy_zendo.py.
