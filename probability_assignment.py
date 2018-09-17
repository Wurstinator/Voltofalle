
from pyeda.inter import *
from sat_model import setup_formula, setup_known
from constants import *


# Rules are arrays of length FIELD_SIZE in which each element is a pair (total points, mine count).
# "open_tiles" is a map from (x,y) pairs to values which are already known.
# Returns a map from (x,y,v) to probability that (x,y) has that given value.
def probability_assignment(col_rules, row_rules, open_tiles=dict()):
    base_formula = setup_formula(col_rules, row_rules)
    ot_formula = setup_known(open_tiles)
    tf = And(base_formula, ot_formula).tseitin()
    return compute_probass(tf)


# Uses the formula that was set up to describe the problem and returns a probability assignment for its solutions.
def compute_probass(formula):
    solutions = list(formula.satisfy_all())
    assignments = list(map(sol_to_ass, solutions))
    return make_prob_assignments(assignments)


# Given a Picosat solution (i.e. an assignment of variables), creates an assignment as a map from (x,y) to values.
def sol_to_ass(solution):
    assignment = dict()
    variables = exprvars("x", FIELD_SIZE, FIELD_SIZE, MAX_VAL+1)
    for x in range(FIELD_SIZE):
        for y in range(FIELD_SIZE):
            val = [v for v in range(MAX_VAL+1) if solution[variables[x, y, v]]][0]
            assignment[(x, y)] = val
    return assignment


# Given a list of all possible assignments, creates a probability map.
def make_prob_assignments(assignments):
    result = dict()
    for x in range(FIELD_SIZE):
        for y in range(FIELD_SIZE):
            for v in range(MAX_VAL+1):
                result[(x, y, v)] = 0
    for a in assignments:
        for x in range(FIELD_SIZE):
            for y in range(FIELD_SIZE):
                result[(x, y, a[(x, y)])] += 1
    for x in range(FIELD_SIZE):
        for y in range(FIELD_SIZE):
            for v in range(MAX_VAL+1):
                result[(x, y, v)] /= len(assignments)
    return result
