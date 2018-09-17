
from pyeda.inter import *
import itertools
from constants import *


# Sets up the formula describing our problem.
def setup_formula(col_rules, row_rules):
    variables = exprvars("x", FIELD_SIZE, FIELD_SIZE, MAX_VAL+1)

    # First: Make sure that every tile has at least one value.
    a = formula_tiles_hasval(variables)

    # Second: Make sure that every tile has at most one value.
    b = formula_tiles_unique(variables)

    # Second: Make sure that the column rules are satisfied.
    col_fs = []
    for x in range(FIELD_SIZE):
        rule = col_rules[x]
        relevant_vars = []
        for y in range(FIELD_SIZE):
            vars = []
            for v in range(MAX_VAL+1):
                vars.append(variables[(x, y, v)])
            relevant_vars.append(vars)
        col_fs.append(setup_sum_rule(rule, relevant_vars))

    # Second: Make sure that the column rules are satisfied.
    row_fs = []
    for y in range(FIELD_SIZE):
        rule = row_rules[y]
        relevant_vars = []
        for x in range(FIELD_SIZE):
            vars = []
            for v in range(MAX_VAL + 1):
                vars.append(variables[(x, y, v)])
            relevant_vars.append(vars)
        row_fs.append(setup_sum_rule(rule, relevant_vars))

    return And(a, b, *col_fs, *row_fs)


# Setup a sentence which makes sure that every tile has at least one value.
def formula_tiles_hasval(variables):
    clauses = []
    for x in range(FIELD_SIZE):
        for y in range(FIELD_SIZE):
            clauses.append(Or(*[variables[x, y, v] for v in range(MAX_VAL+1)]))
    return And(*clauses)


# Setup a sentence which makes sure that every tile has at most one value.
def formula_tiles_unique(variables):
    clauses = []
    for x in range(FIELD_SIZE):
        for y in range(FIELD_SIZE):
            for v1 in range(MAX_VAL+1):
                for v2 in range(MAX_VAL+1):
                    if v1 != v2:
                        clauses.append(Or(Not(variables[x, y, v1]), Not(variables[x, y, v2])))
    return And(*clauses)


# Setup a sentence which makes sure that a row/column satisfies its constraints.
def setup_sum_rule(rule, vars):
    # Set up a set of lists in which each list corresponds to tile assignments satisfying the constraint.
    points, mines = rule
    sums = sum_possibilities(FIELD_SIZE - mines, 1, MAX_VAL, points)
    simple_rows = map((lambda x: ([0] * mines) + x), sums)
    possibilities = set(itertools.chain.from_iterable(map(itertools.permutations, simple_rows)))

    # Convert the lists into clauses.
    variables = map((lambda x: [vars[i][j] for i, j in enumerate(x)]), possibilities)
    clauses = list(map(lambda x: And(*x), variables))
    return Or(*clauses)


# Iterates through all arrays of size N that contain values from A to B and sum to S.
def sum_possibilities(N, A, B, S):
    if N == 0:
        return
    if N == 1:
        if A <= S <= B:
            yield [S]
        else:
            return

    for x in range(A, B+1):
        for subp in sum_possibilities(N-1, A, B, S-x):
            yield [x] + subp


# Creates a formula for the already known values.
def setup_known(open_tiles):
    variables = exprvars("x", FIELD_SIZE, FIELD_SIZE, MAX_VAL + 1)
    clauses = []
    for (x, y) in open_tiles.keys():
        c = variables[x, y, open_tiles[(x, y)]]
        clauses.append(c)
    return And(*clauses)

