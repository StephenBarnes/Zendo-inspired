#!/usr/bin/env python3

import rules as r

print(str(r.random_rule(10)))

# THOUGHTS AT THIS POINT, NOW THAT THE RULE SYSTEM BASICALLY WORKS:

# It'll be way too difficult to generate legal and illegal examples.

# Maybe instead of strings, use numbers?
#	Con: Numbers are less interesting than strings.
#	Will numbers actually be easier to generate examples and counterexamples for?
#		Yes, because we can eg keep the entire range 1..1000, then sieve it!
#			and discard rules that disobey all 

# Maybe instead of strings or numbers, use 3-number sequences!
# Like the classic 2-4-6 example of positive bias.
# This is feasible. Eg each in range 1..100 means we need to keep a sieve of 10^6 entries.
#	But it's probably not feasible to keep a list of all rules' legal sequences, right?
# Maybe even limit the range to 1..10, so the sequence space size is 1000.
#	Then if we have 10^6 rules, we need 10^9 space to store all sequence sets.

# Idea: maybe keep a list of ALL rules, then you can produce "differentiating cases" to quiz the person on
# to see if they really did get the right rule, or if they failed.


