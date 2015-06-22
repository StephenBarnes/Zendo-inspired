#!/usr/bin/env python3

from random import choice, randint, shuffle, random
import string

STRINGS_GENERALLY_LONGER_THAN = 4
STRINGS_GENERALLY_SHORTER_THAN = 10


# Requires file 'words.txt', each of whose lines should be exactly one word consisting of only lowercase letters.
# (Creatable by taking a standard dictionary and doing: :%v/^[a-z]*/d )

ALL_WORDS = open("words.txt", "r").read().splitlines()
REASONABILITY_SAMPLE_SIZE = 1000 # number of words to test when determining whether a rule is reasonable
REASONABILITY_MIN_ACCEPT = 10 # minimum number of words a rule must accept to be "reasonable", out of sample
REASONABILITY_MIN_REJECT = 10 # minimum number of words a rule must reject to be "reasonable", out of sample

NUM_TRIES = 100 # number of times to try generating various rules randomly before giving up


concrete_rules = []
def register_concrete_rule(cls):
    """Decorator to register a concrete subclass of Rule.
    This is used when generating random rules."""
    global concrete_rules
    concrete_rules.append(cls)
    return cls


class IncorrectComplexity(Exception):
    """Raised when some rule failed to be created because it was given
    a complexity too small or too big."""
    pass

class StructureError(Exception):
    """Raised when the rule tree has some bad construction, e.g. when
    we create a "NOT (NOT (X))" rule (because then we should rather
    just have "X")."""
    pass

def test_random_words(rule, num_words):
    words_copy = ALL_WORDS[:]
    shuffle(words_copy)
    word_sample = words_copy[:num_words]
    examples_accepted = list(filter(rule, word_sample))
    examples_rejected = list(filter(lambda w: w not in examples_accepted,
        word_sample))
    return examples_accepted, examples_rejected

class Rule(object):
    """Abstract base class for rules that determine whether strings
    are legal or illegal.
    This is an example of what has been called the "specification
    pattern".
    """
    probability_weight = .5 # this determines how often random_rule()
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
        self.examples_accepted, self.examples_rejected = test_random_words(self, REASONABILITY_SAMPLE_SIZE)
            # (we store these as properties because we'll need them later if we use this rule)
        num_accepted = len(self.examples_accepted)
        num_rejected = len(self.examples_rejected)
        if len(self.examples_accepted) < REASONABILITY_MIN_ACCEPT:
            return False
        if len(self.examples_rejected) < REASONABILITY_MIN_REJECT:
            return False
        return True

def random_rule(complexity, forbidden_classes=None, top_level=False):
    """Generates a random rule, which behaves reasonably, e.g.
    doesn't accept or reject an overwhelming majority of words."""
    #print("random_rule complexity ", complexity)
    if complexity < 1:
        raise IncorrectComplexity()
    if forbidden_classes is None:
        forbidden_classes = []
    legal_concrete_rules = [rule for rule in concrete_rules if rule not in forbidden_classes]
    def get_rule():
        normalizing_const = sum(rule.probability_weight for rule in concrete_rules\
                if rule not in forbidden_classes)
        x = random() * normalizing_const
        shuffle(legal_concrete_rules)
        for rule in legal_concrete_rules:
            if x <= rule.probability_weight:
                #print(rule)
                return rule
            x -= rule.probability_weight
        raise Exception("categorical distribution sampling failed somehow")
    try_limit = (1000 if top_level else 100)
    for try_num in range(1, try_limit):
        concrete_rule = get_rule()
        try:
            #print(concrete_rule)
            ret_rule = concrete_rule.get_random(complexity)
            if ret_rule.reasonable():
                return ret_rule
        except (IncorrectComplexity, StructureError):
            pass # try next rule
        if top_level:
            if try_num == 1:
                print("\tno good rules found, trying again (may take several tries)...")
            else:
                print("\ttry %r..." % try_num)
    raise IncorrectComplexity("could not generate legal rule")

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
        for i in range(NUM_TRIES):
            try:
                left_part = random_rule(left_complexity)
                right_part = random_rule(right_complexity, cls.forbidden_classes().get(left_part.__class__, []))
                return cls(left_part, right_part)
            except (IncorrectComplexity, StructureError):
                continue
        raise IncorrectComplexity()
    def forbidden_classes():
        """Returns a dict mapping from the class of the left subtree to a list
        of classe the right subtree can't have.
        Has to be a function, not a property, because else we have to change
        ordering of classes."""
        return {LengthMinimumRule: [LengthMinimumRule]
                }

