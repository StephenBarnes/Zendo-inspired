#!/usr/bin/env python3

from sklearn.svm import SVC

ALL_WORDS = open("words.txt", "r").read().splitlines()
CLASSIFIER = SVC()

CONCRETE_FEATURES = [] # Each feature is a callable object from strings to reals
def register_concrete_feature(f):
    """Registers a concrete feature object."""
    CONCRETE_FEATURES.append(f)
    return f
def register_concrete_feature_class(c):
    """Registers a concrete feature class, by creating one object with no arguments."""
    register_concrete_feature(c())


class Feature(object):
    """Abstract base for feature classes."""
    def __str__(self):
        raise NotImplementedError()
    def __call__(self):
        raise NotImplementedError

@register_concrete_feature
class WordLengthFeature(Feature):
    def __call__(self, string):
        return len(string)

