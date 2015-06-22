This repo contains two inductive logic games inspired by [Zendo](https://en.wikipedia.org/wiki/Zendo_%28game%29).

Rigid String Zendo
------------------

In Rigid String Zendo, the computer generates a rigid logical rule for accepting or rejecting strings. For instance, "length must be at least 6 xor the string contains the letter 's'". Your job is to figure out the computer's rule by asking it whether various strings are accepted or rejected. Once you think you've induced the rule, the computer will test you.

To run this, ensure that you've [installed Python](https://www.python.org/downloads/), then run rigid_string/zendo.py.

Fuzzy String Zendo
------------------

In Fuzzy String Zendo, the computer selects some features of words (for instance, their length, or the fraction of them that's made of vowels) and then devises a "non-rigid" rule which accepts or rejects strings based on those features. This is implemented by training a support vector classifier with a polynomial kernel to reject one random group of words and accept another random group of words.

Again, you try to figure out the rule by asking for the classifications of various strings. But unlike in Rigid String Zendo, you are not asked to classify strings, but rather to provide your credence that each of several strings will be accepted. Your score is the [Bayes score](https://en.wikipedia.org/wiki/Scoring_rule#Logarithmic_scoring_rule) of your beliefs, considered together with the difficulty and the number of strings you asked the computer to classify.

Note that you need to install [Scikit-Learn](http://scikit-learn.org/stable/install.html) to run this. This is in addition to ensuring that you've [installed Python](https://www.python.org/downloads/). To run the game, execute fuzzy_string/fuzzy_zendo.py.