@register_concrete_rule
class ConjunctionRule(CombinationRule):
    name = "and"
    probability_weight = .2
    combining_complexity = 1
    def forbidden_classes():
        return {LengthMinimumRule: [LengthMinimumRule]
                }
    def combin_func(self, x, y):
        return x and y

@register_concrete_rule
class DisjunctionRule(CombinationRule):
    name = "or"
    probability_weight = .2
    combining_complexity = 1
    def forbidden_classes():
        return {LengthMinimumRule: [LengthMinimumRule]
                }
    def combin_func(self, x, y):
        return x or y

@register_concrete_rule
class XorRule(CombinationRule):
    name = "xor"
    combining_complexity = 2
    probability_weight = .1
    def combin_func(self, x, y):
        return (x or y) and not (x and y)

@register_concrete_rule
class NegationRule(Rule):
    """Rule that negates some other rule."""
    probability_weight = .4
    complexity_cost = 0 # no complexity cost
    def __init__(self, test):
        self.test = test
    def __call__(self, s):
        return not self.test(s)
    def __str__(self):
        return "not (%s)" % str(self.test)
    @classmethod
    def get_random(cls, complexity):
        # a NegationRule takes zero complexity.
        forbidden_classes = [NegationRule, LengthMinimumRule, ConjunctionRule, DisjunctionRule,
                XorRule]
            # Disallow CombinationRules - e.g. we rather represent not(A and B) as (not A) or (not B)
        for i in range(NUM_TRIES):
            try:
                subrule = random_rule(complexity - cls.complexity_cost, forbidden_classes)
                return cls(subrule)
            except (IncorrectComplexity, StructureError):
                pass
        raise IncorrectComplexity()

def random_str(length):
    """Generates a random *lowercase* string of length `length`."""
    result = ""
    for i in range(length):
        result += choice(string.ascii_lowercase)
    return result

@register_concrete_rule
class LengthMinimumRule(Rule):
    probability_weight = .3
    def __init__(self, limit):
        self.limit = limit
    def __call__(self, s):
        return len(s) >= self.limit
    def __str__(self):
        return "length at least %r" % self.limit
    @classmethod
    def get_random(cls, complexity):
        if not (1 <= complexity <= 2):
            raise IncorrectComplexity()
        return cls(randint(STRINGS_GENERALLY_LONGER_THAN, STRINGS_GENERALLY_SHORTER_THAN))
# note that a NegationRule with a LengthMinimumRule is effectively a LengthMaximumRule, so no need
# to implement that

class SubstringRule(Rule):
    """Abstract base for rules which involve some operation
    with a substring."""
    probability_weight = .4
    complexity_cost = 0 # Complexity cost is this plus substring length
    length_max = 3 # Maximum permissible length of the substring
    def __init__(self, substr): 
        self.substr = substr
    def __call__(self, s):
        raise NotImplementedError("abstract base class")
    def __str__(self):
        raise NotImplementedError("abstract base class")
    @classmethod
    def get_random(cls, complexity):
        if complexity < 1 + cls.complexity_cost:
            raise IncorrectComplexity()
        if complexity - cls.complexity_cost > cls.length_max:
            raise IncorrectComplexity() #we don't want substrings longer than 3, else
                # the rule is usually something like (string contains 'qjke') or (length
                # at least 3), which is bad because that substring is *never* in the
                # string.
        return cls(random_str(complexity - cls.complexity_cost))

@register_concrete_rule
class ContainmentRule(SubstringRule):
    """Rule: string must contain some substring."""
    probability_weight = .4
    def __call__(self, s):
        return self.substr in s
    def __str__(self):
        return "contains %r" % self.substr

@register_concrete_rule
class PrefixRule(SubstringRule):
    """Rule: String must start with some substring."""
    probability_weight = .2
    length_max = 2
    def __call__(self, s):
        return s.startswith(self.substr)
    def __str__(self):
        return "starts with %r" % self.substr

@register_concrete_rule
class SuffixRule(SubstringRule):
    """Rule: String must end with some substring."""
    probability_weight = .2
    length_max = 2
    def __call__(self, s):
        return s.endswith(self.substr)
    def __str__(self):
        return "ends with %r" % self.substr

#NOTE maybe implement more rules

if __name__ == "__main__":
    raise Exception("Not intended to be called standalone.")

