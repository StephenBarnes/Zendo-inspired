#!/usr/bin/env python3

from random import choice, randint, shuffle
import string

STRINGS_GENERALLY_LONGER_THAN = 4
STRINGS_GENERALLY_SHORTER_THAN = 10


# Requires file 'words.txt', each of whose lines should be exactly one word consisting of only lowercase letters.
# (Creatable by taking a standard dictionary and doing: :%v/^[a-z]*/d )

ALL_WORDS = open("words.txt", "r").read().splitlines()
REASONABILITY_SAMPLE_SIZE = 1000 # number of words to test when determining whether a rule is reasonable
REASONABILITY_MIN_ACCEPT = 10 # minimum number of words a rule must accept to be "reasonable", out of sample
REASONABILITY_MIN_REJECT = 10 # minimum number of words a rule must reject to be "reasonable", out of sample


concrete_rules = []
def register_concrete_rule(cls):
    """Decorator to register a concrete subclass of Rule.
    This is used when generating random rules."""
    global concrete_rules
    concrete_rules.append(cls)
    return cls


class IncorrectComplexity(Exception):
    pass


class Rule(object):
    """Abstract base class for rules that determine whether strings
    are legal or illegal.
    This is an example of what has been called the "specification
    pattern".
    """
    probability_weight = 0. # this determines how often random_rule()
        # chooses this rule. It's normalized to a categorical
        # distribution over concrete rule classes.
    def __call__(self, s):
        """This should return whether or not the given string
        is legal according to this Rule."""
        raise NotImplementedError("abstract base class")
    @classmethod
    def get_random(cls, complexity):
        """Creates and returns a random instance of this class.
        Resulting rule should have complexity commensurate with
        `complexity`.
        You should implement this in any """
        raise NotImplementedError()
    def reasonable(self):
        """Returns whether this rule is "reasonable", meaning that
        it's suitable for use in the game. This requires that e.g.
        it doesn't accept all strings, nor does it reject all
        strings."""
        words_copy = ALL_WORDS[:]
        shuffle(words_copy)
        word_sample = words_copy[:REASONABILITY_SAMPLE_SIZE]
        accepted = list(filter(self, word_sample))
        num_accepted = len(accepted)
        num_rejected = REASONABILITY_SAMPLE_SIZE - num_accepted
        if num_accepted < REASONABILITY_MIN_ACCEPT:
            return False
        if num_rejected < REASONABILITY_MIN_REJECT:
            return False
        return True

def random_rule(complexity):
    """Generates a random rule, which behaves reasonably, e.g.
    doesn't accept or reject an overwhelming majority of words."""
    if complexity < 1:
        raise IncorrectComplexity()
    while True:
        shuffled_concrete_rules = concrete_rules[:]
        shuffle(shuffled_concrete_rules)
        for concrete_rule in shuffled_concrete_rules:
            try:
                rule = concrete_rule.get_random(complexity)
                if rule.reasonable():
                    return rule
            except IncorrectComplexity:
                pass # try next rule
        print("no good rules found, trying again (be patient)...")

class CombinationRule(Rule):
    """Abstract base class for rules which work by combining two
    simpler rules."""
    name = "(CombinationRule name)"
    combining_complexity = 1 # Complexity of the combination rule itself, added to combinands' complexities
    def combin_func(self, x, y):
        raise NotImplementedError()
    def __init__(self, test1, test2):
        self.test1 = test1
        self.test2 = test2
    def __call__(self, s):
        return self.combin_func(self.test1(s), self.test2(s))
    def __str__(self):
        return "(%s) %s (%s)" % (str(self.test1), self.name, str(self.test2))
    @classmethod
    def get_random(cls, complexity):
        #NOTE: I could implement here a test to prevent, for instance, a combination
        # of two LengthMinimumRules, since that makes no sense.
        if complexity < (1 + 1 + cls.combining_complexity):
            raise IncorrectComplexity()
        # combining takes 1 complexity, then the rest is passed to subrules
        left_complexity = randint(1, complexity - 1 - cls.combining_complexity)
        right_complexity = complexity - cls.combining_complexity - left_complexity
        # We know it's possible to generate a valid rule with these complexities,
        # so keep trying until we do. Else it'll fail and disproportionately
        # generate e.g. single strings of length exactly `complexity`, since
        # that never fails.
        while True:
            try:
                return cls(random_rule(left_complexity),
                        random_rule(right_complexity))
            except IncorrectComplexity:
                pass

@register_concrete_rule
class ConjunctionRule(CombinationRule):
    name = "and"
    def combin_func(self, x, y):
        return x and y

@register_concrete_rule
class DisjunctionRule(CombinationRule):
    name = "or"
    def combin_func(self, x, y):
        return x or y

@register_concrete_rule
class XorRule(CombinationRule):
    name = "xor"
    combining_complexity = 2
    def combin_func(self, x, y):
        return (x or y) and not (x and y)

#TODO implement NOT-rule

def random_str(length):
    """Generates a random *lowercase* string of length `length`."""
    result = ""
    for i in range(length):
        result += choice(string.ascii_lowercase)
    return result

@register_concrete_rule
class ContainmentRule(Rule):
    def __init__(self, substr):
        self.substr = substr
    def __call__(self, s):
        return self.substr in s
    def __str__(self):
        return "string contains %r" % self.substr
    @classmethod
    def get_random(cls, complexity):
        assert complexity >= 1
        return ContainmentRule(random_str(complexity))

@register_concrete_rule
class ContainmentRule(Rule):
    def __init__(self, substr):
        self.substr = substr
    def __call__(self, s):
        return self.substr in s
    def __str__(self):
        return "string contains %r" % self.substr
    @classmethod
    def get_random(cls, complexity):
        assert complexity >= 1
        return ContainmentRule(random_str(complexity))

@register_concrete_rule
class LengthMinimumRule(Rule):
    def __init__(self, limit):
        self.limit = limit
    def __call__(self, s):
        return len(s) >= self.limit
    def __str__(self):
        return "length at least %r" % self.limit
    @classmethod
    def get_random(cls, complexity):
        if complexity != 1:
            raise IncorrectComplexity()
        return LengthMinimumRule(randint(STRINGS_GENERALLY_LONGER_THAN, STRINGS_GENERALLY_SHORTER_THAN - 1))

@register_concrete_rule
class LengthMaximumRule(Rule):
    def __init__(self, limit):
        self.limit = limit
    def __call__(self, s):
        return len(s) <= self.limit
    def __str__(self):
        return "length at most %r" % self.limit
    @classmethod
    def get_random(cls, complexity):
        if complexity != 1:
            raise IncorrectComplexity()
        return LengthMinimumRule(randint(STRINGS_GENERALLY_LONGER_THAN + 1, STRINGS_GENERALLY_SHORTER_THAN))
#TODO remove LengthMaximumRule once you've implemented the NOT-rule

#NOTE maybe implement more rules

if __name__ == "__main__":
    raise Exception("Not intended to be called standalone.")

