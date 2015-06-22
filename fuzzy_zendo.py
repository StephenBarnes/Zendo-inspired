#!/usr/bin/env python3

from random import choice, shuffle, randint
import re
from math import log

import fuzzy_rules as r

# Configuration
########################################################################

NUM_TESTS = lambda d: 4 + d
    # Number of words to test when the user claims GOTIT. This is a function of difficulty.

NUM_STARTING_EXAMPLES = lambda d: (1 if d == 1 else 2)
    # Number of examples of accepted and rejected (each) to show.
    # This is a function of difficulty.
    # Generally, this shouldn't exceed:
    # r.TRAINING_POINTS_PER_CLASS(d) * r.SENSITIVITY_SPECIFICITY_MINIMUM(d)
    #TODO: extend to find more examples, so this is no longer a problem


# Global variables
########################################################################

known_words = {}
num_asks = 0 # Number of words the user has asked to see the class of.

positive_examples, negative_examples = [], []


# The actual game
########################################################################

difficulty = int(input("Enter difficulty, which is number of features (1 is easy, 3 is moderate, 5 is difficult): "))
print("Generating rule...")
rule = r.random_rule(difficulty)
print("Generated rule.\n")


def ensure_minimum_examples(num):
    global positive_examples
    global negative_examples
    positive_examples = list(filter(lambda w: w not in known_words, positive_examples))
    negative_examples = list(filter(lambda w: w not in known_words, negative_examples))
    while len(positive_examples) < num or len(negative_examples) < num:
        new_accepted, new_rejected = r.test_random_words(rule, 100)
        positive_examples.extend(filter(lambda w: w not in known_words, new_accepted))
        negative_examples.extend(filter(lambda w: w not in known_words, new_rejected))

num_starting_examples = NUM_STARTING_EXAMPLES(difficulty)
ensure_minimum_examples(num_starting_examples)
print("You are given that these string(s) are accepted: ", 
    ", ".join(positive_examples[:num_starting_examples]))
for word in positive_examples[:num_starting_examples]:
    known_words[word] = True
print("You are given that these string(s) are rejected: ", 
    ", ".join(negative_examples[:num_starting_examples]))
for word in negative_examples[:num_starting_examples]:
    known_words[word] = False


def test_user_GOTIT():
    """Test the user after he claims GOTIT.
    Returns the user's log score.
    """

    num_tests = NUM_TESTS(difficulty)
    print("\nYou will be asked to judge %s strings. For each one, enter your belief that the string" % num_tests)
    print("will be accepted, from 0 to 1 (e.g. .5).")
    num_to_accept = randint(0, num_tests-2) + 1
        # this ensures we always get at least 1 accepted and 1 rejected, to prevent
        # user from just guessing based on the base rate.
    num_to_reject = num_tests - num_to_accept

    ensure_minimum_examples(max(num_to_accept, num_to_reject))
    shuffle(positive_examples)
    shuffle(negative_examples)
    words_to_test = positive_examples[:num_to_accept] + negative_examples[:num_to_reject]
    shuffle(words_to_test)
    assert len(words_to_test) == num_tests 

    actually_accepted = []
    probabilities_of_correct = []
    for word in words_to_test:
        print()
        guess = -1
        while True:
            try:
                print("Test this word:  %s" % word)
                guess_str = input("Enter your belief that the true rule accepts this word, "
                    "from 0 to 1: ").strip()
                guess = float(guess_str)
                if guess > 1 or guess < 0:
                    raise ValueError()
                break
            except ValueError: # if user entered something that's not a valid probability
                print("String must represent a valid probability.")
                # try again
        accepted = (word in positive_examples)
        probabilities_of_correct.append(guess if accepted else 1. - guess)
        actually_accepted.append(accepted)

    print("\nThe true rule classified those words as follows respectively:")
    print("\t", ", ".join(map((lambda x: "ACCEPTED" if x else "REJECTED"), actually_accepted)))

    if 0 in probabilities_of_correct:
        log_score = float("-inf")
    else:
        log_score = sum(log(prob) for prob in probabilities_of_correct)

    return log_score


# Main game loop
while True:
    command = input("\nEnter lowercase string to test, or GIVEUP to give up, or GOTIT if you "
            "think you know the rule.\n> ").rstrip('\n')
    if command == "GIVEUP":
        print("\nThe rule was:")
        print(str(rule))
        break
    elif command == "GOTIT":
        log_score = test_user_GOTIT()

        print("\nThe rule was:")
        print(str(rule))

        print("\nYour log score was %s (more is better); guessing .5 each time would have given %s." %
                (round(log_score, 5), round(log(.5) * NUM_TESTS(difficulty), 2)))
        print("Difficulty was %s and you tested %s words." % (difficulty, num_asks))

        print("\nKnown classifications at the time you typed GOTIT were:")
        for k, v in known_words.items():
            print("\t" + k.ljust(30) + " : " + ("accepted" if v else "rejected"))
        break
    else: # command is a string to test
        if re.match("^[a-z]+$", command) is None:
            print("Invalid. Enter nonempty lowercase string consisting of only a-z, or GIVEUP, or GOTIT.")
        else:
            accepted = rule(command)
            known_words[command] = accepted
            print("String %r is:  %s" % (command, ("ACCEPTED" if accepted else "REJECTED")))
            num_asks += 1

