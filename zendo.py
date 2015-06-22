#!/usr/bin/env python3

# Zendo-like game; uses rules.py to construct rules and then lets user test or guess the rule.

from random import choice, shuffle, randint
import re

import rules


# Configuration
########################################################################

NUM_TESTS = lambda d: 3 + int(d/2)
    # Number of words to test when the user claims GOTIT. This is a function of difficulty.


# Global variables
########################################################################

known_words = {}
num_asks = 0
difficulty = None


# Game logic
########################################################################

def test_user_GOTIT():
    """Test the user after he claims GOTIT.
    Returns whether user won (i.e. got all tests right).
    """

    num_tests = NUM_TESTS(difficulty)
    print("You will be asked to judge %s strings. Judge all of them correctly (as the rule would)" % num_tests)
    print("and you win, but get any wrong and you lose.")
    num_to_accept = randint(0, num_tests-2) + 1
        # this ensures we always get at least 1 accepted and 1 rejected, to prevent
        # user from just guessing based on the base rate.
    num_to_reject = num_tests - num_to_accept

    words_to_accept = list(filter(lambda w: w not in known_words, rule.examples_accepted))
    words_to_reject = list(filter(lambda w: w not in known_words, rule.examples_rejected))
    while len(words_to_accept) < num_to_accept or len(words_to_reject) < num_to_reject:
        new_accepted, new_rejected = rules.test_random_words(rule, 100)
        words_to_accept.extend(filter(lambda w: w not in known_words, new_accepted))
        words_to_reject.extend(filter(lambda w: w not in known_words, new_rejected))
    shuffle(words_to_accept)
    shuffle(words_to_reject)
    words_to_test = words_to_accept[:num_to_accept] + words_to_reject[:num_to_reject]
    shuffle(words_to_test)
    assert len(words_to_test) == num_tests

    for word in words_to_test:
        guess = "(none)"
        print()
        while guess not in "AR":
            guess = input("Test this word:  %s\nEnter A to accept, or R to reject: " % word).strip()
        guess = (guess == "A")
        correct_classification = (word in words_to_accept)
        if correct_classification == guess:
            print("Correct.")
        else:
            print("Incorrect! The rule actually " + ("ACCEPTS" if correct_classification else "REJECTS")
                    + " this word.")
            return False
    return True

def main_game_loop():
    """Main loop of the game. User can test string, give up, or claim to know rule.
    Returns True if another round is needed, False otherwise."""
    command = input("\nEnter lowercase string to test, or GIVEUP to give up, or GOTIT if you "
            "think you know the rule.\n> ").rstrip('\n')
    if command == "GIVEUP":
        print("\nThe rule was:  ", str(rule))
        return False
    elif command == "GOTIT":
        if test_user_GOTIT():
            print("\nYOU WIN!! :D")
        else:
            print("\nYou lose :(")

        print("\nThe rule was:  ", str(rule))

        global num_asks
        print("\nDifficulty was %s and you tested %s words." % (difficulty, num_asks))
        print("Known classifications at the time you typed GOTIT were:")
        for k, v in known_words.items():
            print("\t" + k.ljust(30) + " : " + ("accepted" if v else "rejected"))
        return False
    else: # command is a string to test
        if re.match("^[a-z]*$", command) is None: # allows empty string
            print("Invalid. Enter lowercase string consisting of only a-z, or GIVEUP, or GOTIT.")
        else:
            accepted = rule(command)
            known_words[command] = accepted
            print("String %r is:  %s" % (command, ("ACCEPTED" if accepted else "REJECTED")))
            global num_asks
            num_asks += 1
        return True

if __name__ == "__main__":
    difficulty = int(input("Enter rule complexity (2 is easy, 4 is moderate, 7 is difficult, 12 is ridiculous): "))
    print("Generating rule...")
    rule = rules.random_rule(difficulty, top_level=True)
    print("Generated rule.")

    example_accepted = choice(rule.examples_accepted)
    known_words[example_accepted] = True
    example_rejected = choice(rule.examples_rejected)
    known_words[example_rejected] = False
    print("\nExample of ACCEPTED string: %s"   % example_accepted)
    print(  "Example of REJECTED string: %s\n" % example_rejected)

    while main_game_loop():
        pass # loop while it returns True

