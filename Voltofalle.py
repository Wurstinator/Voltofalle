
from probability_assignment import probability_assignment
from entropy import entropy_map
import sys
from constants import *

PRINT_ENTROPY_MAP = True


# Rules are arrays of length FIELD_SIZE in which each element is a pair (total points, mine count).
# "open_tiles" is a map from (x,y) pairs to values which are already known.
def solve_voltofalle(col_rules, row_rules, open_tiles=dict()):
    pa = probability_assignment(col_rules, row_rules, open_tiles)
    print_grid(sum_probass(pa, [2, 3]))
    print()
    print_grid(sum_probass(pa, [1, 2, 3]))
    print()
    if PRINT_ENTROPY_MAP:
        em = entropy_map(col_rules, row_rules, open_tiles)
        print_grid(em)


# Given a probability assignment for single values, returns the prob. assignment for a range of values.
def sum_probass(pa, values):
    result = dict()
    for x in range(FIELD_SIZE):
        for y in range(FIELD_SIZE):
            result[(x, y)] = sum([pa[(x, y, v)] for v in values], 0)
    return result


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


cr = [(3, 3), (5, 1), (6, 1), (3, 3), (7, 0)]
rr = [(2, 3), (5, 1), (6, 1), (6, 1), (5, 2)]
known = \
    "--1-1" \
    "-11-2" \
    "-12-2" \
    "21-21" \
    "-2--1"
solve_voltofalle(cr, rr, parse_grid_open_tiles(known))