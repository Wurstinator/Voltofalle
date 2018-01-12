
from pyeda.inter import *
import itertools
import sys

FIELD_SIZE = 5
MAX_VAL = 3
GOOD_VALUES = {2, 3}

# Rules are arrays of length FIELD_SIZE in which each element is a pair (total points, mine count).
# "open_tiles" is a map from (x,y) pairs to values which are already known.
def solve_voltofalle(col_rules, row_rules, open_tiles=dict()):
    # Compute all solutions for the game.
    base_formula = setup_formula(col_rules, row_rules)
    ot_formula = setup_known(open_tiles)
    tf = And(base_formula, ot_formula).tseitin()
    solutions = list(tf.satisfy_all())

    # Convert variable solutions to tile assignments.
    assignments = list(map(sol_to_ass, solutions))

    good_probability = compute_good_tiles(assignments, {2, 3})
    not_bad_probability = compute_good_tiles(assignments, {1, 2, 3})

    print_grid(good_probability)
    print()
    print_grid(not_bad_probability)


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


def sol_to_ass(solution):
    assignment = dict()
    variables = exprvars("x", FIELD_SIZE, FIELD_SIZE, MAX_VAL+1)
    for x in range(FIELD_SIZE):
        for y in range(FIELD_SIZE):
            val = [v for v in range(MAX_VAL+1) if solution[variables[x, y, v]]][0]
            assignment[(x, y)] = val
    return assignment


def compute_good_tiles(assignments, good):
    prob_ass = dict()
    for x in range(FIELD_SIZE):
        for y in range(FIELD_SIZE):
            prob_ass[x, y] = 0
    for ass in assignments:
        for x in range(FIELD_SIZE):
            for y in range(FIELD_SIZE):
                if ass[x, y] in good:
                    prob_ass[x, y] += 1
    for x in range(FIELD_SIZE):
        for y in range(FIELD_SIZE):
            prob_ass[x, y] /= float(len(assignments))
    return prob_ass


def print_grid(prob_ass):
    for y in range(FIELD_SIZE):
        for x in range(FIELD_SIZE):
            p = prob_ass[x, y]
            sys.stdout.write("%.2f\t" % p)
        sys.stdout.write("\n")


# Given a grid consisting of digits 0-9 and dashes, parses the digits into a map that can be passed to solve_voltofalle.
def parse_grid_open_tiles(grid):
    result = dict()
    grid.replace(" ", "")
    grid.replace("\n", "")
    grid.replace("\t", "")
    for i,c in enumerate(grid):
        if c != "-":
            v = int(c)
            x = i % 5
            y = i // 5
            result[(x, y)] = v
    return result


cr = [(5, 2), (6, 2), (6, 2), (2, 3), (7, 1)]
rr = [(3, 3), (3, 3), (6, 1), (7, 1), (7, 2)]
known = \
    "-----" \
    "-----" \
    "----1" \
    "----3" \
    "--3--"
solve_voltofalle(cr, rr, parse_grid_open_tiles(known))