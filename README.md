This repo contains two inductive logic games inspired by [Zendo](https://en.wikipedia.org/wiki/Zendo_%28game%29).

Rigid String Zendo
------------------

In Rigid String Zendo, the computer generates a rigid logical rule for accepting or rejecting strings. For instance, "length must be at least 6 xor the string contains the letter 's'". Your job is to figure out the computer's rule by asking it whether various strings are accepted or rejected. Once you think you've induced the rule, the computer will test you.

To run this, ensure that you've [installed Python 3](https://www.python.org/downloads/), then run rigid_string/zendo.py.

Fuzzy String Zendo
------------------

In Fuzzy String Zendo, the computer selects some features of words (for instance, their length, or the fraction of them that's made of vowels) and then devises a "non-rigid" rule which accepts or rejects strings based on those features. This is implemented by training a support vector classifier with a polynomial kernel to reject one random group of words and accept another random group of words.

Again, you try to figure out the rule by asking for the classifications of various strings. But unlike in Rigid String Zendo, you are not asked to classify strings, but rather to provide your credence that each of several strings will be accepted. Your score is the [Bayes score](https://en.wikipedia.org/wiki/Scoring_rule#Logarithmic_scoring_rule) of your beliefs, considered together with the difficulty and the number of strings you asked the computer to classify.

Note that you need to install [Scikit-Learn](http://scikit-learn.org/stable/install.html) to run this. This is in addition to ensuring that you've [installed Python 3](https://www.python.org/downloads/). To run the game, execute fuzzy_string/fuzzy_zendo.py.

Example
-------

Here's an example of me playing a game of Rigid String Zendo, and being a bit of a dumbass:

	> ./rigid_string/zendo.py
	Enter rule complexity (2 is easy, 4 is moderate, 7 is difficult, 12 is ridiculous): 4
	Generating rule...
	Generated rule.

	Example of ACCEPTED string: underwriter
	Example of REJECTED string: n


	Enter lowercase string to test, or GIVEUP to give up, or GOTIT if you think you know the rule.
	> x
	String 'x' is:  REJECTED

	Enter lowercase string to test, or GIVEUP to give up, or GOTIT if you think you know the rule.
	> xxxx
	String 'xxxx' is:  REJECTED

	Enter lowercase string to test, or GIVEUP to give up, or GOTIT if you think you know the rule.
	> xxxxxx
	String 'xxxxxx' is:  REJECTED

	Enter lowercase string to test, or GIVEUP to give up, or GOTIT if you think you know the rule.
	> xxxxxxxxxxx
	String 'xxxxxxxxxxx' is:  ACCEPTED

	Enter lowercase string to test, or GIVEUP to give up, or GOTIT if you think you know the rule.
	> xxxxxxxx
	String 'xxxxxxxx' is:  ACCEPTED

	Enter lowercase string to test, or GIVEUP to give up, or GOTIT if you think you know the rule.
	> xxxxxxx
	String 'xxxxxxx' is:  REJECTED

	Enter lowercase string to test, or GIVEUP to give up, or GOTIT if you think you know the rule.
	> GOTIT
	You will be asked to judge 5 strings. Judge all of them correctly (as the rule would)
	and you win, but get any wrong and you lose.

	Test this word:  unbarred
	Enter A to accept, or R to reject: R
	Incorrect! The rule actually ACCEPTS this word.

	You lose :(

	The rule was:   (length at least 8) or (contains 'i')

	Difficulty was 4 and you tested 6 words.
	Known classifications at the time you typed GOTIT were:
		xxxxxxx                        : rejected
		x                              : rejected
		xxxx                           : rejected
		xxxxxxxx                       : accepted
		n                              : rejected
		underwriter                    : accepted
		xxxxxxxxxxx                    : accepted
		xxxxxx                         : rejected

