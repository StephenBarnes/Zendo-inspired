#!/usr/bin/env python3

from string import ascii_lowercase
from random import choice, shuffle, random
from sklearn.svm import SVC

# Configuration
########################################################################

TRAINING_POINTS_PER_CLASS = lambda d: 3 + d # function of difficulty

NUMBER_OF_FEATURES = lambda d: d # function of difficulty

SENSITIVITY_SPECIFICITY_MINIMUM = lambda d: 1 - (2 / TRAINING_POINTS_PER_CLASS(d))
    # The minimum acceptable sensitivity and specificity for randomly-generated
    # rules. This is a function of difficulty.
    # At the moment this allows at most two false positives and two false negatives.

NUM_RANDOM_RULE_TRIES = 1000

TEST = True # Whether to run various checks and assertions


# Constants and globals
########################################################################

VOWELS = set("aeiou" + choice(["", "y"])) # some rules will consider y to be a vowel!
CONSONANTS = set(ascii_lowercase) - VOWELS

ALL_WORDS = open("words.txt", "r").read().splitlines()

FEATURES = [] # list of Feature objects

class Feature(object):
    def __init__(self, name, probability_weight, function):
        """Feature objects represent some real-valued property of a string.
        `name` is a descriptive unique string.
        `probability_weight` is proportional to how likely the rule is to use
        this feature.
        `function` maps from the string to the real representing the property.
        """
        self.function = function
        self.name = name
        self.probability = probability_weight
    def __call__(self, s):
        return self.function(s)
    def __str__(self):
        return self.name


# Now we create our features
########################################################################

# Create a string-length feature
FEATURES.append(Feature("length", 50, len))

# Features for number of vowels and number of consonants
num_vowels = lambda s: len([c for c in s if c in VOWELS])
FEATURES.append(Feature("number of occurrences of vowels", 7, num_vowels))
if TEST:
    assert FEATURES[-1](("Xu") * 13) == 13
FEATURES.append(Feature("number of occurrences of consonants", 7, lambda s: len(s) - num_vowels(s)))
if TEST:
    assert FEATURES[-1](("Xu") * 13) == 13
# Features for fraction of word that is vowel vs consonant
fraction_vowels = lambda s: num_vowels(s) / len(s)
FEATURES.append(Feature("fraction which is vowels", 7, fraction_vowels))
if TEST:
    assert .49 < FEATURES[-1](("Xu") * 13) < .51
FEATURES.append(Feature("fraction which is consonants", 7, lambda s: 1 - fraction_vowels(s)))
if TEST:
    assert .49 < FEATURES[-1](("Xu") * 13) < .51

# Features for number of occurrences of each individual character
for char in ascii_lowercase:
    FEATURES.append(Feature("number of occurrences of %r" % char, 30 / len(ascii_lowercase),
        lambda s: len([c for c in s if c == char])))
    if TEST:
        assert FEATURES[-1](("X" + char) * 13) == 13
# Features for fraction of word which is each individual character
for char in ascii_lowercase:
    FEATURES.append(Feature("number of occurrences of %r" % char, 30 / len(ascii_lowercase),
        lambda s: len([c for c in s if c == char]) / len(s)))
    if TEST:
        assert .49 < FEATURES[-1](("X" + char) * 13) < .51


# Done creating features, will now write tools
########################################################################

class BadRuleException(Exception):
    pass

class Rule(object):
    """Represents some rule for accepting or rejecting words."""
    def __init__(self, features, words_to_accept, words_to_reject, difficulty):
        """`features`: list of Feature objects
        `words_to_accept`: training points on the 'accept' side of the line
        `words_to_reject`: training points on the 'reject' side of the line
        `difficulty`: game difficulty
        """
        self.features = features
        self.words_to_accept = words_to_accept
        self.words_to_reject = words_to_reject
        self.difficulty = difficulty

        # Train classifier
        design_matrix = [self.feature_vector(word) for word in words_to_accept + words_to_reject]
        outputs = [1] * len(words_to_accept) + [0] * len(words_to_reject)
        self.classifier = SVC(kernel='poly')
            # 'rbf' kernel tends to produce small bubbles of accepted/rejected surrounded by rejected/accepted
        self.classifier.fit(design_matrix, outputs)

        # Check reasonability
        self.true_positives = [word for word in self.words_to_accept if self(word)]
        self.true_negatives = [word for word in self.words_to_reject if not self(word)]
        if not self.reasonable():
            raise BadRuleException("didn't classify examples reasonably")

    def __call__(self, s):
        assert s # else some features could be infinite, and the SVC can't deal with that
        return self.classifier.predict(self.feature_vector(s))[0]

    def feature_vector(self, word):
        return [feature(word) for feature in self.features]

    def __str__(self):
        return ("Rule with feature set (of which likely only some matter):\n\t\t%s\n"
            "\tand successfully trained to accept:\n\t\t%s"
            "\n\tand successfully trained to reject:\n\t\t%s"
            ) %\
                ("\n\t\t".join(str(feature) for feature in self.features),
                        "\n\t\t".join(self.true_positives),
                        "\n\t\t".join(self.true_negatives))

    def reasonable(self):
        """Check that classification is "reasonable" on the samples this rule was
        trained on, i.e. that we really do accept and reject most of the training
        points we're supposed to.
        If this returns False, it's usually because the features are things like
        'contains letter z', and none of our training points contain 'z'."""
        n_true_positives = len(self.true_positives)
        n_false_negatives = len(self.words_to_accept) - n_true_positives
        n_true_negatives = len(self.true_negatives)
        n_false_positives = len(self.words_to_reject) - n_true_negatives

        sensitivity = n_true_positives / (n_true_positives + n_false_negatives)
        specificity = n_true_negatives / (n_true_negatives + n_false_positives)

        if sensitivity < SENSITIVITY_SPECIFICITY_MINIMUM(self.difficulty):
            return False
        if specificity < SENSITIVITY_SPECIFICITY_MINIMUM(self.difficulty):
            return False
        return True

def random_features(num_features):
    """Returns a list of `num_features` distinct features, sampled according
    to the features' probability weights."""
    available_features = FEATURES[:]
    chosen_features = []
    probability_normalizer = sum(feature.probability for feature in FEATURES)
    for i_feature in range(num_features):
        sample_real = random() * probability_normalizer
        for j_feature, feature in enumerate(available_features):
            sample_real -= feature.probability
            if sample_real <= 0:
                chosen_features.append(feature)
                del available_features[j_feature]
                break
        else: # if we never broke out of the for-loop, ie if no feature was chosen
            raise Exception("somehow failed to sample from feature distribution")
        probability_normalizer -= chosen_features[-1].probability
    assert len(chosen_features) == num_features
    return chosen_features

def random_disjoint_subsets(len_each, arr, num_subsets):
    """Returns `num_subsets` disjoint subsets of `arr`, each containing 
    `len_each` elements."""
    assert len_each * num_subsets <= len(arr)
    shuffled_arr = arr[:]
    shuffle(shuffled_arr)
    for i in range(num_subsets):
        yield shuffled_arr[i * len_each : (i+1) * len_each]

def random_rule(difficulty):
    """Returns a random rule, with specified difficulty."""
    for i in range(NUM_RANDOM_RULE_TRIES):
        try:
            words_to_accept, words_to_reject = random_disjoint_subsets(
                    TRAINING_POINTS_PER_CLASS(difficulty), ALL_WORDS, 2)
            features = random_features(NUMBER_OF_FEATURES(difficulty))
            return Rule(features, words_to_accept, words_to_reject, difficulty)
        except BadRuleException:
            pass
        if i > 0 and (i % 50) == 0:
            print ("\tFailed to find a good rule in %s tries. This may take a minute." % i)
    raise Exception("could not generate random rule: every one of the NUM_RANDOM_RULE_TRIES tries failed")

def test_random_words(rule, num_words):
    words_copy = ALL_WORDS[:]
    shuffle(words_copy)
    word_sample = words_copy[:num_words]
    examples_accepted = list(filter(rule, word_sample))
    examples_rejected = list(filter(lambda w: w not in examples_accepted,
        word_sample))
    return examples_accepted, examples_rejected


if __name__ == "__main__":
    rule = random_rule(int(input("difficulty? ")))
    print(rule)
    print(rule.classifier.dual_coef_)
    while True:
        inp = input("> ")
        print(rule(inp))

